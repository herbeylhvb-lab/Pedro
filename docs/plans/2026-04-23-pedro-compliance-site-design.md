# Pedro Cardenas Campaign Site — Compliance-First Design

**Date:** 2026-04-23
**Author:** Luis Villarreal (with Claude Code)
**Status:** Approved, ready for implementation

---

## Purpose

Build a public-facing website for **Pedro Cardenas, Brownsville City Commissioner, District 4** whose primary job is to pass **10DLC / RumbleUp / TCPA campaign review** for SMS outreach approval.

The site is a **compliance artifact first, marketing site second**. Reviewers must be able to:

1. Visit the URL and see a legitimate-looking candidate/officeholder site.
2. Navigate to the SMS signup page and see correct opt-in disclosure language.
3. Find a privacy policy that contains the carrier-required phrase about not sharing mobile data.
4. Find SMS terms with message frequency, rate disclosure, and STOP/HELP keywords.
5. See a political advertising disclosure on every page.

No integration with RumbleUp, no CRM, no real analytics. Form submissions log locally to prove the form *works* — data retention is not the goal.

## Officeholder (public record)

- **Name:** Pedro E. Cardenas
- **Office:** Brownsville City Commissioner, District 4 (incumbent)
- **First elected:** June 2021
- **Reelected:** June 2025 (1,240 votes vs. Daisy Zamora 1,087)
- **Term ends:** May 2029
- **Education:** BBA, Tecnológico de Monterrey (2003)
- **Known priorities:** Infrastructure, public safety, economic development, small business support, utility affordability, transparency
- **Signature project:** $14M Old Highway 77 reconstruction

## Architecture

Single Flask app serving Jinja templates. No database, no auth, no JS framework.

```
Request flow:
  GET /                  → render templates/index.html
  GET /about             → render templates/about.html
  GET /issues            → render templates/issues.html
  GET /join              → render templates/join.html (compliance-critical)
  POST /join             → validate, log to signups.log, redirect /thank-you
  GET /thank-you         → render templates/thank_you.html
  GET /privacy           → render templates/privacy.html
  GET /sms-terms         → render templates/sms_terms.html
  GET /terms             → render templates/terms.html
```

Served by gunicorn in a Docker container on Railway.

## File Layout

```
Pedro/
├── server.py
├── requirements.txt
├── Dockerfile
├── railway.toml
├── .gitignore
├── README.md
├── docs/plans/2026-04-23-pedro-compliance-site-design.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── issues.html
│   ├── join.html
│   ├── thank_you.html
│   ├── privacy.html
│   ├── sms_terms.html
│   └── terms.html
└── static/
    ├── style.css
    └── placeholder-photo.svg
```

## Compliance Requirements (the actual point of this project)

### Opt-in page (`/join`)

Form fields: `first_name`, `last_name`, `phone`, `email`, `zip`.

Consent checkbox is **unchecked by default**. The disclosure text sits *directly next to* the checkbox (not behind a modal or tooltip). Exact wording:

> By checking this box, I consent to receive recurring automated text messages from Pedro Cardenas for City Commissioner at the phone number provided. Consent is not a condition of any purchase. Msg&data rates may apply. Msg frequency varies. Reply HELP for help, STOP to cancel. [SMS Terms] and [Privacy Policy].

`[SMS Terms]` links to `/sms-terms`, `[Privacy Policy]` links to `/privacy`. Both open in new tab.

### Privacy policy (`/privacy`)

Must contain verbatim (carriers grep for this):

> We do not share your mobile information with third parties or affiliates for marketing or promotional purposes.

Other required sections: what data we collect, why we collect it, how long we retain it, contact email for privacy inquiries.

### SMS terms (`/sms-terms`)

Required elements:

- Program name: "Pedro Cardenas for City Commissioner"
- Message frequency: "Up to 10 messages per month"
- Cost: "Msg&data rates may apply"
- HELP response: "Reply HELP for assistance or contact [CAMPAIGN EMAIL]"
- STOP response: "Reply STOP to unsubscribe at any time"
- Supported carriers disclaimer
- Data sharing disclaimer (redundant with privacy but required on its own page)

