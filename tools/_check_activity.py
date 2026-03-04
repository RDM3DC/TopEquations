"""One-shot activity check."""
import json, subprocess

REPO = "RDM3DC/TopEquations"

def gh(ep):
    r = subprocess.run(["gh", "api", f"repos/{REPO}{ep}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else {}

repo = gh("")
print(f"Stars: {repo.get('stargazers_count', 0)}")
print(f"Forks: {repo.get('forks_count', 0)}")
print(f"Watchers: {repo.get('subscribers_count', 0)}")
print(f"Open Issues: {repo.get('open_issues_count', 0)}")

events = gh("/events?per_page=10")
if isinstance(events, list):
    print(f"\nRecent events ({len(events)}):")
    for e in events[:10]:
        ts = e.get("created_at", "")[:19]
        etype = e.get("type", "?")
        actor = e.get("actor", {}).get("login", "?")
        print(f"  {ts}  {etype:25s}  by {actor}")

issues = gh("/issues?state=open&sort=created&direction=desc&per_page=5")
if isinstance(issues, list):
    print(f"\nOpen issues ({len(issues)}):")
    for i in issues:
        num = i.get("number")
        user = i.get("user", {}).get("login", "?")
        title = i.get("title", "")[:60]
        print(f"  #{num} by {user}: {title}")
