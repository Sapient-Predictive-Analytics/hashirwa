#!/usr/bin/env python3
"""
HashiRWA CSV validator (Jun 2025)

Matches CSV header:
issuer_id,company_name,brand_or_product_line,product_name,category,
certifications,cert_ids_or_details,prefecture_or_region,booth,website,
event,collector,program,nda_required,status,evidence_url,photo_proof_url,
collected_date,visibility,notes
"""
import argparse, csv, os, re, sys
from urllib.parse import urlparse

# Column keys (exactly as in your header)
ID_COL = "issuer_id"
COMPANY_COL = "company_name"
PRODUCT_COL = "product_name"
PROOF_COL = "photo_proof_url"
STATUS_COL = "status"
VIS_COL = "visibility"
DATE_COL = "collected_date"
WEBSITE_COL = "website"
BOOTH_COL = "booth"

# Required-but-realistic columns
REQUIRED_COLS = [ID_COL, COMPANY_COL, STATUS_COL, VIS_COL]

STATUS_ENUM = {"draft", "submitted", "verified"}
VISIBILITY_ENUM = {"public", "private"}

URL_PREFIX_DEFAULT = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$")

def error(msg, rownum=None):
    print(f"[row {rownum}] {msg}" if rownum else msg)

def _validate_url(u: str, url_prefix: str, rownum: int):
    probs = 0
    if not u.startswith(("http://", "https://")):
        probs += 1; error(f"{PROOF_COL} url must start with http(s)://", rownum)
    if url_prefix and not u.startswith(url_prefix):
        probs += 1; error(f"{PROOF_COL} must start with url-prefix", rownum)
    # strip query (?raw=true)
    filename = u.split("/")[-1].split("?")[0]
    if not FILENAME_RE.match(filename):
        probs += 1; error(f"proof filename not kebab-case or bad extension: {filename}", rownum)
    return probs, filename

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT)
    ap.add_argument("--skip-file-check", action="store_true")
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
        seen_ids = set()
        seen_pairs = set()
        rows = 0

        for i, row in enumerate(reader, start=2):
            rows += 1

            # Required non-empty
            for c in REQUIRED_COLS:
                if (row.get(c) or "").strip() == "":
                    problems += 1; error(f"required field '{c}' is empty", i)

            # issuer_id unique
            rid = (row.get(ID_COL) or "").strip()
            if rid:
                if rid in seen_ids:
                    problems += 1; error("duplicate issuer_id", i)
                seen_ids.add(rid)

            # (company, product) uniqueness (best effort)
            pair = ((row.get(COMPANY_COL) or "").strip().lower(),
                    (row.get(PRODUCT_COL) or "").strip().lower())
            if pair[0] and pair[1]:
                if pair in seen_pairs:
                    problems += 1; error("duplicate (company_name, product_name)", i)
                seen_pairs.add(pair)

            # Enum checks
            status = (row.get(STATUS_COL) or "").strip().lower()
            if status and status not in STATUS_ENUM:
                problems += 1; error(f"invalid status '{status}' (expected one of {sorted(STATUS_ENUM)})", i)

            visibility = (row.get(VIS_COL) or "").strip().lower()
            if visibility and visibility not in VISIBILITY_ENUM:
                # If visibility looks like a date, hint likely missing proof URL
                if DATE_RE.match(visibility):
                    error(f"visibility contains a date — check if {PROOF_COL} is empty or columns shifted", i)
                problems += 1; error(f"invalid visibility '{visibility}' (expected one of {sorted(VISIBILITY_ENUM)})", i)

            # If submitted/verified → require proof url
            proofs_raw = (row.get(PROOF_COL) or "").strip()
            if status in {"submitted", "verified"} and not proofs_raw:
                problems += 1; error(f"{PROOF_COL} is required for status '{status}'", i)

            # Validate multiple proof URLs (semicolon-separated)
            if proofs_raw:
                urls = [u.strip() for u in proofs_raw.split(";") if u.strip()]
                if not urls:
                    problems += 1; error(f"{PROOF_COL} is empty after parsing", i)
                for u in urls:
                    p, filename = _validate_url(u, args.url_prefix, i)
                    problems += p
                    if not args.skip_file_check:
                        local = os.path.join(args.proof_dir, filename)
                        if not os.path.exists(local):
                            problems += 1; error(f"missing local proof file: {local}", i)

            # collected_date format if present
            cdate = (row.get(DATE_COL) or "").strip()
            if cdate and not DATE_RE.match(cdate):
                problems += 1; error(f"bad {DATE_COL} (YYYY-MM-DD): {cdate}", i)

            # website scheme if present
            w = (row.get(WEBSITE_COL) or "").strip()
            if w:
                parsed = urlparse(w)
                if parsed.scheme not in {"http", "https"}:
                    problems += 1; error("website must start with http(s)://", i)

            # booth is OPTIONAL (no error if empty)

        if problems:
            error(f"\nValidation FAILED: {problems} problem(s) found across {rows} row(s).")
            sys.exit(1)
        else:
            print(f"OK — {rows} row(s) validated with 0 problems.")
            sys.exit(0)

if __name__ == "__main__":
    main()
