# Phase 5 — Finding Correlation and Risk Prioritization

The Toolkit now correlates equivalent findings deterministically using a normalized title plus affected asset set. Correlated findings retain the union of evidence references and source names, choose the highest observed severity, and retain the strongest confidence.

The resulting risk_score is a **Tinlance FDSE prioritization score**, not CVSS and not a probability of compromise. It is bounded to 0–100 and combines severity, evidence confidence, and an explicit asset-criticality factor. Asset criticality must be supplied by the engagement context; unknown criticality receives a conservative neutral factor.

This score is intended to order engineering work. It must not replace source-specific severity, CVSS, regulatory applicability, or analyst judgment.
