# HashiRWA

HashiRWA is a proof-of-concept marketplace for Japanese agricultural and food-related real-world assets on Cardano.

The project was developed as a Project Catalyst Fund 14 MVP. It focuses on the practical groundwork needed before any serious RWA deployment: issuer discovery, product data intake, verification evidence, investor-facing presentation, wallet-aware demo flows, reference pricing, and measurable engagement analytics.

This repository is not a production marketplace and does not issue investment products. It is an open-source demonstration of the onboarding and data layer that a Cardano RWA marketplace would need before moving toward testnet and mainnet workflows.

Live demo: https://app.hashirwa.trade

## Project goals

HashiRWA tests a simple question: can real Japanese agricultural and food producers be represented in a structured, Cardano-oriented marketplace prototype without overstating their readiness for tokenization?

The MVP answers this by focusing on:

- structured issuer and product records;
- conservative verification status labels;
- due-diligence document links and evidence references;
- investor-facing browsing and watchlist flows;
- Cardano wallet connection as a session-level demo feature;
- product-level reference prices served from an external data layer;
- anonymous and wallet-labelled investor activity tracking;
- a clear path from producer onboarding to later testnet simulations.

## Current status

This repository reflects the Fund 14 close-out version of HashiRWA.

The working application is a Flask/Replit demo with an external AWS data service. The Replit app remains the user-facing demo environment. The AWS side provides lightweight storage and retrieval for listings, product values, certificates, event logs, and analytics summaries.

The current implementation is deliberately modest. It favours understandable data structures and easy inspection over premature production infrastructure.

## What the MVP includes

### Issuer dashboard

The issuer view demonstrates how producer listings may be presented after intake and review. It includes product details, region, certification fields, verification status, and oracle/reference-price fields.

### Investor dashboard

The investor view presents available listings, per-listing reference values, watchlist controls, and refresh buttons that call the backend for current product values.

### Marketplace preview

The marketplace preview shows selected Japanese supplier listings and links into the document-vault pattern used for onboarding and due diligence.

### Cardano wallet session demo

The app includes a browser-wallet detection and session-connection flow for Cardano wallets such as Lace and Yoroi. This is currently a demo login feature only. It does not yet sign messages, build transactions, mint assets, or prove wallet ownership cryptographically.

### AWS-backed data layer

The prototype uses an external lightweight data service controlled by Sapient Swarm. It is used to keep the data layer separate from the Replit demo application.

Current AWS data structure:

```text
s3://sapientswarm-hashirwa-data-alpha/
└── hashirwa/
    ├── public/
    │   ├── listings.json
    │   ├── product_values.json
    │   ├── product_values_chainlink_demo.csv
    │   └── certificates.json
    └── logs/
        └── investor_events/YYYY/MM/DD/events.jsonl
```

Current API surface:

```text
GET  /health
GET  /listings
GET  /product-values
GET  /product-values/{listing_id}
GET  /certificates
GET  /certificates/{listing_id}
POST /events
GET  /analytics/summary
```

The pricing feed is currently an S3-hosted CSV exposed through a small Lambda shim API. The UI labels this simply as an oracle price. It should be understood as a demo reference feed, not a live Chainlink production oracle.

## Pilot issuer dataset

The current issuer dataset contains ten Japanese food and agricultural listings gathered through in-person supplier engagement and booth interviews. The table below summarizes the public demo fields. Some certifications and supporting documents remain intentionally marked as pending until onboarding and evidence review are complete.

| ID | Company | Product | Category | Region | Certification reference |
|---:|---|---|---|---|---|
| 1 | Haranoseichahonpo Inc. | Oku Yame Tea | Green tea | Fukuoka | JFS-B |
| 2 | Miyagi Farm Co.,Ltd. | Egg | Poultry | Okinawa | — |
| 3 | Tomin Sake Company | Tomin Namazake | Sake | Toyama | Liquor Tax Act; Brewery License; Export Health Certificate |
| 4 | Sata Souji Shouten Ltd. | Shochu | Shochu | Kagoshima | — |
| 5 | Unique Bosai Co.,Ltd. | Dashi Rice Porridge | Emergency Food | Tokyo | JFS-B |
| 6 | Marutomo Bussan | Japanese dried shiitake | Dried mushrooms | Oita | Oita Council; HACCP; PCQI |
| 7 | Kimuraya Seafood Co., Ltd. | Mozuku | Seaweed | Tottori | MEL Certification; SDGs Certification |
| 8 | Sawarabi Co.,Ltd. | Edomae Aged Sweet Potato | Snacks | Chiba | — |
| 9 | Ako Aranami Salt Co.,Ltd. | Shiitake Salt | Seasoning | Hyogo | Vegan certification |
| 10 | Sankyo Foods Co.,Ltd. | Genmai Gokochi | Ready-to-eat rice | Osaka | — |

The producer data is handled conservatively. A listing in the demo is not a claim of a finalized token issuance, investment offering, or completed commercial onboarding.

## Cardano components

HashiRWA is Cardano-oriented but intentionally not overbuilt at the MVP stage.

Implemented or demonstrated:

- Cardano wallet connection UI for browser wallets;
- preprod proof-of-listing evidence from earlier milestone work;
- token-ready metadata concepts;
- product/listing data structures that can be mapped into later on-chain metadata;
- investor activity logs that can later be correlated with testnet workflows.

Preprod transaction evidence:

```text
https://preprod.cardanoscan.io/transaction/3ce7adb5714ca14a53dc355a0b39599e3b710fbce4150595a8e0833378b726de
```

Not yet implemented:

