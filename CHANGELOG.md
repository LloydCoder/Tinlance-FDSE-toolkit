# Changelog

## Unreleased

### Phase 1 — Repository reconstruction
- Restored the historical v2 implementation into a traceable legacy tree.
- Added a maintained Python package boundary under src/fdse_toolkit/.
- Added Python project metadata and development dependency groups.
- Added repository architecture and contribution/security documentation.
- Explicitly separated historical claims from verified release status.

## Enterprise reconstruction

### Phases 18–23
- Removed recovered legacy/upload-only artifacts from the active tree after forensic reconciliation.
- Added field operations and enterprise release gates.
- Added release artifacts, SBOMs, resolved dependency snapshots, SHA-256 manifests and tag-based provenance attestation.
- Added the private FDSE operator CLI.
- Added adversarial archive/delivery hardening.
- Added Linux/Windows/macOS and Python 3.11–3.14 source compatibility testing.
- Hardened evidence writes for Windows filesystem behavior and streamed air-gap integrity verification.
