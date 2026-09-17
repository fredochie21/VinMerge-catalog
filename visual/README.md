# VINMERGE Visual Intelligence Integration

This directory is the onboarding-ready visual layer for the VINMERGE master catalogue.

## Architecture

Visual data is attached by reference to canonical vehicle/component/part identifiers. The visual layer does **not** redefine VIN, chassis, frame, model code, vehicle configuration or fitment.

A record can begin with an empty visual layer and acquire assets progressively from dealers, suppliers, licensed catalogues and other approved sources.

## Record contract

Each canonical record that supports visual enrichment should expose:

```json
"visual": {
  "visual_layer_version": "1.0",
  "visual_assets": [],
  "ai_visual_metadata": {
    "enabled": true,
    "visual_embedding_ref": null,
    "detected_part_labels": [],
    "detected_attributes": [],
    "duplicate_group_id": null,
    "normalization_status": "not_processed",
    "fitment_signal": "none",
    "human_review_required": false
  }
}
```

The canonical validation schema is `schema/vinmerge-visual-intelligence.schema.json`.

## Supported visual asset types

- `exploded_diagram`
- `technical_illustration`
- `actual_product`
- `installation_context`
- `packaging`
- `vehicle_context`
- `reference_image`

## Source-of-truth rule

AI-generated metadata is enrichment only. It cannot independently establish VIN identity, chassis/frame identity, exact vehicle configuration, OEM fitment, final interchangeability or supplier stock truth.

## Onboarding flow

`Dealer/Supplier image` → `source + licence recorded` → `quality/normalization` → `AI enrichment` → `duplicate/mismatch checks` → `human review when required` → `verified asset` → `search/product UI`.

## Why this is a separate layer

The current master catalogue is stored through Git LFS. Keeping visual assets and metadata structurally separate prevents image growth from bloating the identifier master and lets the platform replace, add or retire images without changing canonical vehicle records.
