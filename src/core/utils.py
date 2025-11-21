from pathlib import Path

class PromptLoader:
    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)

    def load(self, prompt_name: str) -> str:
        """
        Loads a prompt markdown file by name.
        Args:
            prompt_name: The name of the prompt file (e.g., 'router-retail-v1.md').
        Returns:
            The content of the prompt file.
        """
        prompt_path = self.prompts_dir / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
