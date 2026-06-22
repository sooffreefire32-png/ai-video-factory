import os, json, subprocess, urllib.request, glob

GH_TOKEN  = os.environ.get("GH_TOKEN", "")
CHARACTER = "assets/character.mp4"

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

os.makedirs("output", exist_ok=True)

CHAR_FRAME = "output/char_frame.png"
THUMB_BG   = "output/thumb_bg.jpg"
THUMB_OUT  = "output/thumbnail.jpg"
W, H       = 1280, 720

# ── Step 1: Extract best frame from character.mp4 ─────────────────────────────

char_ok = False
if os.path.exists(CHARACTER) and os.path.getsize(CHARACTER) > 1000:
    for ts in ["00:00:02", "00:00:01", "00:00:03", "00:00:00"]:
        r = subprocess.run([
            "ffmpeg", "-ss", ts, "-i", CHARACTER,
            "-frames:v", "1",
            "-vf", "scale=400:-2",
            "-y", CHAR_FRAME, "-loglevel", "quiet"
        ], capture_output=True)
        if os.path.exists(CHAR_FRAME) and os.path.getsize(CHAR_FRAME) > 2000:
            char_ok = True
            print(f"✅ Character frame extracted at {ts}")
            break
else:
    print("⚠️ character.mp4 not found")

# ── Step 2: DALL-E 3 background via GH_TOKEN ─────────────────────────────────

def try_dalle_bg():
    if not GH_TOKEN:
        return False
    try:
        import base64
        prompt = (
            script.get("thumbnail_prompt", script["title"]) +
            ". YouTube thumbnail background: dramatic cinematic scene, "
            "vivid glowing colors, dark atmosphere, "
            "professional studio quality, NO text, NO people, "
            "16:9 widescreen"
        )
        data = json.dumps({
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1792x1024",
            "quality": "standard",
            "response_format": "b64_json"
        }).encode()

        req = urllib.request.Request(
            "https://models.inference.ai.azure.com/images/generations",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GH_TOKEN}"
            }
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())

        img_b64 = result["data"][0]["b64_json"]
        with open(THUMB_BG, "wb") as f:
            f.write(base64.b64decode(img_b64))
        print("✅ BG from DALL-E 3")
        return True
    except Exception as e:
        print(f"⚠️ DALL-E 3: {e}")
        return False

def try_scene_bg():
    candidates = (
        glob.glob("output/media/scene_1_clip_0.mp4") +
        glob.glob("output/media/scene_1_clip_0.jpg") +
        glob.glob("output/media/scene_2_clip_0.jpg") +
        glob.glob("output/media/scene_1_clip_1.jpg") +
        glob.glob("output/media/scene_1.jpg") +
        glob.glob("output/media/scene_1.mp4")
    )
    if not candidates:
        return False

    src = candidates[0]
    if src.endswith(".mp4"):
        in_args = ["-ss", "00:00:01", "-i", src, "-frames:v", "1"]
    else:
        in_args = ["-i", src]

    subprocess.run([
        "ffmpeg", *in_args,
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
        "-y", THUMB_BG, "-loglevel", "quiet"
    ])
    if os.path.exists(THUMB_BG):
        print("✅ BG from scene media")
        return True
    return False

# ── Step 3: Composite — character frame on BG + title text ───────────────────

def composite_ffmpeg():
    title = script["title"][:38].replace("'","").replace(":","").replace('"',"")

    if char_ok and os.path.exists(CHAR_FRAME):
        # Character on bottom-right + title top-center
        subprocess.run([
            "ffmpeg",
            "-i", THUMB_BG,
            "-i", CHAR_FRAME,
            "-filter_complex", (
                f"[0:v]"
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},"
                f"eq=contrast=1.3:brightness=0.0:saturation=1.4,"
                # Dark gradient overlay for text readability
                f"drawbox=x=0:y=0:w={W}:h=160:color=black@0.65:t=fill,"
                f"drawbox=x=0:y={H-180}:w={W}:h=180:color=black@0.45:t=fill"
                f"[bg];"
                # Character overlay bottom-right
                f"[1:v]scale=380:-2[ch];"
                f"[bg][ch]overlay={W-410}:{H-400},"
                # Title shadow
                f"drawtext=text='{title}':"
                f"fontsize=74:fontcolor=black@0.8:"
                f"x=(w-text_w)/2+4:y=44,"
                # Title main
                f"drawtext=text='{title}':"
                f"fontsize=74:fontcolor=white:"
                f"x=(w-text_w)/2:y=40"
                f"[v]"
            ),
            "-map", "[v]",
            "-frames:v", "1",
            "-y", THUMB_OUT, "-loglevel", "quiet"
        ])
    else:
        # No character — just title on BG
        subprocess.run([
            "ffmpeg", "-i", THUMB_BG,
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},"
                f"eq=contrast=1.3:saturation=1.4,"
                f"drawbox=x=0:y=0:w={W}:h=160:color=black@0.65:t=fill,"
                f"drawtext=text='{title}':"
                f"fontsize=74:fontcolor=black@0.8:"
                f"x=(w-text_w)/2+4:y=44,"
                f"drawtext=text='{title}':"
                f"fontsize=74:fontcolor=white:"
                f"x=(w-text_w)/2:y=40"
            ),
            "-frames:v", "1",
            "-y", THUMB_OUT, "-loglevel", "quiet"
        ])

    ok = os.path.exists(THUMB_OUT) and os.path.getsize(THUMB_OUT) > 2000
    if ok:
        print("✅ Thumbnail composited!")
    else:
        print("❌ Thumbnail composite failed")
    return ok

# ── Run ───────────────────────────────────────────────────────────────────────

bg_ok = try_dalle_bg()
if not bg_ok:
    bg_ok = try_scene_bg()

if bg_ok:
    composite_ffmpeg()
else:
    print("❌ Could not generate thumbnail background")