import os
import streamlit as st
from ai_recipe.ai_wrapper import RecipeGenerator


st.set_page_config(page_title="AI Recipe Generator (Ingredients)", page_icon="🍳", layout="centered")

st.title("🍳 Ingredients ➜ Recipe")
st.caption("Enter ingredients you have; get a recipe.")

with st.sidebar:
    st.header("Settings")
    model_name = st.text_input("Model", value="gemini-2.5-flash")
    temperature = st.slider("Creativity (temperature)", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
    servings = st.number_input("Servings (optional)", min_value=1, max_value=20, value=2, step=1)
    use_servings = st.checkbox("Use servings", value=True)
    diet = st.selectbox("Diet (optional)", ["", "vegan", "vegetarian", "gluten-free", "keto", "paleo"], index=0)
    cook_mode = st.radio("Cooking method", ["Fire", "Non-fire"], horizontal=True, index=0)
    st.divider()

ingredients_text = st.text_area(
    "Ingredients (one per line)",
    placeholder="e.g.\n2 eggs\nspinach\nfeta cheese\ncherry tomatoes",
    height=150,
)

generate = st.button("Generate Recipe", type="primary")

if generate:
    ingredients = [line.strip() for line in ingredients_text.splitlines() if line.strip()]
    if not ingredients:
        st.warning("Please enter at least one ingredient (one per line).")
        st.stop()

    generator = RecipeGenerator(api_key=None, model_name=model_name)
    recipe = generator.generate_recipe_from_ingredients(
        ingredients=ingredients,
        servings=servings if use_servings else None,
        diet=diet or None,
        temperature=temperature,
        no_cook=(cook_mode == "Non-fire"),
    )

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
