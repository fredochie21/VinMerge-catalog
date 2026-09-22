# VINMERGE Visual Ingestion — Production Handover to Morris

## Handover status

The visual-ingestion boundary is ready for developer integration from the current repository baseline. The identifier master catalogue remains authoritative and is not rewritten by the visual pipeline.

## What is implemented

- deterministic visual ingestion script;
- strict JSON-schema validation of incoming manifests and generated sidecars;
- bounded, root-confined local-file ingestion;
- symlink/path-traversal rejection;
- SHA-256 hashing with per-run file identity caching;
- configurable local-file size limit;
- atomic output writes with overwrite protection;
- provenance and licensing fields;
- cross-field review/licensing invariants;
- duplicate asset-ID validation;
- verified-asset image-reference guard;
- CI validation for compilation, tests, manifest validation, sidecar generation and sidecar validation;
- AI visual-enrichment boundary and event contract;
- Stage 2 enrichment specification.

## What Morris must integrate

### 1. Storage adapter
Connect file_path, storage_key, url, thumbnail_url and original_image_ref to the production object/image store. Preserve the original upload as immutable evidence. Local ingestion must remain confined to an explicitly configured ingestion root.

### 2. Upload endpoint
Accept dealer/customer uploads and create an ingestion manifest entry with a unique asset_id and the correct canonical_record_id supplied by the application/catalogue layer.

### 3. Processing worker
Run validation, hashing, image-quality/normalization processing and then the selected vision model/provider. Do not let the model write authoritative vehicle identity or fitment.

### 4. AI enrichment event
Persist the versioned enrichment event with provider, model ID/version, timestamp, input hash, candidate outputs, confidence, quality flags and review state.

### 5. Review queue
Expose pending_review, verified, rejected and archived states. A verified asset must have a usable image reference and permitted licensing. AI output remains advisory until approved by the review workflow.

### 6. Application read path
The application should resolve:
canonical_record_id → visual sidecar → eligible verified visual assets.
Do not duplicate vehicle definitions inside the visual layer.

### 7. Production tests
Add integration tests for upload → storage → ingestion → enrichment event → review → application retrieval, including duplicate uploads, rejected images, missing references, unsupported media and superseded assets.

## Explicit non-goals

Do not:

- rewrite the Git LFS master catalogue from the image pipeline;
- infer VIN/chassis/frame identity from an image alone;
- declare OEM fitment or interchangeability from AI output alone;
- treat supplier stock as a visual inference;
- expose unverified dealer/customer images as verified product imagery.

## Acceptance criteria

Morris can consider the handover complete when a real test upload can be traced end-to-end using its asset_id and canonical_record_id, with immutable original reference, hash, provenance, AI enrichment event, review status and final application retrieval all auditable.

## Reference files

- visual/ingestion/ingest_visual_assets.py
- visual/ingestion/ingestion-manifest.example.json
- schema/vinmerge-visual-ingestion-manifest.schema.json
- schema/vinmerge-visual-index.schema.json
- schema/vinmerge-visual-intelligence.schema.json
- visual/ingestion/ai-enrichment-contract.json
- visual/ingestion/enrichment-event.example.json
- visual/ingestion/AI_VISUAL_ENRICHMENT_SPEC.md
- .github/workflows/visual-ingestion-ci.yml
