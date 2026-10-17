from pglast import ast, parse_sql

from .postgres import (
    get_explain_plan,
    extract_explain_info,
    get_table_rows,
)

from .rules import (
    RiskResult,
    analyze_delete,
    analyze_insert,
    analyze_select,
    analyze_update,
    evaluate_estimated_rows,
    evaluate_relative_risk,
)

def analyze_sql(sql: str, conninfo: str | None = None) -> RiskResult:

    mode = "postgresql" if conninfo is not None else "static"

    # Step 1: Parse SQL
    try:
        statements = parse_sql(sql)

    except Exception as exc:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=[f"SQL parsing failed: {exc}"],
            analysis_mode=mode,
            analysis_status="failed",
        )

    # Step 2: Check statement count
    if len(statements) != 1:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=["Only one SQL statement is allowed"],
            analysis_mode=mode,
        )

    statement = statements[0].stmt

    # Step 3: Static analysis
    if isinstance(statement, ast.DeleteStmt):
        result = analyze_delete(statement)

    elif isinstance(statement, ast.UpdateStmt):
        result = analyze_update(statement)

    elif isinstance(statement, ast.InsertStmt):
        result = analyze_insert(statement)

    elif isinstance(statement, ast.SelectStmt):
        result = analyze_select(statement)

    else:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=["Unsupported SQL statement"],
            analysis_mode=mode,
        )

    # A static rule has already rejected the SQL.
    if result.verdict == "block":
        result.analysis_mode = mode
        return result

    # Static analysis only.
    if conninfo is None:
        return result

    # Step 4: PostgreSQL EXPLAIN
    try:
        plan = get_explain_plan(sql, conninfo)
        info = extract_explain_info(plan)

    except Exception as exc:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=[f"PostgreSQL EXPLAIN failed: {exc}"],
            analysis_mode="postgresql",
            analysis_status="failed",
        )

    # Step 5: Table statistics
    try:
        table_rows = get_table_rows(
            info.relation,
            conninfo,
        )

        if table_rows is None:
            return RiskResult(
                verdict="block",
                score=100,
                reasons=["Table cardinality is unavailable"],
                analysis_mode="postgresql",
                analysis_status="failed",
                estimated_rows=info.estimated_rows,
                scan_type=info.scan_type,
            )

    except Exception as exc:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=[f"Table statistics analysis failed: {exc}"],
            analysis_mode="postgresql",
            analysis_status="failed",
            estimated_rows=info.estimated_rows,
            scan_type=info.scan_type,
        )

    # Step 6: Risk evaluation
    try:
        result = evaluate_relative_risk(
            estimated_rows=info.estimated_rows,
            table_rows=table_rows,
        )

    except Exception as exc:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=[f"Risk evaluation failed: {exc}"],
            analysis_mode="postgresql",
            analysis_status="failed",
            estimated_rows=info.estimated_rows,
            scan_type=info.scan_type,
        )

    # Step 7: Enrich the result
    result.analysis_mode = "postgresql"
    result.analysis_status = "completed"
    result.estimated_rows = info.estimated_rows
    result.scan_type = info.scan_type

    return result
