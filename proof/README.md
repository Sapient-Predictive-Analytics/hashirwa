# Proof Assets

This folder stores non-sensitive proof assets collected during field
research at Japan Food Expo 2025 and other events related to HashiRWA.

## Purpose
The purpose of this directory is to provide:
- product or booth photos supporting the authenticity of issuer listings
- visual verification that data in `data/issuers.csv` was collected on-site
- optional evidence for internal reviewers or collaborators

## Privacy Notice
No personal or identifying information is stored here.
- No faces, emails, business cards, or private contact details are included.
- All photos are either product shots, booth displays, packaging, or certificates.
- When needed, photos may be cropped or blurred to remove sensitive subjects.

## File Naming
All files use predictable slug-based names:

<issuer-slug>.jpg
<issuer-slug>-1.jpg
<issuer-slug>-2.jpg

Examples:

haranoseichahonpo.jpg
miyagi-farm.jpg
tomin-sake.jpg

If a photo is not available yet, the CSV uses a placeholder URL such as:

https://example.com/proof/no_photo

## Usage
These files correspond to the `photo_proof_url` column in `data/issuers.csv`.
Future backend, frontend, or Chainlink integrations may reference these assets.

## Notes
- These assets are optional and not required for MVP functionality.
- This folder may expand later to include certificate scans, QR codes, or
  blockchain-verified metadata.

