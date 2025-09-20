import os
import sys
import streamlit as st
from typing import Optional

# Ensure project root is on sys.path so `ai_recipe` is importable when running from app/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai_recipe import Recipe, RecipeGenerator

MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.6


def render_sidebar() -> bool:
    with st.sidebar:
        st.header("Settings")
        cook_mode = st.radio("Cooking method", ["Fire", "Non-fire"], horizontal=True, index=0)
        st.caption(f"Model: {MODEL_NAME} • Temp: {TEMPERATURE}")
        if st.button("Clear", help="Reset current recipe and Q&A"):
            st.session_state.pop("recipe", None)
            st.session_state.pop("last_answer", None)
    return cook_mode == "Non-fire"


def render_input_area() -> str:
    return st.text_area(
        "Ingredients (one per line)",
        placeholder="e.g.\n2 eggs\nspinach\nfeta cheese\ncherry tomatoes",
        height=150,
        key="ingredients_text",
    )


def render_recipe(recipe: Recipe) -> None:
    st.subheader(recipe.title)
    if recipe.servings:
        st.caption(f"Servings: {recipe.servings}")
    st.markdown("### Ingredients")
    st.markdown("\n".join([f"- {ing}" for ing in recipe.ingredients]))
    st.markdown("### Steps")
    for i, step in enumerate(recipe.steps, start=1):
        st.markdown(f"{i}. {step}")
    if recipe.tips:
        st.markdown("### Tips")
        st.markdown("\n".join([f"- {tip}" for tip in recipe.tips]))
    with st.expander("Show as plain text"):
        st.text(recipe.to_text())


def run() -> None:
    st.set_page_config(page_title="AI Recipe Generator (Ingredients)", page_icon="🍳", layout="centered")
    st.title("🍳 Ingredients ➜ Recipe")
    st.caption("Enter ingredients you have; get a recipe.")

    no_cook = render_sidebar()
    ingredients_text = render_input_area()

    generator = RecipeGenerator(model_name=MODEL_NAME, temperature=TEMPERATURE)

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("Generate Recipe", type="primary", key="gen_btn"):
            ingredients = [line.strip() for line in ingredients_text.splitlines() if line.strip()]
            if not ingredients:
                st.warning("Please enter at least one ingredient (one per line).")
            else:
                try:
                    recipe = generator.generate(ingredients=ingredients, no_cook=no_cook)
                    st.session_state["recipe"] = recipe
                except Exception as e:
                    st.error(str(e))

        recipe: Optional[Recipe] = st.session_state.get("recipe")
        if recipe:
            render_recipe(recipe)
        else:
            st.info("Generate a recipe to see details here.")

    with col2:
        st.subheader("Q&A")
        st.caption("Ask about this recipe")
        q = st.text_input("Your question", key="q_input", placeholder="How long does it take? Can I replace X?")
        if st.button("Ask", key="ask_btn"):
            recipe: Optional[Recipe] = st.session_state.get("recipe")
            if not recipe:
                st.warning("Generate a recipe first.")
            elif not q.strip():
                st.warning("Enter a question.")
            else:
                try:
                    answer = generator.answer_question(recipe=recipe, question=q.strip())
                    st.session_state["last_answer"] = answer
                except Exception as e:
                    st.error(str(e))
        if st.session_state.get("last_answer"):
            st.markdown("**Answer**")
            st.write(st.session_state["last_answer"])


if __name__ == "__main__":
    run()
