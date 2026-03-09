#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from urllib.parse import parse_qs, urlparse

_SHOPEE_PRODUCT_PATH_RE = re.compile(r"^/product/(\d+)/(\d+)(?:/.*)?$", re.IGNORECASE)
_SHOPEE_SLUG_RE = re.compile(r"^/(?P<slug>.+)-i\.(?P<shop_id>\d+)\.(?P<item_id>\d+)(?:\?.*)?$", re.IGNORECASE)


def _ensure_scheme(url: str) -> str:
    text = url.strip()
    if text.startswith(("http://", "https://")):
        return text
    return f"https://{text}"


def parse_shopee_product_url(url: str) -> dict[str, str | int | bool | None]:
    if not url or not url.strip():
        raise ValueError("URL is required")

    prepared = _ensure_scheme(url)
    parsed = urlparse(prepared)

    host = parsed.netloc.lower()
    host_no_port = host.split(":", 1)[0]
    if not host_no_port.endswith("shopee.vn") and ".shopee." not in host_no_port and not host_no_port.startswith("s.shopee."):
        raise ValueError("Not a Shopee URL")

    result: dict[str, str | int | bool | None] = {
        "original_url": url,
        "normalized_url": f"{parsed.scheme}://{parsed.netloc}{parsed.path}" + (f"?{parsed.query}" if parsed.query else ""),
        "host": host_no_port,
        "path": parsed.path,
        "region": host_no_port.rsplit(".", 1)[-1] if "." in host_no_port else None,
        "is_short_url": host_no_port.startswith("s.shopee."),
        "shop_id": None,
        "item_id": None,
        "slug": None,
    }

    path_match = _SHOPEE_PRODUCT_PATH_RE.match(parsed.path)
    if path_match:
        result["shop_id"] = int(path_match.group(1))
        result["item_id"] = int(path_match.group(2))
        return result

    slug_match = _SHOPEE_SLUG_RE.match(parsed.path)
    if slug_match:
        result["slug"] = slug_match.group("slug")
        result["shop_id"] = int(slug_match.group("shop_id"))
        result["item_id"] = int(slug_match.group("item_id"))
        return result

    query = parse_qs(parsed.query)
    if "shopid" in query and "itemid" in query:
        result["shop_id"] = int(query["shopid"][0])
        result["item_id"] = int(query["itemid"][0])

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse Shopee product URL metadata.")
    parser.add_argument("url", help="Shopee product URL")
    parser.add_argument("--json", action="store_true", help="Print as JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = parse_shopee_product_url(args.url)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
