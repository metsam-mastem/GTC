import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "discoveries"))

from discover_techapi import build_inventory, classify


class TechAPIInventoryTests(unittest.TestCase):
    def test_classify_only_supported_json_paths(self):
        self.assertEqual(classify("data/smartphone/apple/2024/device.json"), "smartphone")
        self.assertEqual(classify("data/laptop/lenovo/2020/model.json"), "laptop")
        self.assertIsNone(classify("README.md"))
        self.assertIsNone(classify("data/unknown/vendor/model.json"))
        self.assertIsNone(classify("data/smartphone/README.md"))

    @patch("discover_techapi.fetch_json")
    def test_inventory_reads_brand_subtree_and_respects_limit(self, fetch):
        fetch.side_effect = [
            ([{"path":"data/smartphone/apple","type":"dir","sha":"brand-sha"}], {}),
            ({"sha":"brand-sha","truncated":False,"tree":[
                {"path":"2007/iphone.json","type":"blob","sha":"blob-a","size":512},
                {"path":"2024/not-json.txt","type":"blob","sha":"blob-b","size":12}
            ]}, {})
        ]
        payload = build_inventory("develop", {"smartphone"}, limit=1)
        self.assertTrue(payload["source_inventory_complete"])
        self.assertEqual(payload["total_matching_before_limit"], 1)
        self.assertEqual(payload["record_count"], 1)
        record = payload["records"][0]
        self.assertEqual(record["category"], "smartphone")
        self.assertEqual(record["brand_folder_hint"], "apple")
        self.assertEqual(record["year_folder_hint"], 2007)
        self.assertEqual(record["blob_sha"], "blob-a")
        self.assertIn("GetTechAPI/TechAPI/develop/data/smartphone/apple/2007/iphone.json", record["raw_url"])

    @patch("discover_techapi.fetch_json")
    def test_truncated_brand_subtree_is_split_into_year_subtrees(self, fetch):
        fetch.side_effect = [
            ([{"path":"data/smartphone/apple","type":"dir","sha":"brand-sha"}], {}),
            ({"sha":"brand-sha","truncated":True,"tree":[]}, {}),
            ([{"path":"data/smartphone/apple/2024","type":"dir","sha":"year-sha"}], {}),
            ({"sha":"year-sha","truncated":False,"tree":[
                {"path":"phone.json","type":"blob","sha":"blob-phone","size":900}
            ]}, {})
        ]
        payload = build_inventory("develop", {"smartphone"})
        self.assertTrue(payload["source_inventory_complete"])
        self.assertEqual(payload["record_count"], 1)
        self.assertEqual(payload["records"][0]["path"], "data/smartphone/apple/2024/phone.json")

    @patch("discover_techapi.fetch_json")
    def test_missing_tree_array_is_reported_as_error(self, fetch):
        fetch.side_effect = [
            ([{"path":"data/smartphone/apple","type":"dir","sha":"brand-sha"}], {}),
            ({"sha":"brand-sha","truncated":False,"tree":None}, {})
        ]
        payload = build_inventory("develop", {"smartphone"})
        self.assertFalse(payload["source_inventory_complete"])
        self.assertTrue(payload["discovery_errors"])


if __name__ == "__main__":
    unittest.main()
