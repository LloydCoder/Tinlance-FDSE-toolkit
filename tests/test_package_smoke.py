from fdse_toolkit import __version__
from fdse_toolkit.cli import main


def test_version_is_development_version():
    assert __version__ == "0.1.0.dev0"


def test_cli_help_does_not_execute_legacy_tools(capsys):
    # argparse exits on --help; the stable package CLI intentionally has no
    # implicit network/process execution.
    import sys

    old = sys.argv
    try:
        sys.argv = ["fdse", "--help"]
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 0
    finally:
        sys.argv = old
    assert "Forward-Deployed Security Engineer Toolkit" in capsys.readouterr().out
