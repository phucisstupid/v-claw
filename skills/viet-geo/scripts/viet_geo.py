#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import unicodedata
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "provinces_vn.json"


def _normalize_text(value: str) -> str:
    lowered = value.strip().lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    no_accent = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    cleaned = " ".join(no_accent.replace("-", " ").replace("_", " ").split())
    for prefix in ("tinh ", "thanh pho ", "tp "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
    return cleaned


def _candidate_keys(entry: dict[str, object]) -> set[str]:
    keys: set[str] = set()
    name = str(entry.get("name") or "")
    aliases = entry.get("aliases") or []
    keys.add(_normalize_text(name))
    keys.add(_normalize_text(name).replace(" ", ""))
    for alias in aliases:
        alias_text = _normalize_text(str(alias))
        if alias_text:
            keys.add(alias_text)
            keys.add(alias_text.replace(" ", ""))
    return {k for k in keys if k}


def _score_match(query: str, keys: set[str]) -> int:
    compact_query = query.replace(" ", "")
    score = 0
    for key in keys:
        compact_key = key.replace(" ", "")
        if query == key or compact_query == compact_key:
            score = max(score, 100)
            continue
        if compact_key.startswith(compact_query) or compact_query.startswith(compact_key):
            score = max(score, 85)
            continue
        if query in key or compact_query in compact_key:
            score = max(score, 75)
            continue

        key_tokens = set(key.split())
        query_tokens = set(query.split())
        if query_tokens and key_tokens:
            overlap = len(query_tokens & key_tokens)
            if overlap:
                ratio = overlap / max(len(query_tokens), len(key_tokens))
                score = max(score, int(50 + ratio * 30))

    return score


def load_provinces() -> list[dict[str, object]]:
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as err:
        raise ValueError("Province dataset not found") from err
    if not isinstance(data, list) or not data:
        raise ValueError("Province dataset is invalid")
    return data


def match_location(query: str, top: int = 3) -> dict[str, object]:
    if not query.strip():
        raise ValueError("Query is required")
    normalized_query = _normalize_text(query)
    provinces = load_provinces()

    scored: list[dict[str, object]] = []
    for entry in provinces:
        keys = _candidate_keys(entry)
        score = _score_match(normalized_query, keys)
        if score <= 0:
            continue
        scored.append(
            {
                "score": score,
                "name": entry["name"],
                "slug": entry["slug"],
                "type": entry["type"],
                "region": entry["region"],
                "aliases": entry.get("aliases", []),
            }
        )

    scored.sort(key=lambda item: (-int(item["score"]), str(item["name"])))
    top_matches = scored[: max(1, top)]

    return {
        "query": query,
        "normalized_query": normalized_query,
        "best_match": top_matches[0] if top_matches else None,
        "matches": top_matches,
        "total_matches": len(scored),
        "source": "bundled_public_dataset",
    }


def list_provinces(region: str | None = None) -> list[dict[str, object]]:
    provinces = load_provinces()
    if region:
        region_norm = _normalize_text(region)
        provinces = [p for p in provinces if _normalize_text(str(p.get("region", ""))) == region_norm]
    return sorted(provinces, key=lambda p: str(p["name"]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize and match Vietnamese province/city names")
    parser.add_argument("--query", help="Province/city query text")
    parser.add_argument("--top", type=int, default=3, help="Number of top matches to return (default: 3)")
    parser.add_argument("--list", action="store_true", help="List all provinces/cities in local dataset")
    parser.add_argument("--region", help="Filter --list by region: north, central, south")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.list and not args.query:
        raise SystemExit("Invalid input: --query is required unless --list is used")
    if args.top < 1:
        raise SystemExit("Invalid input: --top must be >= 1")

    try:
        if args.list:
            result: dict[str, object] = {
                "region": args.region,
                "total": 0,
                "items": list_provinces(args.region),
            }
            result["total"] = len(result["items"])
        else:
            result = match_location(args.query, top=args.top)
    except ValueError as err:
        raise SystemExit(f"Invalid input: {err}") from err

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.list:
        print(f"total: {result['total']}")
        for item in result["items"]:
            print(f"- {item['name']} ({item['type']}, {item['region']})")
        return

    print(f"query: {result['query']}")
    print(f"normalized_query: {result['normalized_query']}")
    if result["best_match"] is None:
        print("best_match: none")
        return

    best = result["best_match"]
    print(f"best_match: {best['name']} ({best['type']}, {best['region']})")
    print(f"score: {best['score']}")


if __name__ == "__main__":
    main()
