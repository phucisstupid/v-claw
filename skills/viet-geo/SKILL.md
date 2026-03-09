---
name: viet-geo
description: Normalize and match Vietnamese province/city names with accent-insensitive lookup and local province metadata.
---

# Viet Geo

Use the script to normalize Vietnamese administrative province/city names:

```bash
python3 "{baseDir}/scripts/viet_geo.py" --query "TP HCM" --json
```

Common usage:

- `--query "<text>"`: normalize and best-match a province/city name
- `--top <n>`: return top matches (default: 3)
- `--list`: list all local provinces/cities metadata
- `--region <name>`: filter list by `north`, `central`, or `south`
- `--json`: output JSON

Workflow:

1. Run `--query` with the user text (supports accents, no-accents, abbreviations like `tphcm`, `hn`, `brvt`).
2. Return the best match and short alternatives if confidence is low.
3. Use `--list` when users want a province reference list.

Data source: bundled local JSON (public Vietnamese province/city list) so this skill works offline.
