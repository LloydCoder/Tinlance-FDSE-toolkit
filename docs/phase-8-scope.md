# Phase 8 — Authorized Network and Scope Controls

The historical identity scanner resolved sensitive subdomains directly from a caller-provided domain. That behavior is not promoted into the maintained toolkit without authorization controls.

The maintained scope guard normalizes hostnames/IPs/URLs, supports exact targets, explicit wildcard domains, and CIDR networks, and applies exclusions before authorization. It performs no network activity itself.

Any future network-capable collector MUST require a Scope object and fail closed when a target is not explicitly authorized. DNS resolution, HTTP collection, port checks, or provider validity checks must be separate capabilities with their own tests and egress controls.
