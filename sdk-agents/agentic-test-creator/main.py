#!/usr/bin/env python3
"""
CLI entry point for the agentic-test-creator Agent SDK application.

Usage examples:
    # From a Jira epic
    python main.py --jira PROJ-123 --output-dir tests/e2e

    # From a GitHub PR
    python main.py --pr 42 --output-dir tests/e2e

    # From pasted QA acceptance criteria
    python main.py --text "AC-1: Given a logged-in user..." --output-dir tests/

    # Override framework auto-detection
    python main.py --jira PROJ-456 --framework api --output-dir tests/api

    # Read text from stdin
    echo "AC-1: ..." | python main.py --text - --output-dir tests/
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agent import create_tests, detect_framework
from inputs import detect_and_build, build_text_context, JiraFetcher, build_pr_context, InputMode

SUPPORTED_FRAMEWORKS = ("playwright", "selenium", "api")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentic-test-creator",
        description="Generate Playwright, Selenium, or REST API tests from Jira epics, PRs, or QA text.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--jira",
        metavar="KEY",
        help="Jira epic or story key (e.g. PROJ-123) or full URL",
    )
    source.add_argument(
        "--pr",
        metavar="NUMBER",
        help="GitHub PR number (e.g. 42) or full URL",
    )
    source.add_argument(
        "--text",
        metavar="TEXT",
        help="Acceptance criteria text, or '-' to read from stdin",
    )

    parser.add_argument(
        "--output-dir",
        default="tests",
        help="Directory to write generated test files into (default: tests/)",
    )
    parser.add_argument(
        "--framework",
        choices=SUPPORTED_FRAMEWORKS,
        help=(
            "Test framework to use. If omitted, auto-detected from the "
            "output-dir and its parent directories."
        ),
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Suppress streaming output; print only the final result.",
    )

    return parser.parse_args()


def resolve_framework(args: argparse.Namespace) -> str:
    """Return the framework string, either from --framework or auto-detected."""
    if args.framework:
        return args.framework

    detected = detect_framework(args.output_dir)
    if detected:
        print(f"[auto-detected framework: {detected}]", flush=True)
        return detected

    # Interactive prompt if no signal found
    print("No test framework detected. Which would you like to generate?")
    print("  1) Playwright E2E")
    print("  2) Selenium E2E")
    print("  3) REST API")
    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == "1":
            return "playwright"
        if choice == "2":
            return "selenium"
        if choice == "3":
            return "api"
        print("Please enter 1, 2, or 3.")


def main() -> None:
    args = parse_args()

    # Ensure output directory exists
    output_dir = str(Path(args.output_dir).resolve())
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Build context
    try:
        if args.jira:
            context = JiraFetcher().build_context(args.jira)
        elif args.pr:
            context = build_pr_context(args.pr)
        else:
            text = sys.stdin.read() if args.text == "-" else args.text
            context = build_text_context(text)
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[error] Failed to fetch input: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[source] {context.raw} → {output_dir}", flush=True)

    # Resolve framework
    try:
        framework = resolve_framework(args)
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.", file=sys.stderr)
        sys.exit(1)

    # Run agent
    try:
        result = create_tests(
            context,
            framework,
            output_dir,
            stream_output=not args.no_stream,
        )
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[error] Agent failed: {exc}", file=sys.stderr)
        raise

    if args.no_stream:
        print(result)


if __name__ == "__main__":
    main()
