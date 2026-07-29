#!/usr/bin/env python3
"""Post the daily wrap-up to Slack via an incoming webhook, from data/today_summary.json.

Usage: python3 send_slack.py
Schema for data/today_summary.json is documented in send_email.py.
"""
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "data" / "today_summary.json"


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
    body = json.dumps({"blocks": build_blocks(summary)}).encode()
    request = urllib.request.Request(
        os.environ["SLACK_WEBHOOK_URL"],
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


if __name__ == "__main__":
    send_slack(json.loads(SUMMARY_PATH.read_text()))
