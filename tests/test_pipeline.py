from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative_path: str):
    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


score_submission = _load_module("score_submission", "tools/score_submission.py")
generate_leaderboard = _load_module("generate_leaderboard", "tools/generate_leaderboard.py")
build_site = _load_module("build_site", "tools/build_site.py")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_heuristic_score_computation_is_stable() -> None:
    entry = {
        "equationLatex": r"x = \\frac{1}{2}\\sin(t)",
        "description": "Dimensional consistency checked against baseline model.",
        "assumptions": ["Linear regime", "Fixed boundary conditions"],
        "units": "OK",
        "evidence": [
            "Dimensional analysis confirms unit balance.",
            "Peer reviewed benchmark reproduced experimentally.",
        ],
        "animation": {"status": "planned"},
        "image": {"status": "planned"},
    }

    metrics = score_submission._heuristic(entry)

    assert metrics == {
        "tractability": 17,
        "plausibility": 19,
        "validation": 16,
        "artifactCompleteness": 4,
        "novelty": 20,
        "lineage_hits": 0,
        "score": 76,
    }


def test_load_json_safe_recovers_first_valid_object(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text('{"entries": []} trailing', encoding="utf-8")

    payload = build_site._load_json_safe(broken, {"entries": ["fallback"]})

    assert payload == {"entries": []}


def test_generate_leaderboard_uses_display_threshold(tmp_path: Path) -> None:
    source = tmp_path / "equations.json"
    output = tmp_path / "leaderboard.md"
    _write_json(
        source,
        {
            "entries": [
                {"name": "Above Threshold", "equationLatex": "x=1", "score": 70, "date": "2026-03-21", "firstSeen": "2026-03"},
                {"name": "At Threshold", "equationLatex": "y=2", "score": 65, "date": "2026-03-21", "firstSeen": "2026-03"},
                {"name": "Below Threshold", "equationLatex": "z=3", "score": 64, "date": "2026-03-21", "firstSeen": "2026-03"},
            ]
        },
    )

    generate_leaderboard.generate(source, output)
    text = output.read_text(encoding="utf-8")
    top_section = text.split("## Newest Top-Ranked Equations", 1)[0]

    assert "Above Threshold" in text
    assert "At Threshold" in text
    assert "Below Threshold" not in top_section


def test_site_build_smoke_and_leaderboard_consistency(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    docs = repo_root / "docs"
    (docs / "assets").mkdir(parents=True, exist_ok=True)

    equations = {
        "entries": [
            {
                "id": "eq-high",
                "name": "High Score Equation",
                "equationLatex": "x=1",
                "description": "Promoted equation",
                "score": 80,
                "source": "test",
                "units": "OK",
                "theory": "PASS",
                "date": "2026-03-21",
                "firstSeen": "2026-03",
                "animation": {"status": "planned", "path": ""},
                "image": {"status": "planned", "path": ""},
                "assumptions": [],
                "tags": {"novelty": {"score": 20, "date": "2026-03-21"}},
            },
            {
                "id": "eq-threshold",
                "name": "Threshold Equation",
                "equationLatex": "y=2",
                "description": "Threshold equation",
                "score": 65,
                "source": "test",
                "units": "OK",
                "theory": "PASS",
                "date": "2026-03-21",
                "firstSeen": "2026-03",
                "animation": {"status": "planned", "path": ""},
                "image": {"status": "planned", "path": ""},
                "assumptions": [],
                "tags": {"novelty": {"score": 18, "date": "2026-03-21"}},
            },
            {
                "id": "eq-rising",
                "name": "Rising Equation",
                "equationLatex": "z=3",
                "description": "Not yet promoted",
                "score": 50,
                "source": "test",
                "units": "TBD",
                "theory": "TBD",
                "date": "2026-03-21",
                "firstSeen": "2026-03",
                "animation": {"status": "planned", "path": ""},
                "image": {"status": "planned", "path": ""},
                "assumptions": [],
                "tags": {"novelty": {"score": 10, "date": "2026-03-21"}},
            },
        ]
    }
    submissions = {
        "entries": [
            {
                "submissionId": "sub-1",
                "name": "High Score Equation",
                "equationLatex": "x=1",
                "description": "Promoted equation",
                "source": "test",
                "submitter": "tester",
                "submittedAt": "2026-03-21T00:00:00Z",
                "status": "promoted",
                "units": "OK",
                "theory": "PASS",
                "assumptions": [],
                "animation": {"status": "planned", "path": ""},
                "image": {"status": "planned", "path": ""},
                "review": {"equationId": "eq-high"},
            }
        ]
    }

    _write_json(repo_root / "data" / "equations.json", equations)
    _write_json(repo_root / "data" / "submissions.json", submissions)
    _write_json(repo_root / "data" / "core.json", {"entries": []})
    _write_json(repo_root / "data" / "famous_equations.json", {"entries": []})
    _write_json(repo_root / "data" / "certificates" / "equation_certificates.json", {"entries": []})
    _write_json(repo_root / "data" / "certificates" / "chain_publish_receipt.json", {})
    generate_leaderboard.generate(repo_root / "data" / "equations.json", repo_root / "leaderboard.md")

    build_site.publish_machine_readable_data(repo_root, docs)
    build_site.build_index(repo_root, docs)
    build_site.build_core(repo_root, docs)
    build_site.build_famous(repo_root, docs)
    build_site.build_leaderboard(repo_root, docs)
    build_site.build_rising(repo_root, docs)
    build_site.build_certificates(repo_root, docs)
    build_site.build_submissions(repo_root, docs)
    build_site.build_harvest(repo_root, docs)

    assert (docs / "index.html").exists()
    assert (docs / "leaderboard.html").exists()
    assert (docs / "submissions.html").exists()
    assert (docs / "data" / "equations.json").exists()
    assert (docs / "data" / "leaderboard.json").exists()

    published_equations = json.loads((docs / "data" / "equations.json").read_text(encoding="utf-8"))
    published_leaderboard = json.loads((docs / "data" / "leaderboard.json").read_text(encoding="utf-8"))
    index_html = (docs / "index.html").read_text(encoding="utf-8")
    leaderboard_html = (docs / "leaderboard.html").read_text(encoding="utf-8")

    assert published_equations == equations
    assert [entry["id"] for entry in published_leaderboard["entries"]] == ["eq-high", "eq-threshold"]
    assert leaderboard_html.count("<section class='card'") == 2
    assert "Machine-Readable Access" in leaderboard_html
    assert "./data/leaderboard.json" in leaderboard_html
    assert "<table class='tbl'>" in leaderboard_html
    assert "High Score Equation" in leaderboard_html
    assert "Threshold Equation" in leaderboard_html
    assert "Rising Equation" not in leaderboard_html
    assert "Machine-Readable Exports" in index_html
    assert "./data/equations.json" in index_html