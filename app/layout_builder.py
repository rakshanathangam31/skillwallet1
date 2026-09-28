def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    raw_segments = full_story.split("**Panel")
    story_panels = [seg for seg in raw_segments if seg.strip()]

    layout = []
    for idx, (img, panel_info) in enumerate(zip(image_paths, outline), start=1):
        panel_text = ""
        for seg in story_panels:
            if seg.strip().startswith(str(idx)):
                panel_text = seg.strip().split("\n", 1)[-1].strip() if "\n" in seg.strip() else seg.strip()
                break
        if not panel_text and idx - 1 < len(story_panels):
            panel_text = story_panels[idx - 1].strip()

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": img.replace("\\", "/"),
            "text": panel_text,
            "scene_description": panel_info.get("scene_description", "")
        })
    return layout