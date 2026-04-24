# Pedro Cardenas Compliance Site — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Flask-based, 10DLC/TCPA-compliant campaign website for Pedro Cardenas (Brownsville City Commissioner District 4), deployable to Railway, suitable for carrier/RumbleUp SMS campaign review approval.

**Architecture:** Single Flask app (`server.py`) rendering Jinja templates from `templates/`. One POST form handler for opt-in signup that writes a JSON log line to `signups.log`. Served by gunicorn in a Docker container on Railway. No database, no JS framework, no auth.

**Tech Stack:** Python 3.12, Flask, gunicorn, Jinja2, vanilla CSS, Docker, Railway.

**Design reference:** `docs/plans/2026-04-23-pedro-compliance-site-design.md` — contains verbatim disclosure wording that MUST be reproduced exactly in templates.

**Testing note:** No automated tests. Manual smoke test after deploy (see Task 10).

---

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `server.py`
- Create: `Dockerfile`
- Create: `railway.toml`

**Step 1: Create `requirements.txt`**

```
flask==3.0.3
gunicorn==22.0.0
```

**Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.env
.venv/
venv/
signups.log
.DS_Store
.railway/
```

**Step 3: Create `server.py` skeleton (routes will be filled in later tasks)**

```python
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

SIGNUPS_LOG = Path("signups.log")

