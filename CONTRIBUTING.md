# Contributing

## Repository status

Tinlance FDSE Toolkit is a **publicly visible, proprietary Tinlance repository**. Public visibility is for transparency, collaboration and engineering reuse; it does not grant an open-source license or permission to redistribute proprietary source.

External contributions may be accepted at the maintainer's discretion. Before substantial work, open an issue or discussion describing the proposed change.

## Engineering workflow

Changes follow this sequence:

1. Audit the current implementation.
2. Check authoritative standards, current facts and dependency/security advisories where relevant.
3. Define acceptance criteria.
4. Implement the smallest complete change.
5. Add or update automated tests.
6. Reconcile documentation and the claims register.
7. Run local validation.
8. Open a pull request.
9. Require all applicable CI/security/compatibility checks to pass.
10. Review the merged result before beginning the next phase.

Do not skip a failed gate by weakening the test or changing a requirement without documenting the reason.

## Field-operation safety

Never execute scanners, collectors or tests against customer or third-party infrastructure without explicit authorization and documented scope.

Do not submit customer evidence, secrets, credentials, private keys or personal data to this public repository.

Use synthetic fixtures for tests and examples.

## Documentation changes

Documentation must describe the maintained implementation, not recovered historical artifacts. If a capability is not implemented or independently evidenced, state the limitation.

Avoid claims such as "100% bug-free", universal ROI, guaranteed detection performance or certified production readiness unless the repository contains release-specific evidence supporting the claim.

## Pull requests

A useful pull request should explain:

- what changed
- why it changed
- scope and affected components
- tests/checks performed
- security implications
- documentation/claims changes
- known limitations

Keep changes reviewable and avoid unrelated refactors.

## Review standard

A change is ready when:

- behavior is covered by appropriate tests
- security boundaries remain intact
- documentation matches the implementation
- claims remain evidence-backed
- required workflows are green

For phase work, the next phase does not begin until the previous phase is merged and its required gates are green.
