#!/usr/bin/env python3
"""Filter fetched posts down to the ones not already logged for this account.

Usage: python3 fetch_posts.py <handle> | python3 diff_new_posts.py <handle>
Prints the genuinely-new posts as a JSON array to stdout.
"""
import json
import sys
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_posts.json"


def load_seen_ids(handle: str) -> set[str]:
    if not STATE_PATH.exists():
        return set()
    state = json.loads(STATE_PATH.read_text())
    return {str(post["id"]) for post in state.get(handle, [])}


def new_posts(handle: str, fetched: list[dict]) -> list[dict]:
    seen_ids = load_seen_ids(handle)
    return [post for post in fetched if str(post.get("id")) not in seen_ids]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: diff_new_posts.py <instagram_handle>  (reads fetched posts JSON from stdin)")
    fetched_posts = json.load(sys.stdin)
    print(json.dumps(new_posts(sys.argv[1], fetched_posts), indent=2))
