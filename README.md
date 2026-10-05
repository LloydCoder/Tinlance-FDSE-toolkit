# Tinlance FDSE Toolkit

**Private Forward-Deployed Security Engineer field toolkit for Tinlance Limited.**

## Purpose
This repository is the private operator toolkit used by a Tinlance FDSE (Forward-Deployed Security Engineer) during authorized customer engagements. It turns evidence and structured outputs from the Tinlance security ecosystem into defensible findings, reports, incident playbooks, business-impact analysis, secure delivery packages and offline artifacts.

It is not a customer SaaS, detection engine, compliance authority, multi-tenant platform, or replacement for the Tinlance Agent Platform, ThreatFade, ReconOS, BugFlow, FAS, AI Shield, TwinGuard, KalevioAI or other upstream systems.

## Operating boundary
customer authorization → scoped collection → upstream Tinlance systems → canonical engagement data → evidence/provenance → finding correlation → reports/playbooks/ROI → secure delivery → retest → closure

The Tinlance Agent Platform remains the governed execution authority. This Toolkit does not duplicate identity, authorization, policy, approvals, runtime, sandbox, secrets, budgets, audit or observability authority.

## Enterprise reconstruction status
The recovered historical v2 package is forensic source material, not the current release. Historical statements such as “100% complete”, “zero bugs”, universal ROI validation, binary compatibility, or an expiring download portal are not accepted without evidence.

The active repository now contains the maintained implementation only. Historical upload artifacts and legacy source copies have been removed from the active tree after reconciliation; their Git history remains the forensic record.

## Maintained capabilities
- Versioned engagement, evidence, finding, asset, incident, remediation, regulatory and ROI contracts.
- Evidence provenance and integrity primitives.
- SARIF/generic JSON adapters for upstream tooling.
- Deterministic finding correlation and risk prioritization.
- Validated PDF/DOCX/XLSX report generation.
- Offline-first identity/secret exposure scanning with redaction and bounded input size.
- Explicit field-operation scope controls.
- Governed incident-response playbook generation.
- Source-backed regulatory assessment records.
- Assumption-driven ROI analysis with sensitivity analysis.
- Authenticated AES-256-GCM delivery packages with SHA-256 manifests.
- Offline/air-gap bundle creation and verification.
- Controlled PyInstaller binary builds.
- CycloneDX-style SBOM generation.

## CI gates
Every pull request to main must pass the functional CI and security CI workflows. The maintained package currently enforces automated tests, property testing and a minimum 70% coverage threshold, plus dependency vulnerability auditing and Bandit static analysis.

Green CI is necessary but not sufficient for enterprise certification. Release certification also requires artifact provenance, signed release metadata, compatibility evidence, operator acceptance and claims reconciliation.

## Repository layout
- src/fdse_toolkit/ — maintained implementation.
- schemas/ — canonical external JSON schemas.
- tests/ — maintained automated tests.
- docs/ — architecture, field operations, forensic audit and release evidence.
- .github/workflows/ — required CI/security gates.

## Engineering rule
For every phase: audit the current implementation first, research applicable standards/current facts, implement the smallest complete change, test adversarially, reconcile documentation, require green CI, then proceed. Never promote a historical claim to a product claim without evidence.
