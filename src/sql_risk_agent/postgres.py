from dataclasses import dataclass

import psycopg


@dataclass
class ExplainInfo:
    operation: str
    relation: str
    scan_type: str
    estimated_rows: int
    total_cost: float


def get_explain_plan(sql: str, conninfo: str):

    explain_sql = f"EXPLAIN (FORMAT JSON) {sql}"

    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute(explain_sql)
            result = cur.fetchone()

    return result[0]


def extract_explain_info(plan) -> ExplainInfo:

    root = plan[0]["Plan"]

    operation = root["Operation"]
    relation = root["Relation Name"]
    total_cost = root["Total Cost"]

    scan = root["Plans"][0]

    scan_type = scan["Node Type"]
    estimated_rows = scan["Plan Rows"]

    return ExplainInfo(
        operation=operation,
        relation=relation,
        scan_type=scan_type,
        estimated_rows=estimated_rows,
        total_cost=total_cost,
    )

def get_table_rows(
    relation: str,
    conninfo: str,
    schema: str = "public",
) -> int | None:

    query = """
        SELECT c.reltuples
        FROM pg_catalog.pg_class c
        JOIN pg_catalog.pg_namespace n
          ON n.oid = c.relnamespace
        WHERE n.nspname = %s
          AND c.relname = %s
          AND c.relkind IN ('r', 'p')
    """

    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (schema, relation))
            row = cur.fetchone()

    if row is None or row[0] < 0:
        return None

    return int(row[0])
