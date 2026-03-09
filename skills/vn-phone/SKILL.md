---
name: vn-phone
description: Normalize Vietnamese phone numbers to clean +84 and national formats with quick validity checks. Use when users share phone contacts for shipping, ordering, or payment follow-up.
---

# VN Phone

Use the bundled parser when the user provides a Vietnamese phone number and wants it cleaned:

```bash
python3 "{baseDir}/scripts/vn_phone.py" "<phone>" --json
```

Default output fields include:

- `input`
- `digits_only`
- `normalized_national`
- `normalized_e164`
- `possible_type` (`mobile`, `landline_or_other`, `unknown`)
- `is_valid`

Workflow:

1. Run the script on the user-provided number instead of hand-normalizing it.
2. Return only the normalized number(s) the user requested unless they ask for full metadata.
3. If `is_valid=false`, return the reason and ask for a corrected VN phone number.

Accepted input examples:

- `0909 123 456`
- `+84 909 123 456`
- `84909123456`
- `0912-345-678`
