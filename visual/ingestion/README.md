# VINMERGE Visual Ingestion

This directory contains the deterministic ingestion boundary for the hybrid visual layer.

## Pipeline

incoming manifest -> validate -> hash/normalize metadata -> sidecar records -> downstream storage

The ingestion layer does **not** establish VIN identity, OEM fitment, interchangeability, or supplier stock truth. It only enriches a supplied canonical_record_id with visual evidence and processing metadata.

## Input

An ingestion manifest is a JSON object with:

- manifest_version
- assets[]
- each asset must provide canonical_record_id, asset_id, asset_type, role, source and status
- optional file_path may point to a local image for SHA-256 hashing
- local file_path values must be relative to an explicitly configured ingestion root
- url may be supplied when the image is already stored remotely

## Output

The script writes a sidecar JSON document keyed by canonical_record_id. It preserves one canonical record per identifier and does not copy vehicle definitions into the visual layer.

## Safety rules

- Incoming manifests and generated sidecars are validated against the repository JSON schemas.
- Local files are confined to the configured ingestion root.
- Absolute paths, path traversal outside the root and symlink traversal are rejected.
- Local files have a 25 MiB default size limit; production callers may lower or explicitly raise the limit.
- Duplicate asset_id values are rejected.
- A verified asset requires a usable image reference and source.license_status=permitted.
- pending_review and rejected assets require human review before they can become eligible verified imagery.
- SHA-256 hashes are cached for repeated references to the same stable file during one run.
- Generated output is written atomically and existing output is not overwritten unless --force is explicitly supplied.
- AI metadata remains supporting evidence only.
