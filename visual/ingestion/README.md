# VINMERGE Visual Ingestion

This directory contains the deterministic ingestion boundary for the hybrid visual layer.

## Pipeline

`incoming manifest -> validate -> hash/normalize metadata -> sidecar records -> downstream storage`

The ingestion layer does **not** establish VIN identity, OEM fitment, interchangeability, or supplier stock truth. It only enriches a supplied `canonical_record_id` with visual evidence and processing metadata.

## Input

An ingestion manifest is a JSON object with:

- `manifest_version`
- `assets[]`
- each asset must provide `canonical_record_id`, `asset_id`, `asset_type`, `role`, `source`, `status`
- optional `file_path` may point to a local image for SHA-256 hashing
- `url` may be supplied when the image is already stored remotely

## Output

The script writes a sidecar JSON document keyed by `canonical_record_id`. It preserves one canonical record per identifier and does not copy vehicle definitions into the visual layer.

## Safety rules

- Missing image bytes are allowed when a remote `url` is supplied.
- A local file path must exist and be a regular file before it is hashed.
- Duplicate `asset_id` values are rejected.
- An asset cannot be published as `verified` without either a stored `url` or local image bytes.
- AI metadata remains supporting evidence only.
