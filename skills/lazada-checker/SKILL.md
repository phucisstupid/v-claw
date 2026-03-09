---
name: lazada-checker
description: Parse Lazada product links and extract metadata such as item_id, seller_id, slug, host, and canonical URL when possible.
---

# Lazada Checker

Use the local parser for Lazada URL metadata checks:

```bash
python3 "{baseDir}/scripts/url_parser.py" "https://www.lazada.vn/products/sample-i123456789-s987654321.html" --json
```

Output fields include:

- `item_id`
- `seller_id`
- `slug`
- `host`
- `market`
- `host_type`
- `is_short_url`
- `short_code`
- `url_type`
- `canonical_product_url`

Workflow:

1. Run parser on the user URL.
2. Return only requested fields, or full JSON when asked.
3. For short links (`s.lazada.*`), explain they cannot be expanded offline in v1.

If URL is not Lazada or malformed, script exits with `Invalid input: ...`.
