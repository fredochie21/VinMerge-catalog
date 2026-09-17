import tempfile
import unittest
from pathlib import Path

from ingest_visual_assets import build_sidecar


class VisualIngestionTests(unittest.TestCase):
    def asset(self, **overrides):
        asset = {
            "canonical_record_id": "REC-001",
            "asset_id": "ASSET-001",
            "asset_type": "actual_product",
            "role": "purchase_confidence",
            "source": {
                "type": "dealer",
                "name": "Dealer",
                "source_reference": "upload-1",
                "license": "dealer-owned",
                "license_status": "permitted",
            },
            "status": "pending_review",
            "url": None,
        }
        asset.update(overrides)
        return asset

    def test_groups_assets_without_copying_vehicle_definitions(self):
        result = build_sidecar({"manifest_version": "1.0", "assets": [self.asset()]})
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["canonical_record_id"], "REC-001")
        self.assertEqual(len(result["records"][0]["visual"]["visual_assets"]), 1)

    def test_rejects_duplicate_asset_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate asset_id"):
            build_sidecar({"manifest_version": "1.0", "assets": [self.asset(), self.asset(canonical_record_id="REC-002")]})

    def test_verified_asset_requires_image_reference(self):
        with self.assertRaisesRegex(ValueError, "verified assets require"):
            build_sidecar({"manifest_version": "1.0", "assets": [self.asset(status="verified")]})

    def test_local_file_is_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "part.jpg"
            path.write_bytes(b"test-image")
            result = build_sidecar({"manifest_version": "1.0", "assets": [self.asset(file_path=str(path))]})
            image_hash = result["records"][0]["visual"]["visual_assets"][0]["image_hash"]
            self.assertEqual(len(image_hash), 64)


if __name__ == "__main__":
    unittest.main()
