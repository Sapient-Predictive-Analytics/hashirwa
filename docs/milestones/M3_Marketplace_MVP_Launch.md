# Milestone 3 — Marketplace MVP Launch

## Overview

Milestone 3 delivers the first functional Marketplace MVP layer built on top of the oracle ingestion framework established in Milestone 2.

While M2 validated reference feed ingestion and display, M3 introduces structured issuer listings, a public marketplace interface, investor interaction tools, and a per-listing document vault for due diligence tracking.

This milestone demonstrates the transition from oracle validation to marketplace functionality.

---

## Live Deployment

Production URL:
https://hashi-rwa-dashboard.replit.app

---

## Functional Components Delivered

### 1. Verified Listings

Five verified/demo listings sourced from Japan Food Expo 2025 are publicly available via:

/marketplace

Each listing includes:
- Company name
- Product name
- Category
- Region
- Website link
- Proof image link
- Verification indicator

Listings support filtering by search, category, and region.

---

### 2. Public Marketplace

Endpoint:
GET /marketplace

Capabilities:
- Displays public listings
- Filter support
- Verification status
- Direct proof access
- Website links
- Document Vault access per listing

---

### 3. Document Vault

Each listing has a dedicated due diligence vault.

Endpoints:
POST /documents/add/<listing_id>
GET  /documents/<listing_id>

Capabilities:
- Add document link (GitHub / Drive / IPFS)
- View all documents per listing
- Auto-generated document ID
- Timestamp storage
- Document count badge on marketplace
- Notification logging

---

### 4. Investor Dashboard

Endpoint:
GET /investor

Capabilities:
- Listings enriched with oracle reference data
- Certification oracle indicator
- Price oracle display
- Watchlist toggle (session-based)
- Notification tracking

Endpoints:
POST /watchlist/toggle/<listing_id>
GET  /notifications

---

### 5. API Endpoints

GET /api/listings
GET /api/market
GET /health

These endpoints allow independent verification of:
- Structured listing data
- Oracle reference feed
- Application health

---

## Reviewer Test Flow

1. Visit /marketplace
2. Apply filter
3. Open Document Vault
4. Add document
5. Confirm document count updates
6. Visit /notifications
7. Visit /investor
8. Toggle watchlist
9. Query /api/listings

---

## Acceptance Criteria Status

| Requirement | Status |
|-------------|--------|
| Platform live and stable | Completed |
| 5 verified/demo listings | Completed |
| Document vault functional | Completed |
| Investor tools operational | Completed |
| No critical bugs observed | Completed |

---

## Architectural Progression

Milestone 2:
Oracle ingestion validation.

Milestone 3:
Marketplace structure layered on top of oracle data, including investor interaction and due diligence tracking.

This establishes the foundational marketplace framework for future on-chain integration.
