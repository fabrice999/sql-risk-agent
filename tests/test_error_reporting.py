from sql_risk_agent.analyzer import analyze_sql


def test_invalid_sql():

    result = analyze_sql(
        "DELETE FROM WHERE;"
    )

    assert result.verdict == "block"
    assert result.analysis_status == "failed"
    assert result.analysis_mode == "static"


def test_postgresql_connection_failure(monkeypatch):

    def fake_explain(sql, conninfo):
        raise ConnectionError("connection refused")

    monkeypatch.setattr(
        "sql_risk_agent.analyzer.get_explain_plan",
        fake_explain,
    )

    result = analyze_sql(
        "DELETE FROM orders WHERE id = 42;",
        conninfo="fake-connection",
    )

    assert result.verdict == "block"
    assert result.score == 100
    assert result.analysis_mode == "postgresql"
    assert result.analysis_status == "failed"
    assert "connection refused" in result.reasons[0]


def test_static_block_is_not_analysis_failure():

    result = analyze_sql(
        "DELETE FROM orders;"
    )

    assert result.verdict == "block"
    assert result.score == 90
    assert result.analysis_status == "completed"
