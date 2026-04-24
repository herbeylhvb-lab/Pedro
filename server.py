import json
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
