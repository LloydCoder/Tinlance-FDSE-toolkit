# Changelog

All notable maintained-repository changes are recorded here. Historical recovered-package claims are not treated as release evidence.

## Unreleased

### Documentation and repository health
- Rewrote the public README around the operator journey, installation, usage, boundaries and validation status.
- Added explicit public-visibility/proprietary-licensing language.
- Added private vulnerability-reporting guidance.
- Added community-health files and issue/PR templates.
- Added machine-readable project context through `llms.txt` and `llms-full.txt`.
- Removed stale internal citation artifacts from maintained documentation.

### Phase 25 — Field validation and pilot readiness
- Added the versioned field-validation contract and packaged schema.
- Added mandatory acceptance criteria and evidence-reference requirements.
- Added the synthetic validation record format.
- Added the field-pilot operator runbook.
- Clarified that real customer validation requires an authorized pilot.

### Phases 18–24
- Removed recovered legacy/upload-only artifacts from the active tree after forensic reconciliation.
- Added field operations and enterprise release gates.
- Added release artifacts, SBOMs, dependency snapshots, SHA-256 manifests and tag-based provenance attestation.
- Added the bounded private operator CLI.
- Added adversarial archive/delivery hardening.
- Added Linux/Windows/macOS and Python 3.11–3.14 source compatibility testing.
- Hardened evidence writes for Windows filesystem behavior and streamed air-gap integrity verification.
- Promoted compatibility testing to a continuous main-branch gate.
