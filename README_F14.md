# 🌉 HashiRWA — Fund 14  
### Milestone 1: Data Foundation & Validation Pipeline

This document summarizes the **Fund 14 (F14)** version of HashiRWA.  
It covers the initial dataset, schema design, validation tooling, and evidence collection that laid the groundwork for HashiRWA’s later expansion in Fund 15.

---

## 🧭 Navigation

| Section | Description |
|--------|-------------|
| [Overview](#overview) | Scope of F14 Milestone 1 |
| [Data Schema](#1-data-schema-issuerscsv) | Full schema used in M1 |
| [Validation Tool](#2-validation-tool-validate_issuerspy) | Python validator features |
| [Repository Structure](#3-repository-structure) | Directory layout |
| [Completion Summary](#4-milestone-1-completion-summary) | Deliverables achieved |

---

## 🌟 Overview

**Milestone 1 (Fund 14)** focused on establishing a **clean, validated issuer dataset** collected from Japanese producers at various expos.  
This milestone created:

- the issuer dataset used for early RWA categorization  
- the first version of the CSV schema  
- the validation script for enforcing consistency  
- the `/proof/` directory of photo evidence  
- standardized metadata aligned with CIP-68 principles  
- clean groundwork for future AI-assisted enrichment (M2 and beyond)

This F14 dataset served as the foundation for the more technical HashiRWA #2 (F15) pipeline.

---

## 📂 1. Data Schema (`issuers.csv`)

The table below shows the exact schema used in **Fund 14 – Milestone 1**.

| Column                    | Description                                                         |
|---------------------------|---------------------------------------------------------------------|
| **issuer_id**             | Unique ID for each issuer                                           |
| **company_name**          | Company, producer, or manufacturer name                             |
| **brand_or_product_line** | Brand or product line (optional)                                    |
| **product_name**          | Name of the showcased product                                       |
| **category**              | Product category (e.g., Tea, Sake, Snacks)                          |
| **certifications**        | Certificates or standards held by the issuer                        |
| **cert_ids_or_details**   | Certification numbers or IDs                                        |
| **prefecture_or_region**  | Japanese prefecture or region                                       |
| **booth**                 | Expo booth number                                                   |
| **website**               | Official website URL                                                |
| **event**                 | Event where data was collected                                      |
| **collector**             | Data collector (Sapient team)                                       |
| **program**               | Program type (e.g., “pilot”)                                        |
| **nda_required**          | `yes` / `no`                                                        |
| **status**                | `pending`, `verified`, `active`, `inactive`, `rejected`, `archived` |
| **evidence_url**          | URL to supporting files (optional for M1)                           |
| **photo_proof_url**       | Expo photo proof                                                    |
| **collected_date**        | ISO format `YYYY-MM-DD`                                             |
| **visibility**            | `public`, `private`, or `hidden`                                    |
| **notes**                 | Additional remarks                                                  |

This schema was designed to be **CIP-68 compatible** and ready for future product-level RWA mapping.

---

## 🛠 2. Validation Tool (`validate_issuers.py`)

A custom Python validator was created to ensure all entries in `issuers.csv` meet HashiRWA’s quality standards.

### ✔ The validator checks:

- Required fields  
- URL format (http/https)  
- ISO date formats  
- Status + visibility enums  
- Boolean normalization  
- Duplicate detection  
- Quoted fields containing commas  

### ✔ Usage

**Relaxed mode** (default in M1):

```bash
python scripts/validate_issuers.py data/issuers.csv --allow-empty-urls