CONSENT_TEXT_V1 = (
    "By checking this box, I consent to receive recurring automated text "
    "messages from Pedro Cardenas for City Commissioner at the phone number "
    "provided. Consent is not a condition of any purchase. Msg&data rates "
    "may apply. Msg frequency varies. Reply HELP for help, STOP to cancel. "
    "SMS Terms and Privacy Policy."
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/issues")
def issues():
    return render_template("issues.html")


@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        return handle_signup()
    return render_template("join.html")


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/sms-terms")
def sms_terms():
    return render_template("sms_terms.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


def handle_signup():
    form = request.form
    if not form.get("consent"):
        return render_template("join.html", error="You must agree to the SMS consent to sign up."), 400

    required = ["first_name", "last_name", "phone", "email", "zip"]
    if not all(form.get(f, "").strip() for f in required):
        return render_template("join.html", error="Please complete all fields."), 400

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent", ""),
        "first_name": form["first_name"].strip(),
        "last_name": form["last_name"].strip(),
        "phone": form["phone"].strip(),
        "email": form["email"].strip(),
        "zip": form["zip"].strip(),
        "consent_text": CONSENT_TEXT_V1,
        "consent_version": "v1",
    }
    with SIGNUPS_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return redirect(url_for("thank_you"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

**Step 4: Create `Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD gunicorn server:app --bind 0.0.0.0:$PORT --workers 2 --access-logfile -
```

**Step 5: Create `railway.toml`**

```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "gunicorn server:app --bind 0.0.0.0:$PORT --workers 2 --access-logfile -"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**Step 6: Commit**

```bash
git add requirements.txt .gitignore server.py Dockerfile railway.toml
git commit -m "Scaffold Flask app with routes and Docker/Railway config"
```

---

### Task 2: Base template + global CSS

**Files:**
- Create: `templates/base.html`
- Create: `static/style.css`
- Create: `static/placeholder-photo.svg`

**Step 1: Create `templates/base.html`**

Nav across all pages, footer with political disclosure on every page. Uses `{% block content %}` for page bodies.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Pedro Cardenas for Brownsville City Commissioner, District 4{% endblock %}</title>
  <meta name="description" content="Official site of Pedro Cardenas, Brownsville City Commissioner for District 4.">
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="{{ url_for('home') }}" class="brand">
        <span class="brand-name">Pedro Cardenas</span>
        <span class="brand-office">Brownsville City Commissioner &middot; District 4</span>
      </a>
      <nav class="site-nav" aria-label="Primary">
        <a href="{{ url_for('home') }}">Home</a>
        <a href="{{ url_for('about') }}">About</a>
        <a href="{{ url_for('issues') }}">Issues</a>
        <a href="{{ url_for('join') }}" class="nav-cta">Join</a>
      </nav>
    </div>
  </header>

  <main>
    {% block content %}{% endblock %}
  </main>

  <footer class="site-footer">
    <div class="container">
      <p class="political-disclosure">
        Political advertising paid for by [CAMPAIGN COMMITTEE NAME], [TREASURER NAME], Treasurer.
      </p>
      <nav class="footer-nav" aria-label="Legal">
        <a href="{{ url_for('privacy') }}">Privacy Policy</a>
        <a href="{{ url_for('sms_terms') }}">SMS Terms</a>
        <a href="{{ url_for('terms') }}">Terms of Use</a>
      </nav>
      <p class="copyright">&copy; 2026 Pedro Cardenas for City Commissioner. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>
```

**Step 2: Create `static/style.css`**

Navy (`#0a2540`) primary, red (`#c8102e`) accent, gold (`#d4a017`) highlight. Mobile-first.

```css
:root {
  --navy: #0a2540;
  --navy-light: #15345a;
  --red: #c8102e;
  --gold: #d4a017;
  --text: #1a1a1a;
  --muted: #555;
  --bg: #fff;
  --bg-alt: #f5f5f5;
  --border: #e0e0e0;
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text);
  background: var(--bg);
  line-height: 1.6;
}

.container { max-width: 1100px; margin: 0 auto; padding: 0 1.25rem; }

a { color: var(--red); }
a:hover { color: var(--navy); }

.site-header {
  background: var(--navy);
  color: #fff;
  border-bottom: 4px solid var(--gold);
}
.header-inner {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}
@media (min-width: 720px) {
  .header-inner { flex-direction: row; align-items: center; justify-content: space-between; }
}
.brand { color: #fff; text-decoration: none; display: flex; flex-direction: column; }
.brand-name { font-weight: 700; font-size: 1.25rem; letter-spacing: 0.02em; }
.brand-office { font-size: 0.8rem; color: var(--gold); text-transform: uppercase; letter-spacing: 0.08em; }

.site-nav { display: flex; gap: 1.25rem; flex-wrap: wrap; }
.site-nav a { color: #fff; text-decoration: none; font-weight: 500; }
.site-nav a:hover { color: var(--gold); }
.nav-cta {
  background: var(--red);
  padding: 0.4rem 0.9rem;
  border-radius: 4px;
}
.nav-cta:hover { background: #a00d24; color: #fff; }

main { min-height: 60vh; }

.hero {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
  color: #fff;
  padding: 4rem 0;
}
.hero h1 { font-size: 2.25rem; margin: 0 0 0.5rem; }
.hero .tagline { font-size: 1.2rem; color: var(--gold); margin: 0 0 1.5rem; }
.hero .intro { max-width: 620px; font-size: 1.05rem; color: #e8eef5; }
.btn-cta {
  display: inline-block;
  background: var(--red);
  color: #fff;
  text-decoration: none;
  padding: 0.8rem 1.6rem;
  border-radius: 4px;
  font-weight: 600;
  margin-top: 1.5rem;
}
.btn-cta:hover { background: #a00d24; color: #fff; }

.section { padding: 3rem 0; }
.section-alt { background: var(--bg-alt); }
.section h2 { font-size: 1.75rem; color: var(--navy); margin-top: 0; }

.priority-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  margin-top: 2rem;
}
@media (min-width: 720px) {
  .priority-grid { grid-template-columns: repeat(3, 1fr); }
}
.priority-card {
  background: #fff;
  border-top: 4px solid var(--gold);
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(10, 37, 64, 0.08);
}
.priority-card h3 { color: var(--navy); margin-top: 0; }

.about-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: start;
}
@media (min-width: 720px) {
  .about-grid { grid-template-columns: 300px 1fr; }
}
.photo-wrap { background: var(--bg-alt); border: 1px solid var(--border); padding: 1rem; text-align: center; }
.photo-wrap img, .photo-wrap svg { max-width: 100%; height: auto; }
.photo-wrap .caption { color: var(--muted); font-size: 0.85rem; margin-top: 0.5rem; }

.issue-list { list-style: none; padding: 0; margin: 0; }
.issue-list li {
  background: #fff;
  border-left: 4px solid var(--red);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 4px rgba(10, 37, 64, 0.06);
}
.issue-list h3 { margin-top: 0; color: var(--navy); }

form.signup { max-width: 640px; }
form.signup label { display: block; font-weight: 600; margin-top: 1rem; margin-bottom: 0.35rem; color: var(--navy); }
form.signup input[type="text"],
form.signup input[type="tel"],
form.signup input[type="email"] {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}
form.signup input:focus { outline: 2px solid var(--gold); outline-offset: 1px; }

.consent-box {
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-left: 4px solid var(--gold);
  padding: 1rem 1.25rem;
  margin: 1.5rem 0;
}
.consent-box label { display: flex; gap: 0.75rem; align-items: flex-start; font-weight: 400; margin: 0; color: var(--text); }
.consent-box input[type="checkbox"] { margin-top: 0.35rem; flex-shrink: 0; transform: scale(1.2); }
.consent-box .disclosure-text { font-size: 0.92rem; line-height: 1.5; }

.form-error {
  background: #fdecea;
  color: #7a1820;
  border-left: 4px solid var(--red);
  padding: 0.8rem 1rem;
  margin-bottom: 1rem;
}

button.submit {
  background: var(--red);
  color: #fff;
  border: none;
  padding: 0.85rem 1.75rem;
  font-size: 1.05rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}
button.submit:hover { background: #a00d24; }

.legal-doc { max-width: 760px; }
.legal-doc h1 { color: var(--navy); margin-bottom: 0.25rem; }
.legal-doc .effective { color: var(--muted); font-size: 0.9rem; margin-bottom: 2rem; }
.legal-doc h2 { color: var(--navy); margin-top: 2rem; font-size: 1.25rem; }
.legal-doc p, .legal-doc ul { color: var(--text); }

.site-footer {
  background: var(--navy);
  color: #e8eef5;
  padding: 2rem 0 1.25rem;
  margin-top: 3rem;
}
.site-footer .container { display: flex; flex-direction: column; gap: 0.75rem; }
.political-disclosure { margin: 0; font-size: 0.9rem; color: var(--gold); }
.footer-nav { display: flex; gap: 1.25rem; flex-wrap: wrap; }
.footer-nav a { color: #fff; text-decoration: none; font-size: 0.9rem; }
.footer-nav a:hover { color: var(--gold); }
.copyright { margin: 0; color: #9bb0c7; font-size: 0.85rem; }
```

**Step 3: Create `static/placeholder-photo.svg`**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
  <rect width="300" height="300" fill="#0a2540"/>
  <circle cx="150" cy="115" r="50" fill="#d4a017"/>
  <path d="M60 260 Q150 170 240 260 L240 300 L60 300 Z" fill="#d4a017"/>
  <text x="150" y="225" text-anchor="middle" fill="#fff" font-family="sans-serif" font-size="14" font-weight="600">PEDRO CARDENAS</text>
  <text x="150" y="245" text-anchor="middle" fill="#e8eef5" font-family="sans-serif" font-size="10">Photo coming soon</text>
</svg>
```

**Step 4: Commit**

```bash
git add templates/base.html static/style.css static/placeholder-photo.svg
git commit -m "Add base template, global stylesheet, and photo placeholder"
```

---

### Task 3: Home page

**Files:**
- Create: `templates/index.html`

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}Pedro Cardenas &middot; Brownsville City Commissioner, District 4{% endblock %}

{% block content %}
<section class="hero">
  <div class="container">
    <h1>Pedro Cardenas</h1>
    <p class="tagline">Brownsville City Commissioner &middot; District 4</p>
    <p class="intro">
      Working for the residents of District 4 with a focus on infrastructure,
      public safety, and economic opportunity. Stay connected to what is
      happening in our community.
    </p>
    <a href="{{ url_for('join') }}" class="btn-cta">Stay in touch</a>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2>Priorities</h2>
    <p>Focused on the work that matters most to District 4 residents.</p>

    <div class="priority-grid">
      <div class="priority-card">
        <h3>Infrastructure</h3>
        <p>Continuing investment in streets, drainage, and long-overdue projects like the Old Highway 77 reconstruction.</p>
      </div>
      <div class="priority-card">
        <h3>Public Safety</h3>
        <p>Supporting first responders and building safer neighborhoods that families can be proud to call home.</p>
      </div>
      <div class="priority-card">
        <h3>Economic Opportunity</h3>
        <p>Backing small businesses and making sure Brownsville residents share in the city&rsquo;s growth.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <h2>Get Involved</h2>
    <p>Sign up for text updates on the work happening in District 4.</p>
    <a href="{{ url_for('join') }}" class="btn-cta">Join the list</a>
  </div>
</section>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/index.html
git commit -m "Add home page with hero and priority cards"
```

---

### Task 4: About page

**Files:**
- Create: `templates/about.html`

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}About &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container">
    <h2>About Pedro Cardenas</h2>

    <div class="about-grid">
      <div class="photo-wrap">
        <img src="{{ url_for('static', filename='placeholder-photo.svg') }}" alt="Pedro Cardenas">
        <p class="caption">Official photo</p>
      </div>

      <div>
        <p>
          Pedro E. Cardenas serves the residents of District 4 on the Brownsville City Commission.
          First elected in June 2021 and re-elected in June 2025, he brings a background in business
          administration and account management to his work on the Commission.
        </p>

        <p>
          Pedro holds a Bachelor of Business Administration from Tecnol&oacute;gico de Monterrey (2003).
          Before entering public service, he built a career in business and account management,
          experience that shapes his focus on fiscal responsibility and practical results at City Hall.
        </p>

        <p>
          As Commissioner, Pedro has championed infrastructure investment, including the $14 million
          reconstruction of Old Highway 77, and has worked to strengthen public safety, support local
          small businesses, and keep essential services affordable and reliable for District 4 families.
        </p>

        <p>
          His current term runs through May 2029.
        </p>

        <h3>At a glance</h3>
        <ul>
          <li><strong>Office:</strong> Brownsville City Commissioner, District 4</li>
          <li><strong>First elected:</strong> June 2021</li>
          <li><strong>Reelected:</strong> June 2025</li>
          <li><strong>Education:</strong> BBA, Tecnol&oacute;gico de Monterrey (2003)</li>
          <li><strong>Term ends:</strong> May 2029</li>
        </ul>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/about.html
git commit -m "Add about page with bio and background"
```

---

### Task 5: Issues page

**Files:**
- Create: `templates/issues.html`

**Step 1: Create the template**

Five issue cards based on his real public priorities.

```html
{% extends "base.html" %}
{% block title %}Issues &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container">
    <h2>Where Pedro Stands</h2>
    <p>The priorities driving the work at City Hall for District 4.</p>

    <ul class="issue-list">
      <li>
        <h3>Infrastructure That Lasts</h3>
        <p>
          Streets, drainage, and utilities that hold up to South Texas weather and growing demand.
          The Old Highway 77 reconstruction is one example of the long-term investment District 4
          deserves. Pedro continues to push for projects that fix the roads people use every day.
        </p>
      </li>
      <li>
        <h3>Public Safety</h3>
        <p>
          Safer neighborhoods start with well-resourced first responders and active community
          partnerships. Pedro supports giving police, fire, and EMS the tools they need while
          building trust between city services and the residents they serve.
        </p>
      </li>
      <li>
        <h3>Small Business &amp; Economic Opportunity</h3>
        <p>
          Brownsville grows when small businesses grow. Pedro advocates for policies that help local
          entrepreneurs succeed, from streamlined permitting to targeted support programs for
          neighborhood commercial corridors.
        </p>
      </li>
      <li>
        <h3>Affordable, Reliable Services</h3>
        <p>
          Water, power, and trash service that residents can count on without breaking the family
          budget. Pedro focuses on holding rates in check and making sure essential services are
          delivered consistently across every District 4 neighborhood.
        </p>
      </li>
      <li>
        <h3>Transparent, Responsive Government</h3>
        <p>
          Residents deserve to know how decisions are made and to have real access to their
          Commissioner. Pedro prioritizes open communication, community meetings, and timely
          responses to District 4 concerns.
        </p>
      </li>
    </ul>
  </div>
</section>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/issues.html
git commit -m "Add issues page with 5 policy priorities"
```

---

### Task 6: Join page (compliance-critical)

**Files:**
- Create: `templates/join.html`

This is the page carrier reviewers will scrutinize most. Disclosure wording must be verbatim per the design doc. Consent checkbox is unchecked by default, disclosure is visibly next to it.

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}Join the List &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container">
    <h2>Join the List</h2>
    <p>
      Get occasional text updates from Pedro Cardenas about District 4 priorities,
      community events, and important City Commission decisions.
    </p>

    {% if error %}
      <div class="form-error" role="alert">{{ error }}</div>
    {% endif %}

    <form class="signup" method="POST" action="{{ url_for('join') }}" novalidate>
      <label for="first_name">First name</label>
      <input type="text" id="first_name" name="first_name" required autocomplete="given-name">

      <label for="last_name">Last name</label>
      <input type="text" id="last_name" name="last_name" required autocomplete="family-name">

      <label for="phone">Mobile phone</label>
      <input type="tel" id="phone" name="phone" required autocomplete="tel" placeholder="(956) 555-0123">

      <label for="email">Email</label>
      <input type="email" id="email" name="email" required autocomplete="email">

      <label for="zip">ZIP code</label>
      <input type="text" id="zip" name="zip" required autocomplete="postal-code" pattern="[0-9]{5}" maxlength="5">

      <div class="consent-box">
        <label for="consent">
          <input type="checkbox" id="consent" name="consent" value="yes">
          <span class="disclosure-text">
            By checking this box, I consent to receive recurring automated text messages from
            Pedro Cardenas for City Commissioner at the phone number provided.
            Consent is not a condition of any purchase. Msg&amp;data rates may apply.
            Msg frequency varies. Reply HELP for help, STOP to cancel.
            <a href="{{ url_for('sms_terms') }}" target="_blank" rel="noopener">SMS Terms</a>
            and
            <a href="{{ url_for('privacy') }}" target="_blank" rel="noopener">Privacy Policy</a>.
          </span>
        </label>
      </div>

      <button type="submit" class="submit">Sign me up</button>
    </form>
  </div>
</section>
{% endblock %}
```

**Step 2: Manually verify consent checkbox defaults to unchecked**

Render locally (or trust the HTML — `<input type="checkbox">` without `checked` is unchecked by default). Do NOT add `checked`.

**Step 3: Commit**

```bash
git add templates/join.html
git commit -m "Add join page with TCPA-compliant opt-in form and disclosure"
```

---

### Task 7: Thank-you page

**Files:**
- Create: `templates/thank_you.html`

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}Thank You &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container">
    <h2>Thank you for signing up</h2>
    <p>
      You&rsquo;re on the list. Pedro will keep you posted on what&rsquo;s happening in District 4
      and at City Hall. You can reply <strong>STOP</strong> to any text message to unsubscribe at
      any time, or reply <strong>HELP</strong> for support.
    </p>
    <p>
      <a href="{{ url_for('home') }}" class="btn-cta">Back to home</a>
    </p>
  </div>
</section>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/thank_you.html
git commit -m "Add thank-you confirmation page"
```

---

### Task 8: Privacy policy (compliance-critical)

**Files:**
- Create: `templates/privacy.html`

Must contain the verbatim sentence: "We do not share your mobile information with third parties or affiliates for marketing or promotional purposes."

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}Privacy Policy &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container legal-doc">
    <h1>Privacy Policy</h1>
    <p class="effective">Effective date: April 23, 2026</p>

    <p>
      This Privacy Policy explains how the Pedro Cardenas for City Commissioner campaign (&ldquo;we,&rdquo;
      &ldquo;us,&rdquo; or &ldquo;our&rdquo;) collects, uses, and protects information when you visit this website or sign
      up to receive communications from us.
    </p>

    <h2>Information We Collect</h2>
    <p>When you sign up through our website, we collect:</p>
    <ul>
      <li>First and last name</li>
      <li>Mobile phone number</li>
      <li>Email address</li>
      <li>ZIP code</li>
      <li>Timestamp of signup, IP address, and browser information for recordkeeping</li>
      <li>The exact consent disclosure shown to you at the time of signup</li>
    </ul>

    <h2>How We Use Your Information</h2>
    <p>
      We use the information you provide to send you campaign updates, community information, and
      other communications related to the work of Pedro Cardenas as Brownsville City Commissioner.
      We may contact you by text message, email, or phone using the contact information you provide.
    </p>

    <h2>Your Mobile Information</h2>
    <p>
      <strong>We do not share your mobile information with third parties or affiliates for marketing
      or promotional purposes.</strong> Information collected during SMS opt-in, including your mobile
      number and consent records, is kept confidential and used only to deliver the text message
      program you signed up for.
    </p>
    <p>
      Information may be shared with service providers we use to deliver text messages (for example,
      our SMS platform provider), strictly for the purpose of sending the messages you consented to
      receive, and subject to their own privacy commitments.
    </p>

    <h2>SMS Communications</h2>
    <p>
      Text message enrollment is opt-in and entirely voluntary. You may opt out at any time by
      replying <strong>STOP</strong> to any message. For help, reply <strong>HELP</strong> or
      contact us at [CAMPAIGN EMAIL]. See our
      <a href="{{ url_for('sms_terms') }}">SMS Terms</a> for full program details.
    </p>

    <h2>Data Retention</h2>
    <p>
      We retain signup records, including consent records, for a minimum of four (4) years after
      you unsubscribe, as required by federal telecommunications regulations. After that period,
      records may be deleted or anonymized.
    </p>

    <h2>Your Rights</h2>
    <p>
      You may request access to the information we have about you, ask that it be corrected, or
      request deletion of your information (subject to our legal recordkeeping obligations) by
      contacting us at [CAMPAIGN EMAIL].
    </p>

    <h2>Children&rsquo;s Privacy</h2>
    <p>
      This website is not directed to children under 13, and we do not knowingly collect information
      from children under 13.
    </p>

    <h2>Changes to This Policy</h2>
    <p>
      We may update this Privacy Policy from time to time. The &ldquo;Effective date&rdquo; above will be
      updated when changes are made. Continued use of the website after changes constitutes
      acceptance of the updated policy.
    </p>

    <h2>Contact</h2>
    <p>
      Questions about this policy can be directed to:<br>
      Pedro Cardenas for City Commissioner<br>
      [CAMPAIGN MAILING ADDRESS]<br>
      Email: [CAMPAIGN EMAIL]
    </p>
  </div>
</section>
{% endblock %}
```

**Step 2: Verify carrier-required phrase is verbatim**

Run:
```bash
grep -c "We do not share your mobile information with third parties or affiliates for marketing or promotional purposes" templates/privacy.html
```
Expected output: `1`

**Step 3: Commit**

```bash
git add templates/privacy.html
git commit -m "Add privacy policy with carrier-required mobile data sharing disclosure"
```

---

### Task 9: SMS terms (compliance-critical)

**Files:**
- Create: `templates/sms_terms.html`

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}SMS Terms &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container legal-doc">
    <h1>SMS Terms &amp; Conditions</h1>
    <p class="effective">Effective date: April 23, 2026</p>

    <h2>Program Name</h2>
    <p>Pedro Cardenas for City Commissioner (the &ldquo;Program&rdquo;).</p>

    <h2>Program Description</h2>
    <p>
      The Program sends recurring automated text messages to subscribers with updates from Pedro
      Cardenas, Brownsville City Commissioner for District 4, including community news, City
      Commission updates, and event information.
    </p>

    <h2>How to Opt In</h2>
    <p>
      You may opt in to receive text messages from the Program by completing the signup form on
      this website and affirmatively checking the consent box. By opting in, you consent to receive
      recurring automated text messages at the mobile number you provided. Consent is not a
      condition of any purchase.
    </p>

    <h2>Message Frequency</h2>
    <p>Up to 10 messages per month. Message frequency varies.</p>

    <h2>Message and Data Rates</h2>
    <p>Msg&amp;data rates may apply. Check with your mobile carrier for details about your plan.</p>

    <h2>How to Opt Out</h2>
    <p>
      You may cancel at any time by replying <strong>STOP</strong> to any text message from the
      Program. After you send <strong>STOP</strong>, we will send you a confirmation message, and
      you will not receive additional messages unless you opt back in.
    </p>

    <h2>How to Get Help</h2>
    <p>
      For help, reply <strong>HELP</strong> to any text message, email
      [CAMPAIGN EMAIL], or write to:<br>
      Pedro Cardenas for City Commissioner<br>
      [CAMPAIGN MAILING ADDRESS]
    </p>

    <h2>Supported Carriers</h2>
    <p>
      The Program is available on most major U.S. mobile carriers. Carriers are not liable for
      delayed or undelivered messages.
    </p>

    <h2>Privacy</h2>
    <p>
      We do not share your mobile information with third parties or affiliates for marketing or
      promotional purposes. Mobile information is handled according to our
      <a href="{{ url_for('privacy') }}">Privacy Policy</a>.
    </p>

    <h2>Changes to Terms</h2>
    <p>
      We may update these SMS Terms from time to time. The &ldquo;Effective date&rdquo; above will
      reflect any changes. Continued participation in the Program after changes constitutes
      acceptance of the updated terms.
    </p>

    <h2>Contact</h2>
    <p>
      Pedro Cardenas for City Commissioner<br>
      [CAMPAIGN MAILING ADDRESS]<br>
      Email: [CAMPAIGN EMAIL]
    </p>
  </div>
