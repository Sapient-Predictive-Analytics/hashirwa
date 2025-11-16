#!/usr/bin/env python3
import argparse, csv, os, re, sys
from urllib.parse import urlparse

REQUIRED = ["issuer_id","company_name","booth","status","visibility"]
STATUS = {"draft","submitted","verified"}
VIS = {"public","private"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.(jpg|jpeg|png|webp)$")

URL_PREFIX = "https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/main/proof/"

def err(msg,row): print(f"[row {row}] {msg}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--skip-file-check",action="store_true")
    args = ap.parse_args()

    with open(args.csv,encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    problems = 0

    # Required columns
    for c in REQUIRED:
        if c not in reader.fieldnames:
            print(f"Missing column: {c}")
            sys.exit(1)

    for i,row in enumerate(rows, start=2):

        # Required fields
        for c in REQUIRED:
            if not row.get(c,"").strip():
                problems+=1; err(f"Missing {c}",i)

        # Status
        if row["status"].lower() not in STATUS:
            problems+=1; err("Invalid status",i)

        # Visibility
        if row["visibility"].lower() not in VIS:
            problems+=1; err("Invalid visibility",i)

        # Date
        d=row.get("collected_date","").strip()
        if d and not DATE_RE.match(d):
            problems+=1; err("Bad date format",i)

        # Website
        w=row.get("website","").strip()
        if w:
            p=urlparse(w)
            if p.scheme not in {"http","https"}:
                problems+=1; err("Website must be http(s)",i)

        # Proof URL
        proof=row.get("photo_proof_url","").strip()
        if proof:
            urls=[u.strip() for u in proof.split(";") if u.strip()]
            for u in urls:
                if not u.startswith(URL_PREFIX):
                    problems+=1; err("URL must start with proof prefix",i)
                fname=u.split("/")[-1].split("?")[0]
                if not FILE_RE.match(fname):
                    problems+=1; err("Bad proof filename",i)

    if problems:
        print(f"\nValidation FAILED: {problems} issue(s).")
        sys.exit(1)
    else:
        print("OK — 0 problems 🎉")
        sys.exit(0)

if __name__=="__main__":
    main()
