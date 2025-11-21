import json
from typing import Dict, Any, Optional
from src.core.types import Plan
from src.interfaces.llm import LLMClient
from src.core.utils import PromptLoader

class Planner:
    def __init__(self, llm_client: LLMClient, prompt_loader: PromptLoader):
        self.llm = llm_client
        self.prompt_loader = prompt_loader
        self.prompt_template = self.prompt_loader.load("planner-retail-v2.md")

    def plan(
        self, 
        user_query: str, 
        user_ctx: Dict[str, str], 
        glossary_hits: Optional[list] = None,
        intent_catalog: Optional[list] = None
    ) -> Plan:
        
        inputs_section = f"""
## Actual Inputs
- user_query: "{user_query}"
- user_ctx: {json.dumps(user_ctx)}
- glossary_hits: {json.dumps(glossary_hits or [])}
- intent_catalog: {json.dumps(intent_catalog or [])}
"""
        full_prompt = self.prompt_template + "\n" + inputs_section

        response_text = self.llm.generate_content(
            prompt=full_prompt,
            temperature=0.0,
            response_schema=Plan.model_json_schema()
        )

        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_text)
            return Plan(**data)
        except json.JSONDecodeError:
            # In a real app, we'd have better error handling or retry logic
            return Plan(
                intent_id="error",
                tables=[],
                measures=[],
                dimensions=[],
                filters=[],
                limits={"rows": 0},
                needs_disambiguation=True,
                clarification_question="Failed to generate a valid plan. Please try again."
            )
