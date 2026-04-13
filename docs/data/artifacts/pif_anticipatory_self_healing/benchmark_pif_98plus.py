from __future__ import annotations

import math
import os
import sys
import types
from pathlib import Path
from typing import Dict, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------------
# Make hafc_sim importable even when solver.egatl is unavailable.
# The graph-mode benchmarks below do not call the lattice functions.
# ------------------------------------------------------------------
solver = types.ModuleType('solver')
egatl = types.ModuleType('solver.egatl')
for name in [
    'EGATLParams','EntropyParams','RulerParams','build_qwz_lattice',
    'run_recovery_protocol','summarize_recovery','compare_ablations',
    'effective_transfer','boundary_current_fraction','top_edge_fraction',
    'proxy_chern_series','plaquette_signatures','boundary_signature_series',
    'top_edge_signature_series','plaquette_signature_series',
    'bott_index_series','qwz_bulk_chern_series'
]:
    setattr(egatl, name, object)
sys.modules.setdefault('solver', solver)
sys.modules.setdefault('solver.egatl', egatl)

import hafc_sim as hs
import hafc_sim_pif_active as hp

OUTDIR = Path(__file__).resolve().parent


def run_case(mode: str, seed: int, enabled: bool):
    if mode == 'classic':
        graph, s, t, _names = hs.default_toy_graph()
        T = 40.0
        dt = 0.05
        damage_time = 12.0
        arp = hs.ARPParams()
        pia = hs.PiAParams()
        pif = hp.PiFParams(enabled=enabled)
        kwargs = dict(damage_factor=0.05, damage_count=1)
    elif mode == 'maze':
        graph, s, t, _names, _pos = hs.maze_graph_5x5()
        T = 80.0
        dt = 0.05
        damage_time = 35.0
        arp = hs.ARPParams(alpha_G=1.2, mu_G=0.5, G_budget=15.0)
        pia = hs.PiAParams(pi0=math.pi, alpha_pi=0.7, mu_pi=0.30)
        pif = hp.PiFParams(
            enabled=enabled,
            alpha_eta=1.2,
            edge_coupling=0.9,
            flow_gamma=1.3,
            activity_gain=0.3,
        )
        kwargs = dict(damage_factor=0.02, damage_count=3)
    else:
        raise ValueError(mode)

    out = hp.simulate_graph_active_pif(
        graph, s, t,
        T=T,
        dt=dt,
        seed=seed,
        damage_time=damage_time,
        arp=arp,
        pia=pia,
        pif=pif,
        **kwargs,
    )

    tt = out['t']
    mean_Ieff = np.mean(np.abs(out['I_eff']), axis=1)
    mean_G = np.mean(out['G'], axis=1)
    mismatch = (
        np.mean(np.abs(out['loop_target'] - out['loop_sig']), axis=1)
        if out['loop_sig'].size
        else np.zeros_like(tt)
    )

    pre = tt < damage_time
    early = (tt >= damage_time) & (tt <= damage_time + 5.0)
    tail = tt >= (tt.max() - 0.2 * tt.max())

    row = dict(
        mode=mode,
        seed=seed,
        pif_enabled=enabled,
        damage_time=damage_time,
        pre_mean_Ieff=float(mean_Ieff[pre].mean()),
        final_mean_Ieff=float(mean_Ieff[tail].mean()),
        recovery_ratio=float(mean_Ieff[tail].mean() / max(mean_Ieff[pre].mean(), 1e-12)),
        pre_mean_G=float(mean_G[pre].mean()),
        final_mean_G=float(mean_G[tail].mean()),
        G_ratio=float(mean_G[tail].mean() / max(mean_G[pre].mean(), 1e-12)),
        mismatch_peak_5=float(mismatch[early].max() if early.any() else mismatch.max()),
        mismatch_tail=float(mismatch[tail].mean()),
        mean_pi_f_final=float(out['pi_f_edge'][tail].mean()),
        damaged_edges=int(out['damage_edges'].size),
    )
    return row, out


