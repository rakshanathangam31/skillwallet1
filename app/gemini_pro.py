import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# தற்போதைய சரியான மாடல் பெயர் இங்கு மாற்றப்பட்டுள்ளது
MODELS_TO_TRY = ["gemini-3.8-flash"]

def generate_story(outline: list) -> str:
    formatted_outline = "\n".join([f"Panel {p.get('panel', idx+1)}: {p.get('title', '')} - {p.get('scene_description', '')}" for idx, p in enumerate(outline)])

    prompt = f"""
You are a comic book writer.
Given this 5-panel breakdown, write vivid narration and dialogue for each panel:

{formatted_outline}

Format each panel clearly:
**Panel 1**
NARRATION: [Narration details]
DIALOGUE: [Character words]

Repeat this format for all 5 panels.
"""
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"Story model {model_name} busy: {e}")
            break  # தாமதத்தைத் தவிர்க்க உடனடியாக fallback-க்குச் செல்லுதல்

    return """
**Panel 1**
NARRATION: The shadows lengthened as Leo stood at the boundary of the Whispering Woods. The neon flora hummed with mystical energy.
DIALOGUE: Leo: "No turning back now... the crystal awaits deep within."

**Panel 2**
NARRATION: Glowing luminescence guided his cautious steps across the damp forest floor.
DIALOGUE: Leo: "These tracks weren't here yesterday. Someone is watching."

**Panel 3**
NARRATION: Behind the shimmering curtain of a crystal waterfall, an ethereal chamber called to him.
DIALOGUE: Leo: "This is it. The hidden sanctuary."

**Panel 4**
NARRATION: An ancient stone guardian stared down with unblinking eyes of sapphire quartz.
DIALOGUE: Leo: "I come only in peace to restore the ancient balance."

**Panel 5**
NARRATION: As paws brushed the radiant core, pure golden light surged through every canopy in the realm.
DIALOGUE: Leo: "We did it! The forest is alive again!"
"""