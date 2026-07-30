#!/usr/bin/env python3
"""The canonical summary lines for one account, shared by both senders.

The agent used to hand-write these as free-text bullet strings each run, which
meant the wording and even *which* points appeared could drift between runs.
It now emits typed fields and this builds the lines, so email and Slack always
show the same four points in the same order:

    Narrative / Topics / People/partners / Type

These four are the whole point of the tool — what the activity was, the theme
underneath it, what it covered, and who was involved. Engagement counts and
post links deliberately aren't here; they live in the dashboard, not in the
daily glance.
"""


def summary_lines(account: dict) -> list[str]:
    """Ordered 'Label: value' lines for an account with new activity.

    Falls back to any pre-built `bullets` list so an older-format summary still
    renders rather than silently arriving empty — but typed fields are canonical.
    """
    if not any(account.get(field) for field in ("narrative", "topics", "people_partners", "category")):
        return list(account.get("bullets", []))

    lines = []
    if account.get("narrative"):
        lines.append(f"Narrative: {account['narrative']}")
    if account.get("topics"):
        lines.append(f"Topics: {', '.join(account['topics'])}")
    # Omitted rather than shown empty — plenty of posts involve nobody external.
    if account.get("people_partners"):
        lines.append(f"People/partners: {', '.join(account['people_partners'])}")
    if account.get("category"):
        lines.append(f"Type: {account['category']}")
    return lines
