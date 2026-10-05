# Tinlance FDSE Toolkit

**Forward-Deployed Security Engineer field toolkit — private Tinlance engineering system.**

## Purpose
This repository is the private operating toolkit used by a Tinlance Forward-Deployed Security Engineer to execute authorized customer security engagements. It packages engagement evidence and outputs from specialized Tinlance systems into defensible reports, playbooks, business-impact analysis, secure delivery packages, and offline/air-gapped artifacts.

It is not a customer SaaS, multi-tenant platform, detection engine, compliance authority, or replacement for the Tinlance Agent Platform, ThreatFade, ReconOS, BugFlow, FAS, AI Shield, TwinGuard, or KalevioAI.

## Current status
The historical v2 artifact has been recovered and preserved. The project is undergoing forensic-to-enterprise reconstruction. Historical claims such as 100% complete, fully tested, ROI validation, binary compatibility, secure portal behavior, and regulatory correctness are treated as claims under verification.

## Engineering sequence
1. Forensic baseline and evidence freeze — complete
2. Repository reconstruction — in progress
3. Engagement/domain contracts
4. Evidence and provenance
5. Ecosystem adapters
6. Finding correlation and risk
7. Enterprise reporting
8. Identity scanner hardening
9. Authorized network assessment
10. IR playbook engine
11. Regulatory intelligence
12. ROI/business-impact engine
13. Secure delivery
14. Air-gap mode
15. Binary/reproducible builds
16. Supply-chain security/SBOM
17. Automated tests
18. Adversarial/security verification
19. CI/release engineering
20. FDSE field certification

## Architecture boundary
Customer authorization -> scoped collection -> specialized Tinlance tools -> canonical engagement data -> evidence/provenance -> finding correlation -> reports/playbooks/ROI -> secure delivery -> retest -> closure.

The Tinlance Agent Platform remains the governed execution authority. The Toolkit does not duplicate identity, authorization, policy, approvals, runtime, sandbox, secrets, budgets, audit, or observability responsibilities.

## Repository layout
- legacy/ — recovered historical implementation; forensic reference until each component is migrated and tested.
- src/fdse_toolkit/ — target maintained package namespace.
- docs/ — architecture, forensic records, references, claims and engineering documentation.
- Tinlance-FDSE-toolkit/ — preserved historical release artifacts.
- tests/ — automated tests, added component-by-component after behavior is characterized.

## Development rule
Never start a phase by assuming partial implementation is complete. Audit the current implementation, research current standards, implement the smallest complete change, test it, reconcile documentation, and require a green CI gate before the next phase.
