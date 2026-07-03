# hello-world
just another repo.
Now is the time for all young men to come to the aid of thier country. Now!

## Daily News Digest

A GitHub Actions workflow (`.github/workflows/daily-news-digest.yml`) runs
`news_digest/digest.py` every morning. It pulls World, National (U.S.),
Michigan, and Flint/Swartz Creek headlines from RSS feeds, drops routine
Trump coverage (keeping only historically major Trump stories, e.g.
assassination attempts or war), and emails the result via Gmail SMTP.

### One-time setup

1. **Create a Gmail App Password** (requires 2-Step Verification enabled on
   the sending Gmail account): go to
   https://myaccount.google.com/apppasswords, create one named e.g.
   `news-digest`, and copy the 16-character password.
2. In this repo, go to **Settings → Secrets and variables → Actions** and add:
   - `GMAIL_ADDRESS` — the Gmail address sending the digest
   - `GMAIL_APP_PASSWORD` — the App Password from step 1
   - `DIGEST_TO_EMAIL` — the address that should receive the digest
3. The workflow runs daily at 11:00 UTC (7 AM Eastern during daylight time).
   You can also trigger it manually from the **Actions** tab via
   "Run workflow" to test it.

### Adjusting sources or filtering

Feed URLs, the recency window, and the Trump-relevance keyword lists all
live in `news_digest/config.py`. Some local/state feed URLs are best-effort
guesses (news sites change these without notice) — if a section shows up
empty in the digest, check the Actions run log for a `[warn]` line naming
the broken feed and swap in a working URL.
