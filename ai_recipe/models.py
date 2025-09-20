from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Recipe:
    title: str
    servings: Optional[int]
    ingredients: List[str]
    steps: List[str]
    tips: Optional[List[str]] = None

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
