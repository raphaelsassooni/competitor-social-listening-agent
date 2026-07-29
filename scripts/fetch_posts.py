#!/usr/bin/env python3
"""Fetch an Instagram account's recent posts via the ScrapeCreators API.

Usage: python3 fetch_posts.py <instagram_handle>
Prints the fetched posts as a JSON array to stdout.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

API_URL = "https://api.scrapecreators.com/v2/instagram/user/posts"


def fetch_posts(handle: str) -> list[dict]:
    api_key = os.environ["SCRAPECREATORS_API_KEY"]
    query = urllib.parse.urlencode({"handle": handle})
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"x-api-key": api_key},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    # ScrapeCreators' public docs don't publish a full response sample, so the
    # exact wrapper key is unconfirmed — handle the shapes a JSON API like this
    # commonly uses. Adjust once a live response has been inspected.
    if isinstance(payload, list):
        return payload
    return payload.get("items") or payload.get("posts") or payload.get("data") or []


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: fetch_posts.py <instagram_handle>")
    try:
        posts = fetch_posts(sys.argv[1])
    except urllib.error.HTTPError as error:
        sys.exit(f"ScrapeCreators request failed for '{sys.argv[1]}': {error.code} {error.reason}")
    print(json.dumps(posts, indent=2))
