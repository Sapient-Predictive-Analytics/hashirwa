#!/usr/bin/env python3
"""
HashiRWA CSV validator (clean + aligned with June's CSV structure)
"""

import argparse
import csv
import os
import re
import sys
from urllib.parse import urlparse

# === COLUMN NAMES (MATCH EXACT CSV) ===
ID_COL = "issuer_id"
COMPANY_COL = "company_name"
PRODUCT_COL = "product_name"
PROOF_COL = "photo_proof_url"
STATUS_COL = "status"
VISIBILITY_COL = "visibility"

DATE_COL = "collected_date"
WEBSITE_COL = "website"

# === REQUIRED COLUMNS ===
REQUIRED_COLS = [
    ID_COL,
    COMPANY_COL,
    "booth",
    STATUS_COL,
    PROOF_COL,
    VISIBILITY_COL,
]

STATUS_ENUM = {"draft", "submitted", "verified"}
VISIBILITY_ENUM = {"public", "private"}

URL_PREFIX_DEFAULT = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$")

def error(msg, row=None):
    if row:
        print(f"[row {row}] {msg}")
    else:
        print(msg)

def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT)
    ap.add_argument("--skip-file-check", action="store_true")
    ap.add_argument("--allow-multiple-proof", action="store_true")
    ap.add_argument("--allow-empty-proof", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        error(f"CSV not found: {args.csv_path}")
        sys.exit(2)

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # Check required columns exist
        missing = [c for c in REQUIRED_COLS if c not in headers]
        if missing:
            error(f"CSV missing required columns: {', '.join(missing)}")
            sys.exit(2)

        problems = 0
        seen_ids = set()
        seen_pairs = set()

        for rownum, row in enumerate(reader, start=2):

            # === Required fields check ===
            for col in REQUIRED_COLS:
                if not row.get(col) and not args.allow_empty_proof:
                    problems += 1
                    error(f"required field '{col}' is empty", rownum)

            # === Unique issuer_id ===
            rid = row.get(ID_COL, "").strip()
            if rid:
                if rid in seen_ids:
                    problems += 1
                    error(f"duplicate issuer_id {rid}", rownum)
                seen_ids.add(rid)

            # === Proof URL ===
            urls = (row.get(PROOF_COL) or "").split(";")

            for u in urls:
                u = u.strip()
                if not u:
                    continue

                if not u.startswith(args.url_prefix):
                    problems += 1
                    error(f"{PROOF_COL} must start with url-prefix", rownum)

                filename = u.split("/")[-1].split("?")[0]
                if not FILENAME_RE.match(filename):
                    problems += 1
                    error(f"bad proof filename: {filename}", rownum)

                if not args.skip_file_check:
                    local_path = os.path.join(args.proof_dir, filename)
                    if not os.path.exists(local_path):
                        problems += 1
                        error(f"missing local proof file: {local_path}", rownum)

            # === Status ===
            status = (row.get(STATUS_COL) or "").strip().lower()
            if status not in STATUS_ENUM:
                problems += 1
                error(f"invalid status '{status}'", rownum)

            # === Visibility ===
            vis = (row.get(VISIBILITY_COL) or "").strip().lower()
            if vis not in VISIBILITY_ENUM:
                problems += 1
                error(f"invalid visibility '{vis}'", rownum)

            # === Collected date ===
            date = (row.get(DATE_COL) or "").strip()
            if date and not DATE_RE.match(date):
                problems += 1
                error(f"bad date '{date}'", rownum)

            # === Website ===
            website = (row.get(WEBSITE_COL) or "").strip()
            if website:
                parsed = urlparse(website)
                if parsed.scheme not in {"http", "https"}:
                    problems += 1
                    error("website must start with http(s)://", rownum)

        if problems:
            print(f"\nValidation FAILED: {problems} problem(s)")
            sys.exit(1)
        else:
            print("OK — all rows validated with 0 problems 🎉")
            sys.exit(0)

if __name__ == "__main__":
    main()
