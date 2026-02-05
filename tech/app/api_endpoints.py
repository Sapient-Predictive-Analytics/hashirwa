from __future__ import annotations

import json
import os
import time
import requests
import subprocess
from threading import Lock
from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

# ---------------------------------------------------------------------
# Persistent feed (Milestone 2)
# Shape:
# {
#   "cert_by_issuer": { "1": {"ok":1,"std":"JGAP","sub":"..."} },
#   "price_by_issuer": { "1": {"ok":1,"sku":"...","jpykg":4200.00} }
# }
# ---------------------------------------------------------------------

_CACHE_LOCK = Lock()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(PROJECT_ROOT, "data", "oracle_cache.json")
DATASET_URL_DEFAULT = "https://raw.githubusercontent.com/Sapient-Predictive-Analytics/hashirwa/tech/m2/data/hashirwa_oracle.json"

def _ensure_cache_file():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    if not os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"cert_by_issuer": {}, "price_by_issuer": {}}, f, ensure_ascii=False, indent=2)


def _load_cache():
    _ensure_cache_file()
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_cache(cache: dict):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------------------

@api.get("/api/v1/health")
def api_health():
    return jsonify({"ok": True})


# ---------------------------------------------------------------------
# Listing-based endpoints used by listings.html refresh buttons
# These read from the persistent cache (set via admin endpoints below).
# ---------------------------------------------------------------------

@api.get("/api/v1/demo/cert")
def demo_cert_for_listing():
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400

    ts = int(time.time() * 1000)

    with _CACHE_LOCK:
        cache = _load_cache()
        rec = cache.get("cert_by_issuer", {}).get(issuer_id)

    if not rec:
        return jsonify({"ok": 0, "issuer_id": int(issuer_id), "ts": ts})

    return jsonify({
        "ok": int(rec.get("ok", 0)),
        "std": rec.get("std", "JGAP"),
        "sub": rec.get("sub", ""),
        "issuer_id": int(issuer_id),
        "ts": ts
    })


@api.get("/api/v1/demo/price")
def demo_price_for_listing():
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400

    ts = int(time.time() * 1000)

    with _CACHE_LOCK:
        cache = _load_cache()
        rec = cache.get("price_by_issuer", {}).get(issuer_id)

    if not rec:
        return jsonify({"ok": 0, "issuer_id": int(issuer_id), "ts": ts})

    return jsonify({
        "ok": int(rec.get("ok", 0)),
        "sku": rec.get("sku", ""),
        "jpykg": float(rec.get("jpykg", 0.0)),
        "issuer_id": int(issuer_id),
        "ts": ts
    })

@api.get("/api/v1/cl/cert")
def cl_cert():
    # Chainlink Functions-friendly: returns tiny pipe-separated string
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return ("0|ERR|bad_issuer", 400)

    # refresh cert from GitHub into cache (reuse your existing endpoint logic internally if you prefer)
    # simplest: call the same underlying function you already use; otherwise, just load from cache after refresh_one
    # Here: read from cache only (assumes you've recently refreshed via refresh_cert_one)
    with _CACHE_LOCK:
        cache = _load_cache()
        rec = cache.get("cert_by_issuer", {}).get(issuer_id)

    if not rec:
        return (f"0|CERT|{issuer_id}|NA", 200)

    ok = int(rec.get("ok", 0))
    std = str(rec.get("std", "JGAP"))
    return (
      f"{ok}|CERT|{issuer_id}|{std}",
        200,
      {"Content-Type": "text/plain; charset=utf-8"}
    )


@api.get("/api/v1/cl/price")
def cl_price():
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "bad_issuer_id"}), 400

    # Always fetch GitHub raw for Chainlink verification
    url = request.args.get("url", "").strip() or DATASET_URL_DEFAULT

    # Cache-bust so we don't get stale CDN responses
    cb = int(time.time() * 1000)
    fetch_url = f"{url}?cb={cb}"

    try:
        r = requests.get(
            fetch_url,
            timeout=10,
            headers={"Cache-Control": "no-cache", "Accept": "application/json"},
        )
        r.raise_for_status()
        dataset = r.json()
    except Exception as e:
        return jsonify({"ok": 0, "err": f"fetch_failed: {e}"}), 200

    rec = (dataset.get("price_by_issuer") or {}).get(str(int(issuer_id)))
    if not rec:
        return jsonify({"ok": 0, "kind": "PRICE", "issuer_id": int(issuer_id)}), 200

    # Normalize output fields
    try:
        jpykg = float(rec.get("jpykg", 0.0))
    except Exception:
        jpykg = 0.0

    return jsonify({
        "ok": int(rec.get("ok", 1)),
        "kind": "PRICE",
        "issuer_id": int(issuer_id),
        "sku": str(rec.get("sku", "")),
        "jpykg": round(jpykg, 2)
    }), 200

# ---------------------------------------------------------------------
# Admin endpoints (manual write = Milestone 2)
# Use curl or later add a small admin form page.
# ---------------------------------------------------------------------

