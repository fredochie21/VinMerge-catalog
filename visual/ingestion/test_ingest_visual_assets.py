import hashlib
import tempfile
import unittest
from pathlib import Path

from ingest_visual_assets import build_sidecar, write_atomic_json


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
            "thumbnail_url": None,
            "original_image_ref": None,
            "storage_key": None,
            "mime_type": None,
            "file_size_bytes": None,
            "dimensions": None,
            "image_hash": None,
            "visual_tags": [],
            "notes": None,
        }
        asset.update(overrides)
        return asset

    def test_groups_assets_without_copying_vehicle_definitions(self):
        result = build_sidecar({"manifest_version": "1.0", "assets": [self.asset()]})
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["canonical_record_id"], "REC-001")
        self.assertEqual(len(result["records"][0]["visual"]["visual_assets"]), 1)
        self.assertTrue(result["records"][0]["visual"]["ai_visual_metadata"]["human_review_required"])

    def test_rejects_duplicate_asset_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate asset_id"):
            build_sidecar({
                "manifest_version": "1.0",
                "assets": [self.asset(), self.asset(canonical_record_id="REC-002")],
            })

    def test_verified_asset_requires_image_reference(self):
        with self.assertRaisesRegex(ValueError, "not valid under any of the given schemas|verified assets require file_path or url"):
            build_sidecar({"manifest_version": "1.0", "assets": [self.asset(status="verified")]})

    def test_verified_asset_requires_permitted_license(self):
        asset = self.asset(status="verified", url="https://example.test/image.jpg")
        asset["source"]["license_status"] = "rejected"
        with self.assertRaisesRegex(ValueError, "permitted.*expected|license_status=permitted"):
            build_sidecar({"manifest_version": "1.0", "assets": [asset]})

    def test_local_file_is_hashed_inside_ingestion_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "part.jpg"
            payload = b"test-image"
            path.write_bytes(payload)
            result = build_sidecar(
                {"manifest_version": "1.0", "assets": [self.asset(file_path="part.jpg")]},
                ingestion_root=root,
            )
            image_hash = result["records"][0]["visual"]["visual_assets"][0]["image_hash"]
            self.assertEqual(image_hash, hashlib.sha256(payload).hexdigest())

    def test_rejects_absolute_local_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "part.jpg"
            path.write_bytes(b"test-image")
            with self.assertRaisesRegex(ValueError, "must be relative"):
                build_sidecar(
                    {"manifest_version": "1.0", "assets": [self.asset(file_path=str(path))]},
                    ingestion_root=root,
                )

    def test_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root.parent / "outside.jpg"
            outside.write_bytes(b"test-image")
            try:
                with self.assertRaisesRegex(ValueError, "outside"):
                    build_sidecar(
                        {"manifest_version": "1.0", "assets": [self.asset(file_path="../outside.jpg")]},
                        ingestion_root=root,
                    )
            finally:
                outside.unlink(missing_ok=True)

    def test_rejects_oversized_local_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "part.jpg").write_bytes(b"123456")
            with self.assertRaisesRegex(ValueError, "maximum allowed size"):
                build_sidecar(
                    {"manifest_version": "1.0", "assets": [self.asset(file_path="part.jpg")]},
                    ingestion_root=root,
                    max_file_size=5,
                )

    def test_refuses_output_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out.json"
            output.write_text("original", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                write_atomic_json(output, {"ok": True})
            self.assertEqual(output.read_text(encoding="utf-8"), "original")


if __name__ == "__main__":
    unittest.main()