- signed wallet challenge verification;
- production wallet authentication;
- asset minting;
- marketplace settlement;
- mainnet transactions;
- regulated investment workflows.

## Analytics and event logging

The application tracks investor activity through a lightweight event log. Events are written as JSONL records and then aggregated by the AWS shim API.

Current event types include:

```text
marketplace_view
listing_view
listing_click
watchlist_add
watchlist_remove
document_view
investor_dashboard_view
```

The dashboard summary exposes:

- total event count;
- counts by event type;
- top viewed listings;
- top clicked listings;
- top watchlisted listings;
- recent events.

For the alpha demo, events can be anonymous or labelled with Cardano preprod/testnet wallet identifiers. Wallet addresses are hashed in the analytics layer when submitted through the event endpoint.

## Repository structure

```text
hashirwa/
├── data/                 # local fallback JSON data for the Flask demo
├── scripts/              # utility scripts and data-refresh experiments
├── static/               # favicon and static assets
├── templates/            # Flask/Jinja templates
├── proof/                # onboarding and verification evidence, where public
├── docs/                 # milestone notes and supporting documentation
├── mockups/              # screenshots and UI evidence
├── main.py               # Flask application entry point
├── hashirwa_data_client.py
└── README.md
```

The external AWS Lambda and S3 components are intentionally separated from the Replit app. The Flask app can run locally with fallback data, while the deployed demo can call the external data service.

## Running locally

Install dependencies:

```bash
pip install flask requests
```

Run the app:

```bash
python main.py
```

Open the local URL printed by Flask. The app defaults to port `5000` in the Replit-compatible version.

Optional environment variables:

```bash
SESSION_SECRET=change-me
HASHIRWA_API_BASE_URL=https://your-lambda-function-url
HASHIRWA_API_KEY=
PORT=5000
```

The API key is currently optional for the alpha demo. If this moves beyond controlled testing, the write endpoints should be protected.

## Data model notes

The MVP uses simple, inspectable structures:

- `listings.json` for public listing data;
- `product_values_chainlink_demo.csv` for product-level demo reference values;
- `certificates.json` for certificate references and verification status;
- `events.jsonl` for append-style engagement logs.

The CSV product-value feed is keyed by listing ID and issuer ID. Product display names are shortened for investor readability. For example, `Oku Yame Tea (Gyokuro, Hojicha, Genmaicha, Sencha, Shiraore)` is displayed as `Oku Yame Tea`.

## Roadmap

### 1. Stabilize the HashiRWA foundation

Near-term work should turn the current proof of concept into a more reliable pilot environment:

- keep Replit as the demo front end while externalizing the data service;
- move all listing, certificate, product-value, and analytics reads through the shim API;
- replace local JSON writes with durable storage patterns;
- add signed wallet challenge verification;
- separate anonymous users, wallet-linked users, issuers, and admins;
- formalize issuer intake forms and review states;
- define a public schema for agricultural listing metadata;
- document what counts as verified, pending, demo, or redacted evidence.

### 2. Improve producer onboarding

The next HashiRWA iteration should focus on the operational reality of Japanese producers:

- bilingual intake forms;
- clearer evidence requirements;
- issuer permission and consent records;
- document vault structure for redacted and non-redacted materials;
- certification status history;
- controlled supplier previews;
- exportable issuer packets for review by partners and community auditors.

### 3. Make pricing and reference data more credible

The current oracle price is a demo reference value from a controlled CSV. Future work should improve provenance and update logic:

- maintain source, timestamp, status, and unit for every product value;
- add multiple feed sources where available;
- preserve historical price snapshots;
- distinguish producer-submitted values from external market references;
- prepare adapters for Chainlink or other oracle infrastructure if suitable;
- publish sample schemas and non-sensitive datasets for community review.

### 4. Move toward Cardano testnet workflows

Before mainnet, the project should use Cardano testnets to make the workflow measurable:

- wallet challenge login;
- token-ready metadata generation;
- proof-of-listing transaction flows;
- mint/burn simulations;
- metadata publication tests;
- dashboards that connect off-chain issuer data to testnet events.

### 5. HashiFlo preview: activation and liquidity layer

HashiFlo is the planned next iteration. HashiRWA is the onboarding gateway; HashiFlo is intended to become the activity, valuation, and liquidity-intelligence layer.

The planned HashiFlo direction includes:

- AI-assisted pricing references and valuation signals;
- liquidity and activity logic for agricultural RWAs;
- investor-side dashboards and signals;
- token-ready metadata builder;
- Cardano testnet simulations for minting, burning, metadata publishing, and valuation calls;
- open-source components such as schemas, valuation logic, and a tokenization simulator.

The proposed Fund 15 direction sets measurable targets: 500-1,000 Cardano testnet transactions across RWA workflows, 20-30 Japanese agricultural assets processed through the onboarding prototype, a target of 100+ beta participants, at least three open-source components, and an AI liquidity engine v2.

This is not a promise of production liquidity. It is a roadmap for moving from verified producer intake toward measurable testnet execution and open infrastructure.

## Community and contribution model

HashiRWA is intended to be understandable by Cardano builders, Catalyst reviewers, and domain partners who care about real-world adoption but do not want opaque RWA claims.

Useful contributions include:

- schema review;
- Cardano metadata design;
- wallet-authentication hardening;
- testnet workflow design;
- Japanese/English onboarding UX review;
- data provenance and oracle-adapter feedback;
- documentation improvements;
- responsible critique of the RWA assumptions.

Please avoid treating the demo listings as investment products. The project is still at the prototype and pilot-onboarding stage.

## License

MIT License.
