import json
from typing import Dict, Any, Optional
from src.core.types import Plan
from src.interfaces.llm import LLMClient

class SQLGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_sql(self, plan: Plan, schema_info: str = "") -> str:
        """
        Generates executable SQL from a Plan object.
        """
        # Default schema info if not provided (in a real app, this might come from a catalog service)
        if not schema_info:
            schema_info = """
            - fct_sales (order_id, order_date, product_id, store_id, net_sales, quantity)
            - dim_product (product_id, product_name, category)
            - dim_store (store_id, store_name, region)
            """

        sql_prompt = f"""
        You are a BigQuery SQL Expert. Convert this Plan into executable DuckDB SQL.
        Schema: 
        {schema_info}
        
        Plan: {plan.model_dump_json()}
        
        Rules:
        - Use JOINs correctly.
        - Return ONLY the SQL, no markdown.
        - LIMIT is mandatory.
        """
        
        response = self.llm.generate_content(
            prompt=sql_prompt,
            temperature=0.0
        )
        
        # Clean up markdown if present
        sql = response.replace("```sql", "").replace("```", "").strip()
        return sql
