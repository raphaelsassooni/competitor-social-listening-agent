# Daily run instructions

You are running inside the scheduled GitHub Actions workflow in `.github/workflows/daily-watch.yml`. Do the following, once, then stop.

All API keys are already set as environment variables — read them from the environment, never hardcode or print them.

## 1. Load the brands
Read `data/accounts.json`. It groups accounts by brand:
```json
{"brands": [{"brand": "Moovit", "slack_channel": "moovit-watch", "accounts": [{"handle": "waze", "label": "Waze", "active": true}]}]}
```
Work through one brand at a time. Within each brand, do steps 2–5 for every account with `"active": true`.

## 2. Fetch recent posts
Run `python3 scripts/fetch_posts.py <handle>`. This calls the ScrapeCreators API and prints the account's recent posts as JSON. If it fails for one account (private account, rate limit, API error), note the failure and move on — don't let one account's failure stop the whole run.

## 3. Find what's new
Pipe the fetched posts into `python3 scripts/diff_new_posts.py <handle>`. This prints only the posts not already logged in `data/seen_posts.json`. An empty list means no new activity for that account — skip to the next one.

## 4. Analyze each new post
This is the one step that isn't a script — it's your judgment call. Each post from `fetch_posts.py` already includes `caption`, `media_type`, `like_count`, `comment_count`, and `tagged_accounts` (usernames tagged in the post — a strong signal for who's involved). For every new post, produce:
- **What the activity was** — one plain-language sentence.
- **Narrative/theme** — the underlying angle or story the post is telling.
- **Topics** — a short list of subjects covered.
- **Who was involved** — people, partners, brands named in the caption or in `tagged_accounts`, if any (fine to leave empty).
- **Category** — a short label for the post type (e.g. product update, brand/marketing, community, hiring, partnership, press/news, other).

## 5. Persist what you found
For each new post, build a record combining the fetched fields with your analysis:
```json
{"id": "...", "url": "...", "posted_at": "...", "caption_excerpt": "...", "media_type": "...", "like_count": 0, "comment_count": 0, "category": "...", "narrative": "...", "topics": ["..."], "people_partners": ["..."]}
```
`caption_excerpt` is your own short excerpt of the caption (first sentence or ~150 characters), not the full text — keeps the dashboard scannable. Pipe the list of new records for an account into `python3 scripts/append_posts.py <handle>` to merge them into `data/seen_posts.json`.

## 6. Rebuild the dashboard
Once all brands are done, run `python3 scripts/render_dashboard.py`. This regenerates `DASHBOARD.md` from the updated log — don't hand-edit that file.

## 7. Write today's summary
Write `data/today_summary.json` with one entry per brand, covering every active account within it:
```json
{"brands": [{"brand": "Moovit", "run_date": "2026-07-29", "has_activity": true,
  "accounts": [{"label": "Waze", "new_post_count": 1, "headline": "...", "bullets": ["Narrative: ...", "Topics: ...", "People/partners: ...", "Type: ..."]}]}]}
```
Set `has_activity` to false for a brand where no account had new posts. Keep it short: one headline plus a few bullets per account with new activity.

## 8. Commit
Commit `data/seen_posts.json` and `DASHBOARD.md` with a message like `Daily check: <date>`. Do not commit `.env` or `data/today_summary.json` (both gitignored).

## 9. Send
Run `python3 scripts/send_email.py` and `python3 scripts/send_slack.py`. Both read `data/today_summary.json` and handle the per-brand splitting themselves:
- Email sends one message per brand **that has new activity**, skipping quiet brands entirely.
- Slack posts one message per brand to that brand's own channel, **every day** — a one-line "nothing new" note when quiet.

## Notes
- API keys come from GitHub Actions secrets / environment variables — never hardcode or commit them.
- If every account fails to fetch (bad API key, service outage), don't stay silent and don't send a broken summary — send a short failure notice instead, so a missing day is noticed rather than assumed quiet.
