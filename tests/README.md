# VINMERGE Tests

Tests should protect both the catalog and application integration.

Initial test categories:

- JSON/LFS catalog accessibility and parse validation
- identifier resolution
- vehicle configuration normalization
- duplicate/conflict detection
- schema compatibility
- API integration
- regression tests for transferred application functionality

No application merge to `main` should proceed with failing critical catalog or integration tests.
