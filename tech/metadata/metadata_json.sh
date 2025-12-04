#!/bin/bash

cat << EOF > metadata.json
{
  "721": {
    "$POLICY_ID": {
      "$TOKEN_HEX": {
        "issuer_id": 1,
        "issuer_name": "Haranoseichahonpo Inc.",
        "brand_or_product_line": "Oku Yame Tea",
        "product_name": "Oku Yame Tea (Gyokuro, Hojicha, Genmaicha, Sencha, Shiraore)",
        "category": "Green tea",
        "certificate_type": "JFS-B",
        "certificate_id": "JFS-B24002904-0",
        "prefecture_or_region": "Fukuoka, Japan"
      }
    }
  }
}
EOF
