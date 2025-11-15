#!/usr/bin/env python3
"""
HashiRWA CSV validator

Usage (Windows PowerShell example):
  python scripts/validate_issuers.py data/issuers.csv ^
      --proof-dir proof ^
      --url-prefix https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/ ^
      --skip-file-check

Exit code is non-zero if validation fails.
"""

import argparse
import csv
import os
import re
import sys
from urllib.parse import urlparse

# Columns matching your current CSV schema
ID_COL = "issuer_id"
COMPANY_COL = "company_name"
BRAND_COL = "brand_or_product_line"
PRODUCT_COL = "product_name"
PROOF_COL = "photo_proof_url"

REQUIRED_COLS = [
    ID_COL,
    COMPANY_COL,
    "booth",
    "status",
    "visibility",
    # PROOF_COL is OPTIONAL (but if present, must be valid)
]

STATUS_ENUM = {"draft", "submitted", "verified"}
VISIBILITY_ENUM = {"public", "private"}

DATE_COL = "collected_date"   # if present must be YYYY-MM-DD
WEBSITE_COL = "website"       # optional but if present must be http(s)

URL_PREFIX_DEFAULT = (
    "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"
)

FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def error(msg, rownum=None):
    if rownum is not None:
        print(f"[row {rownum}] {msg}")
    else:
        print(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--proof-dir", default="proof")
    ap.add_argument("--url-prefix", default=URL_PREFIX_DEFAULT)
    ap.add_argument("--skip-file-check", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        error(f"CSV not found: {args.csv_path}")
        sys.exit(2)

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLS if c not in headers]
        if missing:
            error(f"CSV missing required columns: {', '.join(missing)}")
            sys.exit(2)

        problems = 0
        seen_ids = set()
        seen_pairs = set()
        row_count = 0

        for i, row in enumerate(reader, start=2):  # header is line 1
            row_count += 1

            # 1) Required non-empty fields
            for c in REQUIRED_COLS:
                if (row.get(c) or "").strip() == "":
                    problems += 1
                    error(f"required field '{c}' is empty", i)

            # 2) Unique issuer_id
            rid = (row.get(ID_COL) or "").strip()
            if rid:
                if rid in seen_ids:
                    problems += 1
                    error("duplicate issuer_id", i)
                seen_ids.add(rid)

            # 3) Unique (company_name, product_name) pair
            pair = (
                (row.get(COMPANY_COL) or "").strip().lower(),
                (row.get(PRODUCT_COL) or "").strip().lower(),
            )
            if all(pair):
                if pair in seen_pairs:
                    problems += 1
                    error("duplicate (company_name, product_name)", i)
                seen_pairs.add(pair)

            # 4) status enum
            status = (row.get("status") or "").strip().lower()
            if status and status not in STATUS_ENUM:
                problems += 1
                error(
                    f"invalid status '{status}' "
                    f"(expected one of {sorted(STATUS_ENUM)})",
                    i,
                )

            # 5) visibility enum
            visibility = (row.get("visibility") or "").strip().lower()
            if visibility and visibility not in VISIBILITY_ENUM:
                problems += 1
                error(
                    f"invalid visibility '{visibility}' "
                    f"(expected one of {sorted(VISIBILITY_ENUM)})",
                    i,
                )

            # 6) photo_proof_url — allow multiple URLs separated by ';'
            purl_raw = (row.get(PROOF_COL) or "").strip()
            if purl_raw:
                urls = [u.strip() for u in purl_raw.split(";") if u.strip()]
                for u in urls:
                    if not u.startswith(args.url_prefix):
                        problems += 1
                        error(f"{PROOF_COL} URL must start with url-prefix: {u}", i)

                    filename = u.split("/")[-1].split("?")[0]
                    if not FILENAME_RE.match(filename):
                        problems += 1
                        error(
                            f"proof filename not kebab-case or bad extension: {filename}",
                            i,
                        )

                    if not args.skip_file_check:
                        local_path = os.path.join(args.proof_dir, filename)
                        if not os.path.exists(local_path):
                            problems += 1
                            error(f"missing local proof file: {local_path}", i)

            # 7) collected_date format if present
            cdate = (row.get(DATE_COL) or "").strip()
            if cdate and not DATE_RE.match(cdate):
                problems += 1
                error(f"bad {DATE_COL} (YYYY-MM-DD): {cdate}", i)

            # 8) website scheme if present
            w = (row.get(WEBSITE_COL) or "").strip()
            if w:
                parsed = urlparse(w)
                if parsed.scheme not in {"http", "https"}:
                    problems += 1
                    error("website must start with http(s)://", i)

        if problems:
            error(
                f"\nValidation FAILED: {problems} problem(s) found "
                f"across {row_count} row(s)."
            )
            sys.exit(1)
        else:
            print(f"OK — {row_count} row(s) validated with 0 problems.")
            sys.exit(0)


if __name__ == "__main__":
    main()
