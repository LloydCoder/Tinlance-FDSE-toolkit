#!/usr/bin/env python3
"""
Tinlance FDSE Toolkit — Binary Compiler
=========================================
Compiles all toolkit Python scripts into standalone executables.
Enterprise clients can run .exe (Windows) or binaries (Linux)
without needing Python installed.

Components compiled:
  - report_generator    → TinlanceReport.exe / TinlanceReport
  - ir_playbook         → TinlanceIR.exe / TinlanceIR
  - roi_calculator      → TinlanceROI.exe / TinlanceROI
  - identity_scanner    → TinlanceIDScan.exe / TinlanceIDScan
  - toolkit_gui         → TinlanceToolkit.exe / TinlanceToolkit (with GUI)

Usage:
    python build_binaries.py                    # build all
    python build_binaries.py --target report    # build one
    python build_binaries.py --check            # check PyInstaller is available
    python build_binaries.py --spec             # generate .spec files only
"""

import subprocess
import sys
import os
import argparse
import json
import platform
from pathlib import Path
from datetime import datetime

PLATFORM    = platform.system()   # Windows / Linux / Darwin
EXE_SUFFIX  = ".exe" if PLATFORM == "Windows" else ""
OUT_DIR     = Path("/home/claude/toolkit-v2/binaries")
TOOLKIT_DIR = Path("/home/claude/toolkit-v2")

COMPONENTS = {
    "report": {
        "name":   "TinlanceReport",
        "script": str(TOOLKIT_DIR / "report_generator" / "report_generator.py"),
        "desc":   "Security Assessment Report Generator (PDF + Word + Excel)",
        "hidden_imports": ["reportlab", "openpyxl", "docx", "docx.oxml", "docx.shared"],
        "onefile": True,
        "windowed": False,
    },
    "ir": {
        "name":   "TinlanceIR",
        "script": str(TOOLKIT_DIR / "ir_playbook" / "ir_playbook.py"),
        "desc":   "Incident Response Playbook Generator",
        "hidden_imports": ["docx", "docx.oxml", "docx.shared"],
        "onefile": True,
        "windowed": False,
    },
    "roi": {
        "name":   "TinlanceROI",
        "script": str(TOOLKIT_DIR / "roi_calculator" / "roi_calculator.py"),
        "desc":   "ROI Calculator + MTTD/MTTR Dashboard",
        "hidden_imports": ["openpyxl", "docx", "docx.oxml", "reportlab"],
        "onefile": True,
        "windowed": False,
    },
    "idscan": {
        "name":   "TinlanceIDScan",
        "script": str(TOOLKIT_DIR / "identity_scanner" / "identity_scanner.py"),
        "desc":   "Identity Threat Scanner",
        "hidden_imports": ["json", "re", "socket", "hashlib"],
        "onefile": True,
        "windowed": False,
    },
    "gui": {
        "name":   "TinlanceToolkit",
        "script": str(TOOLKIT_DIR / "gui_launcher" / "toolkit_gui.py"),
        "desc":   "Unified Toolkit GUI Launcher",
        "hidden_imports": ["tkinter", "tkinter.ttk", "tkinter.filedialog",
                          "tkinter.messagebox", "tkinter.scrolledtext"],
        "onefile": True,
        "windowed": True,   # No console window for GUI
    },
}


def check_pyinstaller() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ✓ PyInstaller {result.stdout.strip()} available")
            return True
    except Exception:
        pass
    print("  ✗ PyInstaller not found")
    return False


def build_spec(name: str, script: str, hidden_imports: list,
               onefile: bool, windowed: bool, out_dir: Path) -> str:
    """Generate a PyInstaller .spec file."""
    hidden = repr(hidden_imports)
    win_flag = "True" if windowed else "False"
    console_flag = "False" if windowed else "True"

    spec = f"""# -*- mode: python ; coding: utf-8 -*-
# Tinlance FDSE Toolkit — {name} Build Spec
# Generated: {datetime.now().isoformat()}
# Platform: {PLATFORM}

block_cipher = None

a = Analysis(
    ['{script}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports={hidden},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_flag},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    spec_path = out_dir / f"{name}.spec"
    spec_path.write_text(spec)
    return str(spec_path)


def build_component(key: str, comp: dict, out_dir: Path,
                    dry_run: bool = False) -> dict:
    result = {
        "name":    comp["name"],
        "status":  "pending",
        "output":  None,
        "error":   None,
    }

    print(f"\n  Building {comp['name']} — {comp['desc']}")
    print(f"  Script: {comp['script']}")

    if not Path(comp["script"]).exists():
        result["status"] = "skipped"
        result["error"]  = f"Script not found: {comp['script']}"
        print(f"  [SKIP] Script not found")
        return result

    # Generate spec file
    spec_path = build_spec(
        comp["name"], comp["script"], comp["hidden_imports"],
        comp["onefile"], comp["windowed"], out_dir
    )
    print(f"  ✓ Spec file: {spec_path}")

    if dry_run:
        result["status"] = "spec_only"
        result["output"] = spec_path
        print(f"  [DRY RUN] Spec generated, skipping compilation")
        return result

    # Run PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--distpath", str(out_dir / "dist"),
        "--workpath", str(out_dir / "build"),
        "--specpath", str(out_dir),
        "--name", comp["name"],
        "--noconfirm",
        "--clean",
    ]

    if comp["windowed"]:
        cmd.append("--windowed")

    for hi in comp["hidden_imports"]:
        cmd.extend(["--hidden-import", hi])

    cmd.append(comp["script"])

    print(f"  Running PyInstaller...")
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=300
        )
        if proc.returncode == 0:
            binary_name = comp["name"] + EXE_SUFFIX
            binary_path = out_dir / "dist" / binary_name
            if binary_path.exists():
                size = binary_path.stat().st_size / 1024 / 1024
                result["status"] = "success"
                result["output"] = str(binary_path)
                print(f"  ✅ Binary: {binary_path} ({size:.1f} MB)")
            else:
                result["status"] = "error"
                result["error"]  = "Binary not found after build"
                print(f"  ✗ Binary not found after build")
        else:
            result["status"] = "error"
            result["error"]  = proc.stderr[-500:] if proc.stderr else "Unknown error"
            print(f"  ✗ Build failed: {result['error'][-200:]}")
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"]  = "Build timed out after 300 seconds"
        print(f"  ✗ Build timed out")
    except Exception as e:
        result["status"] = "error"
        result["error"]  = str(e)
        print(f"  ✗ Build error: {e}")

    return result


def generate_installation_guide(results: list, out_dir: Path):
    """Generate installation guide for compiled binaries."""
    guide = f"""
