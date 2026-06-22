import os, json, subprocess, glob
from google import genai
from google.genai import types

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
client     = genai.Client(api_key=GEMINI_KEY)

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

out = "output/thumbnail.jpg"

# ── Gemini Imagen 3 ───────────────────────────────────────────────────────────

def try_imagen():
    try:
        prompt = (
            script.get("thumbnail_prompt", script["title"]) +
            ". YouTube thumbnail style: ultra bright vivid colors, "
            "bold eye-catching design, high contrast, "
            "professional quality, 16:9 widescreen, "
            "designed to get clicks from US and UK audience"
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
        with open(out, "wb") as f:
            f.write(img_bytes)
        print("✅ Thumbnail: Gemini Imagen 3")
        return True
    except Exception as e:
        print(f"⚠️ Imagen 3 failed: {e}")
        return False

# ── FFmpeg fallback ───────────────────────────────────────────────────────────

def try_ffmpeg():
    candidates = (
        glob.glob("output/media/scene_1.mp4") +
        glob.glob("output/media/scene_1.jpg") +
        glob.glob("output/media/scene_2.jpg") +
        glob.glob("output/media/scene_3.jpg")
    )
    if not candidates:
        print("⚠️ No media for thumbnail fallback")
        return False

    src   = candidates[0]
    title = script["title"][:35].replace("'","").replace(":","")

    if src.endswith(".mp4"):
        in_args = ["-ss", "00:00:02", "-i", src, "-frames:v", "1"]
    else:
        in_args = ["-i", src]

    subprocess.run([
        "ffmpeg", *in_args,
        "-vf", (
            f"scale=1280:720:force_original_aspect_ratio=increase,"
            f"crop=1280:720,"
            f"eq=contrast=1.4:brightness=0.05:saturation=1.6,"
            f"drawtext=text='{title}':"
            f"fontsize=72:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"box=1:boxcolor=black@0.7:boxborderw=20"
        ),
        "-y", out, "-loglevel", "quiet"
    ])

    if os.path.exists(out):
        print("✅ Thumbnail: FFmpeg fallback")
        return True
    return False

ok = try_imagen()
if not ok:
    try_ffmpeg()