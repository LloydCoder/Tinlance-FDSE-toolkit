"""Authorization and target-scope guardrails for field operations."""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse


class OutOfScopeError(ValueError):
    pass


@dataclass(frozen=True)
class Scope:
    authorized_targets: tuple[str, ...]
    excluded_targets: tuple[str, ...] = ()

    @classmethod
    def from_engagement(cls, engagement: dict) -> "Scope":
        targets = tuple(engagement["scope"]["authorized_targets"])
        excluded = tuple(engagement["scope"].get("excluded_targets", []))
        if not targets:
            raise ValueError("scope must contain at least one authorized target")
        return cls(targets, excluded)

    def is_authorized(self, target: str) -> bool:
        candidate = _normalize_target(target)
        if any(_matches(candidate, excluded) for excluded in self.excluded_targets):
            return False
        return any(_matches(candidate, allowed) for allowed in self.authorized_targets)

    def require(self, target: str) -> None:
        if not self.is_authorized(target):
            raise OutOfScopeError(f"target is not authorized: {target}")


def _normalize_target(target: str) -> str:
    target = target.strip()
    if not target:
        raise ValueError("target cannot be empty")
    parsed = urlparse(target if "://" in target else f"//{target}", scheme="")
    if parsed.hostname:
        return parsed.hostname.rstrip(".").lower()
    try:
        return str(ipaddress.ip_address(target))
    except ValueError as exc:
        raise ValueError("target must be a hostname, IP, or URL") from exc


def _matches(candidate: str, rule: str) -> bool:
    rule = rule.strip().lower().rstrip(".")
    try:
        candidate_ip = ipaddress.ip_address(candidate)
        if "/" in rule:
            return candidate_ip in ipaddress.ip_network(rule, strict=False)
        return candidate_ip == ipaddress.ip_address(rule)
    except ValueError:
        pass
    if rule.startswith("*."):
        suffix = rule[2:].rstrip(".")
        return candidate == suffix or candidate.endswith("." + suffix)
    return candidate == rule
