# Vietnam Claw Roadmap

## Stable core shipped now

- `vietqr`: stable local VietQR URL builder with VN amount shorthand parsing
- `bill-split-vn`: stable local split/settlement logic
- `receipt-parser-vn`: stable text-first receipt parser (heuristic, no OCR)
- `vn-phone`: stable VN phone normalization and validation
- `public-holiday-vn`: VN holiday lookup from no-key public holiday API with upcoming filter
- `viet-geo`: offline VN province/city normalization and metadata matching from bundled public dataset
- `weather-vn`: VN weather forecasts using no-key Open-Meteo geocoding + forecast APIs

## Lower-priority best-effort skills

- `shopee-checker`: local URL parser only
- `lazada-checker`: local URL parser only
- `price-compare-vn`: compares provided metadata/prices only; no live scraping/fetch

These marketplace skills remain supported, but reliability-first roadmap work now prioritizes durable VN utilities over scraping-oriented expansion.

## Next priorities

- Add fixture-based CLI tests for all stable-core skills (happy path + failure path).
- Add lightweight response caching for API-backed skills (`public-holiday-vn`, `weather-vn`) to improve degraded-mode usability.
- Expand `viet-geo` metadata fields with official codes and citation metadata.
- Improve receipt parsing for noisy OCR text while keeping deterministic output schema.

## Reliability boundaries

- API-backed skills (`public-holiday-vn`, `weather-vn`) depend on upstream availability and network.
- `receipt-parser-vn` is heuristic text parsing and must be verified against source receipts.
- Marketplace skills are intentionally best-effort and do not perform scraping in v1.
