import os
import json
from typing import List

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None


def load_env() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return
    load_dotenv()
    here = os.path.dirname(__file__)
    env_path = os.path.join(os.path.dirname(here), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=False)


class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        if genai is None:
            raise RuntimeError("google-generativeai is not installed. Run: pip install -r requirements.txt")
        load_env()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment or .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, temperature: float = 0.6) -> str:
        resp = self.model.generate_content(prompt, generation_config={"temperature": temperature})
        return (getattr(resp, "text", "") or "").strip()

    @staticmethod
    def build_prompt_from_ingredients(ingredients: List[str], no_cook: bool) -> str:
        system = (
            "You are a helpful cooking assistant. Output ONLY valid JSON that matches this schema:\n"
            "{\n  'title': str,\n  'servings': int | null,\n  'ingredients': str[],\n  'steps': str[],\n  'tips': str[] | null\n}\n"
            "No markdown, no backticks, no commentary."
        )
        user = {
            "task": "Create a simple, tasty recipe using only the provided ingredients (plus pantry basics like salt, pepper, oil).",
            "ingredients": ingredients,
            "constraints": [
                "If an ingredient is missing, suggest a reasonable substitution",
                "Keep steps short (max ~20 words each)",
                "Prefer metric units but be flexible",
            ],
        }
        if no_cook:
            user["constraints"].append(
                "No cooking or heat; avoid words like bake, boil, sauté, fry, grill, roast; only no-cook methods."
            )
        return f"{system}\nUSER: {json.dumps(user)}"
