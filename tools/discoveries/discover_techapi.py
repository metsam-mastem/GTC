#!/usr/bin/env python3
"""Discover TechAPI JSON record paths without cloning or downloading the dataset.

The output is a path inventory / import manifest, not a catalogue of verified
device facts. A GitHub tree response may be truncated; that status is retained.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com/repos/GetTechAPI/TechAPI"
DEFAULT_BRANCH = "develop"
CATEGORIES = {"smartphone", "tablet", "watch", "pda", "laptop", "monitor", "soc", "cpu", "gpu"}
MAX_RESPONSE_BYTES = 50 * 1024 * 1024


def fetch_json(url: str) -> tuple[dict[str, Any], dict[str, str]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GTC-TechAPI-Inventory/0.1",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read(MAX_RESPONSE_BYTES + 1)
        response_headers = {key.lower(): value for key, value in response.headers.items()}
    if len(payload) > MAX_RESPONSE_BYTES:
        raise ValueError(f"GitHub API response exceeded {MAX_RESPONSE_BYTES} bytes")
    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("GitHub API response root must be an object")
    return parsed, response_headers


def classify(path: str) -> str | None:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "data" or not path.endswith(".json"):
        return None
    category = parts[1].lower()
    return category if category in CATEGORIES else None


def build_inventory(branch: str, categories: set[str], limit: int = 0) -> dict[str, Any]:
    response, headers = fetch_json(f"{API}/git/trees/{branch}?recursive=1")
    tree = response.get("tree")
    if not isinstance(tree, list):
        raise ValueError("GitHub tree response did not contain a tree array")

    records = []
    for item in tree:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        category = classify(path) if isinstance(path, str) else None
        if category not in categories:
            continue
        relative = path[len("data/"):]
        parts = Path(relative).parts
        records.append({
            "path": path,
            "category": category,
            "brand_folder_hint": parts[1] if len(parts) > 1 else None,
            "year_folder_hint": next((int(part) for part in parts[2:] if len(part) == 4 and part.isdigit()), None),
            "blob_sha": item.get("sha"),
            "size_bytes": item.get("size"),
            "raw_url": f"https://raw.githubusercontent.com/GetTechAPI/TechAPI/{branch}/{path}",
            "web_url": f"https://github.com/GetTechAPI/TechAPI/blob/{branch}/{path}"
        })
    records.sort(key=lambda row: (
        row["category"], row.get("brand_folder_hint") or "",
        row.get("year_folder_hint") or 0, row["path"]
    ))
    total_matching = len(records)
    if limit > 0:
        records = records[:limit]
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "upstream": "GetTechAPI/TechAPI",
        "branch": branch,
        "tree_sha": response.get("sha"),
        "tree_truncated": bool(response.get("truncated")),
        "categories_requested": sorted(categories),
        "total_matching_before_limit": total_matching,
        "record_count": len(records),
        "by_category": dict(Counter(row["category"] for row in records)),
        "api_rate_limit_remaining": headers.get("x-ratelimit-remaining"),
        "api_rate_limit_reset": headers.get("x-ratelimit-reset"),
        "license": "CC-BY-SA-4.0",
        "attribution_required": "Data from TechAPI — https://github.com/GetTechAPI/TechAPI",
        "coverage_note": "Path inventory of one upstream dataset only; it is not a count of all device models worldwide. A truncated tree is incomplete.",
        "records": records
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover TechAPI model JSON paths without cloning the dataset.")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--categories", default=",".join(sorted(CATEGORIES)))
    parser.add_argument("--limit", type=int, default=0, help="0 keeps all matching paths")
    parser.add_argument("--output", type=Path, default=Path("research/inventories/techapi-manifest.json"))
    args = parser.parse_args()
    categories = {part.strip().lower() for part in args.categories.split(",") if part.strip()}
    unknown = categories - CATEGORIES
    if unknown:
        parser.error("unknown categories: " + ", ".join(sorted(unknown)))
    try:
        inventory = build_inventory(args.branch, categories, max(0, args.limit))
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {inventory['record_count']} paths; categories={len(inventory['by_category'])}; truncated={inventory['tree_truncated']}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
