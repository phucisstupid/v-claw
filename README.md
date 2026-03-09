# vietnam-claw

`vietnam-claw` is a small OpenClaw Vietnam skill pack. Clone it into an OpenClaw workspace, or point OpenClaw at its `skills/` directory, and the bundled skills are ready to use.

## Included skills

- `vietqr`: build VietQR payment image URLs from bank, account, amount, and note details
- `shopee-checker`: parse Shopee product URLs into `shop_id`, `item_id`, slug, host, and related metadata
- `bill-split-vn`: split bill totals across participants and generate settlement transfers
- `lazada-checker`: parse Lazada URLs and extract item/seller identifiers and metadata
- `price-compare-vn`: compare best-effort offers from VN marketplace URLs and normalized metadata
- `receipt-parser-vn`: parse OCR-pasted/text receipts into structured merchant/item/total fields

## Roadmap

See [ROADMAP.md](ROADMAP.md) for current shipped status, next priorities, and explicit best-effort limits.

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
python3 skills/shopee-checker/scripts/url_parser.py "https://shopee.vn/ao-thun-basic-i.12345678.987654321" --json
python3 skills/bill-split-vn/scripts/bill_split.py --total 450000 --people "An,Binh,Chi" --paid "An=450000" --json
python3 skills/lazada-checker/scripts/url_parser.py "https://www.lazada.vn/products/sample-i123456789-s987654321.html" --json
python3 skills/price-compare-vn/scripts/compare.py --input "https://shopee.vn/product/123456/999999" --input '{"marketplace":"lazada","url":"https://www.lazada.vn/products/i123456789-s987654321.html","price":189000}' --json
python3 skills/receipt-parser-vn/scripts/receipt_parser.py --text $'CHAO CAFE\nTra dao 35.000\nBanh mi 50.000\nTong cong 85.000' --json
```

For agent use, keep the script simple and let the skill normalize human phrasing first, such as bank nicknames and shorthand amounts like `10k`.
