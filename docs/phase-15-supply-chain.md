# Phase 15 — Supply-Chain and SBOM Controls

The Toolkit now generates a CycloneDX 1.5-style SBOM from the active Python environment. Each component records its package name, version, and PyPI package URL.

The SBOM is a release artifact, not a vulnerability verdict. Dependency vulnerability scanning, license policy, lockfile enforcement, signed SBOMs, and provenance attestation are release gates and are tightened in the CI/release phase.

The historical package had no dependency metadata or lock strategy. The maintained pyproject establishes declared dependencies; release engineering must additionally freeze/verify the exact dependency graph used for each artifact.
