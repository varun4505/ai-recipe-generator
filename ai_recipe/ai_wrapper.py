from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(*_args: Any, **_kwargs: Any) -> None:
        return None


@dataclass
class Recipe:
    title: str
    servings: Optional[int]
    ingredients: List[str]
    steps: List[str]
    tips: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recipe":
        return cls(
            title=str(data.get("title", "Untitled Recipe")),
            servings=(
                int(data["servings"]) if isinstance(data.get("servings"), (int, float, str)) and str(data.get("servings")).isdigit() else None
            ),
            ingredients=[str(x).strip() for x in data.get("ingredients", []) if str(x).strip()],
            steps=[str(x).strip() for x in data.get("steps", []) if str(x).strip()],
            tips=[str(x).strip() for x in data.get("tips", []) if str(x).strip()] or None,
        )

    def to_text(self) -> str:
        lines = [f"Title: {self.title}"]
        if self.servings:
            lines.append(f"Servings: {self.servings}")
        lines.append("\nIngredients:")
        for ing in self.ingredients:
            lines.append(f"- {ing}")
        lines.append("\nSteps:")
        for i, step in enumerate(self.steps, start=1):
            lines.append(f"{i}. {step}")
        if self.tips:
            lines.append("\nTips:")
            for tip in self.tips:
                lines.append(f"- {tip}")
        return "\n".join(lines)


class RecipeGenerator:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        try:
            load_dotenv()
        except Exception:
            pass

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        if genai is not None and self.api_key:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        else:
            self._model = None

    def _build_prompt(self, query: str, servings: Optional[int], diet: Optional[str], no_cook: bool) -> str:
        system = (
            "You are a helpful cooking assistant. Output ONLY valid JSON that matches this schema:\n"
            "{\n  'title': str,\n  'servings': int | null,\n  'ingredients': str[],\n  'steps': str[],\n  'tips': str[] | null\n}\n"
            "No markdown, no backticks, no commentary."
        )
        user = {
            "task": "Generate a concise, tasty recipe",
            "query": query,
            "servings": servings,
            "diet": diet,
            "constraints": [
                "Use accessible ingredients",
                "Keep steps short (max ~20 words each)",
                "Prefer metric units but be flexible",
            ],
        }
        if no_cook:
            user["constraints"].append(
                "No cooking or heat; avoid words like bake, boil, sauté, fry, grill, roast; only no-cook methods."
            )
        return f"{system}\nUSER: {json.dumps(user)}"

    def _build_prompt_from_ingredients(self, ingredients: list[str], servings: Optional[int], diet: Optional[str], no_cook: bool) -> str:
        system = (
            "You are a helpful cooking assistant. Output ONLY valid JSON that matches this schema:\n"
            "{\n  'title': str,\n  'servings': int | null,\n  'ingredients': str[],\n  'steps': str[],\n  'tips': str[] | null\n}\n"
            "No markdown, no backticks, no commentary."
        )
        user = {
            "task": "Create a simple, tasty recipe using only the provided ingredients (plus pantry basics like salt, pepper, oil).",
            "ingredients": ingredients,
            "servings": servings,
            "diet": diet,
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

    def _parse_json(self, text: str) -> Dict[str, Any]:
        s = (text or "").strip()
        if s.startswith("```"):
            if "\n" in s:
                s = s.split("\n", 1)[1]
            if s.endswith("```"):
                s = s[: -3]
            s = s.strip()
        try:
            return json.loads(s)
        except Exception:
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(s[start : end + 1])
            raise ValueError("Model did not return valid JSON.")

    def generate_recipe(
        self,
        query: str,
        servings: Optional[int] = None,
        diet: Optional[str] = None,
        temperature: float = 0.7,
        no_cook: bool = False,
    ) -> Recipe:
        """Generate a recipe for the given query."""
        if self._model is None:
            raise RuntimeError("Gemini model is not available. Set GEMINI_API_KEY and check dependencies.")

        prompt = self._build_prompt(query, servings, diet, no_cook)
        response = self._model.generate_content(prompt, generation_config={"temperature": temperature})

        raw = getattr(response, "text", None) or ""
        data = self._parse_json(raw)
        return Recipe.from_dict(data)

    def generate_recipe_from_ingredients(
        self,
        ingredients: list[str],
        servings: Optional[int] = None,
        diet: Optional[str] = None,
        temperature: float = 0.7,
        no_cook: bool = False,
    ) -> Recipe:
        """Generate a recipe using a list of ingredients."""
        if self._model is None:
            raise RuntimeError("Gemini model is not available. Set GEMINI_API_KEY and check dependencies.")

        prompt = self._build_prompt_from_ingredients(ingredients, servings, diet, no_cook)
        response = self._model.generate_content(prompt, generation_config={"temperature": temperature})
        raw = getattr(response, "text", None) or ""
        data = self._parse_json(raw)
        return Recipe.from_dict(data)
