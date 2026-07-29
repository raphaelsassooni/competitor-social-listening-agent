#!/usr/bin/env python3
"""Regenerate DASHBOARD.md from data/seen_posts.json and data/accounts.json.

Usage: python3 render_dashboard.py

The dashboard is cumulative: every brand in accounts.json gets its own section,
and adding a brand never removes an existing one's history.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS_PATH = ROOT / "data" / "accounts.json"
STATE_PATH = ROOT / "data" / "seen_posts.json"
DASHBOARD_PATH = ROOT / "DASHBOARD.md"
MAX_POSTS_SHOWN_PER_ACCOUNT = 20


def render_post(post: dict) -> list[str]:
    lines = [f"**{post.get('posted_at', '')[:10]}** — {post.get('category', 'Uncategorized')} — {post.get('narrative', '')}"]
    if post.get("like_count") is not None or post.get("comment_count") is not None:
        lines.append(f"{post.get('like_count', 0):,} likes · {post.get('comment_count', 0):,} comments")
    if post.get("topics"):
        lines.append(f"Topics: {', '.join(post['topics'])}")
    if post.get("people_partners"):
        lines.append(f"People/partners: {', '.join(post['people_partners'])}")
    if post.get("url"):
        lines.append(f"[View post]({post['url']})")
    lines.append("")
    return lines


def render() -> str:
    accounts = json.loads(ACCOUNTS_PATH.read_text())
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Competitor Watch", "", f"_Last updated: {now}_", ""]

    any_posts = False
    for brand in accounts["brands"]:
        tracked = ", ".join(account["label"] for account in brand["accounts"])
        lines.append(f"## {brand['brand']}")
        lines.append("")
        lines.append(f"_Competitors tracked: {tracked}_")
        lines.append("")

        for account in brand["accounts"]:
            posts = state.get(account["handle"], [])
            if not posts:
                continue
            any_posts = True
            lines.append(f"### {account['label']}")
            lines.append("")
            for post in posts[:MAX_POSTS_SHOWN_PER_ACCOUNT]:
                lines.extend(render_post(post))

    if not any_posts:
        lines.append("No posts logged yet — this file is regenerated automatically after each daily run. See [`ROUTINE.md`](ROUTINE.md) for how.")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    DASHBOARD_PATH.write_text(render())
