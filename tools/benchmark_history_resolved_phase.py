from __future__ import annotations

import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _hr_repo_root() -> Path:
    return _repo_root().parent / "History-Resolved-Phase-as-a-State-Variable-in-Adaptive-Complex-Networks"


def _make_network(mode: str, **param_kwargs):
    from hrphasenet.graphs import diamond_graph
    from hrphasenet.network import AdaptiveNetwork, NetworkParams

    edges, source, sink = diamond_graph()
    params = NetworkParams(**param_kwargs)
    return AdaptiveNetwork(
        edges=edges,
        n_nodes=4,
        source_node=source,
        sink_node=sink,
        params=params,
        mode=mode,
        seed=99,
    )


def _history_protocol_pair(mode: str, *, omega_end: float = 20.0, pi_0: float = math.pi / 2.0):
    from hrphasenet.drives import chirp_drive, constant_drive

    def make_net():
        return _make_network(
            mode,
            dt=0.01,
            alpha_0=1.0,
            S_c=0.1,
            delta_S=0.1,
            mu_0=0.2,
            S_0=1.0,
            S_eq=0.0,
            alpha_pi=0.3,
            mu_pi=0.1,
            pi_0=pi_0,
        )

    net_a = make_net()
    net_b = make_net()

    for value in constant_drive(1.0 + 0j, 30):
        net_a.step(value)
        net_b.step(value)

    extra_chirp = list(chirp_drive(1.0, omega_start=2.0, omega_end=omega_end, dt=0.01, n_steps=50))
    same_const = list(constant_drive(1.0 + 0j, 50))
    for value_a, value_b in zip(same_const, extra_chirp):
        net_a.step(value_a)
        net_b.step(value_b)

    for value in constant_drive(1.0 + 0j, 30):
        net_a.step(value)
        net_b.step(value)

    return net_a, net_b


def run_pytest(hr_repo_root: Path) -> dict:
    cmd = [sys.executable, "-m", "pytest", "tests", "-q"]
    completed = subprocess.run(
        cmd,
        cwd=hr_repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "passed": completed.returncode == 0,
    }


def monodromy_benchmark() -> dict:
    from hrphasenet.phase import lifted_phase_update, winding_and_parity, wrap

    theta_ref = 0.0
    n_steps = 100
    d_theta = 2.0 * math.pi / n_steps
    for _ in range(n_steps):
        theta_raw = wrap(theta_ref + d_theta)
        theta_ref = float(lifted_phase_update(theta_ref, theta_raw, pi_a=math.pi))
    winding, parity = winding_and_parity(theta_ref)
    return {
        "name": "monodromy",
        "n_steps": n_steps,
        "theta_R_final": theta_ref,
        "winding": int(winding),
        "parity": int(parity),
        "pass": abs(theta_ref - 2.0 * math.pi) <= 1e-2 and int(winding) == 1 and int(parity) == -1,
    }


def freeze_benchmark() -> dict:
    from hrphasenet.phase import lifted_phase_update

    frozen = float(lifted_phase_update(1.0, 2.0, pi_a=math.pi, z_mag=0.0, z_min=1e-9))
    active = float(lifted_phase_update(1.0, 1.5, pi_a=math.pi, z_mag=1.0, z_min=1e-9))
    return {
        "name": "freeze_near_zero",
        "frozen_value": frozen,
        "active_value": active,
        "pass": abs(frozen - 1.0) <= 1e-12 and abs(active - 1.5) <= 1e-12,
    }


def boundedness_benchmark() -> dict:
    from hrphasenet.drives import constant_drive, periodic_drive

    net_const = _make_network(
        "full",
        dt=0.01,
        alpha_0=1.0,
        mu_0=0.5,
        S_0=1.0,
        real_min=1e-6,
        real_max=100.0,
    )
    net_const.run(constant_drive(1.0 + 0j, 200))

    net_periodic = _make_network(
        "full",
        dt=0.01,
        pi_min=0.01,
        pi_max=math.pi,
    )
    net_periodic.run(periodic_drive(1.0, omega=2.0, dt=0.01, n_steps=100))

    max_abs_g = float(np.max(np.abs(net_const.state.G)))
    return {
        "name": "boundedness",
        "max_abs_G_after_200_steps": max_abs_g,
        "entropy_final": float(net_const.state.S),
        "pi_a_final": float(net_periodic.state.pi_a),
        "pass": max_abs_g < 1e6 and net_const.state.S >= 0.0 and 0.01 <= net_periodic.state.pi_a <= math.pi,
    }


