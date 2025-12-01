# HashiRWA Metadata Files

This folder contains metadata files used for Cardano testnet registration and
token minting during **Milestone 1 – Platform Foundation**.

## Purpose

Each JSON file here represents the metadata for a **single sample product
listing**, derived from the issuer details found in:

hashirwa/data/issuers.csv

The metadata is used for:
- Initial Cardano testnet metadata registration  
- Sample token minting for M1  
- Demonstrating the flow: submission → approval → listing → on-chain metadata  

## File Structure

- `metadata-example.json`  
  A simple template showing the expected structure of a metadata entry.

- `haranoseichahonpo-oku-yame-tea.json`  
  The **official M1 metadata file**, based on issuer_id **1 (Haranoseichahonpo Inc.)**
  from `issuers.csv`.  
  This file is used for the test mint and Tx hash demonstration.

## How to Use

1. Select an issuer from `issuers.csv`.  
2. Create a corresponding metadata JSON file in this folder.  
3. Use the metadata file during the minting transaction (Conway CLI).  
4. Record the resulting transaction hash for milestone evidence.

## Notes

- Metadata is kept intentionally simple for M1.  
- Additional issuers and metadata files will be added in later milestones as the
  listing and onboarding modules expand.  
- All metadata values originate from trusted issuer data collected during the
  Food Japan outreach.

