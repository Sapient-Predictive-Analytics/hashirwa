import csv, sys
req = ['issuer_name', 'product_name', 'category', 'certificate_type', 'certificate_id', 'region', 'website_or_qr', 'photo_filename', 'event_source', 'date_collected', 'verified_by', 'notes']
with open("data/issuers.csv", newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for i,row in enumerate(r, start=1):
        miss = [k for k in req if k not in row or row[k]=="" ]
        if miss:
            print(f"Row {i} missing: {miss}"); sys.exit(1)
print("OK")
