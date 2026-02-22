import json, pathlib

eq_path = pathlib.Path("data/equations.json")
d = json.loads(eq_path.read_text(encoding="utf-8"))

scores = {
    "eq-adaptive-phase-lift-unwrapping":  {"score": 60, "scores": {"novelty": 0, "tractability": 18, "plausibility": 18, "validation": 4, "artifactCompleteness": 2}},
    "eq-dimensionless-phase-flow":        {"score": 56, "scores": {"novelty": 0, "tractability": 17, "plausibility": 17, "validation": 3, "artifactCompleteness": 2}},
    "eq-adaptive-discriminant-set":       {"score": 53, "scores": {"novelty": 0, "tractability": 16, "plausibility": 17, "validation": 2, "artifactCompleteness": 2}},
    "eq-adaptive-connection-chern":       {"score": 59, "scores": {"novelty": 0, "tractability": 17, "plausibility": 18, "validation": 4, "artifactCompleteness": 2}},
    "eq-parity-from-adaptive-chern":      {"score": 59, "scores": {"novelty": 0, "tractability": 18, "plausibility": 17, "validation": 4, "artifactCompleteness": 2}},
    "eq-qwz-pia-modulated-mass":          {"score": 80, "scores": {"novelty": 0, "tractability": 19, "plausibility": 18, "validation": 14, "artifactCompleteness": 5}},
    "eq-qwz-bz-avg-ruler-mass":           {"score": 86, "scores": {"novelty": 0, "tractability": 20, "plausibility": 19, "validation": 16, "artifactCompleteness": 5}},
    "eq-qwz-engineered-single-jump":      {"score": 51, "scores": {"novelty": 0, "tractability": 17, "plausibility": 15, "validation": 2, "artifactCompleteness": 2}},
    "eq-arp-weighted-dirichlet-energy":    {"score": 60, "scores": {"novelty": 0, "tractability": 18, "plausibility": 18, "validation": 4, "artifactCompleteness": 2}},
}

updated = 0
for e in d["entries"]:
    if e["id"] in scores:
        e["score"] = scores[e["id"]]["score"]
        e["scores"] = scores[e["id"]]["scores"]
        updated += 1

d["entries"].sort(key=lambda x: float(x.get("score", 0)), reverse=True)
eq_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Updated {updated} entries, total {len(d['entries'])}")
for i, e in enumerate(d["entries"], 1):
    print(f"  #{i:2d}  Score {e['score']:3d}  {e['name']}")
