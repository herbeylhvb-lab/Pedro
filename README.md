# Pedro Cardenas for City Commissioner — Campaign Site

Flask-based compliance-first campaign website for **Pedro Cardenas, Brownsville City Commissioner, District 4**. Designed to pass 10DLC / RumbleUp / TCPA carrier review for SMS outreach approval.

## Stack

- Python 3.12 + Flask 3
- gunicorn in a Docker container
- Deployed to Railway

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
# → http://localhost:5000
```

## Deploy to Railway

1. `railway link` to an existing project (or `railway init`).
2. `railway up` — Railway detects the Dockerfile and builds.
3. Set a custom domain in the Railway dashboard once you have one.

## BEFORE YOU GO LIVE — placeholder checklist

The following tokens are scattered through `templates/` and must be replaced with real values before the site faces the public:

| Token | Meaning | How to fill |
|---|---|---|
| `[CAMPAIGN COMMITTEE NAME]` | Official registered name of the campaign committee | From Texas Ethics Commission filing |
| `[TREASURER NAME]` | Campaign treasurer's name | From TEC filing |
| `[CAMPAIGN EMAIL]` | Dedicated email for HELP replies + privacy inquiries | Set up a campaign mailbox (not personal, not City Hall) |
| `[CAMPAIGN MAILING ADDRESS]` | Campaign committee address | Committee's own P.O. box or business address |

Find them:

```bash
grep -rn "\[CAMPAIGN COMMITTEE NAME\]" templates/
grep -rn "\[TREASURER NAME\]" templates/
grep -rn "\[CAMPAIGN EMAIL\]" templates/
grep -rn "\[CAMPAIGN MAILING ADDRESS\]" templates/
```

Replace in one pass (macOS):

```bash
sed -i '' 's/\[CAMPAIGN COMMITTEE NAME\]/Pedro Cardenas for City Commissioner/g' templates/*.html
sed -i '' 's/\[TREASURER NAME\]/Jane Doe/g' templates/*.html
sed -i '' 's/\[CAMPAIGN EMAIL\]/info@pedrocardenas.com/g' templates/*.html
sed -i '' 's/\[CAMPAIGN MAILING ADDRESS\]/P.O. Box 1234, Brownsville, TX 78520/g' templates/*.html
```

Also swap `static/placeholder-photo.svg` reference in `templates/about.html` for a real JPEG/PNG headshot.

## Submitting for carrier / RumbleUp review

1. Deploy to Railway, get the `*.up.railway.app` URL (or your custom domain).
2. Provide that URL to RumbleUp / your SMS platform as the opt-in source.
3. Reviewer will check `/join`, `/privacy`, and `/sms-terms`. Make sure all three render and contain the required disclosures (they do, by design).

## Signup log

Form submissions append one JSON line each to `signups.log` in the container. On Railway's ephemeral filesystem this file resets on every redeploy — **do not rely on it as a system of record**. For real data retention, mount a Railway volume or swap the log write for a database.

## Compliance references

- **10DLC / TCPA** — US carriers require explicit opt-in disclosure with "Msg&data rates may apply," message frequency, STOP/HELP keywords, and a privacy policy that explicitly states mobile info is not shared with third parties for marketing.
- **Texas Ethics Commission** — political advertising must include "Political advertising paid for by [committee], [treasurer], Treasurer" on all paid communications including websites.

## Design & implementation docs

- `docs/plans/2026-04-23-pedro-compliance-site-design.md` — approved design
- `docs/plans/2026-04-23-pedro-compliance-site-implementation.md` — task-by-task build plan
