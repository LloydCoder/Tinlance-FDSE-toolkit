# Phase 3 — Evidence Integrity and Provenance

The Toolkit now has a content-addressed evidence store. Evidence is copied into an object store named by its SHA-256 digest; metadata is recorded in a versioned manifest; each collection event is recorded in an ordered hash chain.

This design follows the core evidence principles identified by NIST: identify, label, record, acquire, preserve integrity, and maintain chain of custody. NIST defines chain of custody as tracking movement through collection, safeguarding, and analysis while recording handlers, time, and purpose. See NIST SP 800-86 and the NIST CSRC chain-of-custody glossary.

## Security properties
- Evidence objects are addressed by SHA-256.
- Source files are copied, never modified in place.
- Metadata is validated against the canonical evidence schema.
- Manifest and chain records are written atomically.
- Evidence and metadata files are created with restrictive permissions where supported.
- Chain events contain the previous event hash and their own hash.
- Verification detects evidence-object modification, manifest schema violations, event modification, and event deletion/reordering.

## Limitation
A hash chain is tamper-evident, not a substitute for an externally anchored digital signature. Release signing and external anchoring belong to later security/release phases.

## Operational rule
Do not ingest real customer evidence into tests. Field evidence must be collected only under documented authorization and scope.
