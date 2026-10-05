# Phase 4 — Ecosystem Adapter Layer

The Toolkit now has a narrow normalization boundary for upstream security tools. Adapters convert external findings into the canonical FDSE finding contract while retaining the original evidence reference.

Initial adapters:
- Generic JSON findings
- SARIF 2.x-style results

The raw upstream output remains evidence. The adapter is not allowed to manufacture missing evidence references. If an imported result has no separate evidence ID, the caller must first register the raw source artifact with the EvidenceStore and provide that ID.

Future adapters for ThreatFade, ReconOS, BugFlow, FAS, AI Shield, TwinGuard, and KalevioAI must be implemented against their actual versioned output contracts after those repositories are independently audited. No speculative fields are hard-coded as facts.

STIX/TAXII are integration candidates for later intelligence-sharing workflows; they are not required to make the private FDSE Toolkit core operational.
