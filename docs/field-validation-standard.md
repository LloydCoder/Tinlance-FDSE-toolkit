# FDSE Field Validation Standard

## Purpose

Phase 25 changes the release question from **"does the software pass CI?"** to **"can an authorized FDSE use the software to complete a realistic engagement workflow and produce defensible customer artifacts?"**

This standard is deliberately separate from engineering CI. Incident response and professional security testing require operational discipline, evidence, traceability, actionable findings and controlled delivery. The FDSE Toolkit therefore requires operational evidence before claiming field validation.

## Validation levels

### Level 0 — Engineering gate

Required before field validation:

- functional CI green
- security CI green
- compatibility matrix green
- release package/SBOM/hash validation green
- no unresolved release-blocking defects
- claims register reconciled

### Level 1 — Synthetic dry run

A controlled, non-customer environment exercises the complete operator path:

1. authorization/scope record
2. engagement creation
3. evidence intake
4. contract validation
5. finding correlation
6. report generation
7. incident-response playbook generation
8. assumption-driven ROI analysis
9. authenticated delivery package
10. air-gap bundle build/verification
11. evidence/artifact hashes
12. closeout record

A synthetic run proves workflow completeness, not customer acceptance.

### Level 2 — Authorized pilot

A real customer engagement is performed under written authorization and explicitly bounded scope.

Minimum requirements:

- signed authorization or equivalent contractual scope reference
- named operator and escalation contact
- target inventory and exclusions
- evidence-handling and retention rules
- customer-safe test scenario
- independent review of material findings
- customer-facing delivery
- documented acceptance or remediation/retest decision

### Level 3 — Field-proven release

A specific tagged release may be marked field-proven only when:

- Level 0 is green for the exact release
- Level 1 passes all mandatory criteria
- at least one Level 2 engagement is completed
- customer-safe artifacts are preserved
- material findings have traceable evidence
- delivery integrity is verified
- an operator records usability observations
- a reviewer signs the acceptance record
- known limitations are reconciled into the claims register

## Mandatory acceptance criteria

| ID | Criterion | Pass condition |
|---|---|---|
| AC-01 | Scope control | Operator can demonstrate authorized targets and exclusions before collection |
| AC-02 | Evidence provenance | Material evidence has identity, source and provenance metadata |
| AC-03 | Finding traceability | Each material finding references supporting evidence |
| AC-04 | Deterministic correlation | Re-running the same input does not create unexplained duplicate findings |
| AC-05 | Reporting | PDF/DOCX/XLSX outputs are readable and internally consistent |
| AC-06 | Playbook | Incident playbook reflects the observed scenario and does not invent authority |
| AC-07 | ROI | Business-impact calculations expose assumptions and sensitivity |
| AC-08 | Delivery integrity | Encrypted delivery decrypts successfully and manifest hashes verify |
| AC-09 | Offline path | Air-gap bundle verifies successfully without network dependency |
| AC-10 | Data handling | No raw secrets or customer evidence leak into logs, source control or public systems |
| AC-11 | Retest/closure | Engagement has a documented remediation/retest or closure decision |
| AC-12 | Operator usability | An FDSE can complete the workflow without undocumented tribal knowledge |

## Evidence rule

A criterion is not PASS because the operator says it passed.

Every criterion requires an evidence reference: test output, artifact hash, screenshot, log excerpt, customer acceptance reference or another controlled record.

Synthetic evidence must be clearly marked synthetic. Customer evidence must never be committed to this public repository.

## Release status vocabulary

Use only these states:

- **ENGINEERING-READY** — automated engineering gates pass.
- **SYNTHETIC-VALIDATED** — the end-to-end dry run passes.
- **FIELD-PILOTED** — at least one authorized real engagement passes.
- **FIELD-PROVEN** — release-specific pilot evidence and review are complete.
- **PRODUCTION-CERTIFIED** — field-proven release plus the production release/provenance requirements in the release gate.

Do not use "100% bug-free", "fully certified" or equivalent blanket claims.
