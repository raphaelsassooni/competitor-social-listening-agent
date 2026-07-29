#!/usr/bin/env python3
"""Fetch an Instagram account's recent posts via the ScrapeCreators API.

Usage: python3 fetch_posts.py <instagram_handle>
Prints normalized posts (id, url, posted_at, caption, media_type, engagement,
tagged accounts) as a JSON array to stdout — the raw API response is Instagram's
internal post format, ~50KB *per post*, almost all of it irrelevant to this project.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_URL = "https://api.scrapecreators.com/v2/instagram/user/posts"
MEDIA_TYPES = {1: "photo", 2: "video", 8: "carousel"}


def fetch_raw(handle: str) -> list[dict]:
    api_key = os.environ["SCRAPECREATORS_API_KEY"]
    query = urllib.parse.urlencode({"handle": handle})
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"x-api-key": api_key},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if isinstance(payload, list):
        return payload
    return payload.get("items") or payload.get("posts") or payload.get("data") or []


def normalize(post: dict) -> dict:
    caption = (post.get("caption") or {}).get("text", "")
    posted_at = datetime.fromtimestamp(post["taken_at"], tz=timezone.utc).isoformat()
    tagged = [tag["user"]["username"] for tag in (post.get("usertags") or {}).get("in", [])]
    return {
        "id": post["id"],
        "url": post.get("url") or f"https://www.instagram.com/p/{post.get('code')}/",
        "posted_at": posted_at,
        "caption": caption,
        "media_type": MEDIA_TYPES.get(post.get("media_type"), "other"),
        "like_count": post.get("like_count"),
        "comment_count": post.get("comment_count"),
        "tagged_accounts": tagged,
    }


def fetch_posts(handle: str) -> list[dict]:
    return [normalize(post) for post in fetch_raw(handle)]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: fetch_posts.py <instagram_handle>")
    try:
        posts = fetch_posts(sys.argv[1])
    except urllib.error.HTTPError as error:
        sys.exit(f"ScrapeCreators request failed for '{sys.argv[1]}': {error.code} {error.reason}")
    print(json.dumps(posts, indent=2))
