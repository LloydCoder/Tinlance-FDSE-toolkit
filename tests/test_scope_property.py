from hypothesis import given, strategies as st

from fdse_toolkit.scope import Scope


@given(st.text(min_size=1, max_size=120))
def test_scope_never_authorizes_an_unlisted_random_target(value: str):
    scope = Scope(("authorized.example",))
    try:
        result = scope.is_authorized(value)
    except ValueError:
        return
    assert result is False or value.rstrip(".").lower() == "authorized.example"
