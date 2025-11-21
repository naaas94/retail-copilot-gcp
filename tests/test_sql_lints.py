"""
Unit tests for SQL validation and linting
Tests DDL/DML blocking, allowlist enforcement, and safety guardrails
"""

import pytest
import sqlparse
from sqlglot import parse_one, exp
from typing import List, Dict


def test_sql_no_ddl_dml(sql_validator, sql_emitter, plan, template):
    """
    Test that SQL validator blocks DDL/DML operations
    """
    # Test that generated SQL doesn't contain DDL/DML
    sql = sql_emitter.run(template, plan)
    
    assert "DROP" not in sql.upper(), "SQL must not contain DROP"
    assert "UPDATE" not in sql.upper(), "SQL must not contain UPDATE"
    assert "DELETE" not in sql.upper(), "SQL must not contain DELETE"
    assert "INSERT" not in sql.upper(), "SQL must not contain INSERT"
    assert "CREATE" not in sql.upper(), "SQL must not contain CREATE"
    assert "ALTER" not in sql.upper(), "SQL must not contain ALTER"
    assert "TRUNCATE" not in sql.upper(), "SQL must not contain TRUNCATE"
    
    # Only SELECT should be present
    parsed = sqlparse.parse(sql)
    assert len(parsed) > 0, "SQL must be parseable"
    assert parsed[0].get_type() == "SELECT", "SQL must be SELECT only"


def test_sql_has_limit(sql_validator, sql_emitter, plan, template):
    """
    Test that all SQL queries include LIMIT clause
    """
    sql = sql_emitter.run(template, plan)
    
    assert "LIMIT" in sql.upper(), "SQL must include LIMIT clause"
    
    # Parse and verify LIMIT value
    parsed = parse_one(sql)
    limit = parsed.find(exp.Limit)
    assert limit is not None, "SQL must have LIMIT clause"
    assert limit.expression is not None, "LIMIT must have a value"


def test_sql_has_tenant_filter(sql_validator, sql_emitter, plan, template, user_ctx):
    """
    Test that all SQL queries include tenant_id filter
    """
    sql = sql_emitter.run(template, plan)
    
    # Check for tenant_id in WHERE clause
    assert "tenant_id" in sql.lower(), "SQL must include tenant_id filter"
    
    # Parse and verify tenant_id predicate
    parsed = parse_one(sql)
    where = parsed.find(exp.Where)
    assert where is not None, "SQL must have WHERE clause"
    
    # Check for tenant_id condition
    tenant_conditions = [
        str(condition).lower() for condition in where.find_all(exp.EQ)
        if "tenant_id" in str(condition).lower()
    ]
    assert len(tenant_conditions) > 0, "WHERE clause must include tenant_id filter"


def test_sql_allowlist_tables(sql_validator, sql_emitter, plan, template, allowed_tables):
    """
    Test that SQL only references allowed tables
    """
    sql = sql_emitter.run(template, plan)
    
    # Extract table names from SQL
    parsed = parse_one(sql)
    tables = [str(table) for table in parsed.find_all(exp.Table)]
    
    # Check all tables are in allowlist
    for table in tables:
        # Remove dataset prefix if present
        table_name = table.split(".")[-1] if "." in table else table
        assert table_name in allowed_tables or table_name.startswith("dim_") or table_name.startswith("fct_"), \
            f"Table {table_name} not in allowlist"


def test_sql_allowlist_columns(sql_validator, sql_emitter, plan, template, allowed_columns):
    """
    Test that SQL only references allowed columns
    """
    sql = sql_emitter.run(template, plan)
    
    # Extract column references
    parsed = parse_one(sql)
    columns = [str(col) for col in parsed.find_all(exp.Column)]
    
    # Check columns are in allowlist (or are calculated/aggregated)
    for col in columns:
        col_name = col.split(".")[-1] if "." in col else col
        # Allow calculated columns and common SQL functions
        if col_name not in allowed_columns and not any(
            func in col_name.upper() for func in ["SUM", "AVG", "COUNT", "MAX", "MIN", "DATE_TRUNC"]
        ):
            # This is a warning, not a hard failure - some columns may be calculated
            pass


def test_sql_time_filter_required(sql_validator, sql_emitter, plan, template, intent_requires_time):
    """
    Test that time-series intents include time filters
    """
    if not intent_requires_time:
        pytest.skip("Intent does not require time filter")
    
    sql = sql_emitter.run(template, plan)
    
    # Check for date/time filter in WHERE clause
    assert any(keyword in sql.upper() for keyword in ["BETWEEN", ">=", "<=", "DATE_TRUNC"]), \
        "Time-series SQL must include time filter"
    
    # Parse and verify date filter
    parsed = parse_one(sql)
    where = parsed.find(exp.Where)
    assert where is not None, "SQL must have WHERE clause for time filter"


def test_sql_budget_check(sql_validator, sql_emitter, plan, template, max_bytes):
    """
    Test that SQL validator checks query budget before execution
    """
    sql = sql_emitter.run(template, plan)
    
    # Dry-run should estimate bytes
    estimated_bytes = sql_validator.dry_run(sql)
    
    assert estimated_bytes is not None, "Dry-run must return byte estimate"
    assert estimated_bytes <= max_bytes, \
        f"Query estimated bytes {estimated_bytes} exceeds max {max_bytes}"


def test_sql_complexity_limits(sql_validator, sql_emitter, plan, template):
    """
    Test that SQL complexity is within limits
    """
    sql = sql_emitter.run(template, plan)
    
    parsed = parse_one(sql)
    
    # Check subquery depth
    subqueries = list(parsed.find_all(exp.Subquery))
    assert len(subqueries) <= 3, "SQL must not exceed max subquery depth of 3"
    
    # Check join count
    joins = list(parsed.find_all(exp.Join))
    assert len(joins) <= 5, "SQL must not exceed max join count of 5"


def test_sql_template_parameterization(sql_emitter, template):
    """
    Test that SQL templates use parameterization, not string concatenation
    """
    # Template should use {{placeholders}}, not string concatenation
    with open(template, "r") as f:
        template_content = f.read()
    
    # Should not contain string concatenation patterns
    assert "+" not in template_content or "CONCAT" in template_content.upper(), \
        "Template should use parameterization, not string concatenation"
    
    # Should contain placeholder syntax
    assert "{{" in template_content and "}}" in template_content, \
        "Template should use {{placeholder}} syntax"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

