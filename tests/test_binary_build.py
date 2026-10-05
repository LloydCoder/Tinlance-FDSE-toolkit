from pathlib import Path

import pytest

from fdse_toolkit.build_binary import BinaryBuildConfig, build_command


def test_binary_command_is_path_controlled_and_non_shell(tmp_path: Path):
    entry = tmp_path / "app.py"
    entry.write_text("print('fixture')", encoding="utf-8")
    cfg = BinaryBuildConfig(entry, "TinlanceFixture", tmp_path, tmp_path / "dist", tmp_path / "build", tmp_path / "spec")
    command = build_command(cfg)
    assert command[:5] == ["python", "-m", "PyInstaller", "--onefile", "--clean"]
    assert "--noconfirm" in command


def test_binary_builder_rejects_outside_entrypoint(tmp_path: Path):
    outside = tmp_path.parent / "outside.py"
    outside.write_text("print('fixture')", encoding="utf-8")
    cfg = BinaryBuildConfig(outside, "x", tmp_path, tmp_path / "dist", tmp_path / "build", tmp_path / "spec")
    with pytest.raises(ValueError):
        build_command(cfg)
