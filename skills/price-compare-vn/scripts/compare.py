#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

_AMOUNT_SEP_RE = re.compile(r"^[0-9]{1,3}(?:[.,\s][0-9]{3})+$")
_AMOUNT_UNIT_RE = re.compile(r"^([0-9]+(?:[.,][0-9]+)?)\s*(k|nghin|ngan|tr|trieu)$", re.IGNORECASE)

ROOT = Path(__file__).resolve().parents[3]
SHOPEE_SCRIPT = ROOT / "skills" / "shopee-checker" / "scripts" / "url_parser.py"
LAZADA_SCRIPT = ROOT / "skills" / "lazada-checker" / "scripts" / "url_parser.py"


def _load_parser(script_path: Path, module_name: str, attr_name: str):
    if not script_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, attr_name, None)


parse_shopee_url = _load_parser(SHOPEE_SCRIPT, "shopee_url_parser", "parse_shopee_product_url")
parse_lazada_url = _load_parser(LAZADA_SCRIPT, "lazada_url_parser", "parse_lazada_url")


def parse_price_vnd(value: Any) -> int | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        amount = int(value)
        return amount if amount > 0 else None

    if not isinstance(value, str):
        return None

    raw = value.strip().lower()
    raw = raw.replace("vnd", "").replace("vnđ", "").replace("đ", "").strip()
    if not raw:
        return None

    if raw.isdigit():
        amount = int(raw)
        return amount if amount > 0 else None

    if _AMOUNT_SEP_RE.fullmatch(raw):
        amount = int(re.sub(r"[.,\s]", "", raw))
        return amount if amount > 0 else None

    match = _AMOUNT_UNIT_RE.fullmatch(raw)
    if match:
        number = float(match.group(1).replace(",", "."))
        unit = match.group(2).lower()
        multiplier = 1_000 if unit in {"k", "nghin", "ngan"} else 1_000_000
        amount = int(number * multiplier)
        return amount if amount > 0 else None

    return None


def detect_marketplace(url: str) -> str | None:
    lowered = url.lower()
    if "shopee." in lowered:
        return "shopee"
    if "lazada." in lowered:
        return "lazada"
    return None


def normalize_url_offer(url: str) -> dict[str, Any]:
    market = detect_marketplace(url)
    if market == "shopee" and parse_shopee_url:
        parsed = parse_shopee_url(url)
        return {
            "source_type": "url",
            "marketplace": "shopee",
            "url": parsed.get("canonical_product_url") or parsed.get("normalized_url") or url,
            "product_id": f"{parsed.get('shop_id')}:{parsed.get('item_id')}" if parsed.get("shop_id") and parsed.get("item_id") else None,
            "price_vnd": None,
            "metadata": parsed,
        }

    if market == "lazada" and parse_lazada_url:
        parsed = parse_lazada_url(url)
        product_id = str(parsed.get("item_id")) if parsed.get("item_id") else None
        if parsed.get("seller_id"):
            product_id = f"{product_id}:{parsed.get('seller_id')}"
        return {
            "source_type": "url",
            "marketplace": "lazada",
            "url": parsed.get("canonical_product_url") or parsed.get("normalized_url") or url,
            "product_id": product_id,
            "price_vnd": None,
            "metadata": parsed,
        }

    return {
        "source_type": "url",
        "marketplace": market or "unknown",
        "url": url,
        "product_id": None,
        "price_vnd": None,
        "metadata": {"note": "Unsupported marketplace for local parser in v1"},
    }


def normalize_json_offer(text: str) -> dict[str, Any]:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON input: {err.msg}") from err

    if not isinstance(obj, dict):
        raise ValueError("JSON input must be an object")

    url = obj.get("url")
    market = obj.get("marketplace")
    if not market and isinstance(url, str):
        market = detect_marketplace(url)

    currency = str(obj.get("currency") or "VND").upper()
    raw_price = obj.get("price_vnd", obj.get("price"))
    price_vnd = parse_price_vnd(raw_price) if currency == "VND" else None

    normalized = {
        "source_type": "metadata",
        "marketplace": market or "unknown",
        "url": url,
        "product_id": obj.get("product_id") or obj.get("id"),
        "title": obj.get("title"),
        "price_vnd": price_vnd,
        "currency": currency,
        "metadata": obj,
    }

    if currency != "VND":
        normalized["note"] = "Non-VND price is kept as metadata only in v1"
        return normalized

    if isinstance(url, str):
        url_offer = normalize_url_offer(url)
        normalized["marketplace"] = normalized["marketplace"] if normalized["marketplace"] != "unknown" else url_offer.get("marketplace")
        if not normalized["product_id"]:
            normalized["product_id"] = url_offer.get("product_id")
        normalized["parsed_url_metadata"] = url_offer.get("metadata")

    return normalized


def normalize_input(value: str) -> dict[str, Any]:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Input value is empty")

    if stripped.startswith("{"):
        return normalize_json_offer(stripped)
    return normalize_url_offer(stripped)


def compare_offers(inputs: list[str]) -> dict[str, Any]:
    offers = [normalize_input(raw) for raw in inputs]
    priced = [offer for offer in offers if isinstance(offer.get("price_vnd"), int)]
    cheapest = min(priced, key=lambda o: o["price_vnd"]) if priced else None
    comparison_table = [
        {
            "index": idx + 1,
            "marketplace": offer.get("marketplace"),
            "product_id": offer.get("product_id"),
            "url": offer.get("url"),
            "price_vnd": offer.get("price_vnd"),
            "has_price": isinstance(offer.get("price_vnd"), int),
        }
        for idx, offer in enumerate(offers)
    ]

    notes = [
        "v1 does not fetch live prices from marketplaces; provide price in JSON input when needed",
        "URL-only inputs are parsed for identifiers only",
    ]

    return {
        "offers": offers,
        "summary": {
            "total_offers": len(offers),
            "priced_offers": len(priced),
            "cheapest_offer": cheapest,
            "currency": "VND",
        },
        "comparison_table": comparison_table,
        "notes": notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Best-effort price comparison for VN marketplace links/metadata.")
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Repeat for each offer. Accept URL or JSON object with optional price/price_vnd.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = compare_offers(args.input)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    summary = result["summary"]
    print(f"offers: {summary['total_offers']}")
    print(f"priced_offers: {summary['priced_offers']}")
    if summary["cheapest_offer"]:
        best = summary["cheapest_offer"]
        print(f"cheapest: {best.get('marketplace')} {best.get('price_vnd')} VND")
    else:
        print("cheapest: unavailable (no VND price provided)")


if __name__ == "__main__":
    main()
