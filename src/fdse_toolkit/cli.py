"""Stable CLI entry point for the reconstructed Toolkit."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="fdse", description="Tinlance Forward-Deployed Security Engineer Toolkit")
    parser.add_argument("--version", action="version", version="0.1.0.dev0")
    parser.parse_args()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
