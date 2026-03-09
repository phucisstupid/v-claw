# vietnam-claw

`vietnam-claw` is a small OpenClaw Vietnam skill pack. Clone it into an OpenClaw workspace, or point OpenClaw at its `skills/` directory, and the bundled skills are ready to use.

## Included skills

- `vietqr`: build VietQR payment image URLs from bank, account, amount, and note details
- `shopee-checker`: parse Shopee product URLs into `shop_id`, `item_id`, slug, host, and related metadata

## Layout

```text
skills/
  vietqr/
    SKILL.md
    scripts/vietqr.py
  shopee-checker/
    SKILL.md
    scripts/url_parser.py
```

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
python3 skills/vietqr/scripts/vietqr.py --bank VCB --account 0123456789 --amount 25K --note "thanh toan"
python3 skills/vietqr/scripts/vietqr.py --bank VCB --account 0123456789 --amount 2.5k --note "thanh toan"
python3 skills/vietqr/scripts/vietqr.py --bank BIDV --account 0123456789 --amount 50000 --note "test"
python3 skills/vietqr/scripts/vietqr.py --bank VPB --account 0123456789 --amount 50000 --note "test"
python3 skills/shopee-checker/scripts/url_parser.py "https://shopee.vn/ao-thun-basic-i.12345678.987654321" --json
```

Supported VietQR bank aliases now include many common VN banks, for example: `mb`, `vcb`, `ctg`, `bidv`, `agb`, `tcb`, `acb`, `tpb`, `vpb`, `stb`, `hdb`, `vib`, `ocb`, `shb`, `msb`, `sea`, `eib`, `ab`, `pvb`, `nab`, `bab`, `lpb`, `klb`, and `vab`.
