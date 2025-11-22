import re
from typing import List, Optional

class Validator:
    def __init__(self, policy_config: Optional[dict] = None):
        self.policy = policy_config or {}
        self.allowed_tables = {"fct_sales", "dim_product", "dim_store"}

    def validate(self, sql: str, tenant_id: Optional[str] = None) -> bool:
        """
        Validates SQL against safety rules.
        Returns True if safe, raises ValueError if unsafe.
        """
        sql_upper = sql.upper()

        # 1. Block DDL/DML
        forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
        for kw in forbidden_keywords:
            if kw in sql_upper:
                raise ValueError(f"Security Violation: Forbidden keyword '{kw}' detected.")

        # 2. Enforce SELECT only
        if not sql_upper.strip().startswith("SELECT") and not sql_upper.strip().startswith("WITH"):
             raise ValueError("Security Violation: Query must start with SELECT or WITH.")

        # 3. Enforce LIMIT (Simple check)
        if "LIMIT" not in sql_upper:
             raise ValueError("Policy Violation: Query must contain a LIMIT clause.")

        # 4. Enforce table allowlist
        from sqlglot import parse_one, exp
        
        try:
            parsed = parse_one(sql)
            tables = {str(t.name).lower() for t in parsed.find_all(exp.Table)}
            unauthorized = tables - {t.lower() for t in self.allowed_tables}
            if unauthorized:
                raise ValueError(f"Security Violation: Unauthorized tables: {unauthorized}")
                
            # 5. Enforce Tenant Isolation
            # Check if any WHERE clause contains tenant_id equality check
            if tenant_id:
                has_tenant_filter = False
                for where in parsed.find_all(exp.Where):
                    # Naive string check on the where clause expression for PoC
                    if f"tenant_id = '{tenant_id}'" in where.sql().lower():
                        has_tenant_filter = True
                        break
                        
                if not has_tenant_filter:
                     # Fallback to regex if AST check is too complex for this snippet
                     if f"tenant_id = '{tenant_id}'" not in sql.lower():
                        raise ValueError("Security Violation: Missing tenant_id filter")

        except Exception as e:
            raise ValueError(f"SQL parsing error: {e}")
        
        return True
