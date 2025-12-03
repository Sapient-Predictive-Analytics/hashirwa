# 🌉 HashiRWA — Fund 14  

## Milestone 1: Data Foundation & Validation Pipeline

![Status](https://img.shields.io/badge/Status-In%20Progress-blue)
![Milestone](https://img.shields.io/badge/Milestone-1-purple)
![Catalyst](https://img.shields.io/badge/Catalyst-Fund%2014-orange)
![Track](https://img.shields.io/badge/Track-RWA-yellow)
![Language](https://img.shields.io/badge/Language-Python-green)

---

## 📌 Future Notice

HashiRWA is currently being delivered under **Fund 14**.  
A future **Fund 15** expansion will build on this dataset with product-level metadata, tokenization pathways, and oracle integration.  
A dedicated F15 section will be added once Fund 14 milestones are completed.

---

## 📘 Overview

This repository contains **Milestone 1 of HashiRWA**, funded under **Project Catalyst — Fund 14 (RWA Track)**.  
Milestone 1 establishes the initial data foundation required to onboard Japanese agricultural producers, validate collected information, and prepare for future enrichment and on-chain compatibility.

Milestone 1 delivers:

- ✔️ A clean and standardized **issuers.csv** dataset  
- ✔️ A Python-based **validation tool** for issuer metadata  
- ✔️ Photo evidence for issuer verification  
- ✔️ Directory structure for future datasets  
- ✔️ A schema aligned with emerging metadata standards (CIP-68/CIP-113)  
- ✔️ Base preparation for producer onboarding workflows

This forms the data backbone for all later development phases.

---

## 📁 Repository Structure

### Repository Structure

```plaintext
hashirwa/
├── data/                 # issuer dataset (issuers.csv)
├── proof/                # photo evidence for verification
├── scripts/              # validation tool (validate_issuers.py)
├── mockups/              # UI/UX outlines for later milestones
├── docs/                 # supporting reference material
├── tech/                 # engineering notes & strict-mode documentation
└── README.md
```

---

## 📊 1. Data Schema (`issuers.csv`)

The dataset includes the following fields:

| Column | Description |
|--------|-------------|
| issuer_id | Unique ID for each issuer |
| company_name | Company or producer name |
| brand_or_product_line | Brand or product line |
| product_name | Name of the showcased product |
| category | Product category (Tea, Sake, Snacks, etc.) |
| certifications | Certifications held |
| cert_ids_or_details | Certification numbers or details |
| prefecture_or_region | Japanese prefecture or region |
| booth | Expo booth number |
| website | Official website |
| event | Event where data was collected |
| collector | Sapient team data collector |
| program | Program type (e.g., pilot) |
| nda_required | yes / no |

---

## 🧪 2. Validation Tool (`validate_issuers.py`)

A custom Python validator ensures clean and consistent metadata across all entries.

### Features
- Required field checks  
- URL validation  
- ISO date formatting  
- Enum enforcement (`status`, `visibility`, `nda_required`)  
- Duplicate detection  
- Whitespace & comma normalization  

> Extended developer usage (strict mode, write-fixed CSV) is documented in  
> 👉 `/tech/README.md`

---

## 🖼️ 3. Verification Photos (`/proof`)

Folder includes:
- Booth photography  
- Packaging / product photos  
- Certification evidence  
- Producer authenticity materials  

These support milestone verification requirements.

---

## 🧩 4. Mockups & UX (Foundational)

High-level UI/UX mockups illustrating:
- Onboarding flow  
- Listing details  
- Admin review process  

These guide future functional milestones.

---

## 📌 Evidence of Milestone Completion

Milestone 1 evidence includes:

1. **Dataset:** `data/issuers.csv`  
2. **Validation tool:** `scripts/validate_issuers.py`  
3. **Verification photos:** `/proof`  
4. **Documentation:** README + `tech/README.md`  
5. **Directory structure / mockups**  
6. **Commit history** showing milestone progress  

*(The functional platform demo — onboarding → approval → listing → metadata endpoint — is delivered in a separate repository.)*

---

## 🔮 Future Extension (Fund 15)

- Product-level metadata for tokenization  
- Valuation & pricing models  
- Oracle integration  
- Expanded issuer onboarding UI  
- Marketplace testnet listing  
- Full CIP-68 compatibility  
- Smart contract workflows  

A dedicated F15 section will be added after Fund 14 milestones are completed.

---

## 📜 License

MIT License.



