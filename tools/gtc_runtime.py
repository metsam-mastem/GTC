#!/usr/bin/env python3
"""Deterministic GTC catalogue runtime. Python 3.10+, standard library only."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = Path("data/registry/sources.json")
RECORD_ROOTS = (
    "data/mobile", "data/computing", "data/components", "data/gadgets",
    "data/networking", "data/embedded", "data/industrial", "data/scientific",
    "data/power",
)
ALLOWED_ENTITY_TYPES = {"device_model", "device_variant", "component"}
ALLOWED_STATES = {"VERIFIED", "CORROBORATED", "UNVERIFIED", "CONFLICTED", "DEPRECATED"}
ALLOWED_POLICIES = {"allow", "sharealike", "conditional", "facts_and_links_only", "lead_only", "blocked"}
FORBIDDEN_KEYS = {
    "imei", "imsi", "msisdn", "subscriber_id", "owner", "current_owner",
    "owner_notes", "account_id", "phone_number", "email_address",
    "private_key", "password", "access_token", "refresh_token",
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def record_files(root: Path = ROOT) -> list[Path]:
    result: list[Path] = []
    for relative in RECORD_ROOTS:
        folder = root / relative
        if folder.exists():
            result.extend(folder.rglob("*.json"))
    return sorted(result)


def forbidden_fields(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z0-9_]", "", str(key).lower())
            location = f"{prefix}.{key}" if prefix else str(key)
            if normalized in FORBIDDEN_KEYS:
                found.append(location)
            found.extend(forbidden_fields(child, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_fields(child, f"{prefix}[{index}]"))
    return found


def load_sources(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[str]]:
    path = root / SOURCE_FILE
    errors: list[str] = []
    if not path.is_file():
        return {}, [f"source registry missing: {path}"]
    try:
        payload = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot read source registry: {exc}"]
    entries = payload.get("sources") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return {}, ["source registry must contain a sources array"]
    registry: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        label = f"sources[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        source_id = entry.get("source_id")
        if not isinstance(source_id, str) or not re.fullmatch(r"SRC-[A-Z0-9-]+", source_id):
            errors.append(f"{label} has invalid source_id")
            continue
        if source_id in registry:
            errors.append(f"duplicate source_id {source_id}")
        registry[source_id] = entry
        for field in ("name", "source_type", "canonical_url", "license", "ingestion_policy", "checked_at"):
            if field not in entry:
                errors.append(f"{source_id} missing {field}")
        if not str(entry.get("canonical_url", "")).startswith(("https://", "http://")):
            errors.append(f"{source_id} canonical_url must be HTTP(S)")
        if entry.get("ingestion_policy") not in ALLOWED_POLICIES:
            errors.append(f"{source_id} has invalid ingestion_policy")
        try:
            date.fromisoformat(entry.get("checked_at", ""))
        except (TypeError, ValueError):
            errors.append(f"{source_id} checked_at must be ISO date")
    return registry, errors


def validate_record(record: Any, source_ids: set[str], filename: str = "<memory>") -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{filename}: record must be a JSON object"]

    required = ("schema_version", "gtc_id", "entity_type", "canonical_name",
                "taxonomy_ids", "claims", "source_ids", "completeness")
    for key in required:
        if key not in record:
            errors.append(f"{filename}: missing {key}")

    gtc_id = record.get("gtc_id")
    if not isinstance(gtc_id, str) or not re.fullmatch(r"GTC-[A-Z0-9-]+", gtc_id):
        errors.append(f"{filename}: invalid gtc_id")
    if record.get("entity_type") not in ALLOWED_ENTITY_TYPES:
        errors.append(f"{filename}: invalid entity_type")
    if not isinstance(record.get("canonical_name"), str) or not record.get("canonical_name", "").strip():
        errors.append(f"{filename}: canonical_name must be non-empty")
    taxonomy_ids = record.get("taxonomy_ids")
    if not isinstance(taxonomy_ids, list) or not taxonomy_ids or not all(isinstance(x, str) and x for x in taxonomy_ids):
        errors.append(f"{filename}: taxonomy_ids must be a non-empty string array")

    listed_sources = record.get("source_ids")
    if not isinstance(listed_sources, list) or not listed_sources:
        errors.append(f"{filename}: source_ids must be a non-empty array")
        listed_sources = []
    for source_id in listed_sources:
        if source_id not in source_ids:
            errors.append(f"{filename}: unknown source_id {source_id}")

    claims = record.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append(f"{filename}: claims must be a non-empty array")
        claims = []
    seen_claims: set[str] = set()
    for index, claim in enumerate(claims):
        label = f"{filename}: claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label} must be an object")
            continue
        for field in ("claim_id", "field_path", "value", "source_id", "source_url",
                      "evidence_type", "verification_status", "retrieved_at"):
            if field not in claim:
                errors.append(f"{label} missing {field}")
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not re.fullmatch(r"GTC-CLM-[A-Z0-9-]+", claim_id):
            errors.append(f"{label} invalid claim_id")
        elif claim_id in seen_claims:
            errors.append(f"{label} duplicate claim_id {claim_id}")
        else:
            seen_claims.add(claim_id)
        source_id = claim.get("source_id")
        if source_id not in source_ids:
            errors.append(f"{label} unknown source_id {source_id}")
        elif source_id not in listed_sources:
            errors.append(f"{label} source_id is absent from record.source_ids")
        if not isinstance(claim.get("field_path"), str) or not claim.get("field_path", "").strip():
            errors.append(f"{label} field_path must be non-empty")
        if not isinstance(claim.get("source_url"), str) or not claim.get("source_url", "").startswith(("https://", "http://")):
            errors.append(f"{label} source_url must be HTTP(S)")
        if claim.get("verification_status") not in ALLOWED_STATES:
            errors.append(f"{label} invalid verification_status")
        try:
            date.fromisoformat(claim.get("retrieved_at", ""))
        except (TypeError, ValueError):
            errors.append(f"{label} retrieved_at must be ISO date")

    completeness = record.get("completeness")
    if not isinstance(completeness, dict) or not isinstance(completeness.get("state"), str):
        errors.append(f"{filename}: completeness.state is required")
    elif not isinstance(completeness.get("missing_sections"), list):
        errors.append(f"{filename}: completeness.missing_sections must be an array")

    for field in forbidden_fields(record):
        errors.append(f"{filename}: prohibited personal/security field: {field}")
    return errors


def validate_catalog(root: Path = ROOT) -> tuple[list[str], list[str], list[Path]]:
    source_registry, errors = load_sources(root)
    known_sources = set(source_registry)
    paths = record_files(root)
    records: list[tuple[Path, dict[str, Any]]] = []
    id_to_path: dict[str, Path] = {}
    claim_ids: dict[str, Path] = {}
    warnings: list[str] = []

    for path in paths:
        try:
            record = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(root)} invalid JSON: {exc}")
            continue
        errors.extend(validate_record(record, known_sources, str(path.relative_to(root))))
        if not isinstance(record, dict):
            continue
        gtc_id = record.get("gtc_id")
        if isinstance(gtc_id, str):
            if gtc_id in id_to_path:
                errors.append(f"duplicate gtc_id {gtc_id}: {id_to_path[gtc_id]} and {path}")
            else:
                id_to_path[gtc_id] = path
            records.append((path, record))
        for claim in record.get("claims", []) if isinstance(record.get("claims"), list) else []:
            if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str):
                claim_id = claim["claim_id"]
                if claim_id in claim_ids:
                    errors.append(f"duplicate claim_id {claim_id}: {claim_ids[claim_id]} and {path}")
                else:
                    claim_ids[claim_id] = path

    all_ids = set(id_to_path)
    for path, record in records:
        for relation in record.get("relationships", []) if isinstance(record.get("relationships"), list) else []:
            if isinstance(relation, dict):
                target = relation.get("target_gtc_id")
                if target and target not in all_ids:
                    warnings.append(f"{path.relative_to(root)} unresolved relationship target {target}")

        for event in (record.get("lifecycle") or {}).get("events", []):
            if not isinstance(event, dict):
                continue
            for claim_id in event.get("source_claim_ids", []):
                if claim_id not in claim_ids:
                    warnings.append(f"{path.relative_to(root)} event references missing claim {claim_id}")

    return errors, warnings, paths


def build_index(root: Path = ROOT) -> tuple[Path, Path]:
    errors, warnings, paths = validate_catalog(root)
    if errors:
        raise ValueError("catalogue validation failed; run validate for details")
    records = [read_json(path) for path in paths]
    by_type = Counter(item.get("entity_type", "unknown") for item in records)
    by_taxonomy = Counter(tax for item in records for tax in item.get("taxonomy_ids", []))
    by_manufacturer = Counter(
        (item.get("manufacturer") or {}).get("name", "Unknown")
        for item in records if isinstance(item.get("manufacturer"), dict)
    )
    id_set = {item.get("gtc_id") for item in records}
    unresolved = [
        {"source": item.get("gtc_id"), "target": rel.get("target_gtc_id")}
        for item in records
        for rel in item.get("relationships", [])
        if isinstance(rel, dict) and rel.get("target_gtc_id") not in id_set
    ]
    generated = root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    index = {
        "generated_at": timestamp,
        "record_count": len(records),
        "by_entity_type": dict(by_type),
        "by_taxonomy": dict(by_taxonomy),
        "by_manufacturer": dict(by_manufacturer),
        "records": [{
            "gtc_id": item.get("gtc_id"),
            "entity_type": item.get("entity_type"),
            "canonical_name": item.get("canonical_name"),
            "manufacturer": (item.get("manufacturer") or {}).get("name"),
            "taxonomy_ids": item.get("taxonomy_ids", []),
            "release_year": (item.get("lifecycle") or {}).get("release_year"),
            "completeness": (item.get("completeness") or {}).get("state")
        } for item in records]
    }
    coverage = {
        "generated_at": timestamp,
        "record_count": len(records),
        "by_entity_type": dict(by_type),
        "by_taxonomy": dict(by_taxonomy),
        "by_manufacturer": dict(by_manufacturer),
        "unresolved_relationships": unresolved,
        "validation_warnings": warnings,
        "coverage_note": "Repository record counts are not a percentage of all devices worldwide."
    }
    index_path, coverage_path = generated / "catalog-index.json", generated / "coverage.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index_path, coverage_path


def source_audit(root: Path = ROOT, timeout: int = 8) -> Path:
    sources, errors = load_sources(root)
    if errors:
        raise ValueError("; ".join(errors))
    results = []
    for source_id, source in sorted(sources.items()):
        if not source.get("audit_enabled", False):
            continue
        url = source["canonical_url"]
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "GTC-SourceAudit/0.1"})
        status, final_url, error_text = None, url, None
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status, final_url = response.status, response.geturl()
        except urllib.error.HTTPError as exc:
            status = exc.code
            if exc.code in (403, 405, 501):
                try:
                    request = urllib.request.Request(url, headers={"Range": "bytes=0-0", "User-Agent": "GTC-SourceAudit/0.1"})
                    with urllib.request.urlopen(request, timeout=timeout) as response:
                        status, final_url = response.status, response.geturl()
                except Exception as retry_exc:
                    error_text = str(retry_exc)
        except Exception as exc:
            error_text = str(exc)
        results.append({
            "source_id": source_id, "url": url, "final_url": final_url,
            "http_status": status, "reachable": bool(status and 200 <= status < 400),
            "elapsed_ms": round((time.monotonic() - started) * 1000), "error": error_text,
            "checked_at": datetime.now(timezone.utc).isoformat()
        })
        time.sleep(0.15)
    generated = root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    path = generated / "source-health.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checked_sources": len(results),
        "reachable": sum(1 for item in results if item["reachable"]),
        "unreachable": sum(1 for item in results if not item["reachable"]),
        "results": results,
        "note": "HTTP reachability is not proof of source accuracy, authority, license compatibility or freshness."
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="GTC deterministic catalogue runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate", help="validate records and evidence")
    validate_parser.add_argument("--strict", action="store_true", help="fail on all integrity errors")
    sub.add_parser("build-index", help="build searchable catalogue index and coverage JSON")
    audit_parser = sub.add_parser("source-audit", help="check selected source URL reachability")
    audit_parser.add_argument("--timeout", type=int, default=8)
    args = parser.parse_args()

    if args.command == "validate":
        errors, warnings, paths = validate_catalog()
        for item in warnings:
            print(f"WARNING: {item}")
        for item in errors:
            print(f"FAIL: {item}")
        if errors:
            print(f"FAIL: {len(errors)} error(s), {len(paths)} record file(s)")
            return 1
        print(f"PASS: {len(paths)} records; source registry and evidence references valid")
        return 0
    if args.command == "build-index":
        try:
            index, coverage = build_index()
        except ValueError as exc:
            print(f"FAIL: {exc}")
            return 1
        print(f"PASS: {index.relative_to(ROOT)}; {coverage.relative_to(ROOT)}")
        return 0
    if args.command == "source-audit":
        try:
            output = source_audit(timeout=max(2, min(args.timeout, 30)))
        except ValueError as exc:
            print(f"FAIL: {exc}")
            return 1
        print(f"PASS: {output.relative_to(ROOT)}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
