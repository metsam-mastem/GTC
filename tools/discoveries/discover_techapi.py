#!/usr/bin/env python3
"""Discover TechAPI JSON paths by bounded directory subtrees.

The upstream repository is large. A single recursive root tree can be
truncated, so this walker splits discovery at category and manufacturer
directories, then further splits any still-truncated subtree. It does not
download device-record bodies and flags unresolved directories explicitly.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com/repos/GetTechAPI/TechAPI"
DEFAULT_BRANCH = "develop"
CATEGORIES = {"smartphone", "tablet", "watch", "pda", "laptop", "monitor", "soc", "cpu", "gpu"}
MAX_RESPONSE_BYTES = 50 * 1024 * 1024
MAX_WORKERS = 8
MAX_SPLIT_DEPTH = 8


def fetch_json(url: str) -> tuple[Any, dict[str, str]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GTC-TechAPI-Inventory/0.2",
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
    return json.loads(payload.decode("utf-8")), response_headers


def classify(path: str) -> str | None:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "data" or not path.endswith(".json"):
        return None
    category = parts[1].lower()
    return category if category in CATEGORIES else None


def contents_url(path: str, branch: str) -> str:
    encoded = urllib.parse.quote(path, safe="/")
    return f"{API}/contents/{encoded}?ref={urllib.parse.quote(branch, safe='')}"


def metadata_record(path: str, category: str, branch: str,
                    sha: str | None, size: int | None) -> dict[str, Any]:
    parts = Path(path[len("data/"):]).parts
    return {
        "path": path,
        "category": category,
        "brand_folder_hint": parts[1] if len(parts) > 1 else None,
        "year_folder_hint": next((int(part) for part in parts[2:] if len(part) == 4 and part.isdigit()), None),
        "blob_sha": sha,
        "size_bytes": size,
        "raw_url": f"https://raw.githubusercontent.com/GetTechAPI/TechAPI/{branch}/{path}",
        "web_url": f"https://github.com/GetTechAPI/TechAPI/blob/{branch}/{path}"
    }


def scan_directory(category: str, directory_path: str, directory_sha: str,
                   branch: str, depth: int = 0) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    try:
        tree, _ = fetch_json(f"{API}/git/trees/{directory_sha}?recursive=1")
    except Exception as exc:
        return [], [], [f"{directory_path}: {exc}"]

    entries = tree.get("tree") if isinstance(tree, dict) else None
    if not isinstance(entries, list):
        return [], [], [f"{directory_path}: tree response has no tree array"]

    if not tree.get("truncated", False):
        records = []
        for item in entries:
            if not isinstance(item, dict) or item.get("type") != "blob":
                continue
            relative = item.get("path")
            if not isinstance(relative, str) or not relative.endswith(".json"):
                continue
            full_path = f"{directory_path}/{relative}"
            if classify(full_path) == category:
                records.append(metadata_record(full_path, category, branch, item.get("sha"), item.get("size")))
        return records, [], []

    if depth >= MAX_SPLIT_DEPTH:
        return [], [directory_path], []

    try:
        children, _ = fetch_json(contents_url(directory_path, branch))
    except Exception as exc:
        return [], [directory_path], [f"{directory_path}: split listing failed: {exc}"]

    if not isinstance(children, list):
        return [], [directory_path], [f"{directory_path}: Contents API did not return a list"]

    records: list[dict[str, Any]] = []
    unresolved: list[str] = []
    errors: list[str] = []
    for child in children:
        if not isinstance(child, dict):
            continue
        child_path = child.get("path")
        if not isinstance(child_path, str):
            continue
        if child.get("type") == "file" and child_path.endswith(".json"):
            records.append(metadata_record(child_path, category, branch, child.get("sha"), child.get("size")))
        elif child.get("type") == "dir" and isinstance(child.get("sha"), str):
            found, partial, failed = scan_directory(category, child_path, child["sha"], branch, depth + 1)
            records.extend(found)
            unresolved.extend(partial)
            errors.extend(failed)
    return records, unresolved, errors


def build_inventory(branch: str, categories: set[str], limit: int = 0,
                    workers: int = MAX_WORKERS) -> dict[str, Any]:
    tasks: list[tuple[str, str, str]] = []
    unresolved: list[str] = []
    errors: list[str] = []

    for category in sorted(categories):
        try:
            children, _ = fetch_json(contents_url(f"data/{category}", branch))
        except Exception as exc:
            errors.append(f"data/{category}: {exc}")
            continue
        if not isinstance(children, list):
            errors.append(f"data/{category}: Contents API did not return a directory listing")
            continue
        for child in children:
            if isinstance(child, dict) and child.get("type") == "dir" and isinstance(child.get("sha"), str) and isinstance(child.get("path"), str):
                tasks.append((category, child["path"], child["sha"]))
            elif isinstance(child, dict) and child.get("type") == "file" and str(child.get("path", "")).endswith(".json"):
                pass

    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, min(workers, 12))) as executor:
        futures = {
            executor.submit(scan_directory, category, path, sha, branch): (category, path)
            for category, path, sha in tasks
        }
        for future in as_completed(futures):
            found, partial, failed = future.result()
            records.extend(found)
            unresolved.extend(partial)
            errors.extend(failed)

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
        "categories_requested": sorted(categories),
        "total_matching_before_limit": total_matching,
        "record_count": len(records),
        "by_category": dict(Counter(row["category"] for row in records)),
        "truncated_directories": sorted(set(unresolved)),
        "discovery_errors": sorted(set(errors)),
        "source_inventory_complete": not unresolved and not errors,
        "license": "CC-BY-SA-4.0",
        "attribution_required": "Data from TechAPI — https://github.com/GetTechAPI/TechAPI",
        "coverage_note": "This is a path inventory for requested categories in one upstream dataset only, not total worldwide device coverage. Completeness is false when a subtree is truncated or a request fails.",
        "records": records
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover TechAPI model JSON paths without cloning its dataset.")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--categories", default=",".join(sorted(CATEGORIES)))
    parser.add_argument("--limit", type=int, default=0, help="0 keeps all matching paths")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--output", type=Path, default=Path("research/inventories/techapi-manifest.json"))
    args = parser.parse_args()
    categories = {part.strip().lower() for part in args.categories.split(",") if part.strip()}
    unknown = categories - CATEGORIES
    if unknown:
        parser.error("unknown categories: " + ", ".join(sorted(unknown)))
    try:
        inventory = build_inventory(args.branch, categories, max(0, args.limit), args.workers)
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {inventory['record_count']} paths; categories={len(inventory['by_category'])}; complete={inventory['source_inventory_complete']}")
    if inventory["truncated_directories"]:
        print(f"UNRESOLVED TRUNCATED SUBTREES: {len(inventory['truncated_directories'])}")
    if inventory["discovery_errors"]:
        print(f"DISCOVERY ERRORS: {len(inventory['discovery_errors'])}")
    print(f"Output: {args.output}")
    return 0 if not inventory["discovery_errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
