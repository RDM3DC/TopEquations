"""One-off: score famous equations via LLM for comparison."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from llm_score_submission import score_submission

def main():
    api_key = os.environ["OPENAI_API_KEY"]
    api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("LLM_SCORE_MODEL", "gpt-4o-mini")

    famous = json.loads(open("data/famous_equations.json", encoding="utf-8").read())
    results = []
    for e in famous["entries"]:
        entry = {
            "name": e.get("name", ""),
            "equationLatex": e.get("equationLatex", ""),
            "description": e.get("description", ""),
            "units": e.get("units", "TBD"),
            "theory": e.get("theory", "TBD"),
            "assumptions": e.get("assumptions", []),
            "evidence": [],
        }
        scores = score_submission(entry, api_key, api_base, model)
        if scores:
            eid = e["id"]
            t = scores["llm_total"]
            print(f"{eid:35s}  LLM={t:3d}  phys={scores['physical_validity']}  nov={scores['novelty']}  clar={scores['clarity']}  evid={scores['evidence_quality']}  sig={scores['significance']}")
            results.append((eid, t, scores))
        else:
            print(f"{e['id']:35s}  FAILED")

    print("\n=== RANKED ===")
    for eid, t, s in sorted(results, key=lambda x: -x[1]):
        print(f"  {t:3d}  {eid}")

if __name__ == "__main__":
    main()
