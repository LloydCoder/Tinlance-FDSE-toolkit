# Phase 20 — FDSE Operator CLI

The Toolkit is a private field system for one Forward-Deployed Security Engineer. Phase 20 turns the maintained library capabilities into a controlled local operator interface without adding network authority.

Supported commands:
- validate — validate a canonical contract against the maintained local schema.
- report — generate PDF, DOCX and XLSX reports from canonical engagement/findings JSON.
- playbook — generate a client-specific incident-response playbook.
- scan-file — perform bounded offline identity/secret scanning of a local file.
- roi — calculate transparent assumption-driven ROI with sensitivity analysis.
- package — build an integrity-manifested delivery ZIP and optionally encrypt/decrypt it.
- airgap — build or verify an offline bundle.

The CLI intentionally does not discover targets, expand scope, grant authorization, execute arbitrary customer code, or replace the Tinlance Agent Platform. It is an operator surface over already-governed inputs and maintained library functions.
