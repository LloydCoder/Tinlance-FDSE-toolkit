import json
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from fdse_toolkit.delivery import build_delivery_zip
from fdse_toolkit.identity import IdentityScanner


@given(st.text(alphabet=st.characters(min_codepoint=48, max_codepoint=122, blacklist_categories=("Cs",)), min_size=8, max_size=60))
def test_identity_scanner_never_returns_detected_secret(value: str):
    secret = "SYNTHETIC" + value
    findings = IdentityScanner().scan_text(f'password="{secret}"', source="fuzz")
    serialized = json.dumps(findings)
    assert secret not in serialized


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
