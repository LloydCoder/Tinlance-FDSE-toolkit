# Phase 6 — Enterprise Reporting

The historical 1,143-line report generator was audited before replacement. Its input loader directly parsed arbitrary JSON without a canonical contract, demo content contained hard-coded customer/regulatory assertions, and the rendering layer was tightly coupled to the historical data shape. The maintained reporting layer therefore starts from the canonical FDSE contracts rather than wrapping the legacy generator unchanged.

## Outputs
- PDF executive/technical assessment
- editable DOCX report
- XLSX operational findings workbook
- SHA-256 report manifest

## Security controls
- engagement contract validation before generation;
- finding contract validation and deterministic correlation before rendering;
- PDF text escaping to prevent markup injection;
- spreadsheet formula-injection neutralization for values beginning with =, +, -, or @;
- filesystem-safe output names;
- artifact hashes and sizes recorded in a versioned manifest.

## Scope of this phase
This is the maintained reporting core. Branding, advanced charts, evidence screenshots, customer-specific templates, and full report visual regression belong to later hardening phases.
