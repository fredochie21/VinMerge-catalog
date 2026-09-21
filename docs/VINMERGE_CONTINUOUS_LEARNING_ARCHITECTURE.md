# VinMerge Continuous Learning & Enrichment Architecture

## Purpose

VinMerge must continuously improve from real-world vehicle, part, inventory and search evidence without allowing unverified AI output to silently become authoritative fitment.

This architecture adds a controlled learning layer around the frozen authoritative catalogue.

## Non-negotiable rule

The authoritative 825-model catalogue on `main` remains unchanged by learning events.

Learning data is additive evidence and research state. Only verified records may influence production fitment resolution.

## Learning loop

Customer/dealer activity
→ ingestion event
→ normalization
→ identity/fitment analysis
→ research case when unresolved
→ evidence collection
→ review
→ verification
→ publish to VinMerge enrichment/fitment layer
→ future searches use the verified knowledge

## Inputs

- VIN/chassis searches, including unresolved searches
- vehicle identity and variant observations
- part numbers and OEM numbers
- aftermarket and interchange references
- vehicle-to-part fitment observations
- engine/transmission/drivetrain identifiers
- dealer inventory feeds and uploads
- product images and visual enrichment events
- supplier-provided specifications
- human corrections and reviewer decisions
- approved external research evidence

## Unresolved search handling

A failed lookup must not be treated as a dead end.

Create a research case containing, where available:

- search/event ID
- VIN or chassis input (with appropriate privacy controls)
- normalized identifier fields
- detected make/model/year clues
- engine/transmission/drivetrain clues
- market/region
- requested part or component
- matching attempts performed
- reason for failure
- source evidence
- confidence
- review status
- timestamps

## Research states

`DISCOVERED → RESEARCHED → EVIDENCE_ATTACHED → REVIEW_REQUIRED → VERIFIED → PUBLISHED`

Rejected or superseded research must remain auditable rather than being silently deleted.

## Three outcomes

### Vehicle unknown

Research vehicle identity and family/generation relationships.

### Vehicle known, fitment unknown

Research the exact vehicle configuration and vehicle-to-part relationship.

### Vehicle and fitment known, inventory unavailable

Do not create catalogue facts. Route the request to inventory/sourcing workflows.

## Family enrichment

When a verified discovery establishes a family relationship, related models may be queued for enrichment. The system must preserve the distinction between:

- confirmed relationship
- proposed relationship
- unresolved relationship

No family expansion should be inferred solely from naming similarity.

## Evidence and confidence

Every proposed fact should retain:

- source type
- source reference
- observed value
- normalized value
- evidence timestamp
- confidence
- reviewer
- review status

AI may normalize, classify, suggest and identify candidate relationships. AI alone does not establish authoritative VIN identity, exact fitment, interchangeability or supplier-stock truth.

## Production boundary

Production matching may consume:

- the frozen authoritative catalogue
- verified enrichment records
- verified fitment relationships
- verified cross-reference relationships

Production matching must not consume records marked:

- `discovered`
- `planned`
- `review_required`
- `rejected`
- `superseded`

## East Africa feedback loop

The research queue should be prioritized using real regional demand signals such as:

- frequency of unresolved searches
- requested parts
- repeated chassis patterns
- dealer inventory gaps
- fitment ambiguity
- commercial relevance

This allows VinMerge to become more useful from actual East African usage instead of attempting to pre-research every possible vehicle.

## Integration principle

This layer is intentionally independent of the authoritative master catalogue and can be integrated into DDS before or during Morris's platform transfer.

No change to the 825-model master is required.
