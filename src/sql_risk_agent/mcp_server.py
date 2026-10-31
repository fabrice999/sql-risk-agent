
import os
from dataclasses import asdict

from mcp.server.fastmcp import FastMCP

from .agent import run_agent


mcp = FastMCP("PostgreSQL SQL Risk Agent")


@mcp.tool()
def analyze_sql_risk(
    sql: str,
    use_llm: bool = False,
) -> dict:
    """
    Assess the disruption risk of a PostgreSQL SQL statement.

    Uses deterministic AST analysis and, when configured,
    PostgreSQL EXPLAIN without ANALYZE.

    The optional local LLM explains the assessment but
    cannot change the deterministic verdict or score.

    This tool never executes the submitted DML statement.

    Args:
        sql: A single PostgreSQL SQL statement to analyze.
        use_llm: Enable optional Ollama explanation (default False).

    Returns:
        Structured risk assessment including verdict, score,
        reasons, estimated rows, and analysis status.
    """

    conninfo = os.environ.get("SQLRISK_CONNINFO")

    result = run_agent(
        sql=sql,
        conninfo=conninfo,
        use_llm=use_llm,
    )

    return asdict(result)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

