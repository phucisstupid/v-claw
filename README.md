# vietnam-claw

`vietnam-claw` is an OpenClaw Vietnam skill pack focused on durable Vietnam-first workflows built from open APIs, public data, or reliable local logic.

## Stable core

- `vietqr`: stable local VietQR payment URL builder
- `bill-split-vn`: stable local bill split + settlement calculator
- `receipt-parser-vn`: stable text-first receipt parser
- `vn-phone`: stable VN phone normalization/validation
- `public-holiday-vn`: Vietnam public holiday lookup (no-key public API)
- `viet-geo`: offline VN province/city normalization + metadata match
- `fuel-price-vn`: Vietnam fuel price snapshot from a public no-key source

## New utility skills

- `gold-price-vn`
- `bank-rate-vn`
- `interest-rate-vn`
- `tax-pit-vn`
- `net-gross-vn`
- `address-parser-vn`
- `license-plate-vn`
- `electricity-price-vn`
- `water-bill-vn`
- `telecom-vn`
- `food-calorie-vn`

## Removed marketplace skills

These were intentionally removed from the pack:

- `shopee-checker`
- `lazada-checker`
- `price-compare-vn`

## Roadmap

See [ROADMAP.md](ROADMAP.md) for shipped status, priority direction, and explicit best-effort limits.

## Install for OpenClaw

OpenClaw loads skills from `<workspace>/skills` and from any extra directories configured in `~/.openclaw/openclaw.json`.

### Option A — easiest: clone into the active OpenClaw workspace

If this repo lives directly inside the active OpenClaw workspace and the skills are under `<workspace>/skills`, no extra config is needed.

### Option B — recommended when keeping the repo outside the workspace

Clone the repo anywhere, then point OpenClaw at its `skills/` directory in config.

```bash
git clone https://github.com/phucisstupid/vietnam-claw.git
cd vietnam-claw
```

Add this to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "load": {
      "extraDirs": [
        "/absolute/path/to/vietnam-claw/skills"
      ]
    }
  }
}
```

Then start a new OpenClaw turn after cloning or updating the pack.

## Agent install recipe

If an OpenClaw agent is asked to install this pack, it should not ask the user to do the wiring manually if it already has file access.

Preferred workflow for the agent:

1. Clone or update the repo locally.
2. Ensure `~/.openclaw/openclaw.json` exists.
3. Add the repo's `skills/` path to `skills.load.extraDirs` if missing.
4. Avoid duplicating the same path.
5. Tell the user the pack is ready and that a new turn/restart may be needed for skill discovery.

Concrete example:

```bash
mkdir -p ~/.openclaw
if [ ! -d ~/Documents/vietnam-claw/.git ]; then
  git clone https://github.com/phucisstupid/vietnam-claw.git ~/Documents/vietnam-claw
else
  git -C ~/Documents/vietnam-claw pull --ff-only
fi
```

If the config file does not exist, create:

```json
{
  "skills": {
    "load": {
      "extraDirs": [
        "/Users/<you>/Documents/vietnam-claw/skills"
      ]
    }
  }
}
```

If the config file already exists, merge this path into `skills.load.extraDirs` rather than replacing existing entries.

## Quick checks

```bash
python3 skills/vietqr/scripts/vietqr.py --bank VCB --account 0123456789 --amount 150000 --note "thanh toan"
python3 skills/bill-split-vn/scripts/bill_split.py --total 450000 --people "An,Binh,Chi" --paid "An=450000" --json
python3 skills/receipt-parser-vn/scripts/receipt_parser.py --text $'CHAO CAFE\nTra dao 35.000\nBanh mi 50.000\nTong cong 85.000' --json
python3 skills/vn-phone/scripts/vn_phone.py "0909 123 456" --json
python3 skills/public-holiday-vn/scripts/public_holiday_vn.py --year 2026 --from-date 2026-03-10 --limit 5 --json
python3 skills/viet-geo/scripts/viet_geo.py --query "tp hcm" --json
python3 skills/fuel-price-vn/scripts/fuel_price_vn.py --json
python3 skills/bank-rate-vn/scripts/bank_rate_vn.py --currency USD --json
python3 skills/tax-pit-vn/scripts/tax_pit_vn.py --gross 30000000 --dependents 1 --json
python3 skills/address-parser-vn/scripts/address_parser_vn.py "Nguyen Van A, 12 Nguyen Hue, Phuong Ben Nghe, Quan 1, TP HCM, 0909123456" --json
```

## Notes

- `viet-geo` works fully offline from bundled public data.
- `public-holiday-vn`, `fuel-price-vn`, `bank-rate-vn`, and some browser-driven skills require live network access.
- `gold-price-vn` currently works best through browser rendering because the source page is client-rendered.
- Utility estimators such as electricity, water, tax, gross/net, and calories are practical heuristics and may need local rule updates over time.
