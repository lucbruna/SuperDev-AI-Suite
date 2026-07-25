#!/usr/bin/env python3
"""SuperDev CLI - Command line interface."""

from __future__ import annotations

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="superdev",
        description="SuperDev AI Suite CLI",
    )
    parser.add_argument("--version", action="version", version="5.0.0")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize a new project")
    subparsers.add_parser("doctor", help="Check system health")
    subparsers.add_parser("status", help="Show system status")

    args = parser.parse_args()

    if args.command == "init":
        print("Initializing SuperDev project...")
    elif args.command == "doctor":
        print("Checking system health...")
    elif args.command == "status":
        print("SuperDev AI Suite v5.0.0")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