### Political advertising disclosure

Footer on **every page**:

> Political advertising paid for by [CAMPAIGN COMMITTEE NAME], [TREASURER NAME], Treasurer.

Texas Ethics Commission requires this on all paid political communications, including websites.

### Consent logging

Each POST to `/join` writes a JSON line to `signups.log`:

```json
{
  "timestamp": "2026-04-23T19:12:00Z",
  "ip": "203.0.113.42",
  "user_agent": "...",
  "first_name": "...",
  "last_name": "...",
  "phone": "...",
  "email": "...",
  "zip": "...",
  "consent_text": "By checking this box, I consent...[full verbatim disclosure]",
  "consent_version": "v1"
}
```

Logging the **full verbatim consent text** (not just `consent: true`) is what survives a TCPA audit. If the disclosure wording is updated later, bump `consent_version`.

## Visual Design

- **Primary:** Navy `#0a2540`
- **Accent:** Red `#c8102e`
- **Highlight:** Gold `#d4a017`
- **Text:** `#1a1a1a` on white, `#f5f5f5` on navy
- Single `static/style.css`, mobile-first media queries
- System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` (no Google Fonts — privacy-friendly, faster, no external dependency)
- Photo: inline SVG placeholder (silhouette + "Photo coming soon") — replace with real image later

## Deploy

- **Platform:** Railway
- **Entrypoint:** `gunicorn server:app --bind 0.0.0.0:$PORT --workers 2`
- **Dockerfile:** `python:3.12-slim` base, copy app, install requirements, expose `$PORT`
- **railway.toml:** Specifies builder + start command
- **Env vars (none required for MVP):** no secrets; `signups.log` lives on container FS (ephemeral by design — this site is not the system of record)

## Placeholders to Fill Before Launch

Every occurrence of the following in the codebase must be replaced with real values before going live:

| Placeholder | Where used | Notes |
|---|---|---|
| `[CAMPAIGN COMMITTEE NAME]` | Footer on every page, privacy, SMS terms | Texas Ethics Commission registered name |
| `[TREASURER NAME]` | Footer on every page | Texas requires treasurer name on political ads |
| `[CAMPAIGN EMAIL]` | Privacy, SMS terms (HELP contact), contact references | Separate from personal/City Hall email |
| `[CAMPAIGN MAILING ADDRESS]` | Privacy, SMS terms, terms of use | Campaign committee's own address — NOT City Hall |
| `[CAMPAIGN PHONE]` | Optional — HELP fallback number | Can be omitted if email-only HELP is acceptable |

The README will include a checklist for this replacement pass.

## Out of Scope (intentional — YAGNI)

- Admin dashboard for viewing signups (grep the log file)
- CAPTCHA / bot prevention (the site isn't a high-value target; carriers don't test this)
- Email notifications on signup
- Database (ephemeral log is sufficient for compliance demo)
- Multilingual support (English only for v1; Brownsville is 95% Spanish-speaking so Spanish is a future win, but not required for carrier review)
- Analytics / tracking pixels (would complicate the privacy policy)
- Newsletter archive, news section, press page

## Testing Strategy

No automated tests for v1 — this is an 8-page static-ish site with one form handler. Manual smoke test before each deploy:

1. All 8 routes render without 500s.
2. Form POST with valid data → redirects to thank-you, log line appended.
3. Form POST without consent checkbox → form re-renders with error, no log line.
4. Privacy policy contains the exact carrier-required sentence (grep).
5. SMS terms contains "Msg&data rates may apply" verbatim.
6. Every page footer shows the political disclosure.

## Success Criteria

1. Site deploys cleanly to Railway at a public URL.
2. RumbleUp (or equivalent 10DLC reviewer) approves the SMS campaign on first submission.
3. All placeholder tokens are replaced before public launch.
