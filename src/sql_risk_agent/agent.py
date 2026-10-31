
from dataclasses import asdict, dataclass
from typing import Any

from .analyzer import analyze_sql
from .llm import LLMError, explain_risk


@dataclass
class AgentResult:
    sql: str
    verdict: str
    score: int
    reasons: list[str]

    analysis_mode: str
    analysis_status: str
    estimated_rows: int | None
    scan_type: str | None

    llm_status: str
    llm_explanation: str | None
    llm_recommendations: list[str]
    llm_error: str | None = None


def run_agent(
    sql: str,
    conninfo: str | None = None,
    use_llm: bool = True,
) -> AgentResult:
    """
    Run deterministic SQL analysis and optional LLM explanation.

    The LLM never changes the deterministic verdict or score.
    """

    # Step 1: Deterministic analysis
    risk = analyze_sql(sql, conninfo=conninfo)

    # Step 2: Build the authoritative result
    result = AgentResult(
        sql=sql,
        verdict=risk.verdict,
        score=risk.score,
        reasons=list(risk.reasons),
        analysis_mode=risk.analysis_mode,
        analysis_status=risk.analysis_status,
        estimated_rows=risk.estimated_rows,
        scan_type=risk.scan_type,
        llm_status="skipped",
        llm_explanation=None,
        llm_recommendations=[],
    )

    # Step 3: LLM explicitly disabled
    if not use_llm:
        return result

    # Step 4: Do not ask the LLM to explain an incomplete analysis
    if risk.analysis_status != "completed":
        return result

    # Step 5: Prepare structured evidence for the LLM
    risk_data: dict[str, Any] = asdict(risk)

    # Step 6: Request the LLM explanation
    try:
        explanation = explain_risk(
            sql=sql,
            risk_result=risk_data,
        )

        result.llm_status = "completed"
        result.llm_explanation = explanation["explanation"]
        result.llm_recommendations = explanation["recommendations"]

    except LLMError as exc:
        result.llm_status = "failed"
        result.llm_error = str(exc)

    return result

