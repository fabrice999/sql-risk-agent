from dataclasses import dataclass

from pglast import ast

@dataclass
class RiskResult:
    verdict: str
    score: int
    reasons: list[str]

    analysis_mode: str = "static"
    analysis_status: str = "completed"

    estimated_rows: int | None = None
    scan_type: str | None = None

def analyze_delete(statement: ast.DeleteStmt) -> RiskResult:

    if statement.whereClause is None:
        return RiskResult(
            verdict="block",
            score=90,
            reasons=["DELETE statement has no WHERE clause"],
        )

    return RiskResult(
        verdict="allow",
        score=0,
        reasons=[],
    )


def analyze_update(statement: ast.UpdateStmt) -> RiskResult:

    if statement.whereClause is None:
        return RiskResult(
            verdict="block",
            score=90,
            reasons=["UPDATE statement has no WHERE clause"],
        )

    return RiskResult(
        verdict="allow",
        score=0,
        reasons=[],
    )


def analyze_insert(statement: ast.InsertStmt) -> RiskResult:

    return RiskResult(
        verdict="allow",
        score=0,
        reasons=[],
    )


def analyze_select(statement: ast.SelectStmt) -> RiskResult:

    return RiskResult(
        verdict="allow",
        score=0,
        reasons=[],
    )

def evaluate_estimated_rows(estimated_rows: int) -> RiskResult:

    if estimated_rows > 10000:
        return RiskResult(
            verdict="block",
            score=90,
            reasons=[
                f"Estimated affected rows: {estimated_rows}"
            ],
        )

    if estimated_rows > 100:
        return RiskResult(
            verdict="warn",
            score=50,
            reasons=[
                f"Estimated affected rows: {estimated_rows}"
            ],
        )

    return RiskResult(
        verdict="allow",
        score=0,
        reasons=[
            f"PostgreSQL EXPLAIN estimated {estimated_rows} affected rows"
        ],
    )

def evaluate_relative_risk(
    estimated_rows: int,
    table_rows: int,
) -> RiskResult:

    if table_rows <= 0:
        return RiskResult(
            verdict="block",
            score=100,
            reasons=["Table cardinality is unknown or zero"],
        )

    percentage = 100.0 * estimated_rows / table_rows

    if percentage >= 50:
        verdict = "block"
        score = 90

    elif percentage >= 10:
        verdict = "warn"
        score = 50

    else:
        verdict = "allow"
        score = 0

    return RiskResult(
        verdict=verdict,
        score=score,
        reasons=[
            f"Estimated affected rows: {estimated_rows}",
            f"Estimated table rows: {table_rows}",
            f"Estimated affected percentage: {percentage:.2f}%",
        ],
    )
