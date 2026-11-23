import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "discoveries"))

from discover_techapi import build_inventory, classify


class TechAPIInventoryTests(unittest.TestCase):
    def test_classify_accepts_only_json_in_supported_data_categories(self):
        self.assertEqual(classify("data/smartphone/apple/2024/device.json"), "smartphone")
        self.assertEqual(classify("data/laptop/lenovo/2020/model.json"), "laptop")
        self.assertIsNone(classify("README.md"))
        self.assertIsNone(classify("data/unknown/vendor/model.json"))
        self.assertIsNone(classify("data/smartphone/README.md"))

    @patch("discover_techapi.fetch_json")
    def test_inventory_preserves_path_metadata_and_truncation(self, fetch):
        fetch.return_value = ({
            "sha": "tree-sha",
            "truncated": True,
            "tree": [
                {"path": "data/smartphone/apple/2007/iphone.json", "sha": "blob-a", "size": 512},
                {"path": "data/laptop/apple/2020/macbook.json", "sha": "blob-b", "size": 1024},
                {"path": "data/smartphone/samsung/2024/phone.json", "sha": "blob-c", "size": 256},
                {"path": "data/smartphone/apple/2024/not-json.txt", "sha": "blob-d", "size": 12}
            ]
        }, {"x-ratelimit-remaining": "4999", "x-ratelimit-reset": "12345"})

        payload = build_inventory("develop", {"smartphone"}, limit=1)

        self.assertTrue(payload["tree_truncated"])
        self.assertEqual(payload["tree_sha"], "tree-sha")
        self.assertEqual(payload["total_matching_before_limit"], 2)
        self.assertEqual(payload["record_count"], 1)
        record = payload["records"][0]
        self.assertEqual(record["category"], "smartphone")
        self.assertEqual(record["brand_folder_hint"], "apple")
        self.assertEqual(record["year_folder_hint"], 2007)
        self.assertEqual(record["blob_sha"], "blob-a")
        self.assertIn("raw.githubusercontent.com/GetTechAPI/TechAPI/develop/data/smartphone/apple/2007/iphone.json", record["raw_url"])
        self.assertEqual(payload["api_rate_limit_remaining"], "4999")

    @patch("discover_techapi.fetch_json")
    def test_inventory_rejects_missing_tree_array(self, fetch):
        fetch.return_value = ({"sha": "x", "tree": None}, {})
        with self.assertRaises(ValueError):
            build_inventory("develop", {"smartphone"})


if __name__ == "__main__":
    unittest.main()
