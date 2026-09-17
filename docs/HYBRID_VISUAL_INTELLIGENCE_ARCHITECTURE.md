# VINMERGE Hybrid Visual Intelligence Architecture

## Purpose

VINMERGE will use a **hybrid visual system** rather than choosing between technical illustrations and real photographs.

The visual layer supports the identifier master and future parts-matching engine. It must remain additive: visual evidence can assist identification, but it must not silently replace authoritative VIN, chassis, frame, model-code, vehicle-configuration or validated fitment data.

## Visual hierarchy

1. **Exploded diagrams / technical illustrations** — identify where a component sits within a system and provide navigation through assemblies.
2. **Actual product photography** — confirm what the customer or dealer will physically receive.
3. **Installation/context imagery** — show the component in vehicle or installation context where useful.
4. **Packaging imagery** — support brand, label, part-number and package verification.
5. **Vehicle-context imagery** — provide orientation and visual confirmation for vehicle-specific components.

## Intended flow

`VIN / Chassis / Frame / Model Code`

→ `Vehicle Configuration`

→ `Vehicle System`

→ `Exploded Diagram / Technical Illustration`

→ `Diagram Hotspot / Component`

→ `Part / SKU`

→ `Actual Product Images`

→ `Installation / Packaging Images`

The same component can have multiple visual assets and multiple suppliers can contribute actual-product images without changing the canonical identifier record.

## Component-level visual fields

The implementation should support the following concepts on a component or future part/SKU record:

- `visual_assets[]`
- `asset_id`
- `asset_type`
- `role`
- `url`
- `thumbnail_url`
- `source.type`
- `source.name`
- `source.source_reference`
- `source.license`
- `status`
- `image_hash`
- `dimensions`
- `visual_tags[]`
- `ai_visual_metadata`
- `detected_part_labels[]`
- `detected_attributes[]`
- `duplicate_group_id`
- `normalization_status`
- `fitment_signal`
- `human_review_required`

The canonical JSON Schema is in `schema/vinmerge-visual-intelligence.schema.json`.

## AI role

AI is introduced now as an **enrichment and evidence layer**, not as the authority for fitment.

### AI can assist with

- visual part recognition from dealer/customer photographs;
- identifying likely component labels;
- extracting visual attributes such as shape, connector count and visible markings;
- image normalization and quality checks;
- duplicate-image detection;
- matching visually similar images to candidate component records;
- flagging apparent visual mismatches;
- generating search tags and image embeddings for future visual search.

### AI must not independently establish

- VIN identity;
- chassis/frame identity;
- exact vehicle configuration;
- OEM fitment;
- final interchangeability;
- supplier stock truth.

Those relationships require authoritative catalogue data, validated source data or an explicit human-review workflow.

## Why this architecture is onboarding-ready

The visual layer can start empty and grow organically as dealers, manufacturers, catalogues and users contribute assets. A part does not need an exploded diagram to be listed, and an exploded diagram does not need a product photograph to be useful.

This prevents the catalogue from becoming dependent on one image source while allowing VINMERGE to progressively build a proprietary visual intelligence layer.

## Recommended lifecycle

`Asset received`

→ `Source recorded`

→ `Image quality / normalization`

→ `AI enrichment`

→ `Duplicate / mismatch checks`

→ `Human review where required`

→ `Verified visual asset`

→ `Available to search / product UI`

## Data governance principle

Visual assets should reference canonical identifiers rather than duplicate vehicle or part definitions. This keeps the master catalogue normalized and allows image sources to be replaced, expanded or retired without restructuring the identifier intelligence core.
