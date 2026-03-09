#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, InvalidOperation

_AMOUNT_RE = re.compile(r"^([0-9]+(?:[.,][0-9]+)?)\s*([a-zA-Z\u00C0-\u1EF9\u0111\u0110]+)?$")
_UNIT_MULTIPLIERS = {
    "k": 1_000,
    "nghin": 1_000,
    "ngan": 1_000,
    "tr": 1_000_000,
    "trieu": 1_000_000,
}


def parse_amount(text: str) -> int:
    raw = text.strip().lower()
    raw = raw.replace(" ", "")
    raw = raw.replace("vnd", "").replace("vnđ", "").replace("đ", "")
    if not raw:
        raise ValueError("Amount is required")

    if raw.isdigit():
        amount = int(raw)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount

    if re.fullmatch(r"[0-9]{1,3}(?:[.,][0-9]{3})+", raw):
        amount = int(raw.replace(".", "").replace(",", ""))
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount

    match = _AMOUNT_RE.fullmatch(raw)
    if not match:
        raise ValueError("Amount format is invalid")

    number = match.group(1).replace(",", ".")
    unit = (match.group(2) or "").lower()
    multiplier = _UNIT_MULTIPLIERS.get(unit)
    if multiplier is None:
        raise ValueError("Unsupported unit. Use k/nghin/ngan/tr/trieu")

    try:
        scaled = Decimal(number) * Decimal(multiplier)
    except InvalidOperation as err:
        raise ValueError("Amount format is invalid") from err

    if scaled != scaled.to_integral_value() or scaled <= 0:
        raise ValueError("Amount must resolve to a positive whole VND number")

    return int(scaled)


def parse_people(value: str) -> list[str]:
    names = [part.strip() for part in value.split(",") if part.strip()]
    if not names:
        raise ValueError("At least one participant is required")

    unique_names: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = name.casefold()
        if key in seen:
            raise ValueError(f"Duplicate participant: {name}")
        seen.add(key)
        unique_names.append(name)
    return unique_names


def parse_paid(values: list[str], participants: list[str]) -> dict[str, int]:
    if not values:
        return {}

    normalized_map = {name.casefold(): name for name in participants}
    paid: dict[str, int] = {}

    for raw in values:
        if "=" not in raw:
            raise ValueError(f"Paid entry must be name=amount: {raw}")
        name_part, amount_part = raw.split("=", 1)
        key = name_part.strip().casefold()
        if key not in normalized_map:
            raise ValueError(f"Unknown participant in paid entry: {name_part.strip()}")
        canonical_name = normalized_map[key]
        amount = parse_amount(amount_part)
        paid[canonical_name] = amount

    return paid


def _compute_shares(total: int, participants: list[str]) -> dict[str, int]:
    count = len(participants)
    base = total // count
    remainder = total % count

    shares: dict[str, int] = {}
    for idx, name in enumerate(participants):
        shares[name] = base + (1 if idx < remainder else 0)
    return shares


def _compute_settlements(balances: dict[str, int]) -> list[dict[str, int | str]]:
    debtors = [[name, -balance] for name, balance in balances.items() if balance < 0]
    creditors = [[name, balance] for name, balance in balances.items() if balance > 0]

    settlements: list[dict[str, int | str]] = []
    d_idx = 0
    c_idx = 0
    while d_idx < len(debtors) and c_idx < len(creditors):
        debtor_name, debt = debtors[d_idx]
        creditor_name, credit = creditors[c_idx]
        transfer = min(debt, credit)
        settlements.append({"from": debtor_name, "to": creditor_name, "amount": transfer})

        debt -= transfer
        credit -= transfer
        debtors[d_idx][1] = debt
        creditors[c_idx][1] = credit

        if debt == 0:
            d_idx += 1
        if credit == 0:
            c_idx += 1

    return settlements


def split_bill(total: int, participants: list[str], paid_input: dict[str, int]) -> dict[str, object]:
    shares = _compute_shares(total, participants)
    paid = {name: paid_input.get(name, 0) for name in participants}
    paid_total = sum(paid.values())

    if paid_input and paid_total != total:
        raise ValueError(
            f"Paid amounts must sum to total. paid_total={paid_total}, total={total}"
        )

    balances = {name: paid[name] - shares[name] for name in participants}
    settlements = _compute_settlements(balances) if paid_input else []

    return {
        "total": total,
        "participants": participants,
        "share_per_person": shares,
        "paid_per_person": paid,
        "paid_total": paid_total,
        "balances": balances,
        "settlements": settlements,
        "currency": "VND",
        "note": "settlements empty when no paid entries are provided",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split a Vietnamese bill and compute settlements.")
    parser.add_argument("--total", required=True, help="Bill total, e.g. 450000, 450k, 1.2tr")
    parser.add_argument("--people", required=True, help="Comma-separated participants, e.g. An,Binh,Chi")
    parser.add_argument(
        "--paid",
        action="append",
        default=[],
        help="Paid amount per person as name=amount. Repeat flag for multiple people.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        total = parse_amount(args.total)
        participants = parse_people(args.people)
        paid = parse_paid(args.paid, participants)
        result = split_bill(total, participants, paid)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"total: {result['total']} {result['currency']}")
    print("share_per_person:")
    for name, amount in result["share_per_person"].items():
        print(f"- {name}: {amount}")

    if args.paid:
        print("settlements:")
        settlements = result["settlements"]
        if not settlements:
            print("- none")
        else:
            for row in settlements:
                print(f"- {row['from']} -> {row['to']}: {row['amount']}")


if __name__ == "__main__":
    main()
