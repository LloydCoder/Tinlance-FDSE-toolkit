import pytest

from fdse_toolkit.scope import OutOfScopeError, Scope


def test_scope_allows_exact_and_explicit_wildcard_domains():
    scope = Scope(("example.com", "*.approved.example"))
    assert scope.is_authorized("https://example.com/path")
    assert scope.is_authorized("api.approved.example")
    assert not scope.is_authorized("evil.example.com")


def test_scope_honors_exclusions():
    scope = Scope(("*.example.com",), ("admin.example.com",))
    assert scope.is_authorized("api.example.com")
    assert not scope.is_authorized("admin.example.com")


def test_scope_supports_cidr():
    scope = Scope(("198.51.100.0/24",))
    assert scope.is_authorized("198.51.100.42")
    assert not scope.is_authorized("203.0.113.42")


def test_require_fails_closed():
    with pytest.raises(OutOfScopeError):
        Scope(("example.com",)).require("other.example")
