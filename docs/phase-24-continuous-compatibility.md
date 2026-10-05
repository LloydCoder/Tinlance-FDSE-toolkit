# Phase 24 — Continuous Compatibility Gate

Phase 23 established green source compatibility evidence on pull requests. Phase 24 promotes that matrix to a continuous main-branch gate so the supported source-package matrix cannot silently drift after merge.

The compatibility workflow remains distinct from binary certification: it validates the Python package on Linux, Windows and macOS across Python 3.11–3.14. Binary/air-gap certification remains artifact-specific.
