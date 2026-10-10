from dataclasses import dataclass

from pglast import ast


@dataclass
class RiskResult:
    verdict: str
    score: int
    reasons: list[str]


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
        reasons=[],
    )