def ablation_benchmark() -> dict:
    from hrphasenet.drives import periodic_drive

    modes = ["principal", "lift_only", "lift_ruler", "full"]
    results = {}
    for mode in modes:
        net = _make_network(
            mode,
            dt=0.01,
            alpha_0=0.5,
            S_c=0.1,
            delta_S=0.1,
            mu_0=0.1,
            S_0=1.0,
            S_eq=0.0,
        )
        net.run(periodic_drive(1.0, omega=1.0, dt=0.01, n_steps=50))
        results[mode] = {
            "G_real": [float(x) for x in np.real(net.state.G)],
            "G_imag": [float(x) for x in np.imag(net.state.G)],
            "norm": float(np.linalg.norm(net.state.G)),
        }

    principal = np.array(results["principal"]["G_real"]) + 1j * np.array(results["principal"]["G_imag"])
    full = np.array(results["full"]["G_real"]) + 1j * np.array(results["full"]["G_imag"])
    diff_norm = float(np.linalg.norm(full - principal))
    return {
        "name": "ablation_modes",
        "results": results,
        "principal_vs_full_diff_norm": diff_norm,
        "pass": diff_norm > 1e-8,
    }


def history_divergence_benchmark() -> dict:
    net_a, net_b = _history_protocol_pair("full")
    diff = np.abs(net_a.state.G - net_b.state.G)
    max_diff = float(np.max(diff))
    return {
        "name": "history_divergence",
        "max_abs_delta_G": max_diff,
        "pass": max_diff > 1e-6,
    }


def matched_present_state_separation_benchmark() -> dict:
    from hrphasenet.solver import edge_current, nodal_solve

    principal_a, principal_b = _history_protocol_pair("principal")
    full_a, full_b = _history_protocol_pair("full")

    phi_principal_a, _ = nodal_solve(
        principal_a.edges,
        principal_a.state.G,
        principal_a.n_nodes,
        principal_a.source_node,
        principal_a.sink_node,
        source_value=1.0 + 0j,
    )
    phi_principal_b, _ = nodal_solve(
        principal_b.edges,
        principal_b.state.G,
        principal_b.n_nodes,
        principal_b.source_node,
        principal_b.sink_node,
        source_value=1.0 + 0j,
    )
    phi_full_a, _ = nodal_solve(
        full_a.edges,
        full_a.state.G,
        full_a.n_nodes,
        full_a.source_node,
        full_a.sink_node,
        source_value=1.0 + 0j,
    )
    phi_full_b, _ = nodal_solve(
        full_b.edges,
        full_b.state.G,
        full_b.n_nodes,
        full_b.source_node,
        full_b.sink_node,
        source_value=1.0 + 0j,
    )

    principal_raw_a = np.angle(edge_current(principal_a.edges, principal_a.state.G, phi_principal_a))
    principal_raw_b = np.angle(edge_current(principal_b.edges, principal_b.state.G, phi_principal_b))
    full_raw_a = np.angle(edge_current(full_a.edges, full_a.state.G, phi_full_a))
    full_raw_b = np.angle(edge_current(full_b.edges, full_b.state.G, phi_full_b))

    principal_raw_gap = float(np.max(np.abs(principal_raw_a - principal_raw_b)))
    principal_theta_gap = float(np.max(np.abs(principal_a.state.theta_R - principal_b.state.theta_R)))
    full_raw_gap = float(np.max(np.abs(full_raw_a - full_raw_b)))
    full_theta_gap = float(np.max(np.abs(full_a.state.theta_R - full_b.state.theta_R)))

    principal_w_equal = bool(np.array_equal(principal_a.state.w, principal_b.state.w))
    principal_parity_equal = bool(np.array_equal(principal_a.state.b, principal_b.state.b))
    full_w_equal = bool(np.array_equal(full_a.state.w, full_b.state.w))
    full_parity_equal = bool(np.array_equal(full_a.state.b, full_b.state.b))

    return {
        "name": "matched_present_state_separation",
        "principal_raw_phase_gap": principal_raw_gap,
        "principal_theta_R_gap": principal_theta_gap,
        "full_raw_phase_gap": full_raw_gap,
        "full_theta_R_gap": full_theta_gap,
        "principal_w_equal": principal_w_equal,
        "principal_parity_equal": principal_parity_equal,
        "full_w_equal": full_w_equal,
        "full_parity_equal": full_parity_equal,
        "pass": (
            principal_raw_gap <= 1e-9
            and principal_theta_gap <= 1e-9
            and full_raw_gap <= 1e-9
            and full_theta_gap > math.pi
            and principal_w_equal
            and principal_parity_equal
            and not full_w_equal
            and not full_parity_equal
        ),
    }


