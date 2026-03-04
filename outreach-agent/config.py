# Configuration placeholder for outreach agent

PLATFORMS = ["x", "mastodon", "reddit"]
RAISE_ON_ERROR = True

# Simple in-file rate limit config per platform (requests per hour)
RATE_LIMIT = {
    "x": 60,
    "mastodon": 120,
    "reddit": 30,
}
