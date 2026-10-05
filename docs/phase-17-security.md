# Phase 17 — Security Verification Gate

The maintained package now has a dedicated security workflow for dependency vulnerability auditing and Bandit static analysis. GitHub repository secret scanning also provides a separate repository-level credential protection layer.

Security gates are distinct from functional tests: a package can be functionally correct while still carrying a vulnerable dependency or unsafe code pattern.

Critical/high security findings must not be silently waived. Any exception must be documented with scope, rationale, compensating control, owner, and expiry.
