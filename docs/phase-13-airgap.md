# Phase 13 — Air-Gap Mode

The historical air-gap builder was audited and contained legacy concatenated code, duplicate entry points/version constants, and an embedded personal contact address. The maintained builder is a small offline-only package constructor with an explicit manifest and verification routine.

The builder does not claim that the historical binaries are portable. Binary compatibility, signatures, SBOMs, and clean-environment execution are separate release gates.

The offline bundle records every included regular file with SHA-256 and rejects unsafe paths. Verification reads the bundle without network access and checks every artifact digest.
