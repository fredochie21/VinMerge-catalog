# VinMerge Parts Product Master and Image Linking Contract

**Status:** additive proposal, version 1.0.0. This branch does not alter the authoritative 825-vehicle LFS master or current visual sidecar schemas.

## Purpose and ownership

VinMerge is the authoritative catalog/intelligence layer for canonical part identity, part-number references, fitment claims and reference-image associations. DDS remains the marketplace/platform and owns dealer accounts, raw uploads, import batches, stock quantities, prices, condition, availability, listing publication, orders and actual-stock photographs.

DDS currently has local `PartsProduct` and `FitmentMaster` persistence. Treat those as the platform's current operational implementation/projection until an explicit, tested VinMerge synchronization contract is implemented. This proposal does not move or migrate those tables.

## Contracts added

- `schema/vinmerge-parts-product.schema.json`: canonical part identity, taxonomy, attributes and provenance.
- `schema/vinmerge-part-number-reference.schema.json`: one record per OEM, aftermarket, manufacturer, supplier, distributor, dealer SKU or legacy identifier.
- `schema/vinmerge-part-fitment.schema.json`: explicit part-to-vehicle relationship, constraints, evidence and review state.

The schemas deliberately do not define a new visual-asset schema. The existing VinMerge visual sidecar remains the reference-image system.

## Product identity versus reference numbers

A canonical product identifies a defined component/product identity. Each identifier is a separate record linked by `canonical_part_id`. Keep the raw submitted value unchanged. `value_normalized` is a lookup key only; preserve alphabetic prefixes and all meaningful characters.

A dealer SKU is not an OEM number. A part number is not proof of vehicle fitment. A similar description or image is not proof of equivalence. Cross-reference relationships (`EQUIVALENT`, `SUPERSEDES`, `SUPERSEDED_BY`, `ALTERNATIVE`) require evidence and independent review before verified use.

## Fitment

Fitment is an explicit relationship from a canonical part to an existing VinMerge vehicle/profile/configuration reference. Do not copy or redefine the 825-model vehicle master in the parts domain. A `VERIFIED` fitment requires evidence, reviewer identity and timestamp. Product recognition does not establish fitment.

The status/level vocabulary is designed to map to the DDS Fitment Master service. Before runtime integration, reconcile against the deployed branch's actual migration vocabulary and the pending DDS CI-remediation PR; do not assume that a schema enum alone updates the database.

## Images: reuse the existing visual sidecar

The current visual index is keyed by `canonical_record_id`. For a part reference image, use the stable `canonical_part_id` as that record key; retain the existing visual asset contract and ingestion pipeline. Existing asset metadata already carries source type/name/reference, licence status, verification status, hash, storage reference, asset type and role.

Use these existing concepts consistently:
- catalogue/manufacturer image: `asset_type=actual_product` (or `reference_image` where it is only a generic reference), source type `oem_public`, `supplier` or `licensed_catalogue`;
- dealer photo of the physical item: source type `dealer`, asset type `actual_product`, pending review until checked;
- packaging label: `asset_type=packaging`;
- diagram: `exploded_diagram` or `technical_illustration`;
- AI-generated or illustrative material must never be presented as actual stock.

A verified reference image does not prove a dealer owns the stock. DDS actual-stock images remain attached to the specific listing/inventory record and must not be collapsed into the canonical catalogue image. A later DDS integration should connect a `ListingImage` to its `listing_id`, `dealer_inventory_id` and resolved `canonical_part_id` without leaking dealer identity or exact location.

No image is a valid state. A missing image must not block inventory ingestion; use a neutral no-image presentation where listing rules permit. Do not publish assets whose licence is unknown, pending, restricted or rejected.

## 1:1 upload reconciliation contract

Each DDS source row is preserved with its original payload and mapped through a source/dealer mapping profile. A row may resolve to one canonical product only when evidence supports that resolution. Multiple candidates produce review, not an arbitrary winner.

Recommended row outcomes:
- `MATCHED_EXACT`: exact verified identifier/issuer match.
- `MATCHED_CROSS_REFERENCE`: verified cross-reference match.
- `MATCHED_CORROBORATED`: multiple independent references converge under a versioned policy.
- `REVIEW_REQUIRED`: ambiguous, conflicting or candidate-only match.
- `UNRESOLVED`: insufficient identity evidence.
- `REJECTED_INVALID`: invalid or unsafe source row.

Repeated feeds must be idempotent using dealer + source system + stable source row key. Row number is only a fallback and must not be treated as a durable source identity when feed order can change.

## Safe integration sequence

1. Merge and validate these VinMerge contracts independently of the vehicle master.
2. Implement curated part/product/reference records with provenance and review.
3. Add a versioned VinMerge part-reference export/API contract.
4. Extend DDS importer to preserve source rows and mapping profiles, then resolve against verified references.
5. Add a DDS image association bridge for catalogue reference versus actual stock photos.
6. Add reconciliation, image-rights, fitment and privacy tests before production publication.

## Non-negotiable controls

- Never edit or regenerate the authoritative vehicle LFS master in this workstream.
- Never silently promote an unverified part number or cross-reference.
- Never infer fitment from vehicle model alone, description similarity or image similarity.
- Never merge distinct products solely because descriptions or images look alike.
- Never let AI output approve an identity, fitment or image licence.
- Preserve source values, provenance, conflicting evidence and review history.
- Keep test fixtures synthetic and excluded from production seeders/search.