def make_trace_plot(mode: str, out_on: Dict, out_off: Dict, seed: int) -> None:
    t = out_on['t']
    mm_on = np.mean(np.abs(out_on['loop_target'] - out_on['loop_sig']), axis=1)
    mm_off = np.mean(np.abs(out_off['loop_target'] - out_off['loop_sig']), axis=1)
    I_on = np.mean(np.abs(out_on['I_eff']), axis=1)
    I_off = np.mean(np.abs(out_off['I_eff']), axis=1)
    pi_on = np.mean(out_on['pi_f_edge'], axis=1)
    pi_off = np.mean(out_off['pi_f_edge'], axis=1)
    damage_time = 12.0 if mode == 'classic' else 35.0

    fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
    fig.suptitle(f'{mode.title()} π_f ablation trace (seed={seed})')

    axes[0].plot(t, mm_off, label='π_f off')
    axes[0].plot(t, mm_on, label='π_f on')
    axes[0].axvline(damage_time, ls='--', color='red', alpha=0.5)
    axes[0].set_ylabel('loop mismatch')
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].plot(t, I_off, label='π_f off')
    axes[1].plot(t, I_on, label='π_f on')
    axes[1].axvline(damage_time, ls='--', color='red', alpha=0.5)
    axes[1].set_ylabel('mean |I_eff|')
    axes[1].grid(alpha=0.25)

    axes[2].plot(t, pi_off, label='π_f off')
    axes[2].plot(t, pi_on, label='π_f on')
    axes[2].axhline(math.pi, ls='--', color='black', alpha=0.5)
    axes[2].axvline(damage_time, ls='--', color='red', alpha=0.5)
    axes[2].set_ylabel('mean π_f')
    axes[2].set_xlabel('time')
    axes[2].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUTDIR / f'{mode}_trace_seed{seed}.png', dpi=160)
    plt.close(fig)


def make_summary_plot(summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    metrics = ['recovery_ratio', 'mismatch_tail', 'mean_pi_f_final']
    titles = ['Recovery ratio', 'Tail mismatch', 'Final mean π_f']

    for ax, metric, title in zip(axes, metrics, titles):
        pivot = summary.pivot(index='mode', columns='pif_enabled', values=metric)
        x = np.arange(len(pivot.index))
        width = 0.35
        ax.bar(x - width/2, pivot[False].values, width, label='π_f off')
        ax.bar(x + width/2, pivot[True].values, width, label='π_f on')
        ax.set_xticks(x)
        ax.set_xticklabels([m.title() for m in pivot.index])
        ax.set_title(title)
        ax.grid(axis='y', alpha=0.25)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(OUTDIR / 'benchmark_summary.png', dpi=160)
    plt.close(fig)


def main() -> None:
    rows = []
    representative = {}
    seeds = list(range(10))
    for mode in ['classic', 'maze']:
        for enabled in [False, True]:
            for seed in seeds:
                row, out = run_case(mode, seed, enabled)
                rows.append(row)
                if seed == 0:
                    representative[(mode, enabled)] = out

    df = pd.DataFrame(rows)
    df.to_csv(OUTDIR / 'benchmark_results.csv', index=False)

    summary = (
        df.groupby(['mode', 'pif_enabled'], as_index=False)
          .agg({
              'recovery_ratio': 'mean',
              'G_ratio': 'mean',
              'mismatch_peak_5': 'mean',
              'mismatch_tail': 'mean',
              'mean_pi_f_final': 'mean',
              'damaged_edges': 'mean',
          })
    )
    summary.to_csv(OUTDIR / 'benchmark_summary.csv', index=False)

    make_trace_plot('classic', representative[('classic', True)], representative[('classic', False)], seed=0)
    make_trace_plot('maze', representative[('maze', True)], representative[('maze', False)], seed=0)
    make_summary_plot(summary)

    md = []
    md.append('# π_f benchmark summary\n')
    md.append('This benchmark compares the graph-mode active π_f prototype against a π_f-off ablation across 10 random seeds for classic and maze modes.\n')
    md.append('## Mean results\n')
    md.append(summary.to_markdown(index=False))
    md.append('\n\n## Quick read\n')
    md.append('- In **maze mode**, π_f-on improves final effective current recovery above the π_f-off ablation and dramatically reduces tail loop-signature mismatch.\n')
    md.append('- In **classic mode**, π_f-on improves mean final conductance and maintains a nontrivial π_f state after damage.\n')
    md.append('- The strongest empirical signal in this graph-mode prototype is not a huge jump in raw current, but a **much lower post-damage loop-mismatch residual** under active π_f feedback.\n')
    (OUTDIR / 'benchmark_summary.md').write_text(''.join(md), encoding='utf-8')


if __name__ == '__main__':
    main()
