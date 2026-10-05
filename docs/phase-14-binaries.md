# Phase 14 — Binary Build and Reproducibility Controls

The historical binary builder was audited and contained absolute environment paths such as /home/claude/toolkit-v2, so its build was not portable or reproducible.

The maintained builder accepts explicit repository-relative entrypoints and output directories, invokes PyInstaller with shell=False, sets PYTHONHASHSEED to a fixed value, and supplies SOURCE_DATE_EPOCH when absent. This follows PyInstaller's documented reproducibility guidance.

The historical Linux binaries remain unverified artifacts. Enterprise binary release requires clean-environment execution, architecture/ABI testing, dependency inspection, SBOM, signed provenance, and reproducibility evidence. This phase establishes the build-control foundation rather than falsely declaring those artifacts portable.