def operational_memory_gap_benchmark() -> dict:
    from hrphasenet.conductance import suppression_term
    from hrphasenet.solver import edge_current, nodal_solve

    principal_a, principal_b = _history_protocol_pair("principal")
    full_a, full_b = _history_protocol_pair("full")

    phi_principal_a, _ = nodal_solve(
        principal_a.edges,
        principal_a.state.G,
        principal_a.n_nodes,
        principal_a.source_node,
        principal_a.sink_node,
        source_value=1.0 + 0j,
    )
    phi_principal_b, _ = nodal_solve(
        principal_b.edges,
        principal_b.state.G,
        principal_b.n_nodes,
        principal_b.source_node,
        principal_b.sink_node,
        source_value=1.0 + 0j,
    )
    phi_full_a, _ = nodal_solve(
        full_a.edges,
        full_a.state.G,
        full_a.n_nodes,
        full_a.source_node,
        full_a.sink_node,
        source_value=1.0 + 0j,
    )
    phi_full_b, _ = nodal_solve(
        full_b.edges,
        full_b.state.G,
        full_b.n_nodes,
        full_b.source_node,
        full_b.sink_node,
        source_value=1.0 + 0j,
    )

    principal_current_gap = float(
        np.max(
            np.abs(
                np.abs(edge_current(principal_a.edges, principal_a.state.G, phi_principal_a))
                - np.abs(edge_current(principal_b.edges, principal_b.state.G, phi_principal_b))
            )
        )
    )
    full_current_gap = float(
        np.max(
            np.abs(
                np.abs(edge_current(full_a.edges, full_a.state.G, phi_full_a))
                - np.abs(edge_current(full_b.edges, full_b.state.G, phi_full_b))
            )
        )
    )

    principal_suppression_gap = float(
        np.max(
            np.abs(
                suppression_term(principal_a.state.G, principal_a.state.theta_R, principal_a.state.pi_a, principal_a.params.lambda_s)
                - suppression_term(principal_b.state.G, principal_b.state.theta_R, principal_b.state.pi_a, principal_b.params.lambda_s)
            )
        )
    )
    full_suppression_gap = float(
        np.max(
            np.abs(
                suppression_term(full_a.state.G, full_a.state.theta_R, full_a.state.pi_a, full_a.params.lambda_s)
                - suppression_term(full_b.state.G, full_b.state.theta_R, full_b.state.pi_a, full_b.params.lambda_s)
            )
        )
    )

    return {
        "name": "operational_memory_gap",
        "principal_current_mag_gap": principal_current_gap,
        "full_current_mag_gap": full_current_gap,
        "principal_suppression_gap": principal_suppression_gap,
        "full_suppression_gap": full_suppression_gap,
        "pass": (
            principal_current_gap <= 1e-9
            and full_current_gap <= 1e-9
            and principal_suppression_gap <= 1e-12
            and full_suppression_gap > 1e-3
        ),
    }


def memory_threshold_sweep_benchmark() -> dict:
    from hrphasenet.conductance import suppression_term

    omega_end_values = [12.0, 16.0, 20.0]
    sweep = []
    for omega_end in omega_end_values:
        principal_a, principal_b = _history_protocol_pair("principal", omega_end=omega_end)
        full_a, full_b = _history_protocol_pair("full", omega_end=omega_end)

        principal_theta_gap = float(np.max(np.abs(principal_a.state.theta_R - principal_b.state.theta_R)))
        full_theta_gap = float(np.max(np.abs(full_a.state.theta_R - full_b.state.theta_R)))
        principal_suppression_gap = float(
            np.max(
                np.abs(
                    suppression_term(principal_a.state.G, principal_a.state.theta_R, principal_a.state.pi_a, principal_a.params.lambda_s)
                    - suppression_term(principal_b.state.G, principal_b.state.theta_R, principal_b.state.pi_a, principal_b.params.lambda_s)
                )
            )
        )
        full_suppression_gap = float(
            np.max(
                np.abs(
                    suppression_term(full_a.state.G, full_a.state.theta_R, full_a.state.pi_a, full_a.params.lambda_s)
                    - suppression_term(full_b.state.G, full_b.state.theta_R, full_b.state.pi_a, full_b.params.lambda_s)
                )
            )
        )
        sweep.append(
            {
                "omega_end": omega_end,
                "principal_theta_R_gap": principal_theta_gap,
                "full_theta_R_gap": full_theta_gap,
                "principal_suppression_gap": principal_suppression_gap,
                "full_suppression_gap": full_suppression_gap,
                "pass": (
                    principal_theta_gap <= 1e-9
                    and principal_suppression_gap <= 1e-12
                    and full_theta_gap > math.pi
                    and full_suppression_gap > 1e-3
                ),
            }
        )

    return {
        "name": "memory_threshold_sweep",
        "omega_end_values": omega_end_values,
        "sweep": sweep,
        "pass": all(item["pass"] for item in sweep),
    }


