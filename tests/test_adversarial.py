import json
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from fdse_toolkit.delivery import build_delivery_zip
from fdse_toolkit.identity import IdentityScanner


@given(st.text(min_size=0, max_size=1000))
def test_identity_scanner_never_returns_input_as_a_secret(value: str):
    findings = IdentityScanner().scan_text(value, source="fuzz")
    serialized = json.dumps(findings)
    assert value not in serialized or not value


def test_delivery_rejects_absolute_and_parent_paths(tmp_path: Path):
    source = tmp_path / "x.txt"
    source.write_text("x", encoding="utf-8")
    for name in ("/absolute.txt", "../parent.txt", "nested/../../escape.txt"):
        try:
            build_delivery_zip({name: source}, tmp_path / "x.zip")
        except ValueError:
            pass
        else:
            raise AssertionError(name)
