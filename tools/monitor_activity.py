"""Monitor GitHub repo activity after X post. Checks every 2 minutes."""
from __future__ import annotations
import json, time, subprocess, sys
from datetime import datetime

REPO = "RDM3DC/TopEquations"
INTERVAL = 120  # seconds

def gh(endpoint: str) -> dict | list:
    r = subprocess.run(
        ["gh", "api", f"repos/{REPO}{endpoint}"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return {}
    return json.loads(r.stdout)

def snapshot():
    repo = gh("")
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    watchers = repo.get("subscribers_count", 0)
    issues = repo.get("open_issues_count", 0)

    # Recent events (stars, forks, issues, etc.)
    events = gh("/events?per_page=10")
    recent = []
    if isinstance(events, list):
        for e in events[:10]:
            actor = e.get("actor", {}).get("login", "?")
            etype = e.get("type", "?")
            created = e.get("created_at", "")
            recent.append(f"  {created[:19]}  {etype:25s}  by {actor}")

    # New issues
    new_issues = gh("/issues?state=open&sort=created&direction=desc&per_page=5")
    issue_lines = []
    if isinstance(new_issues, list):
        for iss in new_issues[:5]:
            title = iss.get("title", "")[:60]
            num = iss.get("number", "?")
            user = iss.get("user", {}).get("login", "?")
            issue_lines.append(f"  #{num} by {user}: {title}")

    return stars, forks, watchers, issues, recent, issue_lines

prev_stars, prev_forks, prev_watchers, prev_issues = 0, 0, 0, 0

print(f"=== TopEquations Monitor (checking every {INTERVAL}s) ===")
print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
print()

cycle = 0
while True:
    now = datetime.now().strftime("%H:%M:%S")
    stars, forks, watchers, issues, recent, issue_lines = snapshot()

    delta = ""
    if cycle > 0:
        ds = stars - prev_stars
        df = forks - prev_forks
        di = issues - prev_issues
        changes = []
        if ds: changes.append(f"stars {'+' if ds > 0 else ''}{ds}")
        if df: changes.append(f"forks {'+' if df > 0 else ''}{df}")
        if di: changes.append(f"issues {'+' if di > 0 else ''}{di}")
        delta = f"  CHANGES: {', '.join(changes)}" if changes else "  (no changes)"

    print(f"[{now}] Stars={stars} Forks={forks} Watchers={watchers} Issues={issues}{delta}")

    if recent:
        print("  Recent events:")
        for r in recent:
            print(r)

    if issue_lines and cycle == 0:
        print("  Open issues:")
        for il in issue_lines:
            print(il)

    prev_stars, prev_forks, prev_watchers, prev_issues = stars, forks, watchers, issues
    cycle += 1
    sys.stdout.flush()
    time.sleep(INTERVAL)
