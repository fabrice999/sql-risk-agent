from sql_risk_agent.postgres import extract_explain_info


def test_extract_delete_explain_info():

    plan = [
        {
            "Plan": {
                "Node Type": "ModifyTable",
                "Operation": "Delete",
                "Relation Name": "orders",
                "Total Cost": 2317.00,
                "Plans": [
                    {
                        "Node Type": "Seq Scan",
                        "Relation Name": "orders",
                        "Plan Rows": 99990,
                    }
                ],
            }
        }
    ]

    info = extract_explain_info(plan)

    assert info.operation == "Delete"
    assert info.relation == "orders"
    assert info.scan_type == "Seq Scan"
    assert info.estimated_rows == 99990
    assert info.total_cost == 2317.00
