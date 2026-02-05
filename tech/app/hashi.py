from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
)
import json
import os
from datetime import datetime
from api_endpoints import api

app = Flask(__name__)
app.secret_key = "hashirwa-demo-secret"  # for flash() messages
app.register_blueprint(api)

# Path to the JSON datastore
DB_PATH = "data/data.json"

# Allowed listing statuses
ALLOWED_STATUSES = {"pending", "approved", "rejected"}

# ---------- Helper functions ----------


def load_db():
    """Load issuers list from JSON file. Always returns a list."""
    if not os.path.exists(DB_PATH):
        save_db([])  # create empty list file
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    if not isinstance(data, list):
        # normalize to list
        data = []
        save_db(data)
    return data


def save_db(data):
    """Save issuers list back to JSON file."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_id(issuers):
    """Calculate next numeric ID."""
    return max((i.get("id", 0) for i in issuers), default=0) + 1


def find_issuer(issuer_id):
    """Find a single issuer dict by id."""
    issuers = load_db()
    issuer = next((i for i in issuers if i.get("id") == issuer_id), None)
    return issuers, issuer


# ---------- Routes: Public / UX ----------


@app.route("/")
def landing():
    """
    Landing page explaining the HashiRWA flow:
    Onboard -> Review -> Publish -> On-chain metadata.
    """
    issuers = load_db()
    approved_count = sum(1 for i in issuers if i.get("status") == "approved")
    pending_count = sum(1 for i in issuers if i.get("status") == "pending")
    return render_template(
        "landing.html",
        approved_count=approved_count,
        pending_count=pending_count,
    )


@app.route("/listings")
def listings():
    """
    Public marketplace view:
    Only approved issuers are shown.
    """
    issuers = [i for i in load_db() if i.get("status") == "approved"]
    return render_template("listings.html", issuers=issuers)


# ---------- Routes: Producer Onboarding ----------


@app.route("/onboard", methods=["GET", "POST"])
def onboard():
    """
    GET: show producer onboarding form.
    POST: validate + save new pending listing.
    """
    if request.method == "POST":
        issuers = load_db()
        form = request.form

        # Required fields for the demo
        required_fields = [
            "company_name",
            "product_name",
            "prefecture",
            "category",
            "certification",
            "lot_size",
            "harvest_date",
            "contact_email",
        ]
        missing = [f for f in required_fields if not form.get(f)]
        if missing:
            flash("Missing required fields: " + ", ".join(missing), "error")
            return redirect(url_for("onboard"))

        # Very light date validation
        harvest_date = form.get("harvest_date")
        valid_date = False
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                datetime.strptime(harvest_date, fmt)
                valid_date = True
                break
            except ValueError:
                continue
        if not valid_date:
            flash("Harvest date must be YYYY-MM-DD or DD/MM/YYYY.", "error")
            return redirect(url_for("onboard"))

        new_issuer = {
            "id": next_id(issuers),
            "company_name": form.get("company_name"),
            "product_name": form.get("product_name"),
            "prefecture": form.get("prefecture"),
            "category": form.get("category"),
            "certification": form.get("certification"),
            "lot_size": form.get("lot_size"),
            "harvest_date": harvest_date,
            "contact_email": form.get("contact_email"),
            "wallet_address": form.get("wallet_address") or "",
            "proof_url": form.get("proof_url") or "",
            "status": "pending",
            "notes": form.get("notes") or "",
        }

        issuers.append(new_issuer)
        save_db(issuers)
        flash("Thank you! Your listing has been submitted for review.",
              "success")
        return redirect(url_for("landing"))

    # GET → show the onboarding form
    return render_template("onboard.html")


# ---------- Routes: Admin Panel ----------


@app.route("/admin")
def admin_dashboard():
    """
    Simple admin dashboard summary.
    """
    issuers = load_db()
    total = len(issuers)
    pending = sum(1 for i in issuers if i.get("status") == "pending")
    approved = sum(1 for i in issuers if i.get("status") == "approved")
    rejected = sum(1 for i in issuers if i.get("status") == "rejected")
    return render_template(
        "admin_dashboard.html",
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
    )


@app.route("/admin/pending")
def admin_pending():
    """
    List of pending issuers to review.
    """
    issuers = [i for i in load_db() if i.get("status") == "pending"]
    return render_template("admin_pending.html", issuers=issuers)


@app.route("/admin/review/<int:issuer_id>", methods=["GET", "POST"])
def admin_review(issuer_id):
    """
    Review screen: approve or reject a single listing.
    """
    issuers, issuer = find_issuer(issuer_id)
    if issuer is None:
        return "Issuer not found", 404

    if request.method == "POST":
        action = request.form.get("action")
        if action == "approve":
            issuer["status"] = "approved"
            flash("Listing approved and published.", "success")
        elif action == "reject":
            issuer["status"] = "rejected"
            flash("Listing rejected.", "warning")
        else:
            flash("Unknown action.", "error")

        # Safety: never allow an unknown status to slip into JSON
        if issuer["status"] not in ALLOWED_STATUSES:
            issuer["status"] = "pending"
            flash("Invalid status detected, reverted to pending.", "error")

        save_db(issuers)
        return redirect(url_for("admin_pending"))

    return render_template("admin_review.html", issuer=issuer)


@app.route("/admin/published")
def admin_published():
    """
    View of approved listings from admin perspective.
    """
    issuers = [i for i in load_db() if i.get("status") == "approved"]
    return render_template("admin_published.html", issuers=issuers)


# ---------- Route: Simulated on-chain metadata ----------


@app.route("/metadata/<int:issuer_id>")
def metadata(issuer_id):
    """
    Return JSON metadata for a single approved issuer.
    This simulates CIP-style on-chain metadata lookup.
    """
    _, issuer = find_issuer(issuer_id)
    if issuer is None or issuer.get("status") != "approved":
        return jsonify({"error": "not_found_or_not_approved"}), 404

    meta = {
        "version": 1,
        "issuer_id": issuer["id"],
        "company_name": issuer["company_name"],
        "product_name": issuer["product_name"],
        "prefecture": issuer["prefecture"],
        "category": issuer["category"],
        "certification": issuer["certification"],
        "lot_size": issuer["lot_size"],
        "harvest_date": issuer["harvest_date"],
        "proof_url": issuer["proof_url"],
        "notes": issuer["notes"],
        "hashirwa_demo": True,
    }
    return jsonify(meta)


# ---------- Main entrypoint ----------

if __name__ == "__main__":
    # Replit expects host 0.0.0.0 and usually port 8080
    app.run(host="0.0.0.0", port=8080, debug=True)
