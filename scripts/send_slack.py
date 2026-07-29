#!/usr/bin/env python3
"""Post the daily wrap-up to Slack via chat.postMessage, from data/today_summary.json.

Usage: python3 send_slack.py
Schema for data/today_summary.json is documented in send_email.py.
Needs SLACK_BOT_TOKEN (xoxb-...) and SLACK_CHANNEL (e.g. #general) — the bot
must be a member of that channel first (invite it with /invite @<app name>).
"""
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "data" / "today_summary.json"
POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"


def build_blocks(summary: dict) -> list[dict]:
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Competitor watch — {summary['run_date']}"}},
    ]
    for account in summary["accounts"]:
        if account.get("new_post_count"):
            bullet_text = "\n".join(f"• {b}" for b in account.get("bullets", []))
            text = f"*{account['label']} — {account['headline']}*\n{bullet_text}"
        else:
            text = f"*{account['label']}* — nothing new today"
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    blocks.append({"type": "divider"})
    return blocks


def send_slack(summary: dict) -> None:
    body = json.dumps({
        "channel": os.environ["SLACK_CHANNEL"],
        "blocks": build_blocks(summary),
    }).encode()
    request = urllib.request.Request(
        POST_MESSAGE_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}",
            "Content-Type": "application/json",
            "User-Agent": "competitor-social-listening-agent/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(f"Slack API error: {result.get('error')}")


if __name__ == "__main__":
    send_slack(json.loads(SUMMARY_PATH.read_text()))
