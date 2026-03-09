#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from urllib.parse import parse_qs, urlparse

_MARKET_RE = re.compile(r"lazada\.(?P<market>[a-z.]+)$", re.IGNORECASE)
_ITEM_SELLER_RE = re.compile(r"(?:^|[-_/])i(?P<item_id>\d+)(?:-s(?P<seller_id>\d+))?(?:$|[./?&#-])", re.IGNORECASE)


def _ensure_scheme(url: str) -> str:
    text = url.strip()
    if "://" in text:
        return text
    return f"https://{text}"


def _is_lazada_host(host: str) -> bool:
    if not host:
        return False
    if host.startswith("s.lazada."):
        return True
    return host == "lazada.vn" or ".lazada." in host or host.startswith("lazada.")


def _extract_market(host: str) -> str | None:
    match = _MARKET_RE.search(host)
    if not match:
        return None
    return match.group("market")


def _extract_ids_from_path(path: str) -> tuple[int | None, int | None, str | None]:
    clean_path = path.strip("/")
    slug = None
    if clean_path:
        parts = clean_path.split("/")
        candidate = parts[-1]
        if candidate.endswith(".html"):
            candidate = candidate[: -len(".html")]
        slug_part = candidate.split("-i", 1)[0].strip()
        if slug_part and slug_part != candidate and slug_part.lower() != "products":
            slug = slug_part

    match = _ITEM_SELLER_RE.search(path)
    if not match:
        return None, None, slug
    item_id = int(match.group("item_id"))
    seller_group = match.group("seller_id")
    seller_id = int(seller_group) if seller_group else None
    return item_id, seller_id, slug


def _extract_ids_from_query(parsed_query: dict[str, list[str]]) -> tuple[int | None, int | None]:
    item_keys = ("item_id", "itemid", "id")
    seller_keys = ("seller_id", "sellerid", "shop_id", "shopid")

    item_id = None
    seller_id = None

    for key in item_keys:
        values = parsed_query.get(key, [])
        if values and values[0].strip().isdigit():
            item_id = int(values[0].strip())
            break

    for key in seller_keys:
        values = parsed_query.get(key, [])
        if values and values[0].strip().isdigit():
            seller_id = int(values[0].strip())
            break

    return item_id, seller_id


def _canonical_url(host: str | None, item_id: int | None, seller_id: int | None) -> str | None:
    if not host or item_id is None:
        return None
    if seller_id is not None:
        return f"https://{host}/products/i{item_id}-s{seller_id}.html"
    return f"https://{host}/products/i{item_id}.html"


def _extract_short_code(path: str) -> str | None:
    clean = path.strip("/")
    if not clean:
        return None
    if clean.startswith("s."):
        return clean
    parts = clean.split("/")
    if len(parts) >= 2 and parts[0].lower() == "s":
        return parts[1]
    return None


def parse_lazada_url(url: str) -> dict[str, str | int | bool | None]:
    if not url or not url.strip():
        raise ValueError("URL is required")

    prepared = _ensure_scheme(url)
    parsed = urlparse(prepared)
    host = parsed.netloc.lower().split(":", 1)[0]

    if not _is_lazada_host(host):
        raise ValueError("Not a Lazada URL")

    is_short = host.startswith("s.lazada.")
    market = _extract_market(host)
    query = {k.lower(): v for k, v in parse_qs(parsed.query).items()}
    short_code = _extract_short_code(parsed.path) if is_short else None

    item_id, seller_id, slug = _extract_ids_from_path(parsed.path)
    if item_id is None:
        q_item, q_seller = _extract_ids_from_query(query)
        item_id = q_item
        seller_id = seller_id if seller_id is not None else q_seller

    result: dict[str, str | int | bool | None] = {
        "original_url": url,
        "normalized_url": f"{parsed.scheme}://{parsed.netloc}{parsed.path}" + (f"?{parsed.query}" if parsed.query else ""),
        "host": host,
        "market": market,
        "host_type": "short" if is_short else "marketplace",
        "is_short_url": is_short,
        "url_type": "short_link" if is_short else "unknown_lazada",
        "is_product_url": False,
        "short_code": short_code,
        "item_id": item_id,
        "seller_id": seller_id,
        "slug": slug,
        "canonical_product_url": _canonical_url(host, item_id, seller_id),
        "resolution_note": "Short links cannot be expanded offline; IDs may be missing without the final redirected URL." if is_short else None,
    }

    if item_id is not None:
        result["is_product_url"] = True
        result["url_type"] = "product_or_query_ids"

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse Lazada product URL metadata.")
    parser.add_argument("url", help="Lazada URL")
    parser.add_argument("--json", action="store_true", help="Print as JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = parse_lazada_url(args.url)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
