---
name: public-holiday-vn
description: Fetch Vietnam public holidays and upcoming holiday windows from a no-key public API. Use when users ask if a date is a holiday or what VN holidays are coming next.
---

# Public Holiday VN

Use the bundled script for Vietnam public holiday lookups:

```bash
python3 "{baseDir}/scripts/public_holiday_vn.py" --year 2026 --json
```

Common usage:

- `--year <yyyy>`: fetch holidays for one year (default: current year)
- `--from-date <yyyy-mm-dd>`: filter upcoming holidays from a date (default: today)
- `--limit <n>`: max upcoming entries (default: 5)
- `--json`: print structured JSON

Workflow:

1. Collect `year` and optional `from-date` when users ask for upcoming holidays.
2. Run the script; it calls Nager.Date public holidays API for `VN` (no API key).
3. Return holiday name/date and the upcoming subset.
4. If the API is unavailable, report the fetch failure and ask to retry.

Scope note: data coverage follows the upstream public dataset and may label substitute holidays differently by year.
