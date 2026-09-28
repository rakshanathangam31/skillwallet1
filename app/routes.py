import os
import re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def parse_panel_dialogue(story_text: str, panel_idx: int) -> str:
    """Gemini தரும் கதையிலிருந்து குறிப்பிட்ட பேனலின் வசனங்களைப் பிரித்தெடுத்தல்"""
    pattern = rf"\*\*Panel\s*{panel_idx}\*\*([\s\S]*?)(?=\*\*Panel\s*\d+\*\*|$)"
    match = re.search(pattern, story_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return f"Panel {panel_idx} Story continuation..."

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Hero"),
    setting: str = Form("Enchanted Forest"),
    tone: str = Form("Dramatic"),
    art_style: str = Form("Classic Comic Book")
):
    full_prompt = f"{prompt}. Character: {character_name}. Setting: {setting}. Tone: {tone}. Art Style: {art_style}."

    # 1. ஜெமினி மூலம் 5 பேனல் அவுட்லைன் உருவாக்குதல்
    outline = generate_outline(full_prompt)

    # 2. ஜெமினி மூலம் கதை மற்றும் உரையாடல்களை உருவாக்குதல்
    story_text = generate_story(outline)

    # 3. படங்களை உருவாக்குதல்
    image_paths = []
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            image_futures = [
                executor.submit(
                    generate_image,
                    f"{p.get('image_prompt', 'comic scene')}, {art_style}",
                    f"scene_{idx+1}.jpg"
                )
                for idx, p in enumerate(outline)
            ]
            image_paths = [future.result() for future in image_futures]
    except Exception as img_err:
        print(f"Image generation warning: {img_err}")
        image_paths = ["" for _ in outline]

    # 4. பேனல்களை வரிசைப்படுத்துதல்
    layout = []
    for idx, panel_data in enumerate(outline):
        panel_num = idx + 1
        panel_text = parse_panel_dialogue(story_text, panel_num)
        
        layout.append({
            "panel": panel_num,
            "title": panel_data.get("title", f"Panel {panel_num}"),
            "scene_description": panel_data.get("scene_description", ""),
            "image": image_paths[idx] if idx < len(image_paths) else "",
            "text": panel_text
        })

    # 5. PDF உருவாக்குதல்
    try:
        pdf_path = save_pdf(layout)
    except Exception as pdf_err:
        print(f"PDF creation warning: {pdf_err}")
        pdf_path = None

    # 6. முன்னோட்டப் பக்கத்திற்கு அனுப்புதல் (comic_preview.html)
    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "layout": layout,
            "pdf_path": pdf_path,
            "story_prompt": prompt,
            "character_name": character_name
        }
    )