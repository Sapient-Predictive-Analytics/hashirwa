#!/usr/bin/env python3
"""
HashiRWA CSV validator — robust to header whitespace, multi-URL proofs, and Windows usage.
"""

import argparse
import csv
import os
import re
import sys
from urllib.parse import urlparse

# Canonical column names (lowercased & trimmed after normalization)
ID_COL         = "issuer_id"
COMPANY_COL    = "company_name"
PRODUCT_COL    = "product_name"
PROOF_COL      = "photo_proof_url"
STATUS_COL     = "status"
VISIBILITY_COL = "visibility"
DATE_COL       = "collected_date"
WEBSITE_COL    = "website"
BOOTH_COL      = "booth"  # optional by default

REQUIRED_BASE_COLS = [ID_COL, COMPANY_COL, STATUS_COL, VISIBILITY_COL]  # booth/proof handled separately

STATUS_ENUM     = {"draft", "submitted", "verified"}
VISIBILITY_ENUM = {"public", "private"}

URL_PREFIX_DEFAULT = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"

DATE_RE     = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$", re.IGNORECASE)

def error(msg, row=None):
    print(f"[row {row}] {msg}" if row else msg)

def normalize_headers(fieldnames):
    # Trim, collapse spaces, and lowercase
    return [(" ".join((h or "").split())).strip().lower() for h in (fieldnames or [])]

def normalize_row(raw_row, raw_headers, norm_headers):
    # Build a dict keyed by normalized header names with stripped cell values
    row = {}
    for raw_h, norm_h in zip(raw_headers, norm_headers):
        row[norm_h] = (raw_row.get(raw_h) or "").strip()
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof", help="Local folder holding proof images (optional)")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT, help="Required prefix for proof URLs")
    ap.add_argument("--skip-file-check", action="store_true", help="Skip checking local proof files exist")
    ap.add_argument("--allow-multiple-proof", action="store_true", help="Allow ';' separated multiple proof URLs")
    ap.add_argument("--allow-empty-proof", action="store_true", help="Allow empty proof field (even for submitted/verified)")
    ap.add_argument("--require-booth", action="store_true", help="Make booth non-empty")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        error(f"CSV not found: {args.csv_path}")
        sys.exit(2)

    problems = 0
    seen_ids = set()
    seen_pairs = set()

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_headers  = reader.fieldnames or []
        norm_headers = normalize_headers(raw_headers)

        # Quick header presence check
        missing = [c for c in REQUIRED_BASE_COLS if c not in norm_headers]
        if missing:
            error(f"CSV missing required columns: {', '.join(missing)}")
            error(f"Detected headers: {norm_headers}")
            sys.exit(2)

        # Optional checks info
        has_booth = BOOTH_COL in norm_headers
        has_website = WEBSITE_COL in norm_headers
        has_product = PRODUCT_COL in norm_headers
        has_proof = PROOF_COL in norm_headers
        has_date = DATE_COL in norm_headers

        for rownum, raw_row in enumerate(reader, start=2):
            row = normalize_row(raw_row, raw_headers, norm_headers)

            # --- Required base fields ---
            for col in REQUIRED_BASE_COLS:
                if (row.get(col, "") == ""):
                    problems += 1
                    error(f"required field '{col}' is empty", rownum)

            # --- ID uniqueness ---
            rid = row.get(ID_COL, "")
            if rid:
                if rid in seen_ids:
                    problems += 1
                    error(f"duplicate issuer_id '{rid}'", rownum)
                seen_ids.add(rid)

            # --- Company + Product uniqueness (if product present) ---
            if has_product:
                pair = (row.get(COMPANY_COL, "").lower(), row.get(PRODUCT_COL, "").lower())
                if all(pair):
                    if pair in seen_pairs:
                        problems += 1
                        error("duplicate (company_name, product_name)", rownum)
                    seen_pairs.add(pair)

            # --- Status ---
            status = row.get(STATUS_COL, "").lower()
            if status not in STATUS_ENUM:
                problems += 1
                error(f"invalid status '{status}' (expected one of {sorted(STATUS_ENUM)})", rownum)

            # --- Visibility ---
            vis = row.get(VISIBILITY_COL, "").lower()
            if vis not in VISIBILITY_ENUM:
                problems += 1
                error(f"invalid visibility '{vis}' (expected one of {sorted(VISIBILITY_ENUM)})", rownum)

            # --- Booth (optional unless --require-booth) ---
            if args.require_booth and has_booth and row.get(BOOTH_COL, "") == "":
                problems += 1
                error("required field 'booth' is empty", rownum)

            # --- Proof URLs (optional unless status submitted/verified and not --allow-empty-proof) ---
            if has_proof:
                proof_field = row.get(PROOF_COL, "")
                need_proof = (status in {"submitted", "verified"}) and not args.allow_empty_proof

                if not proof_field:
                    if need_proof:
                        problems += 1
                        error(f"{PROOF_COL} is required for status '{status}'", rownum)
                else:
                    # Accept multiple URLs only if allowed; otherwise use first
                    urls = [u.strip() for u in proof_field.split(";")] if args.allow_multiple_proof else [proof_field.strip()]
                    for u in urls:
                        if not u:
                            continue
                        if not u.startswith(args.url_prefix):
                            problems += 1
                            error(f"{PROOF_COL} must start with url-prefix", rownum)

                        # Extract filename before query params
                        filename = u.split("/")[-1].split("?")[0]
                        if not FILENAME_RE.match(filename):
                            problems += 1
                            error(f"bad proof filename: {filename}", rownum)

                        if not args.skip_file_check:
                            local_path = os.path.join(args.proof_dir, filename)
                            if not os.path.exists(local_path):
                                problems += 1
                                error(f"missing local proof file: {local_path}", rownum)

            # --- Date (optional; if present must be YYYY-MM-DD) ---
            if has_date:
                date = row.get(DATE_COL, "")
                if date and not DATE_RE.match(date):
                    problems += 1
                    error(f"bad collected_date (YYYY-MM-DD): {date}", rownum)

            # --- Website (optional; if present must be http/https) ---
            if has_website:
                website = row.get(WEBSITE_COL, "")
                if website:
                    parsed = urlparse(website)
                    if parsed.scheme not in {"http", "https"}:
                        problems += 1
                        error("website must start with http(s)://", rownum)

    if problems:
        print(f"\nValidation FAILED: {problems} problem(s) found across the file.")
        sys.exit(1)
    else:
        print("OK — all rows validated with 0 problems 🎉")
        sys.exit(0)

if __name__ == "__main__":
    main()
