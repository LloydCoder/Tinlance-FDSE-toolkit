from fdse_toolkit.cli import build_parser


def test_cli_exposes_field_operations():
    parser = build_parser()
    for command in ("validate", "report", "playbook", "scan-file", "roi", "package", "airgap"):
        args = parser.parse_args([command] + {
            "validate": ["engagement", "fixture.json"],
            "report": ["--engagement", "e.json", "--findings", "f.json", "--output-dir", "out"],
            "playbook": ["--engagement", "e.json", "--incident", "i.json", "--output", "p.docx"],
            "scan-file": ["fixture.txt"],
            "roi": ["--analysis-id", "a", "--investment-usd", "1", "--baseline-annual-loss-usd", "2", "--risk-reduction", "0.5"],
            "package": ["--artifact", "report.pdf", "report.pdf", "--output-zip", "delivery.zip"],
            "airgap": ["--verify", "bundle.zip"],
        }[command])
        assert args.command == command
\n\ndef test_cli_validates_field_validation_records():\n    parser = build_parser()\n    args = parser.parse_args([\"validate\", \"field-validation\", \"examples/field-validation-record.synthetic.json\"])\n    assert args.kind == \"field-validation\"\n