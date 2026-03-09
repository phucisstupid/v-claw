#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from urllib.parse import urlencode, quote

BASE_URL = "https://img.vietqr.io/image"
BANK_ALIASES = {
    "mbbank": "MBBank",
    "mb": "MBBank",
    "vietcombank": "Vietcombank",
    "vcb": "Vietcombank",
    "techcombank": "Techcombank",
    "tcb": "Techcombank",
    "acb": "ACB",
    "tpbank": "TPBank",
    "tpb": "TPBank",
}
_BANK_RE = re.compile(r"^[A-Za-z0-9]{2,32}$")
_ACCOUNT_RE = re.compile(r"^[0-9]{6,19}$")
_TEMPLATE_RE = re.compile(r"^[A-Za-z0-9_-]{2,32}$")


def build_vietqr_url(
    bank: str,
    account: str,
    amount: int | None = None,
    note: str | None = None,
    account_name: str | None = None,
    template: str = "compact2",
) -> str:
    bank = normalize_bank(bank)
    account = validate_account(account)
    template = validate_template(template)
    path = f"{BASE_URL}/{quote(bank)}-{quote(account)}-{quote(template)}.png"

    params: dict[str, str] = {}
    if amount is not None:
        params["amount"] = str(validate_amount(amount))
    if note:
        params["addInfo"] = note.strip()
    if account_name:
        params["accountName"] = account_name.strip()

    if not params:
        return path
    return f"{path}?{urlencode(params)}"


def normalize_bank(bank: str) -> str:
    raw = bank.strip()
    if not raw:
        raise ValueError("Bank is required")

    alias_key = re.sub(r"[^a-z0-9]+", "", raw.lower())
    if alias_key in BANK_ALIASES:
        return BANK_ALIASES[alias_key]

    if not _BANK_RE.fullmatch(raw):
        raise ValueError("Bank must be 2-32 letters/digits, or a supported alias")
    return raw


def validate_account(account: str) -> str:
    value = account.strip()
    if not _ACCOUNT_RE.fullmatch(value):
        raise ValueError("Account must be numeric and 6-19 digits long")
    return value


def validate_template(template: str) -> str:
    value = template.strip()
    if not _TEMPLATE_RE.fullmatch(value):
        raise ValueError("Template must be 2-32 chars: letters, numbers, '_' or '-'")
    return value


def validate_amount(amount: int) -> int:
    if amount <= 0:
        raise ValueError("Amount must be a positive integer")
    return amount


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate VietQR image URLs.")
    parser.add_argument("--bank", required=True, help="Bank code or bank name alias, e.g. MBBank")
    parser.add_argument("--account", required=True, help="Bank account number")
    parser.add_argument("--amount", type=int, default=None, help="Transfer amount")
    parser.add_argument("--note", default=None, help="Transfer note / addInfo")
    parser.add_argument("--account-name", default=None, help="Account holder name")
    parser.add_argument("--template", default="compact2", help="QR template, e.g. compact2")
    parser.add_argument("--markdown", action="store_true", help="Print markdown image preview")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        url = build_vietqr_url(
            bank=args.bank,
            account=args.account,
            amount=args.amount,
            note=args.note,
            account_name=args.account_name,
            template=args.template,
        )
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.markdown:
        print(f"![VietQR]({url})")
    else:
        print(url)


if __name__ == "__main__":
    main()
