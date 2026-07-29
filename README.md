# Competitor Social Listening Agent

Most of the real work in social media isn't writing captions or producing creative — it's understanding the narrative the market is talking about. Staying aware of what competitors are doing is part of that job, but in practice it's usually manual and inconsistent: something a social media manager checks sporadically, if at all.

This tool automates that specific piece of the work. It monitors a defined set of competitor Instagram accounts, and once a day — if there's been activity — produces a structured summary: what happened, the main narrative or theme, areas of interest, who was involved, and a rough categorisation. That summary is delivered automatically, so market awareness becomes a standing, consistent input rather than something that depends on someone remembering to check.

The output isn't the competitor's content itself — it's the pattern underneath it, which is the part that actually informs strategy and content decisions.

The tool is brand-agnostic: point it at any set of competitor accounts for any brand or agency. The example below (Moovit, tracking Waze, Google Maps and Transit) is a working demonstration, not the point of the tool itself.

Runs unattended on a daily GitHub Actions schedule — no server or laptop required.

## How it works

1. [`data/accounts.json`](data/accounts.json) groups tracked Instagram accounts by the brand they compete with (currently: Moovit, tracking Waze, Google Maps and Transit).
2. Each day, the agent fetches recent posts for every active account via the [ScrapeCreators](https://scrapecreators.com) API.
3. Posts not already logged in `data/seen_posts.json` get analyzed by the agent itself — narrative, topics, people/partners, category. That reasoning step is the actual "AI" in this project; everything else is plain deterministic code.
4. The log (`data/seen_posts.json`) and dashboard ([`DASHBOARD.md`](DASHBOARD.md)) are updated and committed. The dashboard is cumulative — adding a brand never removes an existing one's history.
5. Each brand gets its own wrap-up, kept separate rather than merged:
   - **Email** (via [Resend](https://resend.com)) — one per brand, sent only when that brand actually had new activity.
   - **Slack** — one per brand in its own channel (`#moovit-watch`, etc.), every day, with a one-line note on quiet days so there's always a signal the run happened.

## Tracking a new brand

Ask Claude in a session pointed at this repo — *"track competitors of Similarweb"* — and it will research the brand's category, verify each competitor's real Instagram handle, propose up to five, and update the config once you confirm. The Slack channel for a new brand is created automatically on its first run. No JSON editing, no code changes.

[`ROUTINE.md`](ROUTINE.md) is the exact set of instructions the agent follows each run — read that for the full orchestration.

## Project layout

```
data/accounts.json        which accounts to track — edit this to add/remove competitors
data/seen_posts.json      persistent log of every post already reported, with its analysis
data/today_summary.json   ephemeral per-run summary, consumed by the two senders (not committed)
DASHBOARD.md               human-readable dashboard, regenerated every run
scripts/                   one script per step, each runnable and testable on its own
ROUTINE.md                  the day-to-day instructions the scheduled agent follows
```

## Setup

Needs three free accounts. None require a credit card to start.

| Variable | Where to get it |
|---|---|
| `SCRAPECREATORS_API_KEY` | [scrapecreators.com](https://scrapecreators.com) — 100 free credits, no card |
| `RESEND_API_KEY` | [resend.com](https://resend.com) — free tier |
| `RESEND_FROM_EMAIL` | use `onboarding@resend.dev` (Resend's shared test sender) to skip domain verification |
| `REPORT_TO_EMAIL` | your inbox |
| `SLACK_BOT_TOKEN` | [api.slack.com/apps](https://api.slack.com/apps) → create an app → OAuth & Permissions → add the `chat:write` and `channels:manage` Bot Token Scopes → Install to Workspace |

(Slack's older "Incoming Webhooks" are a deprecated legacy integration — this uses a proper Slack app + bot token instead. `channels:manage` is what lets each new brand's channel be created automatically; a channel the bot creates is one it's already a member of, so no manual invite is needed.)

Copy `.env.example` to `.env` and fill these in for local testing (never commit `.env` — it's gitignored). Run any script directly to test it in isolation, e.g.:

```bash
set -a && source .env && set +a
python3 scripts/fetch_posts.py waze
```

## Running on a schedule

[`.github/workflows/daily-watch.yml`](.github/workflows/daily-watch.yml) runs the whole thing once a day on GitHub's own infrastructure. Each run checks out the repo, hands [`ROUTINE.md`](ROUTINE.md) to Claude Code (authenticated with a Claude subscription token, so no separate API billing), and commits any new findings back.

The variables in the table above live as **repository secrets** — Settings → Secrets and variables → Actions — never in the repo. Add one more alongside them:

| Secret | Where to get it |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | run `claude setup-token` locally |

The workflow also has a manual trigger, so you can run it on demand from the Actions tab instead of waiting for the next scheduled run.
