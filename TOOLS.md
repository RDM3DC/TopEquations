# TOOLS.md — Equation Lab ∑

## Repo Root

`C:\Users\RDM3D\clawdad42\TopEquations`

## Pipeline Tools

| Tool | Path | Purpose |
|------|------|---------|
| submit_equation.py | `tools/submit_equation.py` | Intake: creates submission record in data/submissions.json |
| score_submission.py | `tools/score_submission.py` | Score: evidence-aware heuristic scoring |
| promote_submission.py | `tools/promote_submission.py` | Promote: moves submission into data/equations.json |
| openclaw_submission_pipeline.py | `tools/openclaw_submission_pipeline.py` | One-command orchestrator (submit→score→promote→chain) |
| generate_leaderboard.py | `tools/generate_leaderboard.py` | Rebuilds registry.md and leaderboard.md from equations.json |
| build_site.py | `tools/build_site.py` | Generates all docs/*.html pages |
| export_equation_certificates.py | `tools/export_equation_certificates.py` | Exports certificate data |
| register_equation_certificates.py | `tools/register_equation_certificates.py` | Publishes certificates to blockchain |

## Data Files

- `data/equations.json` — Published equations (display threshold: score >= 68)
- `data/submissions.json` — All submissions with status and scores
- `submissions/YYYY-MM-DD.md` — Daily submission logs

## Chain Access

- Default automation path: `.github/workflows/publish_chain.yml`
- Node URL: supplied by `CHAIN_NODE_URL` repository secret
- Wallet: supplied by `CHAIN_WALLET_PUBLIC_KEY` and `CHAIN_WALLET_PRIVATE_KEY` repository secrets
- Local fallback: `tools/chain_publish_cron.py --node-url <url> --signer-file <wallet.json>`

## Related Workspaces

- Discovery matrix: `C:\Users\RDM3D\.openclaw\workspace\memory\discovery-matrix.md`
- Manim animation workspace: `D:\Manimppyythn`
- Unit bouncer: `C:\Users\RDM3D\.openclaw\workspace\tools\unit_bouncer\unit_bouncer.py`

## Runtime

- Python 3.x (available as `python`)
- Windows PowerShell
- Git (available as `git`)