Tinlance FDSE Toolkit — Pre-Compiled Binaries
==============================================
Built: {datetime.now().strftime('%Y-%m-%d')}
Platform: {PLATFORM}
By: Tinlance Limited (RC: 7962164) | tinlance.com

WHY COMPILED BINARIES?
─────────────────────────────────────────────────────────
Compiled binaries require NO Python installation.
Enterprise security teams can run them directly without
approving script execution policies or installing dependencies.
They are reviewed and approved as standard executables.

AVAILABLE BINARIES
─────────────────────────────────────────────────────────
"""
    for r in results:
        status_sym = "✅" if r["status"] == "success" else "⚠️"
        guide += f"  {status_sym} {r['name']}{EXE_SUFFIX}\n"
        if r.get("output"): guide += f"     Location: {r['output']}\n"
        if r.get("error"):  guide += f"     Note: {r['error'][:100]}\n"
        guide += "\n"

    guide += """
USAGE
─────────────────────────────────────────────────────────

Windows (double-click or command line):
  TinlanceToolkit.exe                          GUI launcher
  TinlanceReport.exe --demo --out ./reports    Demo report
  TinlanceROI.exe --demo --out ./roi           ROI analysis
  TinlanceIR.exe --demo --out ./ir             IR playbook
  TinlanceIDScan.exe --demo --out ./scan       Identity scan

Linux/Mac (terminal):
  ./TinlanceToolkit                            GUI launcher
  ./TinlanceReport --demo --out ./reports      Demo report
  ./TinlanceROI --demo --out ./roi             ROI analysis
  ./TinlanceIR --demo --out ./ir               IR playbook
  ./TinlanceIDScan --demo --out ./scan         Identity scan

SECURITY VERIFICATION
─────────────────────────────────────────────────────────
All binaries can be verified against SHA-256 hashes.
Run the appropriate verify script before execution.

Source code is available at: github.com/LloydCoder/tinlance-threatfade

SUPPORT
─────────────────────────────────────────────────────────
Email:   nwachukwuchinaemerem8@gmail.com
Web:     tinlance.com
Live:    http://13.50.16.19/dashboard
"""
    guide_path = out_dir / "BINARIES_README.txt"
    guide_path.write_text(guide)
    print(f"\n  ✓ Installation guide: {guide_path}")


def main():
    parser = argparse.ArgumentParser(description="Tinlance Binary Compiler")
    parser.add_argument("--target", choices=list(COMPONENTS.keys()) + ["all"],
                        default="all", help="Component to build")
    parser.add_argument("--check",  action="store_true", help="Check PyInstaller availability")
    parser.add_argument("--spec",   action="store_true", help="Generate spec files only (no compilation)")
    parser.add_argument("--out",    default=str(OUT_DIR), help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n  🔧 Tinlance FDSE Toolkit — Binary Compiler")
    print(f"  Platform: {PLATFORM}")
    print(f"  Output:   {out_dir}\n")

    if args.check:
        check_pyinstaller()
        return

    if not check_pyinstaller() and not args.spec:
        print("\n  Install PyInstaller: pip install pyinstaller --break-system-packages")
        print("  Or use --spec flag to generate spec files only")
        if not args.spec:
            return

    targets = COMPONENTS if args.target == "all" else {args.target: COMPONENTS[args.target]}
    results = []

    for key, comp in targets.items():
        result = build_component(key, comp, out_dir, dry_run=args.spec)
        results.append(result)

    generate_installation_guide(results, out_dir)

    # Summary
    success = sum(1 for r in results if r["status"] in ("success", "spec_only"))
    failed  = sum(1 for r in results if r["status"] == "error")

    print(f"\n  Build Summary")
    print(f"  ─────────────────────────────────────────")
    print(f"  Total:   {len(results)}")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Output:  {out_dir}\n")

    # Save results JSON
    results_path = out_dir / "build_results.json"
    results_path.write_text(json.dumps({
        "platform": PLATFORM, "timestamp": datetime.now().isoformat(),
        "results": results
    }, indent=2))

if __name__ == "__main__":
    main()
