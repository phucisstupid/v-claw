---
name: shopee-checker
description: Parse Shopee product URLs and extract identifiers such as shop_id, item_id, slug, host, region, and short-link status. Use when users share Shopee links and ask for quick product/shop metadata checks.
---

# Shopee Checker

Use the bundled parser when a user shares a Shopee link and wants identifiers or a quick metadata check:

```bash
python3 "{baseDir}/scripts/url_parser.py" "<shopee_url>" --json
```

Default output fields include:

- `shop_id`
- `item_id`
- `slug`
- `host`
- `market`
- `host_type`
- `is_short_url`
- `url_type`
- `is_product_url`
- `canonical_product_url`

Workflow:

1. Run the parser on the user-provided URL instead of extracting IDs manually.
2. Return the parsed fields the user asked for, keeping the output brief unless they want the full JSON.
3. If `shop_id` and `item_id` remain empty, say that the URL was recognized as Shopee but did not contain a direct product identifier.

The parser now supports more Shopee URL shapes:

- direct product path (`/product/<shop_id>/<item_id>`)
- slug style (`/<slug>-i.<shop_id>.<item_id>`)
- query-id style (`shopid` + `itemid`, including snake/camel variants)
- app/universal deeplink IDs embedded in query values

If the URL is not Shopee or is malformed, the script exits with `Invalid input: ...`; return that reason and ask for a valid Shopee product URL.
