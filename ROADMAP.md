# Vietnam Claw Roadmap

## Shipped now

- `vietqr`: stable local VietQR URL builder with VN amount shorthand parsing
- `shopee-checker`: stable local Shopee URL metadata parser
- `bill-split-vn`: v1 equal-split calculator with uneven paid amounts and settlements
- `lazada-checker`: v1 Lazada URL parser (product IDs/slug/market + short-link metadata)
- `price-compare-vn`: v1 best-effort offer normalizer + cheapest VND offer picker
- `receipt-parser-vn`: v1 text-first receipt parser (items/qty/subtotal/VAT/service/total heuristics)

## Next priorities

- Add compact fixture-based CLI tests for each skill (happy path + edge/failure).
- Improve receipt parsing heuristics for noisy OCR and multiline item names.
- Add optional richer normalization fields for comparison outputs (shipping, voucher, final paid).

## Best-effort boundaries

- `lazada-checker` and `shopee-checker`: no network expansion of short links.
- `price-compare-vn`: no live scraping/API fetch; compares only provided metadata/prices.
- `receipt-parser-vn`: no image OCR in v1; text parsing is heuristic and must be verified.
