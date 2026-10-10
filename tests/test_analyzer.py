from sql_risk_agent.analyzer import analyze_sql


def test_delete_without_where():
    result = analyze_sql("DELETE FROM orders;")

    assert result.verdict == "block"
    assert result.score == 90
    assert "DELETE statement has no WHERE clause" in result.reasons


def test_delete_with_where():
    result = analyze_sql(
        "DELETE FROM orders WHERE customer_id = 42;"
    )

    assert result.verdict == "allow"
    assert result.score == 0


def test_multiple_statements():
    result = analyze_sql(
        "DELETE FROM orders WHERE id = 1; "
        "DELETE FROM customers;"
    )

    assert result.verdict == "block"
    assert result.score == 100

def test_update_without_where():
    result = analyze_sql(
        "UPDATE orders SET status = 'CANCELLED';"
    )

    assert result.verdict == "block"
    assert result.score == 90
    assert "UPDATE statement has no WHERE clause" in result.reasons


def test_update_with_where():
    result = analyze_sql(
        "UPDATE orders "
        "SET status = 'CANCELLED' "
        "WHERE id = 42;"
    )

    assert result.verdict == "allow"
    assert result.score == 0


def test_insert():
    result = analyze_sql(
        "INSERT INTO orders (id, status) "
        "VALUES (1, 'NEW');"
    )

    assert result.verdict == "allow"
    assert result.score == 0


def test_select():
    result = analyze_sql(
        "SELECT * FROM orders WHERE id = 42;"
    )

    assert result.verdict == "allow"
    assert result.score == 0