@api.post("/api/v1/admin/set_cert")
def admin_set_cert():
    data = request.get_json(force=True, silent=True) or {}
    issuer_id = str(data.get("issuer_id", "")).strip()
    ok = data.get("ok", None)
    std = str(data.get("std", "JGAP")).strip()
    sub = str(data.get("sub", "")).strip()

    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400
    if ok not in (0, 1, True, False):
        return jsonify({"ok": 0, "err": "invalid_ok"}), 400

    rec = {"ok": int(bool(ok)), "std": std, "sub": sub}

    with _CACHE_LOCK:
        cache = _load_cache()
        cache.setdefault("cert_by_issuer", {})[issuer_id] = rec
        _save_cache(cache)

    return jsonify({"ok": 1, "issuer_id": int(issuer_id), "record": rec})


@api.post("/api/v1/admin/set_price")
def admin_set_price():
    data = request.get_json(force=True, silent=True) or {}
    issuer_id = str(data.get("issuer_id", "")).strip()
    sku = str(data.get("sku", "")).strip()
    jpykg = data.get("jpykg", None)

    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400

    try:
        jpykg_f = float(jpykg)
    except Exception:
        return jsonify({"ok": 0, "err": "invalid_jpykg"}), 400

    rec = {"ok": 1, "sku": sku, "jpykg": round(jpykg_f, 2)}

    with _CACHE_LOCK:
        cache = _load_cache()
        cache.setdefault("price_by_issuer", {})[issuer_id] = rec
        _save_cache(cache)

    return jsonify({"ok": 1, "issuer_id": int(issuer_id), "record": rec})

@api.post("/api/v1/admin/refresh_from_dataset")
def admin_refresh_from_dataset():
    data = request.get_json(force=True, silent=True) or {}
    url = str(data.get("url", "")).strip()
    if not url.startswith("http"):
        return jsonify({"ok": 0, "err": "missing_or_invalid_url"}), 400

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        return jsonify({"ok": 0, "err": f"fetch_failed: {e}"}), 500

    # Validate minimal shape
    certs = payload.get("cert_by_issuer", {})
    prices = payload.get("price_by_issuer", {})
    if not isinstance(certs, dict) or not isinstance(prices, dict):
        return jsonify({"ok": 0, "err": "invalid_payload_shape"}), 400

    with _CACHE_LOCK:
        cache = _load_cache()
        cache["cert_by_issuer"] = certs
        cache["price_by_issuer"] = prices
        _save_cache(cache)

    return jsonify({"ok": 1, "cert_count": len(certs), "price_count": len(prices)})

def _fetch_dataset(url: str):
    # cache-bust so GitHub raw updates show immediately
    bust = int(time.time() * 1000)
    full_url = f"{url}?cb={bust}"
    r = requests.get(full_url, timeout=10, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()
    return r.json()

@api.post("/api/v1/admin/refresh_cert_one")
def admin_refresh_cert_one():
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400

    url = (request.args.get("url", "") or "").strip() or DATASET_URL_DEFAULT

    try:
        dataset = _fetch_dataset(url)
        rec = (dataset.get("cert_by_issuer") or {}).get(str(int(issuer_id)))
    except Exception as e:
        return jsonify({"ok": 0, "err": f"fetch_failed: {e}"}), 500

    if not rec:
        return jsonify({"ok": 0, "err": "no_cert_record_in_dataset"}), 404

    with _CACHE_LOCK:
        cache = _load_cache()
        cache.setdefault("cert_by_issuer", {})[issuer_id] = rec
        _save_cache(cache)

    return jsonify({"ok": 1, "issuer_id": int(issuer_id), "record": rec})

@api.post("/api/v1/admin/refresh_price_one")
def admin_refresh_price_one():
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400

    url = (request.args.get("url", "") or "").strip() or DATASET_URL_DEFAULT

    try:
        dataset = _fetch_dataset(url)
        rec = (dataset.get("price_by_issuer") or {}).get(str(int(issuer_id)))
    except Exception as e:
        return jsonify({"ok": 0, "err": f"fetch_failed: {e}"}), 500

    if not rec:
        return jsonify({"ok": 0, "err": "no_price_record_in_dataset"}), 404

    with _CACHE_LOCK:
        cache = _load_cache()
        cache.setdefault("price_by_issuer", {})[issuer_id] = rec
        _save_cache(cache)

    return jsonify({"ok": 1, "issuer_id": int(issuer_id), "record": rec})

@api.post("/api/v1/admin/trigger_chainlink_price")
def trigger_chainlink_price():
    # Called by listings.html refresh button.
    issuer_id = request.args.get("issuer_id", "").strip()
    if not issuer_id.isdigit():
        return jsonify({"ok": 0, "err": "invalid_issuer_id"}), 400

    # Call your working Python sender (chainlink-functions-jp)
    # Adjust the path if your folder is elsewhere.
    cmd = [
        "bash", "-lc",
        f"cd ~/chainlink-functions-jp && source .venv/bin/activate && python3 functions_request.py -- price {issuer_id}"
    ]

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return jsonify({"ok": 0, "err": "chainlink_timeout"}), 504

    if p.returncode != 0:
        return jsonify({"ok": 0, "err": "sender_failed", "stderr": p.stderr[-1000:]}), 500

    # functions_request.py prints JSON to stdout
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return jsonify({"ok": 0, "err": "bad_sender_output", "stdout": p.stdout[-1000:]}), 500

    return jsonify(out), 200