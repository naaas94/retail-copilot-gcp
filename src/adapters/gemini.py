import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from src.interfaces.llm import LLMClient

class GeminiAdapter(LLMClient):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
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

        # If system instruction is supported by the client lib version, pass it
        # For simplicity in this PoC, we might prepend it to prompt if needed, 
        # but 1.5 Flash supports system_instruction in the constructor or generate call usually.
        # We'll stick to the simple generate_content for now.
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
