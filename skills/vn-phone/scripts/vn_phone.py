#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re

_VALID_VN_RE = re.compile(r"^0\d{8,10}$")
_MOBILE_HINT_RE = re.compile(r"^0(?:3|5|7|8|9)\d{8}$")


def _clean_input(phone: str) -> str:
    return re.sub(r"[^0-9+]", "", phone.strip())


def normalize_vn_phone(phone: str) -> dict[str, str | bool | None]:
    if not phone or not phone.strip():
        raise ValueError("Phone number is required")

    cleaned = _clean_input(phone)
    if not cleaned:
        raise ValueError("Phone number is required")

    if cleaned.startswith("+"):
        if not cleaned.startswith("+84"):
            raise ValueError("Only Vietnam country code +84 is supported")
        local = "0" + cleaned[3:]
    elif cleaned.startswith("84") and len(cleaned) >= 10:
        local = "0" + cleaned[2:]
    elif cleaned.startswith("0"):
        local = cleaned
    elif cleaned.isdigit() and len(cleaned) in (9, 10):
        # Common user input without the leading 0.
        local = "0" + cleaned
    else:
        raise ValueError("Not a recognizable Vietnamese phone format")

    if not _VALID_VN_RE.fullmatch(local):
        raise ValueError("Vietnam phone should be 9-11 digits in national format (starting with 0)")

    e164 = "+84" + local[1:]
    if _MOBILE_HINT_RE.fullmatch(local):
        possible_type = "mobile"
    elif len(local) >= 9:
        possible_type = "landline_or_other"
    else:
        possible_type = "unknown"

    return {
        "input": phone,
        "digits_only": re.sub(r"\D", "", phone),
        "normalized_national": local,
        "normalized_e164": e164,
        "possible_type": possible_type,
        "is_valid": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize Vietnamese phone numbers")
    parser.add_argument("phone", help="Vietnamese phone number")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = normalize_vn_phone(args.phone)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
