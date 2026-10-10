import json
import sys
from dataclasses import asdict

from .analyzer import analyze_sql


def main():
    if len(sys.argv) != 2:
        print('Usage: python -m sql_risk_agent.cli "SQL"')
        sys.exit(1)

    sql = sys.argv[1]

    result = analyze_sql(sql)

    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
