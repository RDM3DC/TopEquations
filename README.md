# TopEquations

[![Live Site](https://img.shields.io/badge/Live_Site-rdm3dc.github.io-blue?style=flat-square)](https://rdm3dc.github.io/TopEquations/)
[![Equations](https://img.shields.io/badge/Equations-94-brightgreen?style=flat-square)](https://rdm3dc.github.io/TopEquations/registry.html)
[![Certificates](https://img.shields.io/badge/Blockchain_Certs-94-orange?style=flat-square)](https://rdm3dc.github.io/TopEquations/certificates.html)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-%24rdm3d-00d632?style=flat-square&logo=cashapp)](https://cash.app/$rdm3d)
[![PR Root Guide GPT](https://img.shields.io/badge/GPT-PR_Root_Guide-412991?style=flat-square&logo=openai)](https://chatgpt.com/g/g-695b42b4f0048191b0edb6795c9643cf-pr-root-guide)


Equations are ranked on a composite registry scale backed by a dual-layer review system (deterministic heuristic + calibrated LLM), published on-chain with ECDSA-signed certificates, and displayed on a public site. The heuristic and LLM components are normalized to 0-100, but the public registry is effectively open-ended, so exceptional legacy or manual entries can exceed 100. The scoring pipeline is **prompt-injection hardened** — the deterministic gate (40%) can't be gamed by clever prompting.

**→ [Submit yours](https://github.com/RDM3DC/TopEquations/issues/new?template=equation_submission.yml)** and see where you rank.

---

## Live Site

**[rdm3dc.github.io/TopEquations](https://rdm3dc.github.io/TopEquations/)**

| Page | What's there |
|------|-------------|
| [Canonical Core](https://rdm3dc.github.io/TopEquations/core.html) | 14 anchor equations (Maxwell, Schrödinger, Navier-Stokes, etc.) |
| [Registry](https://rdm3dc.github.io/TopEquations/registry.html) | Ranked derived equations by composite score |
| [Rising](https://rdm3dc.github.io/TopEquations/rising.html) | Below-threshold equations that are close to promotion |
| [All Submissions](https://rdm3dc.github.io/TopEquations/submissions.html) | Every submission with scores and status |
| [Certificates](https://rdm3dc.github.io/TopEquations/certificates.html) | On-chain certificate registry |

---

## How to Submit an Equation

Equations can be submitted in three ways:

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
  "equation": "x(t) = A \cdot e^{-\gamma \pi_\alpha t} \cos(\omega_0 \sqrt{1-(\gamma \pi_\alpha/\omega_0)^2} t + \varphi)",
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
| `source` | No | Origin tag (e.g. `paper-note`, `simulation`, `github-issue`) — default `github-issue` |
| `submitter` | No | Your username for attribution — default `anonymous` |
| `units` | No | `OK` if dimensionally checked, `TBD` otherwise |
| `theory` | No | `PASS`, `PASS-WITH-ASSUMPTIONS`, or `TBD` |
| `assumptions` | No | Array of strings listing key assumptions |
| `evidence` | No | Array of strings — references, derivations, experimental backing |

### 2. Batch Import (for multiple equations)

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

Component scores are normalized to 0-100, but the published registry can include historical or manually promoted entries above 100.

### Layer 1: Deterministic Heuristic (security gate)
No LLM involved — fully deterministic and prompt-injection-proof.

| Axis | Max | What it measures |
|------|-----|-----------------|
| Tractability | 20 | Is the equation well-formed and solvable? |
| Plausibility | 20 | Does it use meaningful mathematical structures? |
| Validation | 20 | Are assumptions stated? Evidence provided? Units checked? |
| Artifact Completeness | 10 | Are visuals (animations, images) attached? |
| Novelty | 30 | Structural complexity, uniqueness, external evidence |

Score ≥ 65 → auto-published to the registry.

### Layer 2: Calibrated LLM Review (advisory)
A GPT-5.4 review with fixed calibration anchors (Schrödinger ~85, Euler identity ~45, tautology ~5). It scores six weighted categories:

- **Traceability** — lineage to existing entries, derivation bridges, recovery clauses
- **Rigor** — dimensional consistency, variable definitions, internal coherence
- **Assumptions** — explicit, falsifiable assumptions and stated operating domain
- **Presentation** — readable notation, explanation quality, artifact readiness
- **Novelty / insight** — whether the submission meaningfully extends the program
- **Fruitfulness** — whether the submission is simulation-ready and easy to build on

The LLM score is advisory and does not gate promotion. It's recorded alongside the heuristic for transparency.

### Blended Score
When an LLM review is available, the advisory blended score is **40% heuristic + 60% LLM**. Promotion still keys off the heuristic review status in the current GitHub workflow.

### Gold Highlight
Gold highlighting is a curator-selected display marker, not an automatic consequence of score. It is reserved for equations judged especially central, bridge-forming, or program-defining within the current TopEquations lineage.

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
  generate_leaderboard.py    # Rebuild registry.md and leaderboard.md
  export_equation_certificates.py  # Generate on-chain certificates
  chain_publish_cron.py      # Local fallback publish script
  reconcile.py               # Daily data integrity check
  parse_github_issue.py      # Strict JSON validator for GitHub Issues
  generate_submitter_receipt.py    # ECDSA-signed submitter receipts
.github/
  workflows/
    submission.yml    # Auto-process GitHub Issue submissions
    publish_chain.yml # Scheduled on-chain certificate publish job
    heartbeat.yml     # 6-hour health check
    reconcile.yml     # Daily integrity reconciliation
  ISSUE_TEMPLATE/
    equation_submission.yml   # Structured submission form
```

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
pytest
ruff check tests tools/score_submission.py tools/generate_leaderboard.py tools/build_site.py
python tools/generate_leaderboard.py
python tools/build_site.py
```

Recommended rebuild order:

1. Update `data/equations.json` or `data/submissions.json`
2. Run `python tools/generate_leaderboard.py`
3. Run `python tools/build_site.py`

This regenerates `registry.md`, the legacy alias `leaderboard.md`, `docs/*.html`, and published machine-readable JSON under `docs/data/`.

## Machine-Readable Outputs

Published static artifacts are available at stable paths in GitHub Pages:

- `docs/data/equations.json` — full promoted equation registry
- `docs/data/registry.json` — current published registry slice
- `docs/data/leaderboard.json` — legacy alias of the registry slice
- `docs/data/submissions.json` — submission queue and review state
- `docs/data/certificates/equation_certificates.json` — published certificate set

These files are generated from source data in `data/` and should be treated as public read-only exports.

## On-Chain Certificates

Promoted equations are published on-chain (Adaptive-Curvature-Coin) with ECDSA-SECP256k1 signed certificates. Each certificate includes:
- Equation hash and metadata
- Submitter hash for attribution
- Score breakdown
- Signed receipt

The default publish cycle runs hourly via GitHub Actions against a cloud-hosted node. Set `CHAIN_NODE_URL`, `CHAIN_WALLET_PUBLIC_KEY`, and `CHAIN_WALLET_PRIVATE_KEY` in repository secrets for automation. The local Windows scheduled task path remains available as a fallback for private or offline deployments.

---

## Tips for High Scores

- **Include an equals sign** — equations without `=` are penalized
- **Define your variables** — clarity matters for both scorers
- **Provide external evidence** — self-citations cap at low scores; peer-reviewed references, arXiv links, or experimental data score much higher
- **State assumptions explicitly** — 2-3 well-defined assumptions improve validation score
- **Don't relabel known equations** — the LLM defaults novelty to LOW and checks for reducibility
- **Dimensional analysis** — mention units/dimensional consistency in your evidence to earn validation points

---

## Canonical Papers

The theoretical foundations behind the equations in this registry are documented in the **Canonical Core** papers:

> **[rdm3dc.github.io/canonical-core](https://rdm3dc.github.io/canonical-core/)** — ARP/AIN, Adaptive-π Geometry, Curve Memory, Phase-Lift, and QPS Mapping.

---

## Contributing Research Artifacts

Every equation has its own GitHub repo (e.g. [RDM3DC/eq-arp-redshift](https://github.com/RDM3DC/eq-arp-redshift)) for storing images, derivations, simulations, data, and notes.

**Research artifacts can be contributed in three ways:**
1. **GitHub Issue** — open an issue on the equation's repo using the "Add Research Artifact" template
2. **Pull Request** — fork the equation repo, add files, open a PR
3. **CLI tool** — `python tools/push_to_equation_repo.py --equation-id <id> --file <path> --folder <folder>`

All submissions are content-moderated (text scanned by OpenAI Moderation API, extension allowlist enforced).

See the **[full contributing guide](CONTRIBUTING.md)** for details, allowed file types, and programmatic quick-start examples.

---

## License

This project is released under the [MIT License](LICENSE).

Data and generated registry outputs are distributed from this repository on the same basis unless a source artifact states otherwise.