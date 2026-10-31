
from unittest.mock import patch

from sql_risk_agent.agent import run_agent
from sql_risk_agent.rules import RiskResult
from sql_risk_agent.llm import LLMError


def fake_risk():
    return RiskResult(
        verdict="block",
        score=90,
        reasons=["Estimated affected percentage: 99.99%"],
        analysis_mode="postgresql",
        analysis_status="completed",
        estimated_rows=99990,
        scan_type="Seq Scan",
    )


def test_agent_without_llm():

    with patch(
        "sql_risk_agent.agent.analyze_sql",
        return_value=fake_risk(),
    ):
        result = run_agent(
            sql="DELETE FROM orders WHERE id > 0;",
            use_llm=False,
        )

    assert result.verdict == "block"
    assert result.score == 90
    assert result.llm_status == "skipped"
    assert result.llm_explanation is None


def test_agent_with_llm():

    with patch(
        "sql_risk_agent.agent.analyze_sql",
        return_value=fake_risk(),
    ), patch(
        "sql_risk_agent.agent.explain_risk",
        return_value={
            "explanation": "The DELETE may affect nearly all rows.",
            "recommendations": [
                "Verify the WHERE condition."
            ],
        },
    ):
        result = run_agent(
            sql="DELETE FROM orders WHERE id > 0;",
            use_llm=True,
        )

    assert result.verdict == "block"
    assert result.score == 90
    assert result.llm_status == "completed"
    assert result.llm_explanation == (
        "The DELETE may affect nearly all rows."
    )


def test_agent_llm_failure():

    with patch(
        "sql_risk_agent.agent.analyze_sql",
        return_value=fake_risk(),
    ), patch(
        "sql_risk_agent.agent.explain_risk",
        side_effect=LLMError("Ollama timed out"),
    ):
        result = run_agent(
            sql="DELETE FROM orders WHERE id > 0;",
            use_llm=True,
        )

    assert result.verdict == "block"
    assert result.score == 90
    assert result.llm_status == "failed"
    assert "timed out" in result.llm_error


def test_agent_skips_llm_when_analysis_failed():

    failed_risk = RiskResult(
        verdict="block",
        score=100,
        reasons=["PostgreSQL EXPLAIN failed"],
        analysis_mode="postgresql",
        analysis_status="failed",
    )

    with patch(
        "sql_risk_agent.agent.analyze_sql",
        return_value=failed_risk,
    ), patch(
        "sql_risk_agent.agent.explain_risk",
    ) as mock_llm:

        result = run_agent(
            sql="DELETE FROM orders WHERE id = 42;",
            use_llm=True,
        )

    assert result.analysis_status == "failed"
    assert result.llm_status == "skipped"
    mock_llm.assert_not_called()

