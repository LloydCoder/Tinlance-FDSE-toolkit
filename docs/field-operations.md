# FDSE Field Operations

## Engagement lifecycle
1. Confirm client identity, written authorization, scope, exclusions, dates and escalation contacts.
2. Create a unique engagement identifier and classify client data before collection.
3. Register authorized assets and collection methods. Do not expand scope from discovered infrastructure.
4. Ingest upstream evidence through supported adapters or controlled file handoff.
5. Validate contracts, preserve provenance and compute evidence identities.
6. Correlate findings deterministically and assign severity/confidence with evidence references.
7. Generate reports, IR playbooks and ROI analysis from the canonical engagement data.
8. Encrypt delivery artifacts using the maintained authenticated package builder; transfer the password through a separate channel.
9. Conduct remediation verification/retest only against explicitly authorized targets.
10. Close the engagement by revoking temporary access, recording evidence disposition and completing the handoff.

## Safety boundary
The Toolkit does not grant authorization. Authorization comes from the engagement record and the upstream Tinlance governed execution layer. A discovery result never becomes permission to scan a new target.

## Data handling
- Never place raw credentials, API tokens or private keys in findings, logs or case studies.
- Keep customer evidence in an engagement-specific workspace with least-privilege filesystem permissions.
- Treat reports and delivery packages as confidential by default.
- Do not upload customer evidence to public issue trackers, public repositories or uncontrolled third-party services.
- Retain or delete customer material according to the signed engagement terms and applicable law.

## Upstream ecosystem boundary
ThreatFade, ReconOS, BugFlow, FAS, AI Shield, TwinGuard and KalevioAI remain authoritative for their own domain outputs. The Toolkit packages and correlates evidence; it does not silently reinterpret upstream authority.

## FDSE operator principle
This is a personal field engineering system, not a customer-facing product. The objective is to let one senior operator deliver repeatable, defensible enterprise security work without turning the Toolkit into a second security platform.
