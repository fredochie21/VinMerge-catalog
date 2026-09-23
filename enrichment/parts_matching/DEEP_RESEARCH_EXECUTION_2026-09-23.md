# Parts Matching Deep Research Execution — 825 Model Slices

Generated: 2026-09-23

## Objective

Execute the resource map against every one of the 825 VinMerge model slices for:

1. positive vehicle identification;
2. exact configuration identification;
3. OEM part fitment;
4. OE supersession;
5. aftermarket cross-reference;
6. contradiction/review handling.

The authoritative 825-model master remains untouched. Research evidence belongs in enrichment/evidence layers and is linked back to the authoritative model identity.

## What is now complete

- 825/825 model slices are represented in `RESOURCE_BINDINGS_825_2026-09-23.json`.
- 825/825 model slices are represented in `RESEARCH_QUEUE_825_2026-09-23.json`.
- 85/85 makes are represented.
- Each slice has a deterministic evidence/resource class set, configuration dimensions, part-category scope and fitment gate.
- The queue is ordered by identifier risk, not by an arbitrary make-by-make preference.

## Evidence gate

A candidate source may discover a relationship, but it cannot automatically become authoritative fitment.

**Tier A:** OEM EPC/catalogue, OEM VIN/build documentation, OEM manuals/technical documentation, OEM TSB/service information.

**Tier B:** TecDoc/TecRMI, manufacturer aftermarket catalogues, OE cross-reference/supersession data.

**Tier C:** specialist catalogue interfaces such as PartSouq, Amayama, CATCAR, 7zap and comparable structured catalogues.

**Tier D:** public datasets, GitHub repositories, Wikidata/Wikipedia, forums, enthusiast communities, dealer/used-parts listings and visual sources.

Positive identification/configuration and vehicle-to-part fitment require authoritative or sufficiently corroborated evidence. Tier C/D material is primarily discovery/corroboration unless the source exposes traceable manufacturer catalogue data.

## Required reasoning chain

`VIN/chassis/model code -> exact configuration -> applicable OEM catalogue -> OEM part -> supersession -> aftermarket number -> corroboration -> Fitment Master status`

The following shortcuts are prohibited:

- model name alone -> fitment;
- shared engine -> identical part;
- visual similarity -> interchangeability;
- generic aftermarket listing -> exact configuration fitment;
- AI inference -> authoritative VIN/configuration/OEM fitment;
- unresolved contradiction -> verified result.

## Part-category coverage

Passenger/light-commercial slices cover braking, suspension/steering, engine service, engine hard parts, transmission, cooling, electrical, body, wheels/hubs and HVAC.

Commercial slices additionally use the commercial vehicle part scope for chassis, axle, brake, clutch, engine and service systems.

## Output states

`QUEUED` -> `IDENTITY_PARTIAL` / `IDENTITY_VERIFIED` -> `CONFIGURATION_PARTIAL` / `CONFIGURATION_VERIFIED` -> `FITMENT_CANDIDATE` -> `FITMENT_VERIFIED`

Any contradiction, insufficient evidence, unsupported inference or source conflict becomes `REVIEW_REQUIRED`; absence of adequate evidence becomes `BLOCKED_NO_EVIDENCE`.

## Important distinction

"825/825 processed" means every model has an assigned research path. It does **not** mean 825 models have verified vehicle identification, 825 exact configurations, or 825 vehicle-to-part fitments.

## Current external evidence anchor

TecAlliance currently describes TecDoc as a standardised aftermarket data platform combining vehicle linkages with article data and supporting VIN, OE-number and part-reference searches. This makes it a major Tier B resource, but it does not replace OEM evidence for authoritative East-African/JDM configuration decisions.

Source: https://www.tecalliance.net/solutions/tecdoc

## Next execution layer

The next evidence-producing pass should populate model-specific evidence records from the queue without changing the authoritative master. Verified relationships then feed the Fitment Master through controlled review gates.
