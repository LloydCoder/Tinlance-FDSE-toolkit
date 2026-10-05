# FDSE Field Pilot Runbook

## Objective

Run one realistic, authorized engagement through the maintained Toolkit and record evidence sufficient to determine whether the system is operationally fit for customer delivery.

This is an operator runbook, not an automated authorization mechanism.

## Before the engagement

Create:

- engagement identifier
- authorization reference
- authorized target list
- exclusions
- escalation contacts
- data classification
- retention/disposition requirement
- selected Toolkit release/version
- validation record identifier

Confirm that all collection and testing activities are authorized. Discovery must never expand scope.

## Execution sequence

### 1. Establish scope

Record the customer, targets, exclusions and authorization reference.

### 2. Intake evidence

Accept only approved upstream outputs or controlled evidence handoff. Validate every canonical document before use.

### 3. Preserve provenance

Record evidence identity, source, collection time and relevant provenance. Never place raw secrets in findings or logs.

### 4. Correlate findings

Run the maintained correlation path. Review severity and confidence. Investigate unexplained duplicates or unsupported conclusions.

### 5. Generate deliverables

Produce the report bundle, incident-response playbook where applicable, ROI analysis where applicable, and delivery manifest.

### 6. Verify delivery

For encrypted delivery:

- verify password policy
- transfer the password separately
- decrypt in a clean destination
- verify the manifest hashes

For air-gap delivery:

- build the bundle
- verify the bundle
- record the verification result

### 7. Independent review

A second qualified person reviews material findings and customer-facing claims before delivery whenever the engagement permits.

### 8. Customer handoff

Deliver the agreed technical and executive artifacts through the authorized channel. Record the acceptance/handoff reference.

### 9. Retest or close

Where remediation is included, retest only explicitly authorized targets. Record the outcome. Revoke temporary access and complete evidence disposition.

## Metrics to capture

Do not optimize for vanity metrics. Record:

- operator time by workflow stage
- reviewer time
- number of findings
- number of material findings
- findings with complete evidence references
- report regeneration failures
- delivery verification failures
- air-gap verification failures
- unsupported/unknown results
- customer clarification requests
- remediation/retest outcome
- operator friction observations

## Exit decision

Use the field-validation schema and classify the run:

- PASS
- CONDITIONAL_PASS
- FAIL
- REQUIRES_RETEST

A pilot failure is useful engineering evidence. Fix the root cause, rerun the affected gate, and record the new release/run relationship.

## Safety

Never use a real customer as a test fixture. Never commit customer evidence to this repository. Never infer authorization from discovered infrastructure. Never represent a synthetic result as customer validation.
