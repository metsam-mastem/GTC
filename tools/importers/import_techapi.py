#!/usr/bin/env python3
"""Create GTC draft records from selected local TechAPI JSON files.

TechAPI data is CC BY-SA 4.0. This adapter does not crawl or clone upstream
repositories. Every imported claim remains UNVERIFIED until GTC review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ID = "SRC-TECHAPI-DATA"
UPSTREAM = "https://github.com/GetTechAPI/TechAPI/blob/develop/"
CATEGORY_MAP = {
    "smartphone": ("data/mobile/phones", "mobile.smartphone", "device_model"),
    "tablet": ("data/mobile/tablets", "mobile", "device_model"),
    "watch": ("data/gadgets/wearables", "gadgets.wearable", "device_model"),
    "pda": ("data/mobile/pda", "mobile", "device_model"),
    "laptop": ("data/computing/laptops", "computing.laptop", "device_model"),
    "monitor": ("data/gadgets/displays", "gadgets.display", "device_model"),
    "soc": ("data/components/socs", "components.soc", "component"),
    "cpu": ("data/components/cpus", "components.cpu", "component"),
    "gpu": ("data/components/gpus", "components.gpu", "component")
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"


def infer_category(relative_path: str) -> str | None:
    return next((part.lower() for part in Path(relative_path).parts if part.lower() in CATEGORY_MAP), None)


def infer_relative_path(path: Path, source_root: Path | None) -> str:
    resolved = path.resolve()
    if source_root and resolved.is_relative_to(source_root):
        return resolved.relative_to(source_root).as_posix()
    try:
        parts = resolved.parts
        index = parts.index("data")
        return Path(*parts[index + 1:]).as_posix()
    except ValueError:
        return path.name


def convert(raw: dict[str, Any], source_relative_path: str, retrieved_at: str) -> tuple[dict[str, Any], Path]:
    category = infer_category(source_relative_path)
    if category not in CATEGORY_MAP:
        raise ValueError(f"unsupported TechAPI category: {source_relative_path}")
    target_dir, taxonomy, entity_type = CATEGORY_MAP[category]
    slug = str(raw.get("slug") or Path(source_relative_path).stem)
    name = str(raw.get("name") or slug)
    brand = str(raw.get("brand") or raw.get("manufacturer") or "unknown")
    gtc_id = "GTC-IMP-TECHAPI-" + slugify(slug).upper()
    source_url = UPSTREAM + source_relative_path.replace("\\", "/")
    upstream_urls = raw.get("source_urls", [])
    if not isinstance(upstream_urls, list):
        upstream_urls = []
    upstream_urls = [x for x in upstream_urls if isinstance(x, str) and x.startswith(("http://", "https://"))]

    claims = []
    mapping = [
        ("release_date", "lifecycle.release_date"),
        ("ram_gb", "hardware.memory.ram_gb"),
        ("battery_mah", "hardware.battery.capacity_mah"),
        ("weight_g", "physical.mass_g"),
        ("soc", "hardware.soc_id"),
        ("display", "hardware.display"),
        ("connectivity", "hardware.connectivity"),
        ("os", "software.operating_system"),
        ("cpu_config", "specifications.cpu"),
        ("gpu_name", "specifications.gpu"),
        ("process_nm", "specifications.process_nm"),
        ("npu_tops", "specifications.npu_tops"),
        ("storage_options_gb", "hardware.storage.options_gb")
    ]
    for field, field_path in mapping:
        if raw.get(field) is not None:
            claims.append({
                "claim_id": f"GTC-CLM-TECHAPI-{slugify(slug + '-' + field).upper()}",
                "field_path": field_path,
                "value": raw[field],
                "source_id": SOURCE_ID,
                "source_url": source_url,
                "supporting_urls": upstream_urls,
                "evidence_type": "curated_dataset",
                "verification_status": "UNVERIFIED",
                "retrieved_at": retrieved_at,
                "upstream_verification": raw.get("verified") if isinstance(raw.get("verified"), bool) else None,
                "note": "Imported from TechAPI. Upstream verified is recorded for context only; GTC verification remains UNVERIFIED."
            })
    claims.append({
        "claim_id": f"GTC-CLM-TECHAPI-{slugify(slug + '-source-record').upper()}",
        "field_path": "extensions.upstream_record",
        "value": {"dataset": "GetTechAPI/TechAPI", "path": source_relative_path, "slug": slug},
        "source_id": SOURCE_ID,
        "source_url": source_url,
        "supporting_urls": upstream_urls,
        "evidence_type": "curated_dataset",
        "verification_status": "UNVERIFIED",
        "retrieved_at": retrieved_at,
        "upstream_verification": raw.get("verified") if isinstance(raw.get("verified"), bool) else None,
        "note": "Imported source record pointer; not an independent validation."
    })

    record: dict[str, Any] = {
        "schema_version": "1.0.0",
        "gtc_id": gtc_id,
        "entity_type": entity_type,
        "canonical_name": name,
        "manufacturer": {
            "manufacturer_id": "MFR-" + slugify(brand).replace("-", "_").upper(),
            "name": brand
        },
        "taxonomy_ids": ["components", taxonomy] if entity_type == "component" else [taxonomy],
        "identity": {
            "model_codes": raw.get("model_codes", []) if isinstance(raw.get("model_codes"), list) else [],
            "codenames": raw.get("codenames", []) if isinstance(raw.get("codenames"), list) else [],
            "aliases": [],
            "part_numbers": raw.get("part_numbers", []) if isinstance(raw.get("part_numbers"), list) else []
        },
        "lifecycle": {
            "release_year": int(str(raw.get("release_date"))[:4]) if raw.get("release_date") and str(raw.get("release_date"))[:4].isdigit() else None,
            "release_date": raw.get("release_date") if isinstance(raw.get("release_date"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw["release_date"]) else None,
            "announcement_date": None,
            "discontinued_date": None,
            "status": "unknown",
            "events": []
        },
        "physical": {"mass_g": raw.get("weight_g")},
        "hardware": {
            "soc_id": raw.get("soc"),
            "memory": {"ram_gb": raw.get("ram_gb")},
            "storage": {"options_gb": raw.get("storage_options_gb", [])},
            "display": raw.get("display"),
            "battery": {"capacity_mah": raw.get("battery_mah")},
            "connectivity": raw.get("connectivity")
        },
        "software": {"operating_system": raw.get("os")},
        "specifications": {
            "cpu": raw.get("cpu_config"),
            "gpu": raw.get("gpu_name"),
            "process_nm": raw.get("process_nm"),
            "npu_tops": raw.get("npu_tops")
        },
        "relationships": [],
        "claims": claims,
        "source_ids": [SOURCE_ID],
        "completeness": {
            "state": "IDENTIFIED" if len(claims) <= 1 else "BASIC_PROFILE",
            "missing_sections": ["independent GTC verification", "variant resolution", "engineering documentation"]
        },
        "extensions": {
            "upstream": "GetTechAPI/TechAPI",
            "upstream_record_path": source_relative_path,
            "upstream_source_urls": upstream_urls,
            "upstream_verified": raw.get("verified"),
            "upstream_license": "CC-BY-SA-4.0",
            "attribution_required": "Data from TechAPI — https://github.com/GetTechAPI/TechAPI",
            "imported_at": retrieved_at
        }
    }
    return record, Path(target_dir) / f"{slugify(slug)}.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create reviewable GTC records from local TechAPI data.")
    parser.add_argument("input", type=Path, help="one JSON file or directory")
    parser.add_argument("--source-root", type=Path, help="TechAPI/data root; preserves upstream path")
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--confirm-license", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.confirm_license:
        parser.error("Review CC BY-SA 4.0 data terms, then pass --confirm-license.")
    input_path = args.input.resolve()
    inputs = [input_path] if input_path.is_file() else sorted(input_path.rglob("*.json"))[:max(1, args.limit)] if input_path.is_dir() else []
    if not inputs:
        parser.error("input path does not exist or contains no JSON files")
    source_root = args.source_root.resolve() if args.source_root else None
    output_root = args.output_root.resolve()
    imported = errors = 0
    today = date.today().isoformat()
    for path in inputs:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("record must be a JSON object")
            relative = infer_relative_path(path, source_root)
            record, target_relative = convert(raw, relative, today)
            target = output_root / target_relative
            if target.exists() and not args.overwrite:
                raise FileExistsError(f"{target} exists; compare first and pass --overwrite only deliberately")
            if args.dry_run:
                print(f"DRY-RUN {path} -> {target} [{record['gtc_id']}]")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"IMPORTED {path} -> {target}")
            imported += 1
        except Exception as exc:
            errors += 1
            print(f"ERROR {path}: {exc}", file=sys.stderr)
    print(f"RESULT imported={imported} errors={errors} dry_run={args.dry_run}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
