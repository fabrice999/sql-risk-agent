import pytest

from sql_risk_agent.rules import evaluate_estimated_rows


@pytest.mark.parametrize(
    "estimated_rows, expected_verdict, expected_score",
    [
        (0, "allow", 0),
        (1, "allow", 0),
        (100, "allow", 0),
        (101, "warn", 50),
        (10000, "warn", 50),
        (10001, "block", 90),
        (99990, "block", 90),
    ],
)
def test_estimated_rows(
    estimated_rows,
    expected_verdict,
    expected_score,
):
    result = evaluate_estimated_rows(estimated_rows)

    assert result.verdict == expected_verdict
    assert result.score == expected_score
