from pglast import ast, parse_sql

from .postgres import get_explain_plan, extract_explain_info
from .rules import (
    RiskResult,
    analyze_delete,
    analyze_insert,
    analyze_select,
    analyze_update,
    evaluate_estimated_rows,
)


def analyze_sql(sql: str, conninfo: str | None = None) -> RiskResult:

    statements = parse_sql(sql)

    if len(statements) != 1:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=["Only one SQL statement is allowed"],
        )

    statement = statements[0].stmt

    if isinstance(statement, ast.DeleteStmt):
        result = analyze_delete(statement)

    elif isinstance(statement, ast.UpdateStmt):
        result = analyze_update(statement)

    elif isinstance(statement, ast.InsertStmt):
        return analyze_insert(statement)

    elif isinstance(statement, ast.SelectStmt):
        return analyze_select(statement)

    else:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=["Unsupported SQL statement"],
        )

    # A dangerous static rule always takes priority.
    if result.verdict == "block":
        return result

    # No PostgreSQL connection: static analysis only.
    if conninfo is None:
        return result

    # PostgreSQL-aware analysis.
    try:
        plan = get_explain_plan(sql, conninfo)
        info = extract_explain_info(plan)
    except Exception as exc:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=[f"PostgreSQL analysis failed: {exc}"],
        )

    return evaluate_estimated_rows(info.estimated_rows)
