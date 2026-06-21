import os, json, subprocess

with open("output/script.json") as f:
    script = json.load(f)

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
thumb_out = "output/thumbnail.jpg"

def try_imagen():
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            script.get("thumbnail_prompt", script["title"]) +
            ". YouTube thumbnail style: bright vivid colors, "
            "bold eye-catching design, high contrast, professional, 16:9"
        )
        resp = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="BLOCK_ONLY_HIGH"
            )
        )
        img_bytes = resp.generated_images[0].image.image_bytes
        with open(thumb_out, "wb") as f:
            f.write(img_bytes)
        print("✅ Thumbnail from Imagen 3")
        return True
    except Exception as e:
        print(f"⚠️ Imagen failed: {e}")
        return False

def try_ffmpeg_thumb():
    """Generate thumbnail from first scene media"""
    import glob
    candidates = (
        glob.glob("output/media/scene_1.mp4") +
        glob.glob("output/media/scene_1.jpg") +
        glob.glob("output/media/scene_2.jpg")
    )
    if not candidates:
        return False

    src = candidates[0]
    title_safe = script["title"][:30].replace("'", "").replace(":", "")

    if src.endswith(".mp4"):
        input_args = ["-i", src, "-ss", "00:00:01", "-frames:v", "1"]
    else:
        input_args = ["-i", src]

    subprocess.run([
        "ffmpeg", *input_args,
        "-vf", (
            f"scale=1280:720:force_original_aspect_ratio=increase,"
            f"crop=1280:720,"
            f"eq=contrast=1.2:brightness=0.05:saturation=1.4,"
            f"drawtext=text='{title_safe}':"
            f"fontsize=70:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"box=1:boxcolor=black@0.65:boxborderw=15"
        ),
        "-y", thumb_out, "-loglevel", "quiet"
    ])
    print("✅ Thumbnail from scene frame (FFmpeg)")
    return True

ok = try_imagen()
if not ok:
    try_ffmpeg_thumb()