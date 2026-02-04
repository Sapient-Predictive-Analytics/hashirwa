from __future__ import annotations
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"ok": True})

# Demo registry: you control this JSON. Swap it later with real verification/pricing logic.
DEMO_CERTS = {
    # key: subject identifier
    # For demo: set ok=True so you can show a positive path.
    "Haranoseichahonpo": {"std": "JGAP", "ok": True},
    # You can also support Japanese name keys if you want:
    "原野製茶本舗": {"std": "JGAP", "ok": True},
}

DEMO_PRICES = {
    # key: SKU/category
    "green_tea_okuyame": {"jpy_per_kg": 4200, "ok": True},
    "sweet_potato_beni_haruka": {"jpy_per_kg": 380, "ok": True},
}

@app.get("/v1/cert")
def cert():
    """
    GET /v1/cert?subject=...
    Returns compact JSON under 256 bytes.
    """
    subject = request.args.get("subject", "").strip()
    if not subject:
        return jsonify({"ok": 0, "err": "missing_subject"}), 400

    rec = DEMO_CERTS.get(subject)
    ts = int(time.time() * 1000)

    if not rec:
        # Negative but still well-formed
        return jsonify({"ok": 0, "std": "JGAP", "sub": subject, "ts": ts})

    return jsonify({"ok": 1 if rec["ok"] else 0, "std": rec["std"], "sub": subject, "ts": ts})

@app.get("/v1/price")
def price():
    """
    GET /v1/price?sku=...
    Returns compact JSON under 256 bytes.
    """
    sku = request.args.get("sku", "").strip()
    if not sku:
        return jsonify({"ok": 0, "err": "missing_sku"}), 400

    rec = DEMO_PRICES.get(sku)
    ts = int(time.time() * 1000)

    if not rec:
        return jsonify({"ok": 0, "sku": sku, "ts": ts})

    return jsonify({"ok": 1, "sku": sku, "jpykg": rec["jpy_per_kg"], "ts": ts})
