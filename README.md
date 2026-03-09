# vietnam-claw

`vietnam-claw` is an OpenClaw Vietnam skill pack focused on durable Vietnam-first workflows built from open APIs, public data, or reliable local logic.

## Stable core (prioritized)

- `vietqr`: stable local VietQR payment URL builder
- `bill-split-vn`: stable local bill split + settlement calculator
- `receipt-parser-vn`: stable text-first receipt parser
- `vn-phone`: stable VN phone normalization/validation
- `public-holiday-vn`: Vietnam public holiday lookup (no-key public API)
- `viet-geo`: offline VN province/city normalization + metadata match
- `weather-vn`: Vietnam weather lookup via no-key Open-Meteo APIs

## Best-effort / lower priority

Marketplace-facing skills remain available but are de-emphasized for core reliability:

- `shopee-checker`
- `lazada-checker`
- `price-compare-vn`

These are still useful for URL parsing and metadata shaping, but live commerce data collection/scraping is intentionally out of scope.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for shipped status, priority direction, and explicit best-effort limits.

## Clone

```bash
git clone https://github.com/phucisstupid/vietnam-claw.git
cd vietnam-claw
```

## Use with OpenClaw

OpenClaw loads workspace skills from `<workspace>/skills`.

If this repo is the workspace, nothing else is required.

If you keep the repo somewhere else, add its `skills/` directory to `skills.load.extraDirs` in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["/absolute/path/to/vietnam-claw/skills"]
    }
  }
}
```

Start a new OpenClaw turn after cloning or updating the pack.

## Quick script checks

```bash
python3 skills/vietqr/scripts/vietqr.py --bank VCB --account 0123456789 --amount 150000 --note "thanh toan"
python3 skills/bill-split-vn/scripts/bill_split.py --total 450000 --people "An,Binh,Chi" --paid "An=450000" --json
python3 skills/receipt-parser-vn/scripts/receipt_parser.py --text $'CHAO CAFE\nTra dao 35.000\nBanh mi 50.000\nTong cong 85.000' --json
python3 skills/vn-phone/scripts/vn_phone.py "0909 123 456" --json
python3 skills/public-holiday-vn/scripts/public_holiday_vn.py --year 2026 --from-date 2026-03-10 --limit 5 --json
python3 skills/viet-geo/scripts/viet_geo.py --query "tp hcm" --json
python3 skills/weather-vn/scripts/weather_vn.py --location "Da Nang" --days 3 --json
```

Notes:

- `viet-geo` works fully offline from bundled public data.
- `public-holiday-vn` and `weather-vn` require live network access to their no-key public APIs.
