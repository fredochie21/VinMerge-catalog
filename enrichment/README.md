# VinMerge Enrichment Layer

This directory contains contracts and supporting definitions for controlled continuous learning.

## Boundary

- The authoritative catalogue remains under `catalog/`.
- Enrichment events and research cases are evidence/state, not authoritative fitment.
- Verified records may be promoted into production-facing enrichment/fitment stores by the DDS/VinMerge integration.
- Unverified AI output must never silently overwrite the authoritative catalogue.

## Initial contracts

- `contracts/learning-event.schema.json` — normalized learning observations.
- `contracts/research-case.schema.json` — unresolved vehicle/fitment research workflow.

## Intended runtime flow

1. Capture search, inventory, part, image or human-correction event.
2. Normalize and deduplicate the observation.
3. Resolve against the current VinMerge catalogue.
4. Create a research case when identity or fitment remains unresolved.
5. Attach evidence and confidence.
6. Require review for facts that affect vehicle identity, fitment, interchangeability or supplier-stock truth.
7. Publish only verified knowledge to production matching.
8. Retain the event history for audit and future enrichment.

This foundation is deliberately additive and does not modify the 825-model master catalogue.
