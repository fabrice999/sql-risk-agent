import argparse
import json
import os
import sys
from dataclasses import asdict

from .analyzer import analyze_sql


def main():

    parser = argparse.ArgumentParser(
        description="PostgreSQL SQL Risk Agent"
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

    args = parser.parse_args()

    conninfo = None

    if args.explain:
        conninfo = os.environ.get("SQLRISK_CONNINFO")

        if not conninfo:
            parser.error(
                "SQLRISK_CONNINFO must be set when using --explain"
            )

    result = analyze_sql(
        sql=args.sql,
        conninfo=conninfo,
    )

    print(json.dumps(asdict(result), indent=2))
    if result.verdict == "block":
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
