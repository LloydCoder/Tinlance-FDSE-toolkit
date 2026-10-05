"""Operator CLI for the private FDSE field toolkit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .airgap import build_airgap_bundle, verify_airgap_bundle
from .contracts import validate_document_file
from .delivery import build_delivery_zip, decrypt_delivery, encrypt_delivery
from .identity.scanner import IdentityScanner
from .playbooks import generate_playbook
from .reporting import generate_report_bundle
from .roi import ROIInput, calculate_roi


def _json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(value: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fdse", description="Tinlance Forward-Deployed Security Engineer Toolkit")
    parser.add_argument("--version", action="version", version="0.1.0.dev0")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a canonical JSON document")
    validate.add_argument("kind", choices=("engagement", "finding", "evidence", "asset", "incident", "remediation", "regulatory-assessment", "roi-analysis", "delivery-manifest", "report-manifest"))
    validate.add_argument("file", type=Path)

    report = sub.add_parser("report", help="generate PDF/DOCX/XLSX reports")
    report.add_argument("--engagement", required=True, type=Path)
    report.add_argument("--findings", required=True, type=Path)
    report.add_argument("--output-dir", required=True, type=Path)

    playbook = sub.add_parser("playbook", help="generate an incident-response playbook")
    playbook.add_argument("--engagement", required=True, type=Path)
    playbook.add_argument("--incident", required=True, type=Path)
    playbook.add_argument("--output", required=True, type=Path)

    scan = sub.add_parser("scan-file", help="scan a local file for credential exposure")
    scan.add_argument("file", type=Path)
    scan.add_argument("--output", type=Path)

    roi = sub.add_parser("roi", help="calculate assumption-driven ROI")
    roi.add_argument("--analysis-id", required=True)
    roi.add_argument("--investment-usd", required=True, type=float)
    roi.add_argument("--baseline-annual-loss-usd", required=True, type=float)
    roi.add_argument("--risk-reduction", required=True, type=float)
    roi.add_argument("--output", type=Path)

    package = sub.add_parser("package", help="build and optionally encrypt a delivery package")
    package.add_argument("--artifact", action="append", nargs=2, metavar=("NAME", "PATH"), required=True)
    package.add_argument("--output-zip", required=True, type=Path)
    package.add_argument("--encrypted-output", type=Path)
    package.add_argument("--password")
    package.add_argument("--decrypt-to", type=Path)

    airgap = sub.add_parser("airgap", help="build or verify an offline bundle")
    mode = airgap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build-from", type=Path)
    mode.add_argument("--verify", type=Path)
    airgap.add_argument("--output", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        validate_document_file(args.kind, args.file)
        print(f"VALID {args.kind}: {args.file}")
    elif args.command == "report":
        engagement = _json(args.engagement)
        findings = _json(args.findings)
        if not isinstance(engagement, dict) or not isinstance(findings, list):
            raise ValueError("engagement must be an object and findings must be an array")
        print(json.dumps(generate_report_bundle(engagement, findings, args.output_dir), indent=2))
    elif args.command == "playbook":
        result = generate_playbook(_json(args.engagement), _json(args.incident), args.output)
        print(result)
    elif args.command == "scan-file":
        findings = IdentityScanner().scan_file(args.file)
        if args.output:
            _write_json(findings, args.output)
        else:
            print(json.dumps(findings, indent=2))
    elif args.command == "roi":
        result = calculate_roi(ROIInput(args.analysis_id, args.investment_usd, args.baseline_annual_loss_usd, args.risk_reduction))
        if args.output:
            _write_json(result, args.output)
        else:
            print(json.dumps(result, indent=2))
    elif args.command == "package":
        artifacts = {name: Path(path) for name, path in args.artifact}
        manifest = build_delivery_zip(artifacts, args.output_zip)
        if args.encrypted_output:
            if not args.password:
                raise ValueError("--password is required with --encrypted-output")
            manifest["encryption"] = encrypt_delivery(args.output_zip, args.encrypted_output, args.password)
        if args.decrypt_to:
            if not args.password or not args.encrypted_output:
                raise ValueError("--decrypt-to requires --encrypted-output and --password")
            decrypt_delivery(args.encrypted_output, args.decrypt_to, args.password)
        print(json.dumps(manifest, indent=2))
    elif args.command == "airgap":
        if args.build_from:
            if not args.output:
                raise ValueError("--output is required with --build-from")
            print(json.dumps(build_airgap_bundle(args.build_from, args.output), indent=2))
        else:
            print(json.dumps(verify_airgap_bundle(args.verify), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
