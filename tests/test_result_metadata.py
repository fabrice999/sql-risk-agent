from sql_risk_agent.analyzer import analyze_sql


def test_static_analysis_metadata():

    result = analyze_sql(
        "DELETE FROM orders WHERE id = 42;"
    )

    assert result.verdict == "allow"
    assert result.analysis_mode == "static"
    assert result.estimated_rows is None
    assert result.scan_type is None


def test_postgresql_analysis_metadata(monkeypatch):

    fake_plan = [
        {
            "Plan": {
                "Node Type": "ModifyTable",
                "Operation": "Delete",
                "Relation Name": "orders",
                "Total Cost": 2317.0,
                "Plans": [
                    {
                        "Node Type": "Seq Scan",
                        "Plan Rows": 99990,
                    }
                ],
            }
        }
    ]

    monkeypatch.setattr(
        "sql_risk_agent.analyzer.get_explain_plan",
        lambda sql, conninfo: fake_plan,
    )

    result = analyze_sql(
        "DELETE FROM orders WHERE created_at < now();",
        conninfo="fake-connection",
    )

    assert result.verdict == "block"
    assert result.analysis_mode == "postgresql"
    assert result.estimated_rows == 99990
    assert result.scan_type == "Seq Scan"
