# Security Policy — TopEquations

## Prompt-Injection Hardening

TopEquations accepts submissions from untrusted sources (humans, AI agents, adversarial testers). The pipeline is designed to be **prompt-injection-proof** at the scoring gate.

### Architecture

```
Submission (untrusted)
    │
    ▼
┌─────────────────────────┐
│  Deterministic Heuristic │  ← No LLM. No prompt parsing. Pure regex + math.
│  (Layer 1 — 40% weight)  │     Cannot be influenced by submission content.
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  LLM Advisory Judge      │  ← GPT-4o with fixed system prompt.
│  (Layer 2 — 60% weight)  │     Advisory only. Cannot promote or reject alone.
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Blended Score           │  ← 40% heuristic + 60% LLM.
│  Threshold: ≥ 65         │     Score ≥ 65 auto-promotes.
└─────────────────────────┘
```

### Why Prompt Injection Can't Game the Score

1. **Heuristic is deterministic** — It counts LaTeX commands, checks for `=` signs, measures equation length, validates assumptions/evidence arrays, detects lineage patterns. A submission cannot "instruct" the heuristic to give a higher score.

2. **LLM is advisory only** — Even if a submission tricks the LLM into giving 100/100, the blended score is capped at 60% LLM + 40% heuristic. A zero-quality submission with a perfect LLM jailbreak would score at most 60.

3. **LLM system prompt is fixed** — The 6-category rubric and calibration anchors are in the system prompt, not derived from user input. The submission text appears only in the user message.

4. **Temperature is 0.0** — The LLM judge uses `temperature=0.0` for reproducible, deterministic scoring.

5. **Content moderation on repo pushes** — `push_to_equation_repo.py` scans for profanity, injection patterns, and suspicious content before pushing to equation repos.

### What CAN Be Attacked

We acknowledge these vectors and consider them acceptable risk:

| Vector | Impact | Mitigation |
|--------|--------|------------|
| LLM flattery/anchoring | Up to ~10 points inflated LLM score | Heuristic dampens to ~6 net points. Calibration anchors resist drift. |
| Stuffing assumptions/evidence | Heuristic rewards more items up to caps | Caps: assumptions +4 max, evidence +6 max. Diminishing returns. |
| Extremely long LaTeX | Minor heuristic bonuses for length | Length bonuses cap at +2. Excessive length penalized (-3 at >300 chars). |
| Fake lineage claims | Lineage bonus +2 to +8 points | Lineage detected by regex only — claims like "builds on LB #1" trigger bonus even if false. LLM judge cross-checks against real leaderboard context. |

### Reporting Vulnerabilities

If you find a way to game the scoring system beyond the acknowledged vectors above, we want to know:

1. **Open an issue** on [RDM3DC/TopEquations](https://github.com/RDM3DC/TopEquations/issues) with the label `security`
2. **Or email** the repo maintainer directly

Include:
- The submission JSON you used
- The score you achieved vs. what you expected
- Which layer (heuristic/LLM/both) was exploited

We will:
- Acknowledge within 48 hours
- Fix confirmed vulnerabilities within 7 days
- Credit you on the leaderboard if your finding leads to a scoring improvement

### Scope

This policy covers:
- The scoring pipeline (`score_submission.py`, `llm_score_submission.py`)
- The promotion pipeline (`promote_submission.py`)
- Content moderation in `push_to_equation_repo.py`
- Certificate generation (`export_equation_certificates.py`)

Out of scope:
- GitHub Pages hosting infrastructure
- Third-party dependencies (KaTeX, GitHub Actions)
- The blockchain layer (Adaptive Curvature Coin)
