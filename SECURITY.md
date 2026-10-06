# Security Policy

The FDSE Toolkit handles security-assessment artifacts. Treat customer data, credentials, private keys, PCAPs, reports and engagement metadata as sensitive.

## Do not disclose sensitive material publicly

Never put the following in a public issue, pull request or discussion:

- real customer credentials or secrets
- private keys or tokens
- customer evidence or reports
- personal data
- network captures or logs containing sensitive information
- exploit details that would materially increase risk before remediation

Use synthetic fixtures for repository tests. Never run network-capable tests against real customer or third-party infrastructure.

## Reporting a vulnerability

Please report suspected vulnerabilities privately rather than opening a public issue.

Preferred route:

1. Open the repository's **Security** tab.
2. If **Private vulnerability reporting** is available, select **Report a vulnerability** and provide the affected version, reproduction steps, impact and any safe evidence.
3. If private vulnerability reporting is not available, contact the repository maintainer through the private GitHub account associated with **@LloydCoder**. Do not post sensitive details publicly.

Do not assume that a public issue is an acceptable substitute for private disclosure.

## What to include

Provide, where safe:

- affected version, commit or release
- affected component/file
- concise vulnerability description
- reproduction steps or a minimal synthetic proof
- security impact
- suggested mitigation, if known
- whether the issue is already exploited or publicly disclosed

Please redact secrets and customer information.

## Response and disclosure

Tinlance will triage reports according to severity and operational impact. Do not publish a vulnerability or proof-of-concept publicly until the maintainer has had an opportunity to assess and coordinate remediation.

This policy intentionally does not promise a fixed response SLA until an explicit maintainer-supported SLA is established.

## Field-operation safety

The Toolkit does not grant authorization to test systems. Field activity requires explicit customer authorization and a documented scope.

Never infer authorization from discovered infrastructure.
