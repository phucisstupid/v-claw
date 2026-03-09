#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from plugins.shopee.url_parser import parse_shopee_product_url


URLS = [
    "https://shopee.vn/product/12345678/987654321",
    "https://shopee.vn/ao-thun-basic-i.12345678.987654321",
    "https://shopee.vn/some-product?shopid=12345678&itemid=987654321",
]


for raw_url in URLS:
    parsed = parse_shopee_product_url(raw_url)
    print(raw_url)
    print(f"shop_id={parsed['shop_id']} item_id={parsed['item_id']} slug={parsed['slug']}")
    print("-")
