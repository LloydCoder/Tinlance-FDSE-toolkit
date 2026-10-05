# Phase 16 — Automated Test Architecture

The maintained Toolkit now has unit/integration-style coverage for contracts, evidence integrity, adapters, risk correlation, reporting, identity scanning, scope controls, IR playbooks, regulatory assessments, ROI, delivery encryption, air-gap packaging, binary build command construction, and SBOM generation.

CI now runs pytest with coverage against the maintained fdse_toolkit package and enforces a 70% minimum. Hypothesis adds property coverage for the fail-closed scope boundary.

The recovered legacy implementation remains forensic reference and is intentionally excluded from the maintained-package coverage target until each component is migrated and independently tested.

Future phases add adversarial/fuzz/security suites rather than treating line coverage as proof of security.
