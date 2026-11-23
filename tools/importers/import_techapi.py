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
import urllib.parse
import urllib.request
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


def parse_raw_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com":
        raise ValueError("remote import only accepts HTTPS raw.githubusercontent.com URLs")
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("query, fragment and user-info are not allowed")
    prefix = "/GetTechAPI/TechAPI/develop/data/"
    if not parsed.path.startswith(prefix):
        raise ValueError("URL must point inside GetTechAPI/TechAPI develop/data/")
    relative = parsed.path[len(prefix):]
    parts = Path(relative).parts
    if not relative or any(part in ("", ".", "..") for part in parts) or not relative.endswith(".json"):
        raise ValueError("URL must identify one JSON file below TechAPI data/")
    if not infer_category(relative):
        raise ValueError("unsupported TechAPI category in URL")
    return relative


def fetch_raw_url(url: str, timeout: int = 15) -> tuple[dict[str, Any], str]:
    relative = parse_raw_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "GTC-TechAPI-Importer/0.2"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read(2 * 1024 * 1024 + 1)
    if len(payload) > 2 * 1024 * 1024:
        raise ValueError("source record exceeds 2 MiB")
    raw = json.loads(payload.decode("utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("upstream JSON root must be an object")
    return raw, relative


def manufacturer_id_for(name: str) -> str:
    return "MFR-" + slugify(name).replace("-", "_").upper()


FIELD_PATHS = {
    "base_model_slug": "identity.base_model_slug",
    "model_codes": "identity.model_codes",
    "model_code": "identity.model_codes",
    "codenames": "identity.codenames",
    "aliases": "identity.aliases",
    "part_numbers": "identity.part_numbers",
    "release_date": "lifecycle.release_date",
    "ram_gb": "hardware.memory.ram_gb",
    "battery_mah": "hardware.battery.capacity_mah",
    "weight_g": "physical.mass_g",
    "dimensions": "physical.dimensions",
    "ip_rating": "physical.ingress_protection_rating",
    "soc": "hardware.soc_slug",
    "display": "hardware.display",
    "cameras": "hardware.cameras",
    "connectivity": "hardware.connectivity",
    "charging_wired_w": "hardware.charging.wired_max_w",
    "charging_wireless_w": "hardware.charging.wireless_max_w",
    "storage_options_gb": "hardware.storage.options_gb",
    "os": "software.operating_system",
    "os_version": "software.version_at_launch",
    "cpu_config": "specifications.cpu",
    "gpu_name": "specifications.gpu",
    "process_nm": "specifications.process_nm",
    "process_node": "specifications.process_node",
    "npu_tops": "specifications.npu_tops",
    "msrp_usd": "pricing.msrp_usd",
    "segment": "specifications.segment",
    "architecture": "specifications.architecture",
    "socket": "specifications.socket",
    "cores": "specifications.cores",
    "threads": "specifications.threads",
    "p_cores": "specifications.performance_cores",
    "e_cores": "specifications.efficiency_cores",
    "base_clock_ghz": "specifications.base_clock_ghz",
    "boost_clock_ghz": "specifications.boost_clock_ghz",
    "l3_cache_mb": "specifications.l3_cache_mb",
    "tdp_w": "specifications.tdp_w",
    "max_tdp_w": "specifications.max_tdp_w",
    "integrated_graphics": "specifications.integrated_graphics",
    "memory_support": "specifications.memory_support",
    "raw_chipset": "specifications.raw_chipset",
    "clock_mhz": "specifications.clock_mhz",
    "gpu_name": "specifications.gpu",
    "gpu_config": "specifications.gpu",
    "memory_type": "specifications.memory_type",
    "channels": "specifications.channels",
    "bandwidth_gbps": "specifications.bandwidth_gbps",
    "interface": "specifications.interface",
    "pcie_version": "specifications.pcie_version",
    "tdp": "specifications.tdp",
    "benchmark_results": "specifications.benchmark_results",
    "benchmarks": "specifications.benchmarks",
    "launch_status": "lifecycle.status",
    "cpu_name": "hardware.processor.name",
    "gpu_type": "hardware.gpu.type",
    "storage_gb": "hardware.storage.capacity_gb",
    "cuda_cores": "specifications.cuda_cores",
    "stream_processors": "specifications.stream_processors",
    "rt_cores": "specifications.rt_cores",
    "tensor_cores": "specifications.tensor_cores",
    "memory_gb": "specifications.memory_gb",
    "memory_type": "specifications.memory_type",
    "memory_bus_bit": "specifications.memory_bus_bit",
    "memory_bandwidth_gbps": "specifications.memory_bandwidth_gbps",
    "base_clock_mhz": "specifications.base_clock_mhz",
    "boost_clock_mhz": "specifications.boost_clock_mhz",
    "fp32_tflops": "specifications.fp32_tflops",
    "blender_score": "specifications.benchmarks.blender_score",
    "timespy_score": "specifications.benchmarks.timespy_score",
    "passmark_g3d_mark": "specifications.benchmarks.passmark_g3d_mark"
}
METADATA_FIELDS = {"slug", "name", "brand", "manufacturer", "verified", "source_urls"}


def manufacturer_name_for(value: Any) -> str:
    raw = str(value or "unknown").strip()
    known = {
        "apple": "Apple", "samsung": "Samsung", "nokia": "Nokia",
        "google": "Google", "xiaomi": "Xiaomi", "qualcomm": "Qualcomm",
        "amd": "AMD", "nvidia": "NVIDIA", "intel": "Intel",
        "lenovo": "Lenovo", "motorola": "Motorola", "huawei": "Huawei",
        "honor": "HONOR", "oneplus": "OnePlus", "oppo": "OPPO",
        "vivo": "vivo", "sony": "Sony", "htc": "HTC", "acer": "Acer",
        "asus": "ASUS", "dell": "Dell", "hp": "HP", "ibm": "IBM",
        "broadcom": "Broadcom", "mediatek": "MediaTek"
    }
    return known.get(raw.lower(), raw)


def set_nested(target: dict[str, Any], dotted_path: str, value: Any) -> None:
    parts = dotted_path.split(".")
    cursor = target
    for part in parts[:-1]:
        child = cursor.get(part)
        if not isinstance(child, dict):
            child = {}
            cursor[part] = child
        cursor = child
    cursor[parts[-1]] = value


def convert(raw: dict[str, Any], source_relative_path: str, retrieved_at: str) -> tuple[dict[str, Any], Path]:
    category = infer_category(source_relative_path)
    if category not in CATEGORY_MAP:
        raise ValueError(f"unsupported TechAPI category: {source_relative_path}")
    target_dir, taxonomy, entity_type = CATEGORY_MAP[category]
    slug = str(raw.get("slug") or Path(source_relative_path).stem)
    name = str(raw.get("name") or slug)
    manufacturer_raw = raw.get("brand") or raw.get("manufacturer") or "unknown"
    manufacturer_name = manufacturer_name_for(manufacturer_raw)
    manufacturer_id = manufacturer_id_for(manufacturer_name)
    gtc_id = "GTC-IMP-TECHAPI-" + slugify(slug).upper()
    source_url = UPSTREAM + source_relative_path.replace("\\", "/")
    upstream_urls = raw.get("source_urls", [])
    if not isinstance(upstream_urls, list):
        upstream_urls = []
    upstream_urls = [x for x in upstream_urls if isinstance(x, str) and x.startswith(("http://", "https://"))]

    record: dict[str, Any] = {
        "schema_version": "1.0.0",
        "gtc_id": gtc_id,
        "entity_type": entity_type,
        "canonical_name": name,
        "manufacturer": {"manufacturer_id": manufacturer_id, "name": manufacturer_name},
        "taxonomy_ids": ["components", taxonomy] if entity_type == "component" else [taxonomy],
        "identity": {
            "model_codes": raw.get("model_codes", []) if isinstance(raw.get("model_codes"), list) else [],
            "codenames": raw.get("codenames", []) if isinstance(raw.get("codenames"), list) else [],
            "aliases": raw.get("aliases", []) if isinstance(raw.get("aliases"), list) else [],
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
        "hardware": {},
        "software": {},
        "specifications": {},
        "pricing": {},
        "relationships": [],
        "claims": [],
        "source_ids": [SOURCE_ID],
        "completeness": {
            "state": "IDENTIFIED",
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

    claims = []
    for field, value in raw.items():
        if field in METADATA_FIELDS or value is None:
            continue
        field_path = FIELD_PATHS.get(field, f"specifications.{field}" if entity_type == "component" else f"extensions.techapi_fields.{field}")
        if field == "release_date" and not (
            isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)
        ):
            field_path = "extensions.techapi_fields.release_date_raw"
        set_nested(record, field_path, value)
        claim_suffix = slugify(slug + "-" + field).upper()
        claims.append({
            "claim_id": f"GTC-CLM-TECHAPI-{claim_suffix}",
            "field_path": field_path,
            "value": value,
            "source_id": SOURCE_ID,
            "source_url": source_url,
            "supporting_urls": upstream_urls,
            "evidence_type": "curated_dataset",
            "verification_status": "UNVERIFIED",
            "retrieved_at": retrieved_at,
            "upstream_verification": raw.get("verified") if isinstance(raw.get("verified"), bool) else None,
            "note": "Imported from TechAPI. This upstream dataset claim remains UNVERIFIED in GTC until independently reviewed."
        })

    if not claims:
        raise ValueError(f"TechAPI record {slug} contains no importable factual fields")
    pointer_claim = {
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
        "note": "Upstream source record pointer; not an independent validation."
    }
    claims.append(pointer_claim)
    record["claims"] = claims
    record["completeness"]["state"] = "BASIC_PROFILE" if len(claims) > 2 else "IDENTIFIED"
    record["completeness"]["missing_sections"] = [
        "independent GTC verification", "regional and board variant resolution",
        "hardware architecture and component inventory", "software and firmware evidence",
        "repair and engineering documentation"
    ]
    if entity_type == "component":
        record["component_type"] = category
    return record, Path(target_dir) / f"{slugify(slug)}.json"

def load_manifest(path: Path, limit: int) -> list[tuple[dict[str, Any], str, str]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = manifest.get("records") if isinstance(manifest, dict) else None
    if not isinstance(entries, list):
        raise ValueError("manifest must contain a records array")
    batch = []
    for entry in entries[:max(1, limit)]:
        if not isinstance(entry, dict) or not isinstance(entry.get("raw_url"), str):
            raise ValueError("each manifest record must include raw_url")
        raw, relative = fetch_raw_url(entry["raw_url"])
        batch.append((raw, relative, entry["raw_url"]))
    return batch


def load_records(input_value: str | None, source_root: Path | None, limit: int, manifest_path: Path | None = None) -> list[tuple[dict[str, Any], str, str]]:
    if manifest_path:
        if input_value:
            raise ValueError("pass either input or --manifest, not both")
        return load_manifest(manifest_path, limit)
    if not input_value:
        raise ValueError("provide an input path, raw GitHub URL or --manifest")
    if input_value.startswith("https://"):
        raw, relative = fetch_raw_url(input_value)
        return [(raw, relative, input_value)]
    input_path = Path(input_value).resolve()
    paths = [input_path] if input_path.is_file() else sorted(input_path.rglob("*.json"))[:max(1, limit)] if input_path.is_dir() else []
    if not paths:
        raise FileNotFoundError("input path does not exist or contains no JSON files")
    batch = []
    for path in paths:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{path} JSON root must be object")
        batch.append((raw, infer_relative_path(path, source_root), str(path)))
    return batch


def main() -> int:
    parser = argparse.ArgumentParser(description="Import selected TechAPI JSON records as GTC drafts.")
    parser.add_argument("input", nargs="?", help="local JSON file/directory or one approved raw GitHub URL")
    parser.add_argument("--manifest", type=Path, help="inventory manifest containing approved TechAPI raw URLs")
    parser.add_argument("--source-root", type=Path, help="TechAPI/data root; preserves relative paths")
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--confirm-license", action="store_true")
    parser.add_argument("--register-manufacturer", action="store_true", help="append an unknown manufacturer to the registry")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.confirm_license:
        parser.error("Review TechAPI CC BY-SA 4.0 data terms, then pass --confirm-license.")
    output_root = args.output_root.resolve()
    source_root = args.source_root.resolve() if args.source_root else None
    registry_path = output_root / "data/registry/manufacturers.json"
    try:
        batch = load_records(args.input, source_root, args.limit, args.manifest)
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    makers = registry.get("manufacturers", [])
    maker_map = {entry.get("manufacturer_id"): entry for entry in makers if isinstance(entry, dict)}
    additions: dict[str, dict[str, Any]] = {}
    imported = errors = 0
    today = date.today().isoformat()

    for raw, relative, origin in batch:
        try:
            record, target_relative = convert(raw, relative, today)
            target = output_root / target_relative
            if target.exists() and not args.overwrite:
                raise FileExistsError(f"{target} already exists; compare before explicit overwrite")
            for existing_path in output_root.glob("data/**/*.json"):
                if existing_path == target:
                    continue
                try:
                    existing = json.loads(existing_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if existing.get("gtc_id") == record["gtc_id"]:
                    raise ValueError(f"GTC ID collision: {record['gtc_id']} already exists at {existing_path}")

            maker = record["manufacturer"]
            maker_id = maker["manufacturer_id"]
            if maker_id not in maker_map and maker_id not in additions:
                if not args.register_manufacturer:
                    raise ValueError(f"unknown manufacturer {maker['name']} ({maker_id}); add it or pass --register-manufacturer")
                additions[maker_id] = {
                    "manufacturer_id": maker_id, "name": maker["name"],
                    "kind": "brand_or_vendor", "country_or_origin": None,
                    "aliases": [], "source_ids": [SOURCE_ID]
                }

            if args.dry_run:
                print(f"DRY-RUN {origin} -> {target} [{record['gtc_id']}]")
                if maker_id in additions:
                    print(f"DRY-RUN register manufacturer {maker_id}: {maker['name']}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                imported += 1
        except Exception as exc:
            errors += 1
            print(f"ERROR {origin}: {exc}", file=sys.stderr)

    if additions and not args.dry_run:
        for maker_id, maker in additions.items():
            if maker_id not in maker_map:
                makers.append(maker)
        temp_path = registry_path.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_path.replace(registry_path)

    print(f"RESULT imported={imported} errors={errors} dry_run={args.dry_run} new_manufacturers={len(additions)}")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
