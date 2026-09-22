# VINMERGE / DDS Transfer Readiness — 2026-09-22

## Authoritative baseline

The current VinMerge-catalog main branch remains the catalogue authority.

Morris's historical branch, morris-initial-transfer, is retained as reference only. It is not the integration baseline because it diverged from current main.

For application transfer, use the current DDS main as the DDS application baseline and consume VinMerge as the catalogue/data authority.

## Corrections completed for transfer

- Phase 2 workflow no longer uses pull_request_target.
- Phase 2 workflow uses contents: read only.
- The requested Phase 2 ref is allowlisted and is not interpolated into shell commands.
- The Phase 2 workflow no longer writes generated code back to the repository.
- Phase 2 coverage is evidence-gated; planned, error and evidence-empty slices cannot be reported as complete.
- Phase 2 research matches remain review-required until evidence supports the identity.
- Visual ingestion now validates both input manifests and generated sidecars against repository schemas.
- Visual local files are confined to an explicit ingestion root.
- Absolute paths, traversal outside the root and symlink traversal are rejected.
- Local image size is bounded and repeated hashing is cached per stable file identity.
- Visual output writes are atomic and existing output is protected from accidental overwrite.
- Verified visual assets require a usable image reference and permitted licensing.
- Visual pending/rejected review state is reflected in the generated review requirement.
- The Morris handover now carries the authoritative 64-character catalogue SHA-256.
- The visual handover references the existing visual-index schema filename.

## Catalogue protection

The authoritative 825-model Git LFS catalogue is not rewritten by the visual pipeline or application transfer.

Current catalogue SHA-256:
21a46da56c155f904be93b2062c09a2df2a667b307efd98c16862fe50faf0969

## Transfer boundary

Morris should integrate the DDS application against the current DDS main and treat VinMerge as the catalogue layer.

No payment implementation is introduced by this transfer-readiness work.

## Acceptance

This branch is intended to be reviewed and merged into VinMerge-catalog main before the active transfer work proceeds. The transfer should then be based on the resulting current main, not on morris-initial-transfer.
