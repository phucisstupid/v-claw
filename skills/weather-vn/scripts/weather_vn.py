#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

_ALIAS_COORDS = {
    "ha noi": (21.0285, 105.8542, "Ha Noi"),
    "hanoi": (21.0285, 105.8542, "Ha Noi"),
    "hn": (21.0285, 105.8542, "Ha Noi"),
    "tp hcm": (10.7769, 106.7009, "Ho Chi Minh"),
    "tphcm": (10.7769, 106.7009, "Ho Chi Minh"),
    "ho chi minh": (10.7769, 106.7009, "Ho Chi Minh"),
    "sai gon": (10.7769, 106.7009, "Ho Chi Minh"),
    "saigon": (10.7769, 106.7009, "Ho Chi Minh"),
    "da nang": (16.0544, 108.2022, "Da Nang"),
    "danang": (16.0544, 108.2022, "Da Nang"),
    "can tho": (10.0452, 105.7469, "Can Tho"),
    "hue": (16.4637, 107.5909, "Hue"),
    "nha trang": (12.2388, 109.1967, "Nha Trang"),
    "da lat": (11.9404, 108.4583, "Da Lat"),
    "vung tau": (10.4114, 107.1362, "Vung Tau"),
    "hai phong": (20.8449, 106.6881, "Hai Phong"),
}

_WEATHER_CODE_MAP = {
    0: "Troi quang",
    1: "It may",
    2: "May vua",
    3: "Nhieu may",
    45: "Suong mu",
    48: "Suong mu dong bang",
    51: "Mua phun nhe",
    53: "Mua phun vua",
    55: "Mua phun nang",
    61: "Mua nhe",
    63: "Mua vua",
    65: "Mua lon",
    71: "Tuyet nhe",
    73: "Tuyet vua",
    75: "Tuyet day",
    80: "Mua rao nhe",
    81: "Mua rao vua",
    82: "Mua rao lon",
    95: "Mua bao dong",
    96: "Mua bao dong kem mua da",
    99: "Bao dong manh kem mua da",
}


def _normalize_text(value: str) -> str:
    lowered = value.strip().lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    no_accent = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return " ".join(no_accent.replace("-", " ").split())