</section>
{% endblock %}
```

**Step 2: Verify required phrases are verbatim**

Run:
```bash
grep -c "Msg&amp;data rates may apply" templates/sms_terms.html
grep -c "Up to 10 messages per month" templates/sms_terms.html
grep -c "We do not share your mobile information" templates/sms_terms.html
```
Each should output `1`.

**Step 3: Commit**

```bash
git add templates/sms_terms.html
git commit -m "Add SMS terms with carrier-required disclosures"
```

---

### Task 10: Terms of use

**Files:**
- Create: `templates/terms.html`

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% block title %}Terms of Use &middot; Pedro Cardenas{% endblock %}

{% block content %}
<section class="section">
  <div class="container legal-doc">
    <h1>Terms of Use</h1>
    <p class="effective">Effective date: April 23, 2026</p>

    <p>
      Welcome to the official website of Pedro Cardenas for City Commissioner. By accessing or
      using this website, you agree to these Terms of Use.
    </p>

    <h2>Acceptable Use</h2>
    <p>
      You agree to use this website only for lawful purposes. You will not attempt to gain
      unauthorized access to any part of the website, interfere with its operation, or submit
      false or misleading information.
    </p>

    <h2>Content</h2>
    <p>
      All content on this website, including text, graphics, and design elements, is provided for
      informational purposes about Pedro Cardenas&rsquo;s work as Brownsville City Commissioner for
      District 4. You may not reproduce or redistribute content for commercial purposes without
      written permission.
    </p>

    <h2>Signup Form</h2>
    <p>
      When you sign up through this website, the information you provide is handled according to
      our <a href="{{ url_for('privacy') }}">Privacy Policy</a> and, for text messaging, our
      <a href="{{ url_for('sms_terms') }}">SMS Terms</a>.
    </p>

    <h2>Disclaimer</h2>
    <p>
      This website is provided &ldquo;as is&rdquo; without warranties of any kind. We make reasonable efforts
      to keep information accurate, but do not guarantee that all content is current or error-free.
    </p>

    <h2>Limitation of Liability</h2>
    <p>
      To the maximum extent permitted by law, Pedro Cardenas for City Commissioner and its
      representatives are not liable for any indirect, incidental, or consequential damages
      arising from your use of this website.
    </p>

    <h2>Governing Law</h2>
    <p>
      These Terms of Use are governed by the laws of the State of Texas.
    </p>

    <h2>Changes</h2>
    <p>
      We may update these Terms from time to time. Continued use of the website after changes
      constitutes acceptance of the updated Terms.
    </p>

    <h2>Contact</h2>
    <p>
      Pedro Cardenas for City Commissioner<br>
      [CAMPAIGN MAILING ADDRESS]<br>
      Email: [CAMPAIGN EMAIL]
    </p>
  </div>
</section>
{% endblock %}
```

