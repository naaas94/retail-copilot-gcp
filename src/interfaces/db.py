from typing import Protocol, Any
import pandas as pd

class DatabaseClient(Protocol):
    def execute_query(self, sql: str) -> pd.DataFrame:
        """
        Executes a SQL query and returns the result as a DataFrame.
        
        Args:
            sql: The SQL query to execute.
            
        Returns:
            A pandas DataFrame containing the results.
        """
        ...
        
    def validate_sql(self, sql: str) -> bool:
        """
        Validates if the SQL is syntactically correct for this dialect.
        """
        ...
