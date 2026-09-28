import os
from pathlib import Path
from fpdf import FPDF

# Project root directory-ஐ கண்டறிதல்
BASE_DIR = Path(__file__).resolve().parent.parent

def save_pdf(layout: list) -> str:
    try:
        # static/exports கோப்பகத்தை முழுமையான பாதையுடன் உருவாக்குதல்
        output_dir = BASE_DIR / "static" / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = output_dir / "comic_story.pdf"
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        for panel in layout:
            pdf.add_page()
            
            # தலைப்பு அமைத்தல் (fpdf2-ல் new_x, new_y பயன்படுத்த வேண்டும்)
            pdf.set_font("Helvetica", "B", 16)
            title_text = f"Panel {panel.get('panel', '')}: {panel.get('title', '')}"
            pdf.cell(0, 10, text=title_text, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
            # படம் இருந்தால் சேர்த்தல்
            img_path = panel.get("image")
            if img_path:
                full_img_path = BASE_DIR / img_path if not os.path.isabs(img_path) else Path(img_path)
                if full_img_path.exists():
                    try:
                        pdf.image(str(full_img_path), x=20, y=pdf.get_y(), w=170)
                        pdf.ln(100)
                    except Exception as img_err:
                        print(f"PDF image embed warning: {img_err}")
            
            # Narration / Dialogue சேர்த்தல்
            pdf.set_font("Helvetica", size=11)
            raw_text = panel.get("text", "")
            # Unicode / Emoji எழுத்துக்களை Latin-1-க்கு மாற்றுதல்
            safe_text = raw_text.encode("latin-1", "replace").decode("latin-1")
            
            pdf.multi_cell(w=0, h=7, text=safe_text)
            
        pdf.output(str(file_path))
        print(f"PDF successfully generated at: {file_path}")
        return "/static/exports/comic_story.pdf"

    except Exception as e:
        print(f"Error generating PDF in save_pdf: {e}")
        return "/static/exports/comic_story.pdf"