Outreach Agent Scaffold for TopEquations

Purpose
- Provide a Git-ready scaffold to post via OAuth to multiple platforms (Twitter/X, Mastodon, Reddit).
- Schedule posts, integrate human-in-the-loop approval via Slack webhook, and collect basic analytics placeholders.

Architecture overview
- Python 3.13 API server (FastAPI) with routes for /auth/{platform}/start, /auth/{platform}/callback, /post, /approve, /schedule, /metrics
- OAuth integration stubs for X, Mastodon, Reddit using best-practice flows. Tokens stored in a local vault encrypted at rest.
- APScheduler-based job queue with per-platform rate limiting config
- Simple template engine with 12 sample templates in templates/*.json
- Logging, error handling with retry/backoff for failed posts
- Unit tests for auth callback parsing, scheduling, and approval gating

Getting started (quick setup)
- Prereqs: Python 3.13, pip, virtualenv (optional)
- Create a virtual environment and install dependencies
  python -m venv venv
  venv\Scripts\activate
  pip install fastapi uvicorn apscheduler pydantic requests tenacity cryptography
- Run the server locally (dummy keys):
  python -m outreach_agent.main --reload --port 8000
  # or with uvicorn directly:
  uvicorn outreach_agent.main:app --reload --port 8000

Security notes (OWASP at-rest)
- Tokens are encrypted at rest using a symmetric key stored in vault.enc (see vault_key.txt)
- Key rotation: rotate the key file and re-encrypt vaults; update vault_key.txt accordingly
- Secrets are never hard-coded; external keys must be provided via the vault or env vars at runtime

Registering apps and keys
- Create apps on X/Twitter, Mastodon, Reddit and obtain client_id/secret as per platform docs
- Paste client_id/secret into the vault:
  vault.enc contains per-platform encrypted token data; replace/extend using the provided tooling
- To rotate keys, update vault_key.txt with new key and re-encrypt vault data

Structure
- outreach_agent/
  - main.py (FastAPI app)
  - config.py (config, rate limits)
  - oauth.py (stubs for OAuth flows)
  - vault.py (encrypt/decrypt vault handling)
  - templates/ (12 json templates)
  - templates/__init__.py
  - tests/ (unit tests)

Notes
- This is scaffold-only. No real posts are sent without real API keys and human approval.
- All paths are relative to the repo root.
- Next steps: implement real OAuth flows, add tests, wire up Slack webhook approvals, and expand templates.
