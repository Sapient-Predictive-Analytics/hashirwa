🌉 Milestone 1 — Data Foundation & Validation Pipeline

Milestone 1 establishes the backend foundation for HashiRWA:
structured issuer data, validation tooling, and a reproducible data pipeline that supports future RWA tokenization and AI-driven enrichment.

📂 1. Data Schema (issuers.csv)

The issuers.csv file follows a strict, validated schema ensuring clean, consistent data ready for downstream processing.

Schema Overview
| Column                    | Description                                                         |
| ------------------------- | ------------------------------------------------------------------- |
| **issuer_id**             | Unique ID for each issuer                                           |
| **company_name**          | Company, producer, or manufacturer name                             |
| **brand_or_product_line** | Brand or line name (optional)                                       |
| **product_name**          | Name of the showcased product                                       |
| **category**              | Product category (e.g., Tea, Sake, Snacks)                          |
| **certifications**        | Certificates held by the producer                                   |
| **cert_ids_or_details**   | Certification numbers or IDs                                        |
| **prefecture_or_region**  | Japanese prefecture/region                                          |
| **booth**                 | Expo booth code                                                     |
| **website**               | Official website                                                    |
| **event**                 | Event where data was collected                                      |
| **collector**             | Data collector (Sapient team)                                       |
| **program**               | Program type (e.g., pilot)                                          |
| **nda_required**          | `yes` or `no`                                                       |
| **status**                | `pending`, `verified`, `active`, `inactive`, `rejected`, `archived` |
| **evidence_url**          | URL to supporting documents (optional for M1)                       |
| **photo_proof_url**       | Photo proofs from Expo                                              |
| **collected_date**        | ISO date `YYYY-MM-DD`                                               |
| **visibility**            | `public`, `private`, or `hidden`                                    |
| **notes**                 | Additional comments                                                 |


This schema is compatible with CIP-68 metadata, and supports future RWA mapping.

🛠 2. Validation Tool (validate_issuers.py)

A custom Python validator ensures all issuer data meets HashiRWA’s quality standards.

✔ Validates:

Required columns

URL schemes (http / https)

ISO date formats

Allowed values for:

status

visibility

nda_required

Quoted fields with commas

Optional strict enforcement of evidence_url

📌 Usage

Relaxed mode (default for M1):

python scripts/validate_issuers.py data/issuers.csv --allow-empty-urls


Strict mode (for future milestones):

python scripts/validate_issuers.py data/issuers.csv


Write normalized output:

python scripts/validate_issuers.py data/issuers.csv --write-fixed data/issuers_clean.csv

## 📁 3. Repository Structure (as of M1)

```
hashirwa/
  data/
    issuers.csv
    proof/
      haranoseichahonpo.jpg
      miyagi-farm.jpg
      tomin-namazake.jpg
      kouzou-shuzo.jpg
      unique-bosai.jpg
      marutomo-bussan.jpg
      kimuraya-seafood.jpg
      sawarabi.jpg
      ako-aranami-salt.jpg
      sankyo-foods.jpg
  scripts/
    validate_issuers.py
  README.md
  LICENSE
```

This clean directory layout ensures easy navigation and future expansion during M2/M3.

🌉 4. Milestone 1 Completion Summary

Milestone 1 successfully delivers the following:

✔ Standardized issuer dataset

✔ Completed CSV schema supporting RWA onboarding

✔ Robust validation script for reproducible quality checks

✔ Normalization of booleans, dates, and statuses

✔ Expo photo proofs organized in /data/proof/

✔ Clear documentation for developers and reviewers

With the backend foundation complete, HashiRWA is ready to advance to Milestone 2: AI-assisted data enrichment, issuer verification, and preparation for CIP-68 on-chain metadata.
