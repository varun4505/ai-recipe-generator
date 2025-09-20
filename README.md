# AI Recipe Generator (Gemini) – Workshop Skeleton

This is a clean, multi-file skeleton of a simple Streamlit app that uses Gemini to generate a recipe from ingredients and includes a Q&A panel about the generated recipe.

## Structure

- `ai_recipe/` – core logic package
  - `models.py` – `Recipe` dataclass
  - `gemini_client.py` – environment loading and Gemini client wrapper
  - `generator.py` – recipe generation and Q&A helpers
- `app/`
  - `streamlit_app.py` – Streamlit UI
- `.env` – put your `GEMINI_API_KEY` here (not committed)
- `requirements.txt` – Python dependencies

## Setup

1) Python 3.10+ recommended. Create venv (optional):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:
```powershell
python -m pip install -r requirements.txt
```

3) Create `.env` in project root with your API key:
```env
GEMINI_API_KEY=your_real_api_key_here
```

## Run the app
```powershell
streamlit run .\app\streamlit_app.py
```

Open the URL shown (e.g., http://localhost:8501).

## Use
- Enter ingredients (one per line).
- Choose "Fire" or "Non-fire" in the sidebar.
- Click "Generate Recipe".
- Ask questions about the recipe in the right panel.
- Use the sidebar "Clear" button to reset.

## Notes
- Model: `gemini-2.5-flash`, Temperature: `0.6` (hardcoded in the UI).
- The app reads `GEMINI_API_KEY` from your environment or `.env` (via `python-dotenv`).
