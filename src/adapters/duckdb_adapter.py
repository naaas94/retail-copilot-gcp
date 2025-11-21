import duckdb
import pandas as pd
from src.interfaces.db import DatabaseClient

class DuckDBAdapter(DatabaseClient):
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)

    def execute_query(self, sql: str) -> pd.DataFrame:
        return self.conn.execute(sql).df()

    def validate_sql(self, sql: str) -> bool:
        try:
            # DuckDB EXPLAIN is a good way to check syntax without running
            self.conn.execute(f"EXPLAIN {sql}")
            return True
        except Exception:
            return False
            
    def load_parquet(self, table_name: str, file_path: str):
        """Helper to load parquet files into the in-memory DB"""
        self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')")
