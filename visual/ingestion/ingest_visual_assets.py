#!/usr/bin/env python3
"""Build a VINMERGE visual sidecar from an ingestion manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ASSET_TYPES = {"exploded_diagram", "technical_illustration", "actual_product", "installation_context", "packaging", "vehicle_context", "reference_image"}
ROLES = {"identification", "navigation", "purchase_confidence", "installation_guidance", "packaging_verification", "vehicle_context", "reference"}
SOURCE_TYPES = {"oem_public", "supplier", "dealer", "user_upload", "licensed_catalogue", "ai_generated", "other"}
STATUSES = {"pending_review", "verified", "rejected", "archived"}
LICENSE_STATUSES = {"unknown", "pending", "permitted", "restricted", "rejected"}
DEFAULT_MAX_FILE_SIZE = 25 * 1024 * 1024
SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schema"
MANIFEST_SCHEMA_PATH = SCHEMA_DIR / "vinmerge-visual-ingestion-manifest.schema.json"
INDEX_SCHEMA_PATH = SCHEMA_DIR / "vinmerge-visual-index.schema.json"
INTELLIGENCE_SCHEMA_PATH = SCHEMA_DIR / "vinmerge-visual-intelligence.schema.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(instance: Any, schema_path: Path, *, dependencies: tuple[Path, ...] = ()) -> None:
    schema = _load_json(schema_path)
    registry = Registry()
    for dependency in dependencies:
        dep_schema = _load_json(dependency)
        registry = registry.with_resource(dep_schema["$id"], Resource.from_contents(dep_schema))
    if "$id" in schema:
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "$"
        raise ValueError(f"schema validation failed at {location}: {error.message}")


def sha256_file(path: Path, cache: dict[tuple[int, int, int, int], str], max_file_size: int) -> tuple[str, int]:
    stat = path.stat()
    if stat.st_size > max_file_size:
        raise ValueError(f"local file exceeds maximum allowed size of {max_file_size} bytes: {path}")
    identity = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if identity in cache:
        return cache[identity], stat.st_size
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    value = digest.hexdigest()
    cache[identity] = value
    return value, stat.st_size


def _safe_local_path(file_path: str, ingestion_root: Path) -> Path:
    candidate = Path(file_path)
    if candidate.is_absolute():
        raise ValueError("file_path must be relative to --ingestion-root")
    current = ingestion_root / candidate
    resolved_root = ingestion_root.resolve(strict=True)
    cursor = ingestion_root
    for part in candidate.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"file_path may not traverse symlinks: {file_path}")
    resolved = current.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("file_path resolves outside --ingestion-root") from exc
    if not resolved.is_file():
        raise ValueError(f"file_path does not exist or is not a regular file: {file_path}")
    return resolved


def require_string(obj: dict[str, Any], key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: '{key}' must be a non-empty string")
    return value.strip()


def validate_asset(
    asset: dict[str, Any],
    index: int,
    *,
    ingestion_root: Path | None,
    hash_cache: dict[tuple[int, int, int, int], str],
    max_file_size: int,
) -> tuple[str, dict[str, Any]]:
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
    if url is not None and not url.strip():
        raise ValueError(f"{context}: url cannot be empty")
    if status == "verified":
        if not file_path and not url:
            raise ValueError(f"{context}: verified assets require file_path or url")
        if license_status != "permitted":
            raise ValueError(f"{context}: verified assets require source.license_status='permitted'")

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
        if ingestion_root is None:
            raise ValueError(f"{context}: local file_path requires --ingestion-root")
        path = _safe_local_path(file_path, ingestion_root)
        output["image_hash"], output["file_size_bytes"] = sha256_file(path, hash_cache, max_file_size)
    return canonical_record_id, output


def status_requires_review(status: str) -> bool:
    return status in {"pending_review", "rejected"}


def build_sidecar(
    manifest: dict[str, Any],
    *,
    ingestion_root: Path | None = None,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> dict[str, Any]:
    _validate(manifest, MANIFEST_SCHEMA_PATH)
    assets = manifest["assets"]

    records: dict[str, dict[str, Any]] = {}
    seen_asset_ids: set[str] = set()
    hash_cache: dict[tuple[int, int, int, int], str] = {}

    for index, raw_asset in enumerate(assets):
        canonical_record_id, asset = validate_asset(
            raw_asset,
            index,
            ingestion_root=ingestion_root,
            hash_cache=hash_cache,
            max_file_size=max_file_size,
        )
        if asset["asset_id"] in seen_asset_ids:
            raise ValueError(f"duplicate asset_id: {asset['asset_id']}")
        seen_asset_ids.add(asset["asset_id"])

        record = records.setdefault(
            canonical_record_id,
            {
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
                        "human_review_required": status_requires_review(asset["status"]),
                    },
                },
            },
        )
        record["visual"]["visual_assets"].append(asset)
        if asset["status"] in {"pending_review", "rejected"}:
            record["visual"]["ai_visual_metadata"]["human_review_required"] = True

    result = {
        "visual_index_version": "1.0",
        "description": "VINMERGE visual sidecar generated from an ingestion manifest.",
        "records": list(records.values()),
    }
    _validate(result, INDEX_SCHEMA_PATH, dependencies=(INTELLIGENCE_SCHEMA_PATH,))
    return result


def write_atomic_json(output: Path, payload: dict[str, Any], *, force: bool = False) -> None:
    output = output.resolve()
    if output.exists() and not force:
        raise ValueError(f"refusing to overwrite existing output without --force: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=output.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ingestion-root", type=Path, default=None)
    parser.add_argument("--max-file-size", type=int, default=DEFAULT_MAX_FILE_SIZE)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.max_file_size <= 0:
        raise SystemExit("--max-file-size must be positive")

    manifest_path = args.manifest.resolve(strict=True)
    if manifest_path.is_symlink():
        raise SystemExit("manifest may not be a symlink")

    output_path = args.output.resolve()
    if manifest_path == output_path:
        raise SystemExit("manifest and output must be different files")

    root = args.ingestion_root.resolve(strict=True) if args.ingestion_root else None
    if root is not None and not root.is_dir():
        raise SystemExit("--ingestion-root must be a directory")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sidecar = build_sidecar(
        manifest,
        ingestion_root=root,
        max_file_size=args.max_file_size,
    )
    write_atomic_json(output_path, sidecar, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
