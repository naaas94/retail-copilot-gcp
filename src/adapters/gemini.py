import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from src.interfaces.llm import LLMClient

class GeminiAdapter(LLMClient):
    def __init__(self, api_key: Optional[str] = None, model_name: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        # Use config default if not specified
        from src.core.config import settings
        model_name = model_name or settings.LLM_MODEL
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json" if response_schema else "text/plain"
        )

        # Handle system instruction
        # gemini-1.5-flash supports system_instruction in generation config or model init, 
        # but for broad compatibility in this PoC, we'll prepend it to the prompt if provided.
        final_prompt = prompt
        if system_instruction:
            final_prompt = f"System Instruction: {system_instruction}\n\n{prompt}"
        
        response = self.model.generate_content(
            final_prompt,
            generation_config=generation_config
        )
        
        return response.text
