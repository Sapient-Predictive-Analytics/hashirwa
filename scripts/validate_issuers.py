#!/usr/bin/env python3
import argparse, csv, sys, os, re
from datetime import datetime
from urllib.parse import urlparse

# === Exact columns in your CSV (lowercased for matching) ===
CSV_COLS = [
    "issuer_id","company_name","brand_or_product_line","product_name","category",
    "certifications","cert_ids_or_details","prefecture_or_region","booth","website",
    "event","collector","program","nda_required","status","evidence_url",
    "photo_proof_url","collected_date","visibility","notes"
]
REQUIRED_COLS = set(CSV_COLS)

ALLOWED_STATUS = {"verified","pending","rejected","archived","active","inactive"}
ALLOWED_VISIBILITY = {"public","private","hidden"}

def norm(s): return (s or "").strip().lower()

def has_http(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http","https")
    except Exception:
        return False

def normalize_yesno(val: str) -> str:
    v = norm(val)
    if v in {"yes","true","1","y"}:  return "yes"
    if v in {"no","false","0","n"}:   return "no"
    raise ValueError(f"expected yes/no, got '{val}'")

def normalize_date(val: str) -> str:
    s = (val or "").strip()
    if not s:
        raise ValueError("empty")
    s = s.replace("/", "-")
    # DD-MM-YYYY -> ISO
    m = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", s)
    if m:
        dd, mm, yyyy = m.groups()
        dt = datetime(int(yyyy), int(mm), int(dd))
        return dt.strftime("%Y-%m-%d")
    # ISO-ish
    try:
        dt = datetime.fromisoformat(s)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        raise ValueError("expected YYYY-MM-DD")

def main():
    ap = argparse.ArgumentParser(description="HashiRWA issuers.csv validator (tailored)")
    ap.add_argument("csv_path")
    ap.add_argument("--assume-http", action="store_true",
                    help="Auto-prefix http:// if a URL has no scheme (counts as a fix).")
    ap.add_argument("--allow-empty-urls", action="store_true",
                    help="Permit empty website/evidence_url/photo_proof_url.")
    ap.add_argument("--write-fixed", metavar="OUT_CSV",
                    help="Write normalized copy without modifying the original.")
    args = ap.parse_args()

    if not os.path.exists(args.csv_path):
        print(f"ERROR: CSV not found: {args.csv_path}")
        sys.exit(2)

    issues = []
    fixed_rows = []
    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("ERROR: No header found.")
            sys.exit(2)

        # Build case-insensitive header map
        header_actual = [h.strip() for h in reader.fieldnames]
        header_lc = [h.lower() for h in header_actual]
        colmap = {h.lower(): h for h in header_actual}

        missing = [c for c in REQUIRED_COLS if c not in header_lc]
        extra = [h for h in header_lc if h not in REQUIRED_COLS]
        if missing:
            print("ERROR: Missing required columns:", ", ".join(missing))
            sys.exit(2)
        if extra:
            print("NOTE: Extra columns present (ignored by rules):", ", ".join(extra))

        rownum = 1
        for row in reader:
            rownum += 1
            out = dict(row)

            # status
            raw_status = row[colmap["status"]]
            st = norm(raw_status)
            if st not in ALLOWED_STATUS:
                issues.append(f"[row {rownum}][status] Invalid '{raw_status}'. "
                              f"Allowed: {sorted(ALLOWED_STATUS)}")
            else:
                out[colmap["status"]] = st

            # visibility
            raw_vis = row[colmap["visibility"]]
            vis = norm(raw_vis)
            if vis not in ALLOWED_VISIBILITY:
                issues.append(f"[row {rownum}][visibility] Invalid '{raw_vis}'. "
                              f"Allowed: {sorted(ALLOWED_VISIBILITY)}")
            else:
                out[colmap["visibility"]] = vis

            # nda_required
            try:
                out[colmap["nda_required"]] = normalize_yesno(row[colmap["nda_required"]])
            except ValueError as e:
                issues.append(f"[row {rownum}][nda_required] {e}.")

            # collected_date
            try:
                out[colmap["collected_date"]] = normalize_date(row[colmap["collected_date"]])
            except ValueError as e:
                issues.append(f"[row {rownum}][collected_date] Bad date '{row[colmap['collected_date']]}' ({e}).")

            # URL checks
            for col in ("website","evidence_url","photo_proof_url"):
                raw = (row[colmap[col]] or "").strip()
                if not raw:
                    if not args.allow_empty_urls:
                        issues.append(f"[row {rownum}][{col}] URL is empty.")
                else:
                    if not has_http(raw):
                        if args.assume_http:
                            out[colmap[col]] = f"http://{raw}"
                        else:
                            issues.append(f"[row {rownum}][{col}] Must start with http(s):// -> '{raw}'")

            fixed_rows.append(out)

    if issues:
        for msg in issues: print(msg)
        print(f"\nValidation FAILED: {len(issues)} issue(s).")
    else:
        print("Validation PASSED ✅")

    if args.write_fixed:
        with open(args.write_fixed, "w", newline="", encoding="utf-8") as g:
            writer = csv.DictWriter(g, fieldnames=header_actual)
            writer.writeheader()
            writer.writerows(fixed_rows)
        print(f"Wrote normalized copy to: {args.write_fixed}")

    sys.exit(1 if issues else 0)

if __name__ == "__main__":
    main()
