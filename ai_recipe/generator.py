import json
from typing import List, Optional

from .models import Recipe
from .gemini_client import GeminiClient


def _parse_json(text: str) -> dict:
    s = (text or "").strip()
    if s.startswith("```"):
        if "\n" in s:
            s = s.split("\n", 1)[1]
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(s[start : end + 1])
        raise ValueError("Model did not return valid JSON.")


class RecipeGenerator:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.6) -> None:
        self.client = GeminiClient(model_name)
        self.temperature = temperature

    def generate(self, ingredients: List[str], no_cook: bool) -> Recipe:
        prompt = self.client.build_prompt_from_ingredients(ingredients, no_cook)
        text = self.client.generate(prompt, temperature=self.temperature)
        data = _parse_json(text)
        return Recipe(
            title=str(data.get("title", "Untitled Recipe")),
            servings=(
                int(data["servings"]) if isinstance(data.get("servings"), (int, float, str)) and str(data.get("servings")).isdigit() else None
            ),
            ingredients=[str(x).strip() for x in data.get("ingredients", []) if str(x).strip()],
            steps=[str(x).strip() for x in data.get("steps", []) if str(x).strip()],
            tips=[str(x).strip() for x in data.get("tips", []) if str(x).strip()] or None,
        )

    def answer_question(self, recipe: Recipe, question: str) -> str:
        context = {
            "instruction": (
                "Answer the user's question strictly using the information in the recipe. "
                "If the answer is not specified in the recipe, respond: 'Not specified in this recipe.'"
            ),
            "recipe": {
                "title": recipe.title,
                "servings": recipe.servings,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
                "tips": recipe.tips,
            },
            "question": question,
        }
        prompt = (
            "You are a cooking assistant. Only use the provided recipe JSON as your source.\n"
            "Respond in plain text, concise.\n\n"
            f"DATA:\n{json.dumps(context, ensure_ascii=False)}"
        )
        return self.client.generate(prompt, temperature=self.temperature)