**Step 2: Commit**

```bash
git add templates/terms.html
git commit -m "Add terms of use page"
```

---

### Task 11: README with placeholder checklist

**Files:**
- Create: `README.md`

**Step 1: Create the README**

```markdown
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

Find and replace:

```bash
grep -rn "\[CAMPAIGN COMMITTEE NAME\]" templates/
grep -rn "\[TREASURER NAME\]" templates/
grep -rn "\[CAMPAIGN EMAIL\]" templates/
grep -rn "\[CAMPAIGN MAILING ADDRESS\]" templates/
```

You can use `sed -i '' 's/\[CAMPAIGN EMAIL\]/info@pedrocardenas.com/g' templates/*.html` (macOS) or the GNU equivalent on Linux to do batch replacement.

Also swap:

- `static/placeholder-photo.svg` reference in `templates/about.html` for a real JPEG/PNG headshot.

## Submitting for carrier / RumbleUp review

1. Deploy to Railway, get the `*.up.railway.app` URL (or your custom domain).
2. Provide that URL to RumbleUp / your SMS platform as the opt-in source.
3. Reviewer will check `/join`, `/privacy`, and `/sms-terms`. Make sure all three render and contain the required disclosures (they do, by design).

## Signup log

Form submissions append one JSON line each to `signups.log` in the container. On Railway's ephemeral filesystem this file resets on every redeploy — **do not rely on it as a system of record**. For real data retention, mount a Railway volume or swap the log write for a database.

## Compliance references

- **10DLC / TCPA** — US carriers require explicit opt-in disclosure with "Msg&data rates may apply," message frequency, STOP/HELP keywords, and a privacy policy that explicitly states mobile info is not shared with third parties for marketing.
- **Texas Ethics Commission** — political advertising must include "Political advertising paid for by [committee], [treasurer], Treasurer" on all paid communications including websites.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "Add README with deploy instructions and placeholder checklist"
```

---

### Task 12: Smoke test and initial push

**Step 1: Install deps and run locally**

```bash
cd ~/Pedro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py &
SERVER_PID=$!
sleep 2
```

**Step 2: Hit each route and confirm 200**

```bash
for path in / /about /issues /join /privacy /sms-terms /terms; do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000$path)
  echo "$path → $code"
done
```

Expected: all routes return `200`.

**Step 3: Confirm carrier-required phrases**

```bash
curl -s http://localhost:5000/privacy | grep -c "We do not share your mobile information"
curl -s http://localhost:5000/sms-terms | grep -c "Msg&amp;data rates may apply"
curl -s http://localhost:5000/sms-terms | grep -c "Up to 10 messages per month"
```

Expected: each returns `1`.

**Step 4: Submit form and confirm redirect + log**

```bash
curl -s -o /dev/null -w "%{http_code} → %{redirect_url}\n" \
  -X POST http://localhost:5000/join \
  -d "first_name=Test&last_name=User&phone=9565550123&email=test@example.com&zip=78520&consent=yes"
```

Expected: `302 → http://localhost:5000/thank-you`.

Then verify log line:
```bash
tail -1 signups.log | python3 -m json.tool
```

Expected: a JSON object containing `consent_text` with the full disclosure wording.

**Step 5: Submit without consent and confirm rejection**

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST http://localhost:5000/join \
  -d "first_name=Test&last_name=User&phone=9565550123&email=test@example.com&zip=78520"
```

Expected: `400`.

**Step 6: Stop local server**

```bash
kill $SERVER_PID
```

**Step 7: Push to origin**

```bash
git push -u origin main
```

**Step 8: Deploy to Railway (manual — user does this)**

Handoff to user with Railway deploy instructions from the README.

---

## Commit cadence summary

One commit per task = 12 commits, each small and reviewable. No squashing — preserves the audit trail, which matters for a compliance project.

## What's NOT in this plan

- Custom domain configuration (done in Railway dashboard, not in code)
- Actual placeholder replacement (done by user before launch)
- Real photo of Pedro (user provides; swap the SVG)
- RumbleUp / SMS platform setup itself (separate from the website)
