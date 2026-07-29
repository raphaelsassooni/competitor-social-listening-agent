#!/usr/bin/env python3
"""Regenerate DASHBOARD.md from data/seen_posts.json and data/accounts.json.

Usage: python3 render_dashboard.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS_PATH = ROOT / "data" / "accounts.json"
STATE_PATH = ROOT / "data" / "seen_posts.json"
DASHBOARD_PATH = ROOT / "DASHBOARD.md"
MAX_POSTS_SHOWN_PER_ACCOUNT = 20


def render() -> str:
    accounts = json.loads(ACCOUNTS_PATH.read_text())
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}

    tracked_labels = ", ".join(account["label"] for account in accounts["accounts"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Competitor Watch — {accounts['company']}",
        "",
        f"_Tracking: {tracked_labels}_",
        "",
        f"_Last updated: {now}_",
        "",
    ]

    any_posts = False
    for account in accounts["accounts"]:
        handle = account["handle"]
        posts = state.get(handle, [])
        if not posts:
            continue
        any_posts = True
        lines.append(f"## {account['label']}")
        lines.append("")
        for post in posts[:MAX_POSTS_SHOWN_PER_ACCOUNT]:
            posted_at = post.get("posted_at", "")[:10]
            lines.append(f"**{posted_at}** — {post.get('category', 'Uncategorized')} — {post.get('narrative', '')}")
            if post.get("topics"):
                lines.append(f"Topics: {', '.join(post['topics'])}")
            if post.get("people_partners"):
                lines.append(f"People/partners: {', '.join(post['people_partners'])}")
            if post.get("url"):
                lines.append(f"[View post]({post['url']})")
            lines.append("")

    if not any_posts:
        lines.append("No posts logged yet — this file is regenerated automatically after each daily run. See [`ROUTINE.md`](ROUTINE.md) for how.")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    DASHBOARD_PATH.write_text(render())
