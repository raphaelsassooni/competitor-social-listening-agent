# Competitor Social Listening Agent

An AI agent that checks a configurable list of competitor Instagram accounts once a day and, when there's new activity, sends a short summary — what happened, the narrative/theme, topics covered, people/partners involved, and a post-type category — by email and Slack.

Built as a portfolio piece for Deeep Social. Runs unattended as a [Claude Code Routine](https://claude.com/blog/introducing-routines-in-claude-code) on a daily schedule — no server or laptop required.

## How it works

1. [`data/accounts.json`](data/accounts.json) lists which Instagram handles to track (currently: Moovit's competitors — Waze, Google Maps, Transit). Add or remove a competitor by editing this file, not the code.
2. Each day, the routine fetches recent posts for every active account via the [ScrapeCreators](https://scrapecreators.com) API.
3. Posts not already logged in `data/seen_posts.json` get analyzed by the agent itself — narrative, topics, people/partners, category. That reasoning step is the actual "AI" in this project; everything else is plain deterministic code.
4. The log (`data/seen_posts.json`) and dashboard ([`DASHBOARD.md`](DASHBOARD.md)) are updated and committed.
5. A short, scannable summary is emailed (via [Resend](https://resend.com)) and posted to Slack.

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
| `SLACK_WEBHOOK_URL` | Slack → Apps → Incoming Webhooks |

Copy `.env.example` to `.env` and fill these in for local testing (never commit `.env` — it's gitignored). Run any script directly to test it in isolation, e.g.:

```bash
export $(cat .env | xargs)
python3 scripts/fetch_posts.py waze
```

## Running on a schedule

This repo is meant to be connected to a Claude Code Routine set to run once a day, with the variables above configured as routine secrets (not committed to the repo). See [`ROUTINE.md`](ROUTINE.md) for what the routine does on every run.
