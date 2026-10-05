# FDSE Toolkit Architecture

## Purpose
A private Forward-Deployed Security Engineer field system used by Tinlance to execute authorized customer security engagements and turn evidence from specialized Tinlance tools into defensible engineering deliverables.

## Boundaries
The Toolkit owns engagement workspaces, scope/authorization records, evidence packaging, normalization, finding presentation/correlation, report generation, IR playbooks, business-impact/ROI modeling, secure delivery, and offline/air-gapped packaging.

It does not become:
- a second detection engine;
- a second governed agent runtime;
- a replacement for FAS evidence semantics;
- a replacement for ThreatFade, ReconOS, BugFlow, AI Shield, TwinGuard, or KalevioAI;
- a customer-facing multi-tenant SaaS.

The Tinlance Agent Platform remains the authoritative governed execution layer for identity, authorization, policy, approvals, runtime, tools/MCP, sandbox, secrets, budgets, evidence/audit, and observability.

## Target flow
Customer authorization → scoped collection → specialized Tinlance tools → canonical engagement data → evidence/provenance → finding correlation → reports/playbooks/ROI → secure delivery → retest → closure.
