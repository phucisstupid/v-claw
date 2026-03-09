---
name: receipt-parser-vn
description: Parse Vietnamese receipt text (including OCR-pasted text) into merchant/date/items/totals with practical heuristics.
---

# Receipt Parser VN

Use the text-first parser for pasted receipt text:

```bash
python3 "{baseDir}/scripts/receipt_parser.py" --text "CHAO CAFE\nTong cong 85.000" --json
```

Or from file:

```bash
python3 "{baseDir}/scripts/receipt_parser.py" --file /path/to/receipt.txt --json
```

Output fields include:

- `merchant`
- `date`
- `items`
- `items[].qty`
- `subtotal`
- `vat`
- `service_charge`
- `totals_detected`
- `total`
- `warnings`

Workflow:

1. Ask user for OCR text/pasted receipt text (or a text file path).
2. Run parser and return structured JSON fields needed by the user.
3. Flag that parsing is heuristic and should be verified against receipt.

This v1 is text-only and does not run image OCR.
