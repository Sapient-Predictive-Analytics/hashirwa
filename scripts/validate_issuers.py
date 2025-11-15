#!/usr/bin/env python3
"""
HashiRWA CSV validator (CSV schema aligned to issuers.csv)

Usage (Windows PowerShell):
  python scripts/validate_issuers.py data/issuers.csv `
    --proof-dir proof `
    --url-prefix https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/ `
    --skip-file-check

Notes:
- Allows multiple URLs in photo_proof_url separated by ';'
- Accepts '?raw=true' query on filenames
- Booth is optional
- Auto-heals common column shift: if photo_proof_url is empty but collected_date has a URL,
  it will treat that value as photo_proof_url (warn only)
"""
import argparse, csv, os, re, sys
from urllib.parse import urlparse

# Columns exactly as in your header
ID_COL = "issuer_id"
COMPANY_COL = "company_name"
BRAND_COL = "brand_or_product_line"
PRODUCT_COL = "product_name"
BOOTH_COL = "booth"
STATUS_COL = "status"
PROOF_COL = "photo_proof_url"
DATE_COL = "collected_date"
VIS_COL = "visibility"
WEBSITE_COL = "website"

REQUIRED_COLS = [
    ID_COL,
    COMPANY_COL,
    STATUS_COL,
    PROOF_COL,     # required when status in submitted/verified (see rule below)
    VIS_COL,
    # BOOTH optional
]

STATUS_ENUM = {"draft", "submitted", "verified"}
VISIBILITY_ENUM = {"public", "private"}

URL_PREFIX_DEFAULT = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"
FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def error(msg, rownum=None):
    print(f"[row {rownum}] {msg}" if rownum else msg)

def _split_urls(value: str):
    # allow multiple URLs separated by ';'
    return [u.strip() for u in value.split(";") if u.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT)
    ap.add_argument("--skip-file-check", action="store_true")
    ap.add_argument("--allow-missing-proof", action="store_true",
                    help="do not enforce proof for submitted/verified")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        error(f"CSV not found: {args.csv_path}"); sys.exit(2)

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLS if c not in headers]
        if missing:
            error(f"CSV missing required columns: {', '.join(missing)}"); sys.exit(2)

        problems = 0
        seen_ids, seen_pairs = set(), set()
        row_count = 0

        for i, row in enumerate(reader, start=2):
            row_count += 1

            # ---- gentle auto-heal: URL accidentally in collected_date
            if not (row.get(PROOF_COL) or "").strip():
                maybe_url = (row.get(DATE_COL) or "").strip()
                if maybe_url.startswith("http://") or maybe_url.startswith("https://"):
                    # move value into photo_proof_url for validation purpose
                    row[PROOF_COL] = maybe_url
                    row[DATE_COL] = ""
                    print(f"[row {i}] note: moved URL from {DATE_COL} to {PROOF_COL} (auto-heal)")

            # ---- required presence (except booth)
            for c in [ID_COL, COMPANY_COL, STATUS_COL, VIS_COL]:
                if (row.get(c) or "").strip() == "":
                    problems += 1; error(f"required field '{c}' is empty", i)

            # ---- unique ids & (company, product)
            rid = (row.get(ID_COL) or "").strip()
            if rid:
                if rid in seen_ids: problems += 1; error("duplicate issuer_id", i)
                seen_ids.add(rid)

            pair = ((row.get(COMPANY_COL) or "").strip().lower(),
                    (row.get(PRODUCT_COL) or "").strip().lower())
            if all(pair):
                if pair in seen_pairs: problems += 1; error("duplicate (company_name, product_name)", i)
                seen_pairs.add(pair)

            # ---- enums
            status = (row.get(STATUS_COL) or "").strip().lower()
            if status and status not in STATUS_ENUM:
                problems += 1; error(f"invalid status '{status}' (expected one of {sorted(STATUS_ENUM)})", i)

            vis = (row.get(VIS_COL) or "").strip().lower()
            if vis and vis not in VISIBILITY_ENUM:
                problems += 1; error(f"invalid visibility '{vis}' (expected one of {sorted(VISIBILITY_ENUM)})", i)

            # ---- website scheme if present
            w = (row.get(WEBSITE_COL) or "").strip()
            if w:
                parsed = urlparse(w)
                if parsed.scheme not in {"http", "https"}:
                    problems += 1; error("website must start with http(s)://", i)

            # ---- collected_date format if present
            cdate = (row.get(DATE_COL) or "").strip()
            if cdate and not DATE_RE.match(cdate):
                problems += 1; error(f"bad {DATE_COL} (YYYY-MM-DD): {cdate}", i)

            # ---- proof URLs
            proofs_raw = (row.get(PROOF_COL) or "").strip()
            proofs = _split_urls(proofs_raw) if proofs_raw else []

            # enforce proof only when status is submitted/verified unless flag provided
            if status in {"submitted", "verified"} and not args.allow_missing-proof:
                if not proofs:
                    problems += 1; error(f"{PROOF_COL} is required for status '{status}'", i)

            for u in proofs:
                if not u.startswith(args.url_prefix):
                    problems += 1; error(f"{PROOF_COL} URL must start with url-prefix: {u}", i)
                # check filename (strip ?raw=true)
                filename = u.split("/")[-1].split("?")[0]
                if not FILENAME_RE.match(filename):
                    problems += 1; error(f"proof filename not kebab-case or bad extension: {filename}", i)
                if not args.skip_file_check:
                    local = os.path.join(args.proof_dir, filename)
                    if not os.path.exists(local):
                        problems += 1; error(f"missing local proof file: {local}", i)

        if problems:
            error(f"\nValidation FAILED: {problems} problem(s) found across {row_count} row(s).")
            sys.exit(1)
        else:
            print(f"OK — {row_count} row(s) validated with 0 problems."); sys.exit(0)

if __name__ == "__main__":
    main()
