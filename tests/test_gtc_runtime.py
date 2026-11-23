import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from gtc_runtime import forbidden_fields, validate_record
from importers.import_techapi import convert, infer_relative_path, parse_raw_url, manufacturer_id_for, load_manifest


class RuntimeValidationTests(unittest.TestCase):
    def setUp(self):
        self.sources = {"SRC-TEST"}
        self.record = {
            "schema_version": "1.0.0",
            "gtc_id": "GTC-TEST-DEVICE-001",
            "entity_type": "device_model",
            "canonical_name": "Test Device",
            "manufacturer": {"manufacturer_id": "MFR-TEST", "name": "Test Manufacturer"},
            "taxonomy_ids": ["mobile"],
            "identity": {"model_codes": ["TEST-001"]},
            "claims": [{
                "claim_id": "GTC-CLM-TEST-001",
                "field_path": "lifecycle.release_year",
                "value": 2020,
                "source_id": "SRC-TEST",
                "source_url": "https://example.org/device",
                "evidence_type": "manufacturer",
                "verification_status": "UNVERIFIED",
                "retrieved_at": "2026-11-23"
            }],
            "source_ids": ["SRC-TEST"],
            "completeness": {"state": "IDENTIFIED", "missing_sections": []}
        }

    def test_valid_record_passes(self):
        self.assertEqual(validate_record(self.record, self.sources, manufacturer_ids={"MFR-TEST"}), [])

    def test_unknown_manufacturer_fails(self):
        errors = validate_record(self.record, self.sources, manufacturer_ids={"MFR-OTHER"})
        self.assertTrue(any("unknown manufacturer_id" in x for x in errors))

    def test_known_manufacturer_passes(self):
        self.assertEqual(validate_record(self.record, self.sources, manufacturer_ids={"MFR-TEST"}), [])

    def test_unknown_source_fails(self):
        self.record["claims"][0]["source_id"] = "SRC-MISSING"
        self.assertTrue(any("unknown source_id" in x for x in validate_record(self.record, self.sources, manufacturer_ids={"MFR-TEST"})))

    def test_duplicate_claim_id_fails(self):
        self.record["claims"].append(dict(self.record["claims"][0]))
        self.assertTrue(any("duplicate claim_id" in x for x in validate_record(self.record, self.sources, manufacturer_ids={"MFR-TEST"})))

    def test_private_identifier_is_rejected(self):
        self.record["extensions"] = {"imei": "000000000000000"}
        self.assertTrue(any("prohibited personal/security field" in x for x in validate_record(self.record, self.sources)))

    def test_missing_provenance_fails(self):
        self.record["claims"][0].pop("source_url")
        self.assertTrue(any("missing source_url" in x for x in validate_record(self.record, self.sources)))

    def test_nested_personal_fields_detected(self):
        self.assertTrue(forbidden_fields({"nested": [{"current_owner": "x"}]}))

    def test_single_file_path_category_inference(self):
        relative = infer_relative_path(Path("/tmp/TechAPI/data/smartphone/apple/iphone.json"), None)
        self.assertEqual(relative, "smartphone/apple/iphone.json")

    def test_raw_url_is_limited_to_approved_repository(self):
        url = "https://raw.githubusercontent.com/GetTechAPI/TechAPI/develop/data/smartphone/apple/iphone.json"
        self.assertEqual(parse_raw_url(url), "smartphone/apple/iphone.json")
        with self.assertRaises(ValueError):
            parse_raw_url("https://evil.example/data/smartphone/phone.json")
        with self.assertRaises(ValueError):
            parse_raw_url("https://raw.githubusercontent.com/other/repo/main/data/smartphone/phone.json")

    def test_manufacturer_id_is_stable(self):
        self.assertEqual(manufacturer_id_for("Samsung"), "MFR-SAMSUNG")
        self.assertEqual(manufacturer_id_for("HMD Global"), "MFR-HMD_GLOBAL")

    def test_techapi_manifest_loader_uses_validated_url(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps({"records": [{"raw_url": "https://evil.example/file.json"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_manifest(path, 1)

    def test_techapi_import_preserves_additional_upstream_fields_as_claims(self):
        raw = {
            "slug": "sample-engineering-device",
            "name": "Sample Engineering Device",
            "brand": "Example",
            "release_date": "2024-03-01",
            "msrp_usd": 699,
            "cameras": [{"type": "main", "mp": 50}],
            "charging_wired_w": 45,
            "dimensions": {"height_mm": 150, "width_mm": 70, "depth_mm": 8},
            "raw_gsmarena": {"launch_status": "Discontinued"},
            "verified": True,
            "source_urls": ["https://example.org/spec"]
        }
        record, _ = convert(raw, "smartphone/example/2024/sample-engineering-device.json", "2026-11-23")
        by_path = {claim["field_path"]: claim["value"] for claim in record["claims"]}
        self.assertEqual(by_path["pricing.msrp_usd"], 699)
        self.assertEqual(by_path["hardware.cameras"], [{"type": "main", "mp": 50}])
        self.assertEqual(by_path["hardware.charging.wired_max_w"], 45)
        self.assertEqual(by_path["physical.dimensions"], {"height_mm": 150, "width_mm": 70, "depth_mm": 8})
        self.assertEqual(by_path["extensions.techapi_fields.raw_gsmarena"], {"launch_status": "Discontinued"})
        self.assertTrue(all(claim["verification_status"] == "UNVERIFIED" for claim in record["claims"]))

    def test_techapi_import_keeps_upstream_unverified(self):
        raw = {
            "slug": "sample-phone",
            "name": "Sample Phone",
            "brand": "Example",
            "release_date": "2024-01-01",
            "ram_gb": 8,
            "verified": True,
            "source_urls": ["https://example.org/spec"]
        }
        record, target = convert(raw, "smartphone/example/2024/sample-phone.json", "2026-11-23")
        self.assertEqual(record["gtc_id"], "GTC-IMP-TECHAPI-SAMPLE-PHONE")
        self.assertEqual(target.as_posix(), "data/mobile/phones/sample-phone.json")
        self.assertTrue(all(c["verification_status"] == "UNVERIFIED" for c in record["claims"]))
        self.assertTrue(all(c["upstream_verification"] is True for c in record["claims"]))


if __name__ == "__main__":
    unittest.main()
