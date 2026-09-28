import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.8-flash"

def generate_outline(prompt: str) -> list:
    """Prompt-ஐப் பெற்று 5-பேனல் காமிக் அவுட்லைனை JSON வடிவில் உருவாக்குதல்"""
    system_prompt = f"""
You are an expert comic book story creator.
Based on the following idea, break down the story into exactly 5 sequential panels.

Story Idea: {prompt}

Return ONLY a valid JSON list containing exactly 5 objects with these keys:
- "panel": panel number (1 to 5)
- "title": a brief title for the panel
- "scene_description": clear visual description of what happens in the scene
- "image_prompt": detailed text prompt to generate the comic image

Example format:
[
  {{"panel": 1, "title": "Opening", "scene_description": "Hero enters...", "image_prompt": "comic art, vibrant..."}},
  ...
]
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=system_prompt,
        )
        text = response.text.strip()
        # JSON clean-up
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini Flash Error: {e}")
        # API எரர் அல்லது வரம்பு மீறினால் Fallback அவுட்லைன்
        return [
            {"panel": 1, "title": "The Journey Begins", "scene_description": f"Introduction to {prompt}", "image_prompt": f"comic scene of {prompt}, panel 1"},
            {"panel": 2, "title": "The Hidden Path", "scene_description": "Discovering an uncharted path", "image_prompt": "glowing neon pathway, fantasy forest, panel 2"},
            {"panel": 3, "title": "The Secret Chamber", "scene_description": "Arriving at the ancient sanctuary", "image_prompt": "crystalline chamber inside waterfall, panel 3"},
            {"panel": 4, "title": "The Guardian", "scene_description": "Encountering the mystical guardian", "image_prompt": "ancient stone guardian awakening, panel 4"},
            {"panel": 5, "title": "The Crystal Restored", "scene_description": "Restoring power to the neon realm", "image_prompt": "glowing crystal core radiating light, panel 5"}
        ]