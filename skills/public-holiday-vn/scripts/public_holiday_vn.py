#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

BASE_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/VN"


def _parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as err:
        raise ValueError("Date must be in YYYY-MM-DD format") from err


def _fetch_json(url: str, timeout: float = 10.0) -> object:
    request_headers = {
        "User-Agent": "vietnam-claw-public-holiday-vn/1.0",
        "Accept": "application/json",
    }
    from urllib.request import Request

    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=timeout) as response:
        content = response.read().decode("utf-8")
    return json.loads(content)


def fetch_holidays(year: int) -> list[dict[str, object]]:
    if year < 1900 or year > 2100:
        raise ValueError("year must be in range 1900..2100")

    url = BASE_URL.format(year=year)
    try:
        payload = _fetch_json(url)
    except HTTPError as err:
        raise RuntimeError(f"Holiday API returned HTTP {err.code}") from err
    except URLError as err:
        raise RuntimeError(f"Holiday API unavailable: {err.reason}") from err
    except TimeoutError as err:
        raise RuntimeError("Holiday API request timed out") from err
    except json.JSONDecodeError as err:
        raise RuntimeError("Holiday API returned invalid JSON") from err

    if not isinstance(payload, list):
        raise RuntimeError("Holiday API response shape is unexpected")

    holidays: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        date_value = item.get("date")
        local_name = item.get("localName")
        name = item.get("name")
        if not isinstance(date_value, str):
            continue

        try:
            parsed_date = dt.date.fromisoformat(date_value)
        except ValueError:
            continue

        holidays.append(
            {
                "date": parsed_date.isoformat(),
                "local_name": local_name,
                "name": name,
                "types": item.get("types", []),
                "global": bool(item.get("global", True)),
            }
        )

    holidays.sort(key=lambda h: h["date"])
    return holidays


def build_result(year: int, from_date: dt.date, limit: int) -> dict[str, object]:
    holidays = fetch_holidays(year)
    upcoming = [h for h in holidays if str(h["date"]) >= from_date.isoformat()][:limit]

    return {
        "country_code": "VN",
        "year": year,
        "source": "Nager.Date public API",
        "from_date": from_date.isoformat(),
        "total_holidays": len(holidays),
        "upcoming_count": len(upcoming),
        "upcoming": upcoming,
        "holidays": holidays,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vietnam public holiday lookup (no-key public API)")
    parser.add_argument("--year", type=int, default=dt.date.today().year, help="Year to fetch holidays for")
    parser.add_argument(
        "--from-date",
        default=dt.date.today().isoformat(),
        help="Upcoming filter start date (YYYY-MM-DD), default today",
    )
    parser.add_argument("--limit", type=int, default=5, help="Max upcoming holidays to return (default: 5)")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.limit < 1:
        raise SystemExit("Invalid input: --limit must be >= 1")

    try:
        from_date = _parse_date(args.from_date)
        result = build_result(year=args.year, from_date=from_date, limit=args.limit)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err
    except RuntimeError as err:
        raise SystemExit(f"Fetch error: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"country_code: {result['country_code']}")
    print(f"year: {result['year']}")
    print(f"from_date: {result['from_date']}")
    print(f"total_holidays: {result['total_holidays']}")
    print("upcoming:")
    for holiday in result["upcoming"]:
        name = holiday["local_name"] or holiday["name"]
        print(f"- {holiday['date']}: {name}")


if __name__ == "__main__":
    main()
