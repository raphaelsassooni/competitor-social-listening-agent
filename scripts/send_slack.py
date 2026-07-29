#!/usr/bin/env python3
"""Post one wrap-up per brand to that brand's own Slack channel.

Usage: python3 send_slack.py
Schema for data/today_summary.json is documented in send_email.py.

Unlike email, this sends for every brand every day — a one-line note on quiet
days, so there's always a signal the run happened.

Needs SLACK_BOT_TOKEN with scopes: chat:write, channels:manage (to create a
brand's channel on first use), channels:join (to join a channel that already
existed). Channels are named per brand in data/accounts.json.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "data" / "today_summary.json"
ACCOUNTS_PATH = ROOT / "data" / "accounts.json"
SLACK_API = "https://slack.com/api"


def slack_call(method: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{SLACK_API}/{method}",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}",
            "Content-Type": "application/json",
            "User-Agent": "competitor-social-listening-agent/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def ensure_channel(name: str) -> str:
    """Return a channel reference for `name`, creating it if it doesn't exist yet.

    A channel the bot creates is one it's automatically a member of. If the
    channel already exists we fall back to addressing it by name, which
    chat.postMessage accepts — that avoids needing read scopes just to look up
    an ID we don't otherwise need.
    """
    created = slack_call("conversations.create", {"name": name})
    if created.get("ok"):
        return created["channel"]["id"]
    if created.get("error") == "name_taken":
        return f"#{name}"
    raise RuntimeError(f"Slack conversations.create failed for #{name}: {created.get('error')}")


def build_blocks(brand: dict) -> list[dict]:
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Competitors of {brand['brand']} — {brand['run_date']}"}},
    ]
    if not brand.get("has_activity"):
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_Nothing new today._"}})
        return blocks

    for account in brand["accounts"]:
        if account.get("new_post_count"):
            bullet_text = "\n".join(f"• {b}" for b in account.get("bullets", []))
            text = f"*{account['label']} — {account['headline']}*\n{bullet_text}"
        else:
            text = f"*{account['label']}* — nothing new today"
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    return blocks


def post_brand(brand: dict, channel_name: str) -> None:
    channel = ensure_channel(channel_name)
    result = slack_call("chat.postMessage", {"channel": channel, "blocks": build_blocks(brand)})
    if result.get("error") == "not_in_channel":
        raise RuntimeError(
            f"The bot isn't in #{channel_name} (a channel it didn't create). Invite it in Slack "
            f"with /invite, or delete the channel and let the next run recreate it."
        )
    if not result.get("ok"):
        raise RuntimeError(f"chat.postMessage failed: {result.get('error')}")


def send_slack(summary: dict) -> None:
    accounts = json.loads(ACCOUNTS_PATH.read_text())
    channel_by_brand = {b["brand"]: b["slack_channel"] for b in accounts["brands"]}

    # One brand's failure shouldn't stop the others from being delivered.
    failures = []
    for brand in summary["brands"]:
        name = brand["brand"]
        try:
            post_brand(brand, channel_by_brand[name])
            print(f"posted: {name} -> #{channel_by_brand[name]}")
        except (RuntimeError, KeyError, urllib.error.URLError) as error:
            failures.append(f"{name}: {error}")
            print(f"FAILED: {name}: {error}")

    if failures:
        raise SystemExit(f"{len(failures)} brand(s) failed to post: " + "; ".join(failures))


if __name__ == "__main__":
    send_slack(json.loads(SUMMARY_PATH.read_text()))
