#!/usr/bin/env python3
"""Send one wrap-up email per brand with new activity, from data/today_summary.json.

Usage: python3 send_email.py

Brands with no new activity are skipped entirely — no "nothing new" emails, since
that would mean one dead email per brand per day. Slack covers the quiet days.

Expected schema for data/today_summary.json:
{
  "brands": [
    {
      "brand": "Moovit",
      "run_date": "2026-07-29",
      "has_activity": true,
      "accounts": [
        {
          "label": "Waze",
          "new_post_count": 1,
          "headline": "Waze rolled out a new fuel-price overlay",
          "bullets": ["Narrative: ...", "Topics: ...", "People/partners: ...", "Type: ..."]
        }
      ]
    }
  ]
}
"""
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "data" / "today_summary.json"
RESEND_URL = "https://api.resend.com/emails"


def build_html(brand: dict) -> str:
    accounts_html = ""
    for account in brand["accounts"]:
        if account.get("new_post_count"):
            bullets_html = "".join(f"<li style='margin:4px 0;color:#3f3f46;'>{b}</li>" for b in account.get("bullets", []))
            body = f"<p style='margin:6px 0 8px;font-weight:600;color:#18181b;'>{account['headline']}</p><ul style='margin:0;padding-left:18px;'>{bullets_html}</ul>"
        else:
            body = "<p style='margin:6px 0 0;color:#a1a1aa;'>Nothing new today.</p>"
        accounts_html += (
            "<div style='padding:16px 0;border-bottom:1px solid #e4e4e7;'>"
            f"<p style='margin:0;font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:#71717a;'>{account['label']}</p>"
            f"{body}"
            "</div>"
        )

    return f"""
    <div style="max-width:520px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,sans-serif;">
      <p style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#71717a;margin:0 0 4px;">Competitor Watch</p>
      <h1 style="font-size:20px;margin:0 0 2px;color:#18181b;">Competitors of {brand['brand']}</h1>
      <p style="font-size:14px;color:#71717a;margin:0 0 20px;">{brand['run_date']}</p>
      {accounts_html}
      <p style="margin:20px 0 0;font-size:12px;color:#a1a1aa;">Full history in the project dashboard on GitHub.</p>
    </div>
    """


def send_brand_email(brand: dict) -> None:
    body = json.dumps({
        "from": os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev"),
        "to": [os.environ["REPORT_TO_EMAIL"]],
        "subject": f"Competitor watch — {brand['brand']} — {brand['run_date']}",
        "html": build_html(brand),
    }).encode()

    request = urllib.request.Request(
        RESEND_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type": "application/json",
            # Cloudflare (in front of Resend's API) blocks urllib's default UA as bot traffic.
            "User-Agent": "competitor-social-listening-agent/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


def send_email(summary: dict) -> None:
    for brand in summary["brands"]:
        if brand.get("has_activity"):
            send_brand_email(brand)
            print(f"emailed: {brand['brand']}")
        else:
            print(f"skipped (no activity): {brand['brand']}")


if __name__ == "__main__":
    send_email(json.loads(SUMMARY_PATH.read_text()))
