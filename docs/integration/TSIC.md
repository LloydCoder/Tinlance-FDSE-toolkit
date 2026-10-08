# TSIC integration

The FDSE Toolkit is the delivery-evidence/reporting layer for Tinlance engagements.

- **TSIC** owns ecosystem integration contracts and certification.
- **FDSE Toolkit** owns delivery reporting, evidence-backed artifact generation and route-aware reporting semantics.
- **FDSE** owns delivery orchestration and route selection.
- **Agent Platform** owns governed consequential execution.

The Toolkit must preserve the upstream `delivery_route` (`engineering` or `transformation`) and the evidence/provenance references used to derive every material report or playbook.

## Conformance

`scripts/tsic_conformance.py` consumes the immutable TSIC-29 adapter revision and verifies:

- canonical identity, event, delivery, trace and economic-attribution contracts;
- FDSE Toolkit authority boundaries;
- provenance-preserving evidence;
- separation of Engineering and Transformation;
- route-aware economic attribution;
- no execution/detection/policy authority leakage.

Run:

```bash
python scripts/tsic_conformance.py
```

A passing gate certifies compatibility with the reviewed contract surface; it does not claim a field deployment or production customer certification.
