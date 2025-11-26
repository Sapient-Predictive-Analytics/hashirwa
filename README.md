# 🌉 HashiRWA — Fund 14  
### Milestone 1: Data Foundation & Validation Pipeline

![Status](https://img.shields.io/badge/Status-In%20Progress-teal?style=flat-square)
![Milestone](https://img.shields.io/badge/Milestone-1-blueviolet?style=flat-square)
![Fund](https://img.shields.io/badge/Catalyst-Fund%2014-red?style=flat-square)
![Track](https://img.shields.io/badge/Track-RWA-orange?style=flat-square)
![Language](https://img.shields.io/badge/Language-Python-yellow?style=flat-square)

> **Future Notice:**  
> HashiRWA is currently being delivered under **Fund 14**.  
> A future **Fund 15** expansion will build on this dataset with product-level metadata, tokenization pathways, and oracle integration. A dedicated F15 section will be added once Fund 14 milestones are completed.

## Overview

This repository contains **Milestone 1 of HashiRWA**, funded under **Project Catalyst — Fund 14 (RWA Track)**.  
The milestone establishes the initial data foundation needed to onboard issuers, validate collected information, and prepare for future enrichment and on-chain compatibility.

Milestone 1 delivers:
- a clean and standardized `issuers.csv` dataset  
- a validation tool for quality assurance  
- photo evidence for issuer verification  
- directory structure for future datasets  
- schema designed to align with upcoming CIP-68 metadata work  

This forms the base layer for all later development phases.

## 1. Data Schema (`issuers.csv`)

The schema used in Fund 14 Milestone 1 includes the following fields:

| Column                    | Description                                                         |
|---------------------------|---------------------------------------------------------------------|
| **issuer_id**             | Unique ID for each issuer                                           |
| **company_name**          | Company or producer name                                            |
| **brand_or_product_line** | Brand or product line                                               |
| **product_name**          | Name of the showcased product                                       |
| **category**              | Product category (e.g., Tea, Sake, Snacks)                          |
| **certifications**        | Certifications held                                                 |
| **cert_ids_or_details**   | Certification numbers or details                                    |
| **prefecture_or_region**  | Japanese prefecture or region                                       |
| **booth**                 | Expo booth number                                                   |
| **website**               | Official website                                                    |
| **event**                 | Event where the data was collected                                  |
| **collector**             | Sapient team data collector                                         |
| **program**               | Program type (e.g., pilot)                                          |
| **nda_required**          | yes / no                                                            |
| **status**                | pending / verified / active / inactive / rejected / archived        |
| **evidence_url**          | Optional URL to supporting documents                                |
| **photo_proof_url**       | Photo proof taken at the expo                                       |
| **collected_date**        | ISO date (YYYY-MM-DD)                                               |
| **visibility**            | public / private / hidden                                           |
| **notes**                 | Additional comments                                                 |

This schema supports clean ingestion, structured sorting, and future RWA metadata mapping.

## 2. Validation Tool (`validate_issuers.py`)

A custom Python validation script ensures consistency and data quality across all `issuers.csv` entries.

### Features
- Required field checks  
- URL validation  
- ISO date formatting  
- Allowed enums (`status`, `visibility`, `nda_required`)  
- Duplicate issuer detection  
- Whitespace and comma-handling normalization  
- Optional strict mode for evidence URLs  

### Usage

Relaxed mode (default for M1):
```bash
python scripts/validate_issuers.py data/issuers.csv --allow-empty-urls

3. Repository Structure
hashirwa/
│
├── data/
│   ├── issuers.csv
│   └── proof/
│       ├── haranoseichahonpo.jpg
│       ├── miyagi-farm.jpg
│       ├── tomin-namazake.jpg
│       ├── kouzou-shuzo.jpg
│       ├── unique-bosai.jpg
│       ├── marutomo-bussan.jpg
│       ├── kimuraya-seafood.jpg
│       ├── sawarabi.jpg
│       ├── ako-aranami-salt.jpg
│       └── sankyo-foods.jpg
│
├── scripts/
│   └── validate_issuers.py
│
├── README.md
└── LICENSE

4. Milestone 1 Completion Summary

Milestone 1 successfully delivers:

✔ A standardized issuer dataset

✔ Completed CSV schema suitable for RWA onboarding

✔ Fully functional validator script

✔ Normalization of boolean, date, and status fields

✔ Organized photo proofs in /data/proof/

✔ Clear developer and reviewer documentation

✔ A robust starting point for Milestone 2 (AI-assisted enrichment)

✔ Schema alignment toward future CIP-68 on-chain metadata

HashiRWA Fund 14 establishes the data backbone on which future functionality — including Fund 15 expansion — will be built.
