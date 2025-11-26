# 🌉 HashiRWA #2 — Fund 15  
### Milestone 1: Data Foundation & Validation Pipeline

![Status](https://img.shields.io/badge/Status-In%20Progress-teal?style=flat-square)
![Milestone](https://img.shields.io/badge/Milestone-1-blueviolet?style=flat-square)
![Fund](https://img.shields.io/badge/Catalyst-Fund%2015-red?style=flat-square)
![Track](https://img.shields.io/badge/Track-RWA-orange?style=flat-square)
![Language](https://img.shields.io/badge/Language-Python-yellow?style=flat-square)

---

## 🔗 Previous Version (Fund 14)

You can view the archived F14 version of HashiRWA here:

👉 **[View HashiRWA Fund 14 README](./README_F14.md)**

---

## 🧭 Navigation

| Section | Description |
|--------|-------------|
| [Overview](#overview) | What Milestone 1 delivers |
| [Data Schema](#1-data-schema-issuerscsv) | Column definitions |
| [Validation Pipeline](#2-validation--consistency-checks) | Automated checks |
| [Folder Structure](#3-folder-structure) | Repo layout |
| [Usage Guide](#4-usage-guide) | How to run validators |
| [Next Steps](#next-steps) | Milestone 2–4 roadmap |

---

## 🌟 Overview

This repository contains **Milestone 1** for **HashiRWA #2 (Fund 15)** under the **Real-World Asset Track**.

Milestone 1 establishes the **base data infrastructure** for expanding from issuer-level metadata (Fund 14) to product-level metadata, tokenization pathways, and oracle integration.

Deliverables include:

- a clean, standardized `issuers.csv`
- evidence-backed issuer onboarding
- Python-based validator tools
- reproducible data checks for Catalyst audits

This is the foundation for the F15 roadmap.

---

## 📂 1. Data Schema (`issuers.csv`)

The dataset follows a strict schema to ensure consistent, machine-readable records.

| Column | Description |
|--------|-------------|
| **issuer_id** | Unique identifier |
| **company_name** | Producer or manufacturer |
| **brand_or_product** | Main product or brand |
| **country** | Country (ISO) |
| **prefecture_or_state** | Region / prefecture / state |
| **city** | City |
| **category** | High-level category |
| **subcategory** | Optional refinement |
| **contact_person** | Point of contact |
| **contact_email** | Verified email |
| **website** | Official URL |
| **address** | Physical address |
| **latitude** | Optional GPS |
| **longitude** | Optional GPS |
| **proof_image_path** | Path to photo proof in `/proof/` |
| **remarks** | Notes |

---

## 🛡️ 2. Validation & Consistency Checks

The pipeline performs:

- schema checks  
- URL + email format validation  
- required-field checks  
- duplicate detection  
- proof-path verification  
- encoding & whitespace cleanup  

A `validation_report.json` is auto-generated.

---

## 🗂️ 3. Folder Structure


The pipeline performs:

- schema checks  
- URL + email format validation  
- required-field checks  
- duplicate detection  
- proof-path verification  
- encoding & whitespace cleanup  

A `validation_report.json` is auto-generated.


---

## 🧪 4. Usage Guide

Run the validator:

```bash
python validation/validate_csv.py

✓ Schema valid
✓ 24 issuers checked
⚠ 1 missing proof image: JP_014
Report saved to validation_report.json



