# Enterprise Release Gate

A green CI run is a prerequisite, not the final enterprise gate.

## Mandatory evidence
- Maintained source and schemas are the only active implementation.
- Functional CI is green.
- Security CI is green.
- Dependency vulnerability policy is satisfied.
- Automated tests and property tests are green.
- Report, delivery, identity, scope, IR, ROI and air-gap regression fixtures pass.
- Release SBOM identifies the exact dependency graph.
- Build provenance identifies source revision, builder, build definition and dependencies.
- Release artifacts are signed and hashes are recorded.
- Supported OS/architecture matrix has actual clean-environment evidence.
- Operator acceptance confirms the field workflow.
- Claims register contains no unsupported production claims.
- Customer-data handling and retention procedure is documented.

## Explicit non-gates
The following are not sufficient evidence by themselves: a historical ZIP manifest, a successful demo, a single beta-user statement, line coverage alone, a benchmark from an upstream product, or a generated document that looks professional.

## Certification states
- DEVELOPMENT — changes are still being reconstructed.
- FIELD-READY — all functional/security gates pass and operator workflow is usable, but release provenance/compatibility evidence is incomplete.
- ENTERPRISE-CERTIFIED — every mandatory evidence item above is independently recorded for the exact release artifact.

No release may be labelled ENTERPRISE-CERTIFIED until the final state is supported by an immutable release record.
