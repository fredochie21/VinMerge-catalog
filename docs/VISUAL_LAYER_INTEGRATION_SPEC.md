# VINMERGE Visual Layer — Integration Specification

## Status

Implemented as an additive architecture on `main`.

## Canonical integration

The master catalogue remains the authoritative identifier source. The visual layer is keyed by `canonical_record_id` and may be materialized into API responses as the `visual` object.

Recommended runtime response shape:

```text
canonical vehicle/component/part record
    + visual layer by canonical_record_id
    = VINMERGE enriched record
```

Do not copy vehicle definitions into the visual index.

## Empty-state behavior

Every supported record may safely return:

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

This makes the catalogue immediately onboarding-ready even before any images exist.

## Asset priority in the product UI

1. Exploded/technical illustration for component location and navigation.
2. Actual product image for purchase confirmation.
3. Installation/context image when useful.
4. Packaging image for part-number/brand verification.
5. Vehicle-context image for orientation.

The UI should gracefully fall back when a layer is unavailable; no record should be rejected solely because an image is missing.

## AI controls

AI visual output must carry confidence and review state. AI can propose labels, attributes, duplicates, visual similarity and mismatch flags. It must not silently convert those signals into authoritative fitment.

## Dealer onboarding

Dealer upload should capture at minimum:

- canonical record/part reference;
- asset type;
- source type and source name;
- licence/permission status;
- original image reference;
- image hash when processed;
- review status.

The platform can then run normalization, AI enrichment and duplicate/mismatch checks before publishing the image.

## Important implementation note

The current master catalogue is a Git LFS object. Therefore this repository stores the visual contract and sidecar architecture separately rather than attempting to rewrite the large LFS object through GitHub's text contents API. When the catalogue is next regenerated or processed through the development pipeline, the `visual` object should be materialized for canonical records from this contract.
