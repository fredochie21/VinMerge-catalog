# VINMERGE Architecture Baseline

## 1. Data foundation

The Identifier Intelligence Master is the canonical Phase 1 vehicle identity layer.

`VIN / Chassis / Frame / Model Code → Make → Model → Series / Trim / Grade → Generation → Production / Model Year → Engine → Transmission → Vehicle Configuration`

## 2. Layer separation

### Identifier intelligence
Canonical vehicle identity and identifier resolution.

### Fitment intelligence
Future mapping of resolved vehicles to parts, OE numbers, aftermarket numbers and compatibility rules.

### Inventory intelligence
Dealer stock, quantity, location, price, availability and supplier information.

### Media intelligence
Images and other media associated with stable vehicle/part identifiers, with source and confidence metadata.

### AI intelligence
AI-assisted interpretation, enrichment, classification and user assistance. AI output must remain distinguishable from authoritative source data.

### Transaction intelligence
Orders, payments, dealer balances, delivery, returns, refunds and settlement logic. This layer is separate from catalogue identity.

## 3. Resolution flow

User input → identifier normalization → identifier resolution → canonical vehicle → fitment lookup → inventory lookup → ranked availability → transaction.

The application should not skip identifier resolution merely because a make/model string is available.

## 4. East Africa scope

The initial market is Kenya, with architecture designed for Uganda, Tanzania, Rwanda and broader East Africa. Kenya-installed population and JDM-import relevance should remain important ranking signals.

## 5. Enrichment architecture

External data, images and AI-generated information should be additive enrichment. Each enrichment record should support provenance, source, timestamp, confidence and review state where applicable.

## 6. Change control

The master catalog is maintained separately from application code. Application changes are developed on feature/transfer branches and proposed to `main` through review.
