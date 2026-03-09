---
name: bill-split-vn
description: Split Vietnamese bill totals across participants and compute settlement transfers when paid amounts are provided.
---

# Bill Split VN

Use the script to split a bill and generate clear per-person settlement:

```bash
python3 "{baseDir}/scripts/bill_split.py" --total 450000 --people "An,Binh,Chi" --paid "An=450000" --json
```

Inputs:

- `--total <amount>` supports plain VND (`450000`) and shorthand (`450k`, `1.2tr`)
- `--people "name1,name2,..."`
- optional repeated `--paid "name=amount"`
- `--json` for structured output

Workflow:

1. Collect bill `total` and participant list.
2. If users also provide paid amounts, include `--paid` entries for those people.
3. Run the script; return `share_per_person` and `settlements`.
4. If paid amounts are provided, they must sum to total; otherwise ask for corrected inputs.

Rounding behavior: when total is not divisible evenly, v1 assigns the remainder (+1 VND each) from the first participant onward.

Scope note: v1 handles equal owed share only, but supports uneven paid amounts for settlement.
