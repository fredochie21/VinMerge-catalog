#!/usr/bin/env python3
"""Build a VINMERGE visual sidecar from an ingestion manifest.

No fitment inference is performed. The script validates the visual contract,
hashes local files when supplied, and groups assets by canonical record ID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ASSET_TYPES = {"exploded_diagram", "technical_illustration", "actual_product", "installation_context", "packaging", "vehicle_context", "reference_image"}
ROLES = {"identification", "navigation", "purchase_confidence", "installation_guidance", "packaging_verification", "vehicle_context", "reference"}
SOURCE_TYPES = {"oem_public", "supplier", "dealer", "user_upload", "licensed_catalogue", "ai_generated", "other"}
STATUSES = {"pending_review", "verified", "rejected", "archived"}
LICENSE_STATUSES = {"unknown", "pending", "permitted", "restricted", "rejected"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_string(obj: dict[str, Any], key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: '{key}' must be a non-empty string")
    return value.strip()


def validate_asset(asset: dict[str, Any], index: int) -> tuple[str, dict[str, Any]]:
    context = f"assets[{index}]"
    if not isinstance(asset, dict):
        raise ValueError(f"{context} must be an object")

    canonical_record_id = require_string(asset, "canonical_record_id", context)
    asset_id = require_string(asset, "asset_id", context)
    asset_type = require_string(asset, "asset_type", context)
    role = require_string(asset, "role", context)
    status = require_string(asset, "status", context)
    if asset_type not in ASSET_TYPES:
        raise ValueError(f"{context}: unsupported asset_type '{asset_type}'")
    if role not in ROLES:
        raise ValueError(f"{context}: unsupported role '{role}'")
    if status not in STATUSES:
        raise ValueError(f"{context}: unsupported status '{status}'")

    source = asset.get("source")
    if not isinstance(source, dict):
        raise ValueError(f"{context}: source must be an object")
    source_type = require_string(source, "type", f"{context}.source")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"{context}.source: unsupported type '{source_type}'")
    license_status = source.get("license_status", "unknown")
    if license_status not in LICENSE_STATUSES:
        raise ValueError(f"{context}.source: invalid license_status '{license_status}'")

    file_path = asset.get("file_path")
    url = asset.get("url")
    if file_path is not None and not isinstance(file_path, str):
        raise ValueError(f"{context}: file_path must be a string when supplied")
    if url is not None and not isinstance(url, str):
        raise ValueError(f"{context}: url must be a string when supplied")
    if status == "verified" and not file_path and not url:
        raise ValueError(f"{context}: verified assets require file_path or url")

    output = {
        "asset_id": asset_id,
        "asset_type": asset_type,
        "role": role,
        "url": url,
        "thumbnail_url": asset.get("thumbnail_url"),
        "source": {
            "type": source_type,
            "name": source.get("name"),
            "source_reference": source.get("source_reference"),
            "license": source.get("license"),
            "license_status": license_status,
        },
        "status": status,
        "image_hash": asset.get("image_hash"),
        "original_image_ref": asset.get("original_image_ref") or file_path,
        "storage_key": asset.get("storage_key"),
        "mime_type": asset.get("mime_type"),
        "file_size_bytes": asset.get("file_size_bytes"),
        "dimensions": asset.get("dimensions"),
        "visual_tags": asset.get("visual_tags", []),
        "notes": asset.get("notes"),
    }
    if file_path:
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"{context}: file_path does not exist or is not a file: {file_path}")
        output["image_hash"] = sha256_file(path)
        output["file_size_bytes"] = path.stat().st_size
    return canonical_record_id, output


def build_sidecar(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("manifest_version") != "1.0":
        raise ValueError("manifest_version must be '1.0'")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise ValueError("assets must be an array")

    records: dict[str, dict[str, Any]] = {}
    seen_asset_ids: set[str] = set()
    for index, raw_asset in enumerate(assets):
        canonical_record_id, asset = validate_asset(raw_asset, index)
        if asset["asset_id"] in seen_asset_ids:
            raise ValueError(f"duplicate asset_id: {asset['asset_id']}")
        seen_asset_ids.add(asset["asset_id"])
        record = records.setdefault(canonical_record_id, {
            "canonical_record_id": canonical_record_id,
            "visual": {
                "visual_layer_version": "1.0",
                "visual_assets": [],
                "ai_visual_metadata": {
                    "enabled": True,
                    "visual_embedding_ref": None,
                    "detected_part_labels": [],
                    "detected_attributes": [],
                    "duplicate_group_id": None,
                    "normalization_status": "not_processed",
                    "fitment_signal": "none",
                    "human_review_required": False,
                },
            },
        })
        record["visual"]["visual_assets"].append(asset)

    return {"visual_index_version": "1.0", "description": "VINMERGE visual sidecar generated from an ingestion manifest.", "records": list(records.values())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    sidecar = build_sidecar(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
