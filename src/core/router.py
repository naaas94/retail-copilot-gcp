import json
from typing import Dict, Any, Optional
from src.core.types import RouterOutput
from src.interfaces.llm import LLMClient
from src.core.utils import PromptLoader

class Router:
    def __init__(self, llm_client: LLMClient, prompt_loader: PromptLoader):
        self.llm = llm_client
        self.prompt_loader = prompt_loader
        self.prompt_template = self.prompt_loader.load("router-retail-v1.md")

    def route(
        self, 
        user_query: str, 
        user_ctx: Dict[str, str], 
        glossary_hits: Optional[list] = None,
        policy_profile: Optional[Dict[str, Any]] = None
    ) -> RouterOutput:
        
        # Construct the full prompt with inputs
        # In a real system, we'd use Jinja2, but f-string is fine for PoC
        inputs_section = f"""
## Actual Inputs
- user_query: "{user_query}"
- user_ctx: {json.dumps(user_ctx)}
- glossary_hits: {json.dumps(glossary_hits or [])}
- policy_profile: {json.dumps(policy_profile or {})}
"""
        full_prompt = self.prompt_template + "\n" + inputs_section

        # Call LLM
        response_text = self.llm.generate_content(
            prompt=full_prompt,
            temperature=0.0,
            response_schema=RouterOutput.model_json_schema()
        )

        # Parse response (Gemini API can return JSON directly, but we'll parse just in case)
        try:
            # Clean up markdown code blocks if present
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_text)
            return RouterOutput(**data)
        except json.JSONDecodeError:
            # Fallback or error handling
            return RouterOutput(
                route="clarify", 
                reason="Failed to parse router output", 
                clarify_question="I'm having trouble understanding. Could you rephrase?"
            )
