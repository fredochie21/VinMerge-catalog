# VINMERGE Schemas

This directory contains versioned contracts between the master catalog and application services.

Planned contracts:

- `identifier-resolution` — VIN/chassis/frame/model-code resolution inputs and outputs
- `vehicle-entity` — canonical resolved vehicle structure
- `parts-fitment` — future fitment contract; do not implement by mutating the identifier master
- `image-enrichment` — future image references, provenance, confidence and enrichment status
- `ai-enrichment` — future machine-generated enrichment metadata with audit/provenance fields

Schema changes must be backward-compatible where practical and reviewed before integration into `main`.
