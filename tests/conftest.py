import pytest
import json
from unittest.mock import MagicMock
from src.core.planner import Planner
from src.core.utils import PromptLoader
from src.core.utils import PromptLoader
from src.interfaces.llm import LLMClient
from src.core.context import SecurityContext

# Mock LLM Client
class MockLLM(LLMClient):
    def generate_content(self, prompt, temperature=0.0, response_schema=None, system_instruction=None):
        # Check if it's a router prompt
        if "router" in prompt.lower() or "route" in prompt.lower():
            route = "sql"
            reason = "Mock reason"
            
            if "disclosure" in prompt or "DELETE" in prompt:
                route = "unsafe"
                reason = "PII exfiltration" if "disclosure" in prompt else "DML operation"
            elif "lay off" in prompt:
                route = "handoff"
                reason = "HR advisory"
            elif "restricted" in prompt or "margin" in prompt and "viewer" in prompt:
                 # Simulate policy enforcement
                 route = "unsafe"
                 reason = "Policy violation"
                 
            return json.dumps({
                "route": route,
                "reason": reason
            })
        
        # Default to Plan for planner
        needs_disambiguation = False
        intent_id = "net_sales"
        
        if "margin" in prompt.lower():
            needs_disambiguation = True
            intent_id = ""
            
        return json.dumps({
            "intent_id": intent_id,
            "tables": ["fct_sales", "dim_product"],
            "measures": [{"name": "net_sales", "table": "fct_sales", "column": "net_sales", "unit": "USD", "aggregation": "SUM"}],
            "dimensions": [{"name": "category", "table": "dim_product", "column": "category", "type": "category"}],
            "filters": [],
            "time_window": None,
            "limits": {"rows": 100},
            "viz_hint": None,
            "needs_disambiguation": needs_disambiguation,
            "reasoning": "Mock plan"
        })

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
def prompt_loader():
    # Mock prompt loader to avoid file I/O issues in tests if prompts dir is missing
    loader = MagicMock(spec=PromptLoader)
    def load_side_effect(name):
        if "router" in name:
            return "Router Prompt Template"
        return "Planner Prompt Template"
    loader.load.side_effect = load_side_effect
    return loader

@pytest.fixture
def planner(mock_llm, prompt_loader):
    return Planner(mock_llm, prompt_loader)

@pytest.fixture
def golden_set():
    return [
        {
            "input": {
                "user_query": "Show net sales by category",
                "user_ctx": SecurityContext(tenant_id="t1", user_id="u1", role="admin")
            },
            "expected_output": {"plan": True},
            "allowed_measures": ["net_sales"],
            "allowed_units": ["USD"],
            "expected_output": {"route": "sql"} # Added for router test
        }
    ]

@pytest.fixture
def glossary():
    return [
        {"term": "net sales", "table": "fct_sales", "column": "net_sales", "measure": "net_sales", "unit": "USD"},
        {"term": "category", "table": "dim_product", "column": "category"}
    ]

@pytest.fixture
def golden_queries():
    return [
        {"user_query": "Show sales", "user_ctx": SecurityContext(tenant_id="t1", user_id="u1", role="admin")}
    ]

@pytest.fixture
def router(mock_llm, prompt_loader):
    from src.core.router import Router
    from src.core.types import RouterOutput
    # Mock Router.run to return deterministic output for tests
    # Since Router uses LLM, we can either mock LLM or mock Router.run
    # test_router.py tests Router.run logic, so we should mock LLM.
    # But MockLLM returns a Plan JSON, not RouterOutput JSON.
    # We need MockLLM to be smarter or mock Router.run directly for some tests.
    # Let's make MockLLM return different JSON based on prompt content? 
    # Or just mock Router.run for simplicity in this fix.
    
    router = Router(mock_llm, prompt_loader)
    # Do not mock router.route directly, let it use mock_llm
    return router

@pytest.fixture
def policy_profiles():
    return {
        "viewer": {"allowed_intents": ["view_dashboard"], "blocked_intents": ["ad_hoc_query"]}
    }

@pytest.fixture
def sql_validator():
    from src.core.validator import Validator
    validator = Validator()
    # Mock dry_run for testing
    validator.dry_run = MagicMock(return_value=100)
    return validator

@pytest.fixture
def sql_emitter():
    # Mock SQL Emitter/Generator
    emitter = MagicMock()
    # Default to returning a safe, valid SQL with time filter
    emitter.generate_sql.return_value = "SELECT * FROM fct_sales WHERE tenant_id = 't1' AND order_date >= '2024-01-01' LIMIT 100"
    return emitter

@pytest.fixture
def plan():
    return {
        "intent_id": "net_sales",
        "measures": [],
        "dimensions": [],
        "filters": [],
        "limits": {"rows": 100}
    }

@pytest.fixture
def template(tmp_path):
    # Create a dummy template file
    p = tmp_path / "template.sql"
    p.write_text("SELECT * FROM {{table}}")
    return str(p)

@pytest.fixture
def user_ctx():
    return SecurityContext(tenant_id="t1", user_id="u1", role="admin")

@pytest.fixture
def allowed_tables():
    return ["fct_sales", "dim_product", "dim_store"]

@pytest.fixture
def allowed_columns():
    return ["net_sales", "category", "store_name"]

@pytest.fixture
def intent_requires_time():
    return True

@pytest.fixture
def max_bytes():
    return 1000000
