# Phase 21 — Adversarial and Archive-Safety Hardening

The field Toolkit handles customer security artifacts, so archive integrity must include hostile-input resistance rather than only happy-path hashes.

The air-gap verifier now rejects duplicate archive names, invalid artifact counts, manifest size mismatches and bundles above a bounded uncompressed-size limit. Delivery package inputs reject empty/ambiguous names and oversized packages.

These controls reduce archive confusion, resource-exhaustion and integrity-bypass risk. They do not replace malware scanning or safe extraction controls on the receiving workstation.
