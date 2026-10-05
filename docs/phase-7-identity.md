# Phase 7 — Identity Threat Scanner

The historical scanner was audited before replacement. Its credential detector hashed matches, but it also contained broad generic patterns and a live DNS resolver that could be used without an explicit authorization/scope boundary. The maintained Phase 7 scanner therefore starts as an offline-first text/file detector.

## Security properties
- No matched secret value is returned in findings.
- Captured secret groups are hashed with SHA-256; reports contain only the digest and redaction marker.
- Provider-specific patterns require provider context where the token format is ambiguous. Paystack secret keys are context-gated because Paystack and other providers can share sk_ prefixes.
- Inputs have a configurable maximum size.
- No network requests are performed by the base scanner.
- Validity checks are intentionally disabled; later authorized validation will be a separate, explicit capability with scope and approval controls.

The design follows the pattern/validation distinction used by mature secret-scanning systems. Provider pattern formats change, so this catalog is a maintained detection hint set rather than a claim of complete provider coverage.

## Deferred
DNS exposure, public GitHub enumeration, CT lookups, provider validity checks, and organization sweeps move to the authorized network/recon phase where scope enforcement and outbound-network policy can be tested independently.
