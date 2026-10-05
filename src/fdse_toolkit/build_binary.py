"""Controlled PyInstaller build command construction."""
from __future__ import annotations

import os
import subprocess  # nosec B404 - controlled local build tool; shell execution is disabled
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BinaryBuildConfig:
    entrypoint: Path
    name: str
    repo_root: Path
    dist_dir: Path
    work_dir: Path
    spec_dir: Path

    def validate(self) -> None:
        root = self.repo_root.resolve()
        entry = self.entrypoint.resolve()
        if not entry.is_file() or root not in entry.parents:
            raise ValueError("entrypoint must be a file inside repo_root")
        if not self.name or any(ch in self.name for ch in "/\\"):
            raise ValueError("invalid binary name")


def build_command(config: BinaryBuildConfig) -> list[str]:
    config.validate()
    return [
        "python", "-m", "PyInstaller", "--onefile", "--clean", "--noconfirm",
        "--name", config.name,
        "--distpath", str(config.dist_dir.resolve()),
        "--workpath", str(config.work_dir.resolve()),
        "--specpath", str(config.spec_dir.resolve()),
        str(config.entrypoint.resolve()),
    ]


def build_binary(config: BinaryBuildConfig) -> Path:
    command = build_command(config)
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "1"
    env.setdefault("SOURCE_DATE_EPOCH", "0")
    config.dist_dir.mkdir(parents=True, exist_ok=True)
    config.work_dir.mkdir(parents=True, exist_ok=True)
    config.spec_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True, shell=False, cwd=config.repo_root, env=env)  # nosec B603 - argv is constructed from repo-controlled validated paths
    output = config.dist_dir / config.name
    if not output.is_file():
        raise RuntimeError(f"PyInstaller did not produce expected binary: {output}")
    return output
