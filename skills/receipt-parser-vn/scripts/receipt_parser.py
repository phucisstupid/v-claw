#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_AMOUNT_TOKEN_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[.,\s]\d{3})+|\d+)(?:\s?(?:vnd|vnđ|đ))?(?!\d)", re.IGNORECASE)
_DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
_DATE_ONLY_RE = re.compile(r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$")

_TOTAL_HINTS = (
    "tong cong",
    "tổng cộng",
    "thanh toan",
    "thành tiền",
    "can tra",
    "cần trả",
    "total",
    "grand total",
)
_SUBTOTAL_HINTS = (
    "tam tinh",
    "tạm tính",
    "subtotal",
    "sub total",
    "truoc thue",
    "trước thuế",
)
_VAT_HINTS = (
    "vat",
    "thue gtgt",
    "thuế gtgt",
    "thue",
    "tax",
)
_SERVICE_HINTS = (
    "phi phuc vu",
    "phí phục vụ",
    "service charge",
    "svc",
)
_QTY_PATTERNS = (
    re.compile(r"(?i)\b(?P<qty>\d+)\s*[x×]\s*"),
    re.compile(r"(?i)\b[x×]\s*(?P<qty>\d+)\b"),
    re.compile(r"(?i)\bsl\s*[:=]?\s*(?P<qty>\d+)\b"),
)


def parse_amount_token(token: str) -> int:
    cleaned = re.sub(r"[\s.,]", "", token)
    if not cleaned.isdigit():
        raise ValueError("Amount token is invalid")
    return int(cleaned)


def extract_last_amount_match(line: str) -> re.Match[str] | None:
    matches = list(_AMOUNT_TOKEN_RE.finditer(line))
    if not matches:
        return None
    for match in reversed(matches):
        token = match.group(1)
        compact = re.sub(r"[\s.,]", "", token)
        # Ignore tiny numeric fragments like store branch numbers in item parsing.
        if token.isdigit() and len(compact) < 4:
            continue
        return match
    return None


def extract_last_amount(line: str) -> int | None:
    match = extract_last_amount_match(line)
    if not match:
        return None
    try:
        return parse_amount_token(match.group(1))
    except ValueError:
        return None


def _contains_any(line: str, hints: tuple[str, ...]) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in hints)


def _extract_quantity(name_part: str) -> tuple[int, str]:
    qty = 1
    cleaned_name = name_part.strip()

    for pattern in _QTY_PATTERNS:
        found = pattern.search(cleaned_name)
        if not found:
            continue
        try:
            parsed_qty = int(found.group("qty"))
        except (ValueError, TypeError):
            continue
        if parsed_qty <= 0:
            continue
        qty = parsed_qty
        cleaned_name = pattern.sub(" ", cleaned_name).strip(" .:-")
        break

    return qty, cleaned_name


def parse_receipt_text(text: str) -> dict[str, object]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Receipt text is empty")

    merchant = lines[0]
    receipt_date = None
    totals: list[dict[str, object]] = []
    items: list[dict[str, object]] = []

    subtotal = None
    total_amount = None
    vat_amount = None
    service_charge = None

    for idx, line in enumerate(lines):
        if idx == 0:
            continue

        if receipt_date is None:
            date_match = _DATE_RE.search(line)
            if date_match:
                receipt_date = date_match.group(1)
        if _DATE_ONLY_RE.fullmatch(line):
            continue

        amount_match = extract_last_amount_match(line)
        if amount_match is None:
            continue

        amount = parse_amount_token(amount_match.group(1))

        if _contains_any(line, _TOTAL_HINTS):
            total_amount = amount
            totals.append({"type": "total", "label": line, "amount": amount})
            continue

        if _contains_any(line, _SUBTOTAL_HINTS):
            subtotal = amount
            totals.append({"type": "subtotal", "label": line, "amount": amount})
            continue

        if _contains_any(line, _SERVICE_HINTS):
            service_charge = amount
            totals.append({"type": "service_charge", "label": line, "amount": amount})
            continue

        if _contains_any(line, _VAT_HINTS):
            vat_amount = amount
            totals.append({"type": "vat", "label": line, "amount": amount})
            continue

        if len(line) < 4:
            continue

        name_part = line[: amount_match.start()].strip(" .:-")
        if not name_part:
            continue

        qty, name = _extract_quantity(name_part)
        if not name:
            name = name_part

        unit_price = amount // qty if qty > 0 and amount % qty == 0 else None
        items.append({
            "name": name,
            "qty": qty,
            "line_total": amount,
            "unit_price": unit_price,
        })

    items_subtotal = sum(item["line_total"] for item in items)
    if subtotal is None and items:
        subtotal = items_subtotal
    if total_amount is None and totals:
        # fall back to the last detected labeled amount (best effort)
        total_amount = totals[-1]["amount"]

    result = {
        "merchant": merchant,
        "date": receipt_date,
        "currency": "VND",
        "items": items,
        "items_count": len(items),
        "items_subtotal": items_subtotal,
        "subtotal": subtotal,
        "vat": vat_amount,
        "service_charge": service_charge,
        "totals_detected": totals,
        "total": total_amount,
        "warnings": [
            "Text-first heuristic parser; verify values against the original receipt",
            "Image OCR is not included in v1",
        ],
    }

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse VN receipt text into structured data.")
    parser.add_argument("--text", help="Raw receipt text")
    parser.add_argument("--file", help="Path to UTF-8 text file with receipt content")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.text and not args.file:
        raise SystemExit("Invalid input: --text or --file is required")

    try:
        raw_text = args.text if args.text else Path(args.file).read_text(encoding="utf-8")
        result = parse_receipt_text(raw_text)
    except FileNotFoundError:
        raise SystemExit("Invalid input: receipt file not found")
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"merchant: {result['merchant']}")
    print(f"date: {result['date']}")
    print(f"items_count: {result['items_count']}")
    print(f"subtotal: {result['subtotal']}")
    print(f"vat: {result['vat']}")
    print(f"service_charge: {result['service_charge']}")
    print(f"total: {result['total']}")


if __name__ == "__main__":
    main()
