"""
Unit tests for Planner component
Tests JSON schema validation, slot coverage, and glossary grounding
"""

import pytest
import jsonschema
from typing import Dict, Any


# Planner output schema (mirrors prompts/planner-retail-v2.md)
PLAN_SCHEMA = {
    "type": "object",
    "required": ["intent_id", "measures", "dimensions", "filters", "time_window", 
                "limits", "viz_hint", "needs_disambiguation", "reasoning"],
    "properties": {
        "intent_id": {"type": ["string", "null"]},
        "measures": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "table", "column", "unit", "aggregation"],
                "properties": {
                    "name": {"type": "string"},
                    "table": {"type": "string"},
                    "column": {"type": "string"},
                    "unit": {"type": "string"},
                    "aggregation": {"type": "string", "enum": ["SUM", "AVG", "COUNT", "MAX", "MIN"]}
                }
            }
        },
        "dimensions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "table", "column", "type"],
                "properties": {
                    "name": {"type": "string"},
                    "table": {"type": "string"},
                    "column": {"type": "string"},
                    "type": {"type": "string", "enum": ["category", "time", "geography"]}
                }
            }
        },
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["field", "operator", "value", "source"],
                "properties": {
                    "field": {"type": "string"},
                    "operator": {"type": "string"},
                    "value": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                    "source": {"type": "string"}
                }
            }
        },
        "time_window": {
            "type": ["object", "null"],
            "properties": {
                "grain": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"}
            }
        },
        "limits": {
            "type": "object",
            "required": ["rows"],
            "properties": {
                "rows": {"type": "integer"},
                "categories": {"type": ["integer", "null"]}
            }
        },
        "viz_hint": {
            "type": ["object", "null"],
            "properties": {
                "type": {"type": "string"},
                "x_axis": {"type": ["string", "null"]},
                "y_axis": {"type": ["string", "null"]},
                "series": {"type": ["string", "null"]}
            }
        },
        "needs_disambiguation": {"type": "boolean"},
        "reasoning": {"type": "string"}
    }
}


def test_planner_plan_schema_and_slots(planner, golden_set):
    """
    Test that planner produces valid JSON schema and required slots
    """
    for case in golden_set:
        if "expected_output" not in case or "plan" not in case["expected_output"]:
            continue
            
        plan = planner.run(
            case["input"]["user_query"],
            glossary_hits=case.get("glossary_hits", []),
            intent_catalog=case.get("intent_catalog", []),
            user_ctx=case["input"]["user_ctx"],
            temperature=0.0
        )
        
        # Validate JSON schema
        jsonschema.validate(instance=plan, schema=PLAN_SCHEMA)
        
        # Slot coverage: measures must be grounded
        if plan["intent_id"] and not plan["needs_disambiguation"]:
            assert len(plan["measures"]) > 0, "Plan must have at least one measure"
            for m in plan["measures"]:
                assert m["name"] in case.get("allowed_measures", []), \
                    f"Measure {m['name']} not in allowed list"
                assert "unit" in m and m["unit"] in case.get("allowed_units", []), \
                    f"Measure {m['name']} must have valid unit"
        
        # Time filter required for time-series intents
        if case.get("intent_id") in ["net_sales", "margin_by_category", "avg_ticket"]:
            time_fields = [f["field"] for f in plan["filters"]]
            assert "order_date" in time_fields or plan["time_window"] is not None, \
                "Time-series intent must have time filter"


def test_planner_glossary_grounding(planner, glossary):
    """
    Test that planner grounds measures/dimensions in glossary
    """
    query = "Show net sales by category"
    glossary_hits = [
        {"term": "net sales", "table": "fct_sales", "column": "net_sales", 
         "measure": "net_sales", "unit": "USD"},
        {"term": "category", "table": "dim_product", "column": "category"}
    ]
    
    plan = planner.run(
        query,
        glossary_hits=glossary_hits,
        user_ctx={"tenant": "tenant_123", "role": "analyst"},
        temperature=0.0
    )
    
    # Check that measures reference glossary
    for measure in plan["measures"]:
        assert measure["table"] in [h["table"] for h in glossary_hits], \
            "Measure table must be grounded in glossary"
        assert measure["column"] in [h["column"] for h in glossary_hits if h.get("column")], \
            "Measure column must be grounded in glossary"


def test_planner_disambiguation_trigger(planner):
    """
    Test that planner correctly triggers disambiguation on ambiguous terms
    """
    query = "Show margin trends"
    glossary_hits = [
        {"term": "margin", "table": "ambiguous", "similarity": 0.5}  # Low similarity
    ]
    
    plan = planner.run(
        query,
        glossary_hits=glossary_hits,
        user_ctx={"tenant": "tenant_123", "role": "analyst"},
        temperature=0.0
    )
    
    assert plan["needs_disambiguation"] == True, \
        "Planner should trigger disambiguation for ambiguous terms"
    assert plan["intent_id"] is None or plan["intent_id"] == "", \
        "Intent should be null when disambiguation needed"


def test_planner_determinism(planner, golden_queries):
    """
    Test that planner produces deterministic outputs
    """
    for q in golden_queries:
        plan1 = planner.run(q["user_query"], user_ctx=q["user_ctx"], temperature=0.0)
        plan2 = planner.run(q["user_query"], user_ctx=q["user_ctx"], temperature=0.0)
        
        assert plan1 == plan2, "Planner must be deterministic with temperature=0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

