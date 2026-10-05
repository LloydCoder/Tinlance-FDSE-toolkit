# Phase 2 — Canonical Engagement and Domain Contracts

## Decision
The Toolkit uses JSON Schema Draft 2020-12 for canonical engagement-domain contracts. JSON Schema 2020-12 is the current published JSON Schema specification and supports explicit schema identifiers and structural validation.

## Contract principles
- Every canonical object has an explicit schema version.
- IDs are stable and typed by prefix.
- Findings reference evidence; they do not contain raw secret material.
- Evidence carries SHA-256 integrity and provenance metadata.
- Scope and authorization are explicit engagement data.
- Regulatory statements distinguish legal requirements, guidance, and Tinlance recommendations.
- Delivery artifacts are content-addressed by SHA-256.
- Unknown values use explicit status/confidence fields rather than invented facts.
- Runtime schema resolution is local-only; validation must not fetch schemas from the network.

## Schemas
- engagement
- asset
- evidence
- finding
- remediation
- incident
- delivery-manifest

## Compatibility policy
Schema changes that alter required fields or semantics require a new schema version and migration strategy. Additive optional fields may remain within a minor compatibility release when consumers are tolerant of unknown fields at the integration boundary.

## Boundary
These contracts define FDSE Toolkit domain data. They do not redefine the authority model of the Tinlance Agent Platform or FAS.
