from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Retail Copilot (Local PoC)"
    ENV: str = "development"
    DEBUG: bool = True
    
    # LLM
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-pro"
    TEMPERATURE: float = 0.0
    
    # Database
    DUCKDB_PATH: str = "retail_copilot.duckdb"
    
    # Paths
    PROMPTS_DIR: str = "prompts"
    CATALOG_DIR: str = "catalog"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
