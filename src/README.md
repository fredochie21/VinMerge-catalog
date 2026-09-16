# VINMERGE Application Source

Morris's existing application code should be transferred here, preserving its current working structure where practical.

Application code must consume the catalog through explicit interfaces rather than embedding or duplicating the master vehicle dataset.

Recommended future service boundaries:

- identifier resolution
- vehicle search
- parts search / fitment
- inventory and supplier availability
- image enrichment
- AI assistance
- transaction and order services

Existing application functionality takes precedence during the initial transfer; refactoring should follow after the application is safely represented in this repository.
