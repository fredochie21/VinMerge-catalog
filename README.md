# VINMERGE — Identifier Intelligence Master

AI-powered automotive spare-parts sourcing platform initially focused on Kenya and expanding across East Africa.

## Repository purpose

This repository contains the VINMERGE vehicle-identifier intelligence foundation and the application code that will consume it.

The master catalog is the authoritative Phase 1 identifier layer. It maps vehicle identifiers through:

`VIN / Chassis / Frame / Model Code → Make → Model → Series / Trim / Grade → Generation → Production / Model Year → Engine → Transmission → Vehicle Configuration`

Detailed parts fitment is a subsequent layer and must not corrupt the identifier master.

## Branch policy

- `main` — protected baseline and integration branch.
- `morris-initial-transfer` — initial application-code transfer and integration work for Morris.
- Feature work should use dedicated branches and be merged through pull requests.
- Do not directly modify or replace the master catalog on `main` during application development.

## Directory architecture

```text
catalog/    Authoritative VINMERGE master catalog and future versioned catalog assets
schemas/    Data contracts, JSON Schemas, API contracts and validation definitions
src/        Application and integration source code
scripts/    Import, validation, migration, enrichment and maintenance utilities
tests/      Automated tests for catalog integrity and application integration
docs/       Architecture, handover, data governance and operating documentation
```

## Master catalog

The current baseline is:

`catalog/VINMERGE_East_Africa_MASTER_CATALOG_825_CUMULATIVE_AI_IMAGE_PUBLIC_ENRICHMENT_2026-09-15.json`

The catalog is tracked with Git LFS. Do not convert it to an ordinary Git blob or commit an alternative copy under another filename without an explicit versioning decision.

## Application integration principles

1. Treat the catalog as a data service/source of truth, not as application business logic.
2. Resolve identifiers before attempting parts-fitment logic.
3. Preserve source identifiers exactly; normalize only in dedicated normalized fields.
4. Never silently overwrite conflicting identifier evidence.
5. Record provenance, confidence and enrichment state for machine-generated or externally enriched data.
6. Design image enrichment as a separate, expandable layer linked to vehicle/part entities by stable identifiers.
7. AI enrichment must be auditable and must not silently replace authoritative catalogue data.
8. Kenya relevance and East African/JDM coverage are first-class requirements.

## Morris initial transfer

Morris should transfer the existing application into `morris-initial-transfer` first. The transfer should preserve existing functionality while separating application code from the authoritative catalog.

Before merge to `main`, changes should be reviewed for:

- catalog integrity
- schema compatibility
- identifier-resolution behaviour
- API/data-contract compatibility
- secrets and credentials (none committed)
- test coverage
- deployment/configuration impact

## Security

Never commit API keys, passwords, payment credentials, private customer data, production database dumps, or environment secrets. Use environment variables or an approved secret-management mechanism.
