#!/usr/bin/env python3
"""Merge analyzed post records into data/seen_posts.json for one account.

Usage: python3 append_posts.py <handle>  (reads a JSON array of records from stdin)
Each record: {"id", "url", "posted_at", "caption_excerpt", "media_type",
              "like_count", "comment_count", "category", "narrative",
              "topics": [...], "people_partners": [...]}
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_posts.json"
MAX_RECORDS_PER_ACCOUNT = 200


def append_posts(handle: str, new_records: list[dict]) -> None:
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    existing = state.get(handle, [])
    existing_ids = {str(post["id"]) for post in existing}

    for record in new_records:
        record["id"] = str(record["id"])
        record.setdefault("first_seen_at", datetime.now(timezone.utc).isoformat())
        if record["id"] not in existing_ids:
            existing.insert(0, record)
            existing_ids.add(record["id"])

    state[handle] = existing[:MAX_RECORDS_PER_ACCOUNT]
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: append_posts.py <instagram_handle>  (reads JSON array of analyzed records from stdin)")
    append_posts(sys.argv[1], json.load(sys.stdin))