def memory_onset_phase_diagram_benchmark() -> dict:
    from hrphasenet.conductance import suppression_term

    pi_0_values = [math.pi / 4.0, math.pi / 3.0, math.pi / 2.0, 2.0 * math.pi / 3.0, 3.0 * math.pi / 4.0]
    omega_end_values = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
    rows = []
    onset_summary = []

    for pi_0 in pi_0_values:
        onset_omega_end = None
        for omega_end in omega_end_values:
            principal_a, principal_b = _history_protocol_pair("principal", omega_end=omega_end, pi_0=pi_0)
            full_a, full_b = _history_protocol_pair("full", omega_end=omega_end, pi_0=pi_0)

            principal_theta_gap = float(np.max(np.abs(principal_a.state.theta_R - principal_b.state.theta_R)))
            full_theta_gap = float(np.max(np.abs(full_a.state.theta_R - full_b.state.theta_R)))
            principal_suppression_gap = float(
                np.max(
                    np.abs(
                        suppression_term(principal_a.state.G, principal_a.state.theta_R, principal_a.state.pi_a, principal_a.params.lambda_s)
                        - suppression_term(principal_b.state.G, principal_b.state.theta_R, principal_b.state.pi_a, principal_b.params.lambda_s)
                    )
                )
            )
            full_suppression_gap = float(
                np.max(
                    np.abs(
                        suppression_term(full_a.state.G, full_a.state.theta_R, full_a.state.pi_a, full_a.params.lambda_s)
                        - suppression_term(full_b.state.G, full_b.state.theta_R, full_b.state.pi_a, full_b.params.lambda_s)
                    )
                )
            )
            full_memory_on = full_theta_gap > math.pi and full_suppression_gap > 1e-3
            if onset_omega_end is None and full_memory_on:
                onset_omega_end = omega_end

            rows.append(
                {
                    "pi_0": pi_0,
                    "omega_end": omega_end,
                    "principal_theta_R_gap": principal_theta_gap,
                    "full_theta_R_gap": full_theta_gap,
                    "principal_suppression_gap": principal_suppression_gap,
                    "full_suppression_gap": full_suppression_gap,
                    "full_memory_on": full_memory_on,
                }
            )

        below_threshold = [row for row in rows if row["pi_0"] == pi_0 and row["omega_end"] < 12.0]
        above_threshold = [row for row in rows if row["pi_0"] == pi_0 and row["omega_end"] >= 12.0]
        onset_summary.append(
            {
                "pi_0": pi_0,
                "onset_omega_end": onset_omega_end,
                "principal_collapsed_all": all(row["principal_theta_R_gap"] <= 1e-9 and row["principal_suppression_gap"] <= 1e-12 for row in below_threshold + above_threshold),
                "full_off_below_threshold": all(row["full_theta_R_gap"] <= 1e-9 and row["full_suppression_gap"] <= 1e-12 for row in below_threshold),
                "full_on_at_or_above_threshold": all(row["full_theta_R_gap"] > math.pi and row["full_suppression_gap"] > 1e-3 for row in above_threshold),
            }
        )

    return {
        "name": "memory_onset_phase_diagram",
        "pi_0_values": pi_0_values,
        "omega_end_values": omega_end_values,
        "rows": rows,
        "onset_summary": onset_summary,
        "pass": all(
            item["onset_omega_end"] == 12.0
            and item["principal_collapsed_all"]
            and item["full_off_below_threshold"]
            and item["full_on_at_or_above_threshold"]
            for item in onset_summary
        ),
    }


