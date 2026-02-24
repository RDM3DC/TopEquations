# HEARTBEAT.md — Equation Lab ∑

Run these checks in order. If any check produces work, do that work. If none do, reply `HEARTBEAT_OK`.

## 1. Scan for Pending Submissions

```powershell
python -c "import json; subs=json.load(open('data/submissions.json')); pending=[s for s in subs if s.get('status')=='needs-review']; print(f'{len(pending)} pending') if pending else print('0 pending')"
```

If pending > 0:
- Run `python tools/score_submission.py --submission-id <id>` for each
- If score >= 68, run `python tools/promote_submission.py --submission-id <id> --from-review`
- Rebuild site: `python tools/generate_leaderboard.py` then `python tools/build_site.py`

## 2. Check Leaderboard Freshness

If `data/equations.json` was modified more recently than `docs/leaderboard.html`:
- Run `python tools/generate_leaderboard.py` then `python tools/build_site.py`

## 3. Check for Unpublished Certificates

If any equation in `data/equations.json` lacks a certificate hash:
- Run `python tools/export_equation_certificates.py`
- Run `python tools/register_equation_certificates.py --node-url http://127.0.0.1:5000 --signer-file D:/coins2/Adaptive-Curvature-Coin/wallet.json --mine`

## 4. If All Clear

Reply `HEARTBEAT_OK`.
