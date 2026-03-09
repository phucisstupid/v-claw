---
name: weather-vn
description: Get Vietnam weather forecasts using no-key Open-Meteo APIs with Vietnamese location-friendly matching.
---

# Weather VN

Use the script for Vietnam weather lookups:

```bash
python3 "{baseDir}/scripts/weather_vn.py" --location "Da Nang" --days 3 --json
```

Common usage:

- `--location "<vn place>"`: required Vietnamese location text
- `--days <1-7>`: forecast days (default: 3)
- `--json`: print structured JSON

Workflow:

1. Normalize user location text (accent-insensitive aliases are supported, e.g. `tphcm`, `ha noi`, `hue`).
2. Script geocodes with Open-Meteo geocoding API constrained to `VN`.
3. Script fetches current weather + daily forecast via Open-Meteo forecast API.
4. Return concise conditions and temperatures; include API error if fetch fails.

Scope note: this skill depends on live network/API availability.