def _fetch_json(url: str, query: dict[str, object], timeout: float = 12.0) -> object:
    full_url = f"{url}?{urlencode(query, doseq=True)}"
    request = Request(
        full_url,
        headers={
            "User-Agent": "vietnam-claw-weather-vn/1.0",
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def geocode_vn_location(location: str) -> dict[str, object]:
    normalized = _normalize_text(location)
    if normalized in _ALIAS_COORDS:
        lat, lon, display_name = _ALIAS_COORDS[normalized]
        return {
            "name": display_name,
            "admin1": None,
            "country_code": "VN",
            "latitude": lat,
            "longitude": lon,
            "source": "local_alias",
        }

    query = {
        "name": location,
        "count": 5,
        "language": "vi",
        "format": "json",
        "countryCode": "VN",
    }

    try:
        payload = _fetch_json(GEOCODE_URL, query)
    except HTTPError as err:
        raise RuntimeError(f"Geocoding API returned HTTP {err.code}") from err
    except URLError as err:
        raise RuntimeError(f"Geocoding API unavailable: {err.reason}") from err
    except TimeoutError as err:
        raise RuntimeError("Geocoding API request timed out") from err
    except json.JSONDecodeError as err:
        raise RuntimeError("Geocoding API returned invalid JSON") from err

    if not isinstance(payload, dict):
        raise RuntimeError("Geocoding response is invalid")

    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise ValueError("No Vietnam location match found")

    first = None
    for item in results:
        if not isinstance(item, dict):
            continue
        if str(item.get("country_code", "")).upper() != "VN":
            continue
        first = item
        break
    if first is None:
        first = results[0] if isinstance(results[0], dict) else None

    if first is None:
        raise ValueError("No valid geocoding result found")

    return {
        "name": first.get("name") or location,
        "admin1": first.get("admin1"),
        "country_code": (first.get("country_code") or "VN").upper(),
        "latitude": first.get("latitude"),
        "longitude": first.get("longitude"),
        "source": "open-meteo-geocoding",
    }


def fetch_weather(lat: float, lon: float, days: int) -> dict[str, object]:
    query = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "Asia/Ho_Chi_Minh",
        "forecast_days": days,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
        ],
    }

    try:
        payload = _fetch_json(FORECAST_URL, query)
    except HTTPError as err:
        raise RuntimeError(f"Forecast API returned HTTP {err.code}") from err
    except URLError as err:
        raise RuntimeError(f"Forecast API unavailable: {err.reason}") from err
    except TimeoutError as err:
        raise RuntimeError("Forecast API request timed out") from err
    except json.JSONDecodeError as err:
        raise RuntimeError("Forecast API returned invalid JSON") from err

    if not isinstance(payload, dict):
        raise RuntimeError("Forecast response is invalid")

    current = payload.get("current")
    daily = payload.get("daily")
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise RuntimeError("Forecast response missing current/daily data")

    dates = daily.get("time") or []
    weather_codes = daily.get("weather_code") or []
    max_temps = daily.get("temperature_2m_max") or []
    min_temps = daily.get("temperature_2m_min") or []
    precip = daily.get("precipitation_sum") or []

    forecast_days: list[dict[str, object]] = []
    for idx, date_text in enumerate(dates):
        if idx >= len(weather_codes) or idx >= len(max_temps) or idx >= len(min_temps) or idx >= len(precip):
            continue
        code = weather_codes[idx]
        description = _WEATHER_CODE_MAP.get(code, "Khong ro")
        forecast_days.append(
            {
                "date": date_text,
                "weather_code": code,
                "description_vi": description,
                "temp_min_c": min_temps[idx],
                "temp_max_c": max_temps[idx],
                "precipitation_mm": precip[idx],
            }
        )

    current_code = current.get("weather_code")
    current_description = _WEATHER_CODE_MAP.get(current_code, "Khong ro")

    return {
        "current": {
            "time": current.get("time") or dt.datetime.now().isoformat(),
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_kmh": current.get("wind_speed_10m"),
            "precipitation_mm": current.get("precipitation"),
            "weather_code": current_code,
            "description_vi": current_description,
        },
        "forecast": forecast_days,
    }


def build_weather_report(location: str, days: int) -> dict[str, object]:
    geo = geocode_vn_location(location)

    lat = geo.get("latitude")
    lon = geo.get("longitude")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise RuntimeError("Location data missing latitude/longitude")

    weather = fetch_weather(float(lat), float(lon), days)

    return {
        "location_query": location,
        "resolved_location": {
            "name": geo.get("name"),
            "admin1": geo.get("admin1"),
            "country_code": geo.get("country_code"),
            "latitude": lat,
            "longitude": lon,
            "source": geo.get("source"),
        },
        "timezone": "Asia/Ho_Chi_Minh",
        "days": days,
        "current": weather["current"],
        "forecast": weather["forecast"],
        "source": "Open-Meteo (no-key APIs)",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vietnam weather lookup using Open-Meteo no-key APIs")
    parser.add_argument("--location", required=True, help="Vietnam location query")
    parser.add_argument("--days", type=int, default=3, help="Forecast days (1-7, default: 3)")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.days < 1 or args.days > 7:
        raise SystemExit("Invalid input: --days must be between 1 and 7")

    try:
        result = build_weather_report(args.location, args.days)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err
    except RuntimeError as err:
        raise SystemExit(f"Fetch error: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    resolved = result["resolved_location"]
    current = result["current"]
    print(f"location: {resolved['name']} ({resolved['country_code']})")
    if resolved.get("admin1"):
        print(f"admin1: {resolved['admin1']}")
    print(f"temperature_now_c: {current['temperature_c']}")
    print(f"condition: {current['description_vi']}")
    print("forecast:")
    for item in result["forecast"]:
        print(
            f"- {item['date']}: {item['description_vi']}, "
            f"{item['temp_min_c']}..{item['temp_max_c']} C, rain {item['precipitation_mm']} mm"
        )


if __name__ == "__main__":
    main()
