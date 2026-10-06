# FDSE Toolkit Claims Register

Historical claims from the recovered package are not release evidence unless independently reproduced. The maintained Toolkit uses the following narrower claims.

| Claim | Current status | Evidence / remaining gate |
|---|---|---|
| "100% complete / fully tested" | Superseded | Replaced by explicit CI, security, release and compatibility gates; no universal perfection claim. |
| 418x ROI | Rejected as a universal claim | Maintained ROI requires customer-specific assumptions and sensitivity analysis. |
| 847 ms MTTD | Historical upstream claim | Must be independently evidenced by the relevant ThreatFade benchmark for any engagement. |
| 0% false positives over 100 runs | Historical upstream claim | Requires reproducible corpus, methodology and run records. |
| AES-256 secure delivery | Implemented, bounded claim | Maintained package uses AES-256-GCM with scrypt, authenticated metadata, password policy, integrity manifest and atomic writes. Security remains subject to normal cryptographic review. |
| Expiring download portal | Not implemented here | The Toolkit provides an authenticated package builder, not a hosted portal with expiry/revocation/audit. |
| Ubuntu/Debian binary support | Not claimed | Source package has compatibility evidence; binary targets require clean-environment artifact testing and provenance. |
| Five-document automated delivery | Narrowed | Current maintained report core produces PDF/DOCX/XLSX plus manifest; other engagement artifacts are separate operator workflows. |
| Enterprise source-package portability | Supported with evidence | Linux/Windows/macOS and Python 3.11–3.14 compatibility workflow is green. |
| Release provenance | Implemented in release workflow | Tagged releases invoke GitHub build-provenance attestation; an actual production release tag must still be used before claiming a signed production release. |
| Field validation | Defined, synthetic-ready | Phase 25 adds a versioned field-validation contract, measurable acceptance criteria and a pilot runbook. Real customer validation requires an authorized pilot. |

This register is normative for product and sales language. Do not publish superseded historical claims as current Toolkit capabilities.
