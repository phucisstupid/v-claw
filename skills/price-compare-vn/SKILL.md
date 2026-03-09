---
name: price-compare-vn
description: Best-effort comparison for VN marketplace offers using product links and/or structured metadata with optional prices.
---

# Price Compare VN

Use the script to compare multiple offer inputs:

```bash
python3 "{baseDir}/scripts/compare.py" \
  --input "https://shopee.vn/product/123456/999999" \
  --input '{"marketplace":"lazada","url":"https://www.lazada.vn/products/i123-s9.html","price":189000}' \
  --json
```

Accepted `--input` values:

- marketplace URL (Shopee/Lazada parsing only)
- JSON object with normalized metadata (`marketplace`, `url`, `product_id`, `title`, `price` or `price_vnd`, optional `currency`)

Workflow:

1. Accept multiple `--input` values.
2. Parse URL inputs locally for IDs/metadata.
3. Use provided VND prices to compute cheapest offer.
4. If no price data exists, return comparison structure with `cheapest_offer=null`.
5. Return `comparison_table` as a compact normalized view for quick side-by-side checks.

This v1 does not fetch live prices from marketplace APIs/pages.
