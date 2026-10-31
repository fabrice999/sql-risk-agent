
import argparse
import json
import os

from dataclasses import asdict

from .agent import run_agent


def main():
    parser = argparse.ArgumentParser(
        description="PostgreSQL SQL Risk AI Agent"
    )

    parser.add_argument(
        "sql",
        help="SQL statement to analyze",
    )

    parser.add_argument(
        "--explain",
        action="store_true",
        help="Enable PostgreSQL EXPLAIN analysis",
    )

    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable local LLM explanation",
    )

    args = parser.parse_args()

    conninfo = None

    if args.explain:
        conninfo = os.environ.get("SQLRISK_CONNINFO")

        if not conninfo:
            parser.error(
                "SQLRISK_CONNINFO is required with --explain"
            )

    result = run_agent(
        sql=args.sql,
        conninfo=conninfo,
        use_llm=not args.no_llm,
    )

    print(json.dumps(asdict(result), indent=2))

    # A blocked statement or incomplete analysis must not be approved.
    if result.verdict == "block" or result.analysis_status != "completed":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

