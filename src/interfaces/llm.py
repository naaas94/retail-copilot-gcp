from typing import Protocol, List, Dict, Any, Optional

class LLMClient(Protocol):
    def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates content from the LLM.
        
        Args:
            prompt: The user prompt.
            system_instruction: Optional system prompt.
            temperature: Sampling temperature.
            response_schema: Optional JSON schema for structured output.
            
        Returns:
            The generated text response.
        """
        ...
