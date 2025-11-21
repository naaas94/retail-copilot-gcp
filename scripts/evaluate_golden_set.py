import sys
import os
import json
import glob
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.router import Router
from src.core.planner import Planner
from src.core.utils import PromptLoader
from src.adapters.gemini import GeminiAdapter
from src.core.config import settings
from src.core.context import get_mock_context

def load_golden_set(path: str) -> List[Dict[str, Any]]:
    files = glob.glob(os.path.join(path, "*.json"))
    cases = []
    for f in files:
        with open(f, "r") as fd:
            cases.append(json.load(fd))
    return cases

def evaluate():
    print(f"🚀 Starting Evaluation on {settings.ENV} environment...")
    
    # Initialize Components
    if not settings.GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found. Skipping evaluation.")
        return

    llm = GeminiAdapter(api_key=settings.GOOGLE_API_KEY)
    loader = PromptLoader(settings.PROMPTS_DIR)
    router = Router(llm, loader)
    planner = Planner(llm, loader)
    
    # Load Data
    golden_set_path = os.path.join("eval", "golden_set")
    cases = load_golden_set(golden_set_path)
    print(f"📂 Loaded {len(cases)} test cases from {golden_set_path}")
    
    results = {"passed": 0, "failed": 0, "details": []}
    
    for case in cases:
        case_id = case.get("id", "unknown")
        query = case["input"]["user_query"]
        user_ctx = case["input"]["user_ctx"]
        expected_route = case["expected_output"]["route"]
        
        print(f"\n🧪 Testing Case: {case_id} - '{query}'")
        
        try:
            # 1. Test Router
            route_out = router.route(query, user_ctx=user_ctx)
            
            if route_out.route != expected_route:
                print(f"  ❌ Router Mismatch: Expected {expected_route}, Got {route_out.route}")
                results["failed"] += 1
                results["details"].append({"id": case_id, "stage": "router", "error": "Route mismatch"})
                continue
            
            print(f"  ✅ Router: {route_out.route}")
            
            # 2. Test Planner (if SQL)
            if expected_route == "sql":
                plan_out = planner.plan(query, user_ctx=user_ctx)
                # Basic validation: check if intent matches if specified
                expected_intent = case["expected_output"].get("plan", {}).get("intent_id")
                if expected_intent and plan_out.intent_id != expected_intent:
                     print(f"  ❌ Plan Intent Mismatch: Expected {expected_intent}, Got {plan_out.intent_id}")
                     results["failed"] += 1
                     results["details"].append({"id": case_id, "stage": "planner", "error": "Intent mismatch"})
                     continue
                print(f"  ✅ Planner: Intent {plan_out.intent_id}")

            results["passed"] += 1
            
        except Exception as e:
            print(f"  🔥 Exception: {str(e)}")
            results["failed"] += 1
            results["details"].append({"id": case_id, "error": str(e)})

    # Summary
    print("\n" + "="*30)
    print("📊 Evaluation Summary")
    print("="*30)
    print(f"Total Cases: {len(cases)}")
    print(f"Passed:      {results['passed']}")
    print(f"Failed:      {results['failed']}")
    accuracy = (results['passed'] / len(cases)) * 100 if cases else 0
    print(f"Accuracy:    {accuracy:.1f}%")
    
    if results["failed"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    evaluate()