def _markdown(report: dict) -> str:
    lines = []
    lines.append("# History-Resolved Phase Benchmark Report")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Pytest")
    lines.append("")
    lines.append(f"- Command: `{report['pytest']['command']}`")
    lines.append(f"- Passed: `{report['pytest']['passed']}`")
    if report["pytest"]["stdout"]:
        lines.append(f"- Stdout: `{report['pytest']['stdout']}`")
    if report["pytest"]["stderr"]:
        lines.append(f"- Stderr: `{report['pytest']['stderr']}`")
    lines.append("")
    lines.append("## Targeted Benchmarks")
    lines.append("")
    lines.append("| Benchmark | Pass | Key output |")
    lines.append("| --- | --- | --- |")
    for benchmark in report["benchmarks"]:
        name = benchmark["name"]
        passed = "yes" if benchmark["pass"] else "no"
        if name == "monodromy":
            detail = f"theta_R={benchmark['theta_R_final']:.6f}, w={benchmark['winding']}, b={benchmark['parity']}"
        elif name == "freeze_near_zero":
            detail = f"frozen={benchmark['frozen_value']:.6f}, active={benchmark['active_value']:.6f}"
        elif name == "boundedness":
            detail = f"max|G|={benchmark['max_abs_G_after_200_steps']:.6f}, pi_a={benchmark['pi_a_final']:.6f}"
        elif name == "ablation_modes":
            detail = f"||G_full-G_principal||={benchmark['principal_vs_full_diff_norm']:.6e}"
        elif name == "history_divergence":
            detail = f"max|delta G|={benchmark['max_abs_delta_G']:.6e}"
        elif name == "matched_present_state_separation":
            detail = (
                f"principal dtheta={benchmark['principal_theta_R_gap']:.6e}, "
                f"full dtheta={benchmark['full_theta_R_gap']:.6f}"
            )
        elif name == "operational_memory_gap":
            detail = (
                f"principal dsupp={benchmark['principal_suppression_gap']:.6e}, "
                f"full dsupp={benchmark['full_suppression_gap']:.6f}"
            )
        elif name == "memory_threshold_sweep":
            first = benchmark["sweep"][0]
            last = benchmark["sweep"][-1]
            detail = (
                f"omega_end {first['omega_end']:.0f}-{last['omega_end']:.0f}, "
                f"principal dtheta~0, full dtheta~2pi"
            )
        elif name == "memory_onset_phase_diagram":
            onsets = ", ".join(
                f"pi_0={item['pi_0'] / math.pi:.2f}pi -> {item['onset_omega_end']:.0f}"
                for item in benchmark["onset_summary"]
            )
            detail = f"onset map: {onsets}"
        else:
            detail = "see JSON"
        lines.append(f"| {name} | {passed} | {detail} |")
    lines.append("")
    lines.append("This report is generated by `tools/benchmark_history_resolved_phase.py` and is intended to back score-facing claims with locally executed Python checks.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    repo_root = _repo_root()
    hr_repo_root = _hr_repo_root()
    artifacts_dir = repo_root / "data" / "artifacts"
    docs_artifacts_dir = repo_root / "docs" / "data" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    docs_artifacts_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hr_repo_root": str(hr_repo_root),
        "pytest": run_pytest(hr_repo_root),
        "benchmarks": [
            monodromy_benchmark(),
            freeze_benchmark(),
            boundedness_benchmark(),
            ablation_benchmark(),
            history_divergence_benchmark(),
            matched_present_state_separation_benchmark(),
            operational_memory_gap_benchmark(),
            memory_threshold_sweep_benchmark(),
            memory_onset_phase_diagram_benchmark(),
        ],
    }
    report["all_passed"] = report["pytest"]["passed"] and all(item["pass"] for item in report["benchmarks"])

    json_path = artifacts_dir / "history_resolved_phase_benchmark_report.json"
    md_path = artifacts_dir / "history_resolved_phase_benchmark_report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")

    (docs_artifacts_dir / json_path.name).write_text(json.dumps(report, indent=2), encoding="utf-8")
    (docs_artifacts_dir / md_path.name).write_text(_markdown(report), encoding="utf-8")

    print(f"wrote: {json_path}")
    print(f"wrote: {md_path}")
    print(f"all_passed: {report['all_passed']}")


if __name__ == "__main__":
    main()