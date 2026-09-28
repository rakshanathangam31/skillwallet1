import os
import re
import time
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

def sanitize_filename(text: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', text)[:20]
    return f"{clean}_{int(time.time()*1000)}.jpg"

def fetch_single_image(prompt: str, file_path: str) -> str:
    clean_prompt = re.sub(r'[^a-zA-Z0-9 ]', ' ', prompt).strip()
    short_prompt = " ".join(clean_prompt.split()[:12])
    encoded = urllib.parse.quote(f"{short_prompt}, comic style, vibrant")
    seed = int(time.time() * 1000) % 99999
    
    # Ultra-fast turbo endpoint with optimized size for instant loading
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=480&height=360&nologo=true&seed={seed}&model=turbo"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(image_url, headers=headers, timeout=10)
        if res.status_code == 200 and len(res.content) > 2000:
            with open(file_path, "wb") as f:
                f.write(res.content)
            return "/" + file_path.replace("\\", "/")
    except Exception as e:
        print(f"Fast retry for: {short_prompt[:15]} - {e}")
    
    # Instant visual online fallback if main server delays
    try:
        fb_url = f"https://picsum.photos/seed/{seed}/480/360"
        fb_res = requests.get(fb_url, headers=headers, timeout=4)
        if fb_res.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(fb_res.content)
            return "/" + file_path.replace("\\", "/")
    except Exception:
        pass

    return "/" + file_path.replace("\\", "/")

def generate_image(prompt: str, filename: str = None) -> str:
    if not filename:
        filename = sanitize_filename(prompt)
    output_dir = os.path.join("static", "panels")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    return fetch_single_image(prompt, file_path)