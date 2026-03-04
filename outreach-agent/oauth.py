# OAuth stubs for X (Twitter), Mastodon, Reddit
from fastapi import Request

async def oauth_start(platform: str):
    return {"status":"stub","platform":platform}

async def oauth_callback(platform: str, request: Request):
    # Parse query params as placeholder
    return {"status":"stub","platform":platform, "params": dict(request.query_params)}
