---
name: vietqr
description: Generate VietQR payment image URLs for Vietnamese bank transfers from bank/account details. Use when users ask to create a VietQR link, return a markdown QR preview, or validate VietQR bank/account/amount input.
---

# VietQR

Use the bundled script when the user wants a VietQR payment link or markdown QR preview:

```bash
python3 "{baseDir}/scripts/vietqr.py" --bank <bank> --account <account>
```

Optional flags:

- `--amount <positive_int|k_suffix>` (examples: `10000`, `10k`, `25K`, `2.5k`)
- `--note "<transfer note>"`
- `--account-name "<account holder>"`
- `--template <template>` (default: `compact2`)
- `--markdown` (print `![VietQR](...)`)

Bank aliases already handled by the script include common shortcuts for many Vietnam banks, such as `mb`, `vcb`, `ctg`, `bidv`, `agb`, `tcb`, `acb`, `tpb`, `vpb`, `stb`, `hdb`, `vib`, `ocb`, `shb`, `msb`, `sea`, `eib`, `ab`, `pvb`, `nab`, `bab`, `lpb`, `klb`, and `vab`.

Workflow:

1. Ask only for the missing bank, account, amount, or note fields needed for the user's request.
2. Run the script instead of hand-building the URL.
3. Return the generated URL directly, or the markdown image form when the user wants something they can paste into chat/docs.

If the script exits with `Invalid input: ...`, return that reason clearly and ask only for the incorrect field.
