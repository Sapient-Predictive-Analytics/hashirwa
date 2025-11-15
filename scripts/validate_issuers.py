#!/usr/bin/env python3
"""
HashiRWA CSV validator (issuer_id schema)

Usage (Windows PowerShell):
  python scripts/validate_issuers.py data/issuers.csv --skip-file-check ^
    --url-prefix https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/

Optional relaxers:
  --allow-missing-proof   (do not require photo_proof_url even if status=submitted/verified)
  --allow-empty-booth     (do not require booth)
"""
import argparse, csv, os, re, sys
from urllib.parse import urlparse

# --- columns in your CSV ---
ID_COL        = "issuer_id"
COMPANY_COL   = "company_name"
PRODUCT_COL   = "product_name"
PROOF_COL     = "photo_proof_url"
BOOTH_COL     = "booth"
STATUS_COL    = "status"
VIS_COL       = "visibility"
DATE_COL      = "collected_date"
WEBSITE_COL   = "website"

REQUIRED_COLS = [ID_COL, COMPANY_COL, STATUS_COL, VIS_COL]  # booth/proof can be required via flags
STATUS_ENUM   = {"draft", "submitted", "verified"}
VIS_ENUM      = {"public", "private"}

URL_PREFIX_DEFAULT = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"
DATE_RE      = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_RE  = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$")

def error(msg, rownum=None):
    print(f"[row {rownum}] {msg}" if rownum else msg)

def split_urls(field: str):
    # allow semicolon-separated list; trim spaces; drop empties
    parts = [u.strip() for u in (field or "").split(";")]
    return [p for p in parts if p]

def validate_proof_urls(urls, url_prefix, skip_file_check, proof_dir):
    problems = []
    for u in urls:
        if not u.startswith(url_prefix):
            problems.append(f"{PROOF_COL} must start with url-prefix: {u}")
            continue
        # strip query (?raw=true)
        filename = u.split("/")[-1].split("?")[0]
        if not FILENAME_RE.match(filename):
            problems.append(f"proof filename not kebab-case or bad extension: {filename}")
        if not skip_file_check:
            if not os.path.exists(os.path.join(proof_dir, filename)):
                problems.append(f"missing local proof file: {os.path.join(proof_dir, filename)}")
    return problems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT)
    ap.add_argument("--skip-file-check", action="store_true")
    ap.add_argument("--allow-missing-proof", action="store_true")
    ap.add_argument("--allow-empty-booth", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        error(f"CSV not found: {args.csv_path}")
        sys.exit(2)

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [c for c in ([ID_COL, COMPANY_COL, PRODUCT_COL, PROOF_COL, BOOTH_COL,
                                WEBSITE_COL, DATE_COL, STATUS_COL, VIS_COL]) if c not in headers]
        if missing:
            error(f"CSV missing expected columns: {', '.join(missing)}")
            sys.exit(2)

        problems = 0
        seen_ids, seen_pairs = set(), set()
        rows = 0

        for i, row in enumerate(reader, start=2):
            rows += 1

            # required basics
            for c in REQUIRED_COLS:
                if not (row.get(c) or "").strip():
                    problems += 1; error(f"required field '{c}' is empty", i)

            # uniqueness
            rid = (row.get(ID_COL) or "").strip()
            if rid in seen_ids:
                problems += 1; error("duplicate issuer_id", i)
            seen_ids.add(rid)

            pair = ((row.get(COMPANY_COL) or "").strip().lower(),
                    (row.get(PRODUCT_COL) or "").strip().lower())
            if all(pair):
                if pair in seen_pairs:
                    problems += 1; error("duplicate (company_name, product_name)", i)
                seen_pairs.add(pair)

            # enums
            status = (row.get(STATUS_COL) or "").strip().lower()
            if status and status not in STATUS_ENUM:
                problems += 1; error(f"invalid status '{status}' (expected {sorted(STATUS_ENUM)})", i)

            vis = (row.get(VIS_COL) or "").strip().lower()
            if vis and vis not in VIS_ENUM:
                problems += 1; error(f"invalid visibility '{vis}' (expected {sorted(VIS_ENUM)})", i)

            # booth rule (optional strict)
            booth = (row.get(BOOTH_COL) or "").strip()
            if not args.allow_empty_booth and not booth:
                problems += 1; error("booth is required (use --allow-empty-booth to relax)", i)

            # website
            w = (row.get(WEBSITE_COL) or "").strip()
            if w:
                scheme = urlparse(w).scheme
                if scheme not in {"http", "https"}:
                    problems += 1; error("website must start with http(s)://", i)

            # date
            d = (row.get(DATE_COL) or "").strip()
            if d and not DATE_RE.match(d):
                problems += 1; error(f"bad {DATE_COL} (YYYY-MM-DD): {d}", i)

            # proof urls
            urls = split_urls(row.get(PROOF_COL) or "")
            if not urls and (status in {"submitted", "verified"}) and not args.allow_missing_proof:
                problems += 1; error(f"{PROOF_COL} is required for status '{status}' "
                                     f"(or run with --allow-missing-proof)", i)
            if urls:
                for msg in validate_proof_urls(urls, args.url_prefix, args.skip_file_check, args.proof_dir):
                    problems += 1; error(msg, i)

        if problems:
            error(f"\nValidation FAILED: {problems} problem(s) found across {rows} row(s).")
            sys.exit(1)
        print(f"OK — {rows} row(s) validated with 0 problems.")
        sys.exit(0)

if __name__ == "__main__":
    main()
