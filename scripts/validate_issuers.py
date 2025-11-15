#!/usr/bin/env python3
"""
HashiRWA CSV validator — aligned to June's current issuers.csv
- Allows multiple photo_proof_url (semicolon-separated)
- Requires proof only when status in {submitted, verified}
- Ignores ?raw=true when checking filenames
- Safer CSV parsing (skipinitialspace) to avoid ", " issues
"""

import argparse, csv, os, re, sys
from urllib.parse import urlparse

# --- Columns (exact names) ---
ID_COL = "issuer_id"
COMPANY_COL = "company_name"
PRODUCT_COL = "product_name"
PROOF_COL = "photo_proof_url"
STATUS_COL = "status"
VISIBILITY_COL = "visibility"
DATE_COL = "collected_date"
WEBSITE_COL = "website"
BOOTH_COL = "booth"

REQUIRED_COLS = [ID_COL, COMPANY_COL, BOOTH_COL, STATUS_COL, VISIBILITY_COL]  # proof handled conditionally

STATUS_ENUM = {"draft", "submitted", "verified"}
VISIBILITY_ENUM = {"public", "private"}

URL_PREFIX_DEFAULT = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$", re.I)

def err(msg, row=None): print(f"[row {row}] {msg}" if row else msg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT)
    ap.add_argument("--skip-file-check", action="store_true")
    ap.add_argument("--allow-empty-proof", action="store_true",
                    help="Allow empty photo_proof_url even when status=submitted/verified")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        err(f"CSV not found: {args.csv_path}"); sys.exit(2)

    problems = 0
    seen_ids = set()
    seen_pairs = set()

    # safer parsing: treat ", <space>" as empty
    with open(args.csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        headers = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLS + [PROOF_COL, DATE_COL, WEBSITE_COL] if c not in headers]
        if missing:
            err(f"CSV missing required columns: {', '.join(missing)}"); sys.exit(2)

        for rownum, row in enumerate(reader, start=2):
            # Required (except proof which is conditional)
            for c in REQUIRED_COLS:
                if (row.get(c) or "").strip() == "":
                    problems += 1; err(f"required field '{c}' is empty", rownum)

            # Unique id
            rid = (row.get(ID_COL) or "").strip()
            if rid:
                if rid in seen_ids: problems += 1; err("duplicate issuer_id", rownum)
                seen_ids.add(rid)

            # Optional uniqueness on (company, product)
            pair = ((row.get(COMPANY_COL) or "").strip().lower(),
                    (row.get(PRODUCT_COL) or "").strip().lower())
            if all(pair):
                if pair in seen_pairs: problems += 1; err("duplicate (company_name, product_name)", rownum)
                seen_pairs.add(pair)

            # Status/visibility
            status = (row.get(STATUS_COL) or "").strip().lower()
            if status not in STATUS_ENUM:
                problems += 1; err(f"invalid status '{status}' (expected one of {sorted(STATUS_ENUM)})", rownum)
            vis = (row.get(VISIBILITY_COL) or "").strip().lower()
            if vis not in VISIBILITY_ENUM:
                problems += 1; err(f"invalid visibility '{vis}' (expected one of {sorted(VISIBILITY_ENUM)})", rownum)

            # Proof URLs (semicolon-separated)
            proof_raw = (row.get(PROOF_COL) or "").strip()
            need_proof = (status in {"submitted", "verified"}) and not args.allow_empty-proof
            if need_proof and proof_raw == "":
                problems += 1; err(f"{PROOF_COL} is required for status '{status}'", rownum)
            else:
                for u in [p.strip() for p in proof_raw.split(";") if p.strip()]:
                    if not u.startswith(args.url_prefix):
                        problems += 1; err(f"{PROOF_COL} must start with url-prefix", rownum)
                    filename = u.split("/")[-1].split("?")[0]
                    if not FILENAME_RE.match(filename):
                        problems += 1; err(f"bad proof filename: {filename}", rownum)
                    if not args.skip_file_check:
                        if not os.path.exists(os.path.join(args.proof_dir, filename)):
                            problems += 1; err(f"missing local proof file: {os.path.join(args.proof_dir, filename)}", rownum)

            # Collected date
            cdate = (row.get(DATE_COL) or "").strip()
            if cdate and not DATE_RE.match(cdate):
                problems += 1; err(f"bad collected_date (YYYY-MM-DD): {cdate}", rownum)

            # Website
            w = (row.get(WEBSITE_COL) or "").strip()
            if w:
                sch = urlparse(w).scheme
                if sch not in {"http", "https"}:
                    problems += 1; err("website must start with http(s)://", rownum)

    if problems:
        print(f"\nValidation FAILED: {problems} problem(s) found across file.")
        sys.exit(1)
    else:
        print("OK — all rows validated with 0 problems 🎉")
        sys.exit(0)

if __name__ == "__main__":
    main()
