# VinMerge Vincario Evidence & Enrichment Integration Note

**Date:** 2026-09-23  
**Scope:** research/enrichment architecture only.  
**Authoritative 825-model master:** unchanged.

## Decision

Vincario is treated as an **optional external VIN identity/configuration evidence source**, not as the VinMerge catalog and not as the authoritative parts-fitment engine.

No paid catalogue dependency is introduced.

## What the Vincario documentation adds to our approach

The documented API response model confirms that a useful VIN evidence record can contain more than make/model/year. Relevant fields include:

- VIN
- provider vehicle ID
- make/model IDs
- make/model
- model year
- series
- version
- variant
- vehicle specification
- product/body type
- market
- steering
- drive
- engine displacement/power/code/model/type
- fuel type/system
- transmission/full transmission and gears
- production start/stop
- build/registration dates where available
- manufacturer and plant
- check digit and sequential number
- dimensions, wheelbase and track
- brakes and suspension
- emissions
- selected equipment/specification fields

These fields should inform our canonical schema and evidence collection, but provider identifiers and values remain **external observations** until corroborated.

## Revised identity/configuration chain

Submitted VIN/chassis
        ↓
Identifier validation + routing
        ↓
VIN structure / chassis evidence
        ↓
External provider observation (optional)
        ↓
Canonical vehicle identity
        ↓
Version / variant / model-code / build context
        ↓
Exact configuration
        ↓
OEM / dealer / customer evidence
        ↓
Parts candidate
        ↓
Fitment verification

A successful external VIN decode therefore establishes an **identity/configuration candidate**, not automatic part fitment.

## Field-level evidence policy

For every external observation, preserve:

- source/provider
- queried identifier
- captured timestamp
- raw response or immutable response reference
- provider vehicle/make/model IDs
- returned field/value
- canonical VinMerge field mapping
- evidence tier
- contradiction flag
- review status
- promotion status

Do not overwrite an authoritative VinMerge field merely because an external provider returns a value.

## Contradiction handling

The supplied Land Rover benchmark demonstrates why field-level review is required. The returned record includes potentially inconsistent or questionable values, including wheel rim size versus wheel-size text and a field labelled Engine Torque (RPM) whose label/value pairing requires validation.

Therefore:

- preserve the raw provider observation;
- map only semantically clear fields automatically;
- flag questionable fields;
- corroborate configuration-critical fields;
- do not let one anomalous field invalidate an otherwise useful identity observation;
- do not silently repair provider data.

## Identifier routing

### 17-character VIN

Use the normal VIN route:

1. validate length/characters/structure;
2. apply VinMerge VIN rules;
3. optionally query external VIN providers;
4. collect make/model/year/version/variant/configuration observations;
5. corroborate critical fields;
6. continue to OEM/dealer/customer fitment evidence.

### Chassis/frame/model-code identifier

Do **not** treat failure of a generic 17-character VIN decoder as a vehicle-not-found result.

Route instead through:

- regional/JDM frame databases;
- OEM EPC/catalogue identifiers;
- manufacturer model-code documentation;
- engine/transmission/chassis evidence;
- dealer/customer observations.

## Learning from DDS

Dealer upload → VIN/chassis + vehicle claim → part/OE/brand/dimensions/images → inventory observation → customer search/enquiry → order/installation outcome → return/correction/rejection → evidence aggregation → corroboration/review → Fitment Master.

Dealer and customer observations must not become authoritative solely because they are repeated. Repeated independent successful observations strengthen a relationship; returns, corrections and failed installations are retained as negative evidence.

## Confidence separation

Maintain separate statuses for:

- **IDENTITY_STATUS**
- **CONFIGURATION_STATUS**
- **FITMENT_STATUS**
- **SOURCE_CONFIDENCE**
- **REVIEW_STATUS**

Example: identity_status = VERIFIED_CANDIDATE; configuration_status = STRONG_CANDIDATE; fitment_status = NOT_ESTABLISHED; source_confidence = EXTERNAL_PROVIDER; review_status = CORROBORATION_REQUIRED.

This prevents a detailed VIN decode from being mistaken for verified parts compatibility.

## Provider independence

VinMerge must remain operational if Vincario is unavailable.

Therefore:

- no Vincario vehicle IDs become canonical primary keys;
- no provider response is required for all searches;
- no provider-specific field is mandatory where equivalent internal evidence exists;
- provider usage is measurable and auditable;
- external provider cost/credit usage is tracked separately;
- dealer/customer evidence can progressively reduce dependence on external identity enrichment.

## Golden-test use

The existing five identifier test cases remain the controlled benchmark:

- VM-01: SALLAAA138A474049 — 17-character VIN
- VM-02: DB42-0031215 — chassis/frame
- VM-03: WDD2120542A95813 — 17-character VIN
- VM-04: FJA300-4057096 — chassis/frame
- VM-05: WVIZZZ2HZEAO12141 — 17-character VIN

VM-01's observed Vincario response is retained as benchmark evidence. Remaining test cases should be used strategically; credits must not be consumed merely to populate fields.

## Catalog design consequence

The Vincario documentation strengthens, rather than changes, the existing VinMerge design:

**VinMerge should capture rich vehicle identity/configuration evidence first, then learn parts relationships from authoritative sources plus real DDS dealer/customer outcomes.**

The 825-model authoritative master remains controlled. Research/enrichment layers can grow around it without silently rewriting the master.

## Explicit non-goals

This note does not:

- purchase or require an external parts catalogue;
- make Vincario a parts catalogue;
- declare any part compatible solely from a VIN decode;
- promote external observations into authoritative Fitment Master records;
- alter the 825-model master;
- expose API credentials;
- require Vincario for production operation.