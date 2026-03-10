# vietnam-claw

`vietnam-claw` is an OpenClaw Vietnam skill pack focused on durable Vietnam-first workflows built from open APIs, public data, or reliable local logic.

## Included skills

- `vietqr`
- `bill-split-vn`
- `receipt-parser-vn`
- `vn-phone`
- `public-holiday-vn`
- `viet-geo`
- `fuel-price-vn`
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

## Roadmap

See [ROADMAP.md](ROADMAP.md) for priority direction and best-effort limits.

## Install for OpenClaw

OpenClaw loads skills from `<workspace>/skills` and from extra directories configured in `~/.openclaw/openclaw.json`.

### Option A — clone into the active OpenClaw workspace

If this repo lives directly inside the active OpenClaw workspace and the skills are under `<workspace>/skills`, no extra config is needed.

### Option B — keep the repo anywhere and load it via config

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

Start a new OpenClaw turn after cloning or updating the pack.

## Copy-paste prompt for an agent

If you want another agent to install this pack for you, copy-paste this directly:

```text
Install the Vietnam skill pack from https://github.com/phucisstupid/v-claw.git into my OpenClaw setup.

Do this automatically if you have file access:
1. Clone the repo to ~/Documents/vietnam-claw if it does not exist.
2. If it already exists, update it with git pull --ff-only.
3. Ensure ~/.openclaw/openclaw.json exists.
4. Add ~/Documents/vietnam-claw/skills to skills.load.extraDirs if it is missing.
5. Preserve any existing config entries and avoid duplicate paths.
6. Tell me when installation is complete.

Do not ask me to edit the config manually unless you truly cannot access the file.
```

## Agent install behavior

If an agent is asked to install this pack and already has file access, it should:

1. Clone or update the repo locally.
2. Ensure `~/.openclaw/openclaw.json` exists.
3. Add the repo's `skills/` path to `skills.load.extraDirs` if missing.
4. Avoid duplicating the same path.
5. Tell the user the pack is ready and that a new turn or restart may be needed for skill discovery.

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
