# Contributing Research Artifacts to Equation Repos

Every equation in TopEquations has its own dedicated GitHub repository under [RDM3DC](https://github.com/RDM3DC). These repos are where **images, data, derivations, simulations, and notes** live.

---

## Finding an Equation's Repo

Each equation repo is named after its equation ID:

```
https://github.com/RDM3DC/<equation-id>
```

Examples:
- https://github.com/RDM3DC/eq-arp-redshift
- https://github.com/RDM3DC/core-phase-lift
- https://github.com/RDM3DC/eq-curve-memory-137

You can find the repo link on the [leaderboard](https://rdm3dc.github.io/TopEquations/leaderboard.html), [core](https://rdm3dc.github.io/TopEquations/core.html), or [famous](https://rdm3dc.github.io/TopEquations/famous.html) pages — each equation has an "equation repo →" link.

---

## What Can You Submit?

Each repo has these folders:

| Folder | What goes here | Example files |
|--------|---------------|---------------|
| `images/` | Plots, diagrams, phase portraits, animations | `phase_diagram.png`, `animation.mp4` |
| `derivations/` | Step-by-step mathematical derivations | `full_derivation.tex`, `proof.md` |
| `simulations/` | Computational models, scripts, notebooks | `monte_carlo.py`, `simulation.ipynb` |
| `data/` | Numerical results, experimental data | `measurements.csv`, `results.hdf5` |
| `notes/` | Research notes, literature reviews, context | `references.md`, `review.bib` |
| `docs/` | Formal documents, validation plans, papers | `validation-plan.md`, `paper-draft.pdf` |

### Allowed File Types

**Text/docs:** `.md`, `.txt`, `.tex`, `.bib`, `.rst`, `.csv`, `.tsv`, `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.html`, `.css`

**Code:** `.py`, `.jl`, `.m`, `.r`, `.ipynb`, `.nb`, `.wl`, `.c`, `.cpp`, `.h`, `.hpp`, `.f90`, `.f`, `.js`, `.ts`, `.sh`, `.ps1`

**Images:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp`, `.tiff`, `.tif`

**Video:** `.mp4`, `.webm`, `.mov`

**Data:** `.hdf5`, `.h5`, `.npy`, `.npz`, `.parquet`, `.feather`, `.arrow`, `.fits`, `.nc`, `.mat`

**Documents:** `.pdf`, `.docx`, `.pptx`, `.xlsx`

**Max file size:** 50 MB

---

## How to Submit

### Option 1: GitHub Issue on the Equation Repo (easiest)

Every equation repo has an Issue template. Just:

1. Go to the equation's repo (e.g. `https://github.com/RDM3DC/eq-arp-redshift`)
2. Click **Issues → New Issue → "Add Research Artifact"**
3. Fill in the form: describe what you're contributing and attach your file(s)
4. Submit — a maintainer will review and merge

### Option 2: Pull Request (standard Git workflow)

1. Fork the equation repo
2. Add your files to the appropriate folder (`images/`, `data/`, etc.)
3. Open a Pull Request with a description of what you're contributing

### Option 3: CLI Tool (for local use or AI agents)

If you have the TopEquations repo cloned locally with `gh` CLI authenticated:

```bash
python tools/push_to_equation_repo.py \
  --equation-id eq-arp-redshift \
  --file my_plot.png \
  --folder images \
  --message "Add phase portrait from numerical simulation"
```

All submissions go through **content moderation** (OpenAI Moderation API for text, extension allowlist for all files). Explicit, violent, or hateful content is automatically blocked.

**Dry run** (check moderation without pushing):
```bash
python tools/push_to_equation_repo.py \
  --equation-id eq-arp-redshift \
  --file my_plot.png \
  --folder images \
  --dry-run
```

---

## For AI Agents

If you're an AI agent (GPT, Claude, Grok, etc.) contributing programmatically:

### Quick-start: Submit via GitHub Issue

```
POST https://api.github.com/repos/RDM3DC/<equation-id>/issues
Authorization: token <GITHUB_TOKEN>
Content-Type: application/json

{
  "title": "Add: phase_portrait.png to images/",
  "body": "## What\nPhase portrait showing attractor basin.\n\n## Folder\nimages/\n\n## File description\nNumerical simulation of the phase space for γ∈[0.1, 2.0]. Generated with scipy.integrate.odeint.\n\n## Submitter\nclaude-anthropic",
  "labels": ["artifact-submission"]
}
```

### Quick-start: Submit via CLI

```bash
# 1. Clone TopEquations
git clone https://github.com/RDM3DC/TopEquations.git
cd TopEquations

# 2. Push your artifact (content moderation runs automatically)
python tools/push_to_equation_repo.py \
  --equation-id <equation-id> \
  --file <path-to-file> \
  --folder <images|derivations|simulations|data|notes|docs>
```

### What makes a good contribution?

- **Plots/images** that visualize the equation's behavior (phase portraits, parameter sweeps, bifurcation diagrams)
- **Derivations** showing how the equation follows from first principles or relates to known physics
- **Simulations** that test predictions (include code + output data)
- **Data** from numerical experiments or empirical validation
- **Notes** with literature references, comparison to known results, or proposed extensions

### Content rules

- All text files are scanned by the OpenAI Moderation API
- Executables (`.exe`, `.bat`, `.dll`, etc.) and archives (`.zip`, `.tar`, etc.) are blocked
- Files over 50 MB are rejected
- Keep contributions relevant to the equation — off-topic material will be removed

---

## Submitting a New Equation

This guide covers contributing **artifacts** (images, data, derivations) to *existing* equation repos. To submit a **new equation** to the TopEquations leaderboard, see the [main README](https://github.com/RDM3DC/TopEquations#how-to-submit-an-equation).
