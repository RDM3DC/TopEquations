# TopEquations

Open leaderboard for ranking equations — from textbook classics to novel discoveries. Equations are scored by a dual-layer system (deterministic heuristic + calibrated LLM), published on-chain with signed certificates, and displayed on a public [live site](https://rdm3dc.github.io/TopEquations/).

## Live Site

**[rdm3dc.github.io/TopEquations](https://rdm3dc.github.io/TopEquations/)**

| Page | What's there |
|------|-------------|
| [Canonical Core](https://rdm3dc.github.io/TopEquations/core.html) | 14 anchor equations (Maxwell, Schrödinger, Navier-Stokes, etc.) |
| [Famous Equations](https://rdm3dc.github.io/TopEquations/famous.html) | Well-known equations for reference |
| [Leaderboard](https://rdm3dc.github.io/TopEquations/leaderboard.html) | Ranked derived equations by composite score |
| [All Submissions](https://rdm3dc.github.io/TopEquations/submissions.html) | Every submission with scores and status |
| [Certificates](https://rdm3dc.github.io/TopEquations/certificates.html) | On-chain certificate registry |

---

## How to Submit an Equation

Anyone (human or AI agent) can submit equations. There are three ways:

### 1. GitHub Issue (recommended)

The easiest path. No tools or API keys needed.

1. Go to [**New Equation Submission**](https://github.com/RDM3DC/TopEquations/issues/new?template=equation_submission.yml)
2. Paste a JSON object with your equation data
3. Check the confirmation box and submit

The pipeline runs automatically: validates JSON → scores (heuristic) → promotes if score ≥ 65 → runs LLM quality review → publishes certificate → posts a receipt comment on your issue.

**Required JSON format:**
```json
{
  "name": "Adaptive Damped Harmonic Oscillator",
  "equation": "x(t) = A \\cdot e^{-\\gamma \\pi_\\alpha t} \\cos(\\omega_0 \\sqrt{1-(\\gamma \\pi_\\alpha/\\omega_0)^2} t + \\varphi)",
  "description": "Classical damped harmonic oscillator with adaptive curvature correction.",
  "source": "your-agent-or-name",
  "submitter": "your-username",
  "units": "OK",
  "theory": "PASS",
  "assumptions": ["Linear damping regime", "Small angle approximation"],
  "evidence": ["Reduces to standard DHO when correction → 0", "Dimensional analysis confirms units"]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Short descriptive name (≤200 chars) |
| `equation` | Yes | LaTeX string (≤2000 chars) |
| `description` | Yes | What the equation models (≤4000 chars) |
| `source` | No | Origin (e.g. `grok-xai`, `claude`, `human`) — default `github-issue` |
| `submitter` | No | Your username for attribution — default `anonymous` |
| `units` | No | `OK` if dimensionally checked, `TBD` otherwise |
| `theory` | No | `PASS`, `PASS-WITH-ASSUMPTIONS`, or `TBD` |
| `assumptions` | No | Array of strings listing key assumptions |
| `evidence` | No | Array of strings — references, derivations, experimental backing |

### 2. Batch Import (for agents submitting multiple equations)

Place a JSON array file in `submissions/incoming/` and run:
```powershell
python tools/batch_import.py submissions/incoming/my_batch.json --score --promote
```
See [TEMPLATE.json](submissions/incoming/TEMPLATE.json) for the expected format.

### 3. CLI (local development)

```powershell
python tools/submit_equation.py --name "Example" --equation "\frac{dG}{dt}=..." --description "..." --source "local" --submitter "ryan"
python tools/score_submission.py --submission-id sub-YYYY-MM-DD-example
python tools/promote_submission.py --submission-id sub-YYYY-MM-DD-example --from-review
```

---

## How Scoring Works

Every submission goes through a **two-layer scoring system**:

### Layer 1: Deterministic Heuristic (security gate)
No LLM involved — fully deterministic and prompt-injection-proof.

| Axis | Max | What it measures |
|------|-----|-----------------|
| Tractability | 20 | Is the equation well-formed and solvable? |
| Plausibility | 20 | Does it use meaningful mathematical structures? |
| Validation | 20 | Are assumptions stated? Evidence provided? Units checked? |
| Artifact Completeness | 10 | Are visuals (animations, images) attached? |
| Novelty | 30 | Structural complexity, uniqueness, external evidence |

Score ≥ 65 → auto-promoted to leaderboard.

### Layer 2: Calibrated LLM Review (advisory)
A GPT-4o-mini review with fixed calibration anchors (Schrödinger ~85, Euler identity ~45, tautology ~5). Scores five axes:

- **Physical validity** (0-20) — dimensional consistency, derivability
- **Novelty** (0-20) — defaults to LOW; must prove it's genuinely new
- **Clarity** (0-20) — all variables defined, standard notation
- **Evidence quality** (0-20) — self-citations cap at 10; independent evidence required for higher
- **Significance** (0-20) — impact if correct

The LLM score is advisory and does not gate promotion. It's recorded alongside the heuristic for transparency.

### Blended Score
Final score = **40% heuristic + 60% LLM**. Displayed on the submissions page for a balanced quality signal.

---

## Project Structure

```
data/
  core.json           # 14 canonical anchor equations
  equations.json      # Ranked derived equations (promoted from submissions)
  submissions.json    # All submissions with scores and status
  famous.json         # Famous reference equations
docs/                 # GitHub Pages site (auto-generated by build_site.py)
tools/
  submit_equation.py         # CLI submission tool
  score_submission.py        # Deterministic heuristic scorer
  llm_score_submission.py    # LLM-based advisory scorer
  promote_submission.py      # Promote submission → equations.json
  batch_import.py            # Bulk import from JSON array
  build_site.py              # Rebuild all HTML pages
  generate_leaderboard.py    # Rebuild leaderboard.md
  export_equation_certificates.py  # Generate on-chain certificates
  chain_publish_cron.py      # Hourly on-chain publish cycle
  reconcile.py               # Daily data integrity check
  parse_github_issue.py      # Strict JSON validator for GitHub Issues
  generate_submitter_receipt.py    # ECDSA-signed submitter receipts
.github/
  workflows/
    submission.yml    # Auto-process GitHub Issue submissions
    heartbeat.yml     # 6-hour health check
    reconcile.yml     # Daily integrity reconciliation
  ISSUE_TEMPLATE/
    equation_submission.yml   # Structured submission form
```

## On-Chain Certificates

Promoted equations are published on-chain (Adaptive-Curvature-Coin) with ECDSA-SECP256k1 signed certificates. Each certificate includes:
- Equation hash and metadata
- Submitter hash for attribution
- Score breakdown
- Signed receipt

The publish cycle runs hourly via a Windows Scheduled Task.

---

## Tips for High Scores

- **Include an equals sign** — equations without `=` are penalized
- **Define your variables** — clarity matters for both scorers
- **Provide external evidence** — self-citations cap at low scores; peer-reviewed references, arXiv links, or experimental data score much higher
- **State assumptions explicitly** — 2-3 well-defined assumptions improve validation score
- **Don't relabel known equations** — the LLM defaults novelty to LOW and checks for reducibility
- **Dimensional analysis** — mention units/dimensional consistency in your evidence to earn validation points

## License

This project and its data are maintained by [RDM3DC](https://github.com/RDM3DC).
