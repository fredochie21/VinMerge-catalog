# VINMERGE AI Visual Enrichment — Stage 2

## Objective

Stage 2 enriches ingested visual assets with machine-assisted metadata while preserving the VINMERGE catalogue as the authoritative source of vehicle identity and fitment.

## Pipeline

`Ingestion → validation → image normalization/quality checks → hash/duplicate detection → AI candidate enrichment → human review → verified visual asset`

## AI may produce

- candidate part/component labels;
- candidate visual attributes;
- search tags;
- image-quality flags;
- normalization status;
- candidate duplicate groups;
- a human-review flag.

## AI may not establish

- VIN/chassis/frame identity;
- exact vehicle configuration;
- OEM fitment;
- interchangeability;
- supplier stock availability;
- final approval of a visual asset.

## State model

`pending_review` is the default for newly ingested dealer/customer assets. AI enrichment must remain advisory until a human or trusted workflow verifies the asset. Rejected assets must not be presented as verified purchase imagery.

## Implementation boundary

The ingestion sidecar remains separate from the Git LFS master catalogue. Enrichment workers consume the sidecar asset references and write only approved visual metadata back to the visual layer. The canonical identifier catalogue is not rewritten by AI.

## Required production controls

1. Immutable original-image reference.
2. Deterministic SHA-256 hash where the source file is available.
3. Provenance and licensing status.
4. Model/provider/version recorded for every AI enrichment event.
5. Timestamp and enrichment job ID.
6. Confidence values for candidate detections.
7. Human-review status and reviewer/event audit trail.
8. Ability to invalidate or supersede an enrichment without deleting the original evidence.
