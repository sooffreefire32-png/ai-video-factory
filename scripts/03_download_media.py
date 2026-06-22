import os, json, requests, subprocess, time

KEY = os.environ["PIXABAY_API_KEY"]

with open("output/script.json") as f:
    script = json.load(f)

os.makedirs("output/media", exist_ok=True)
os.makedirs("assets", exist_ok=True)

# ── download helper ───────────────────────────────────────────────────────────

def download(url, path, timeout=90):
    try:
        r = requests.get(url, timeout=timeout, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=16384):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"    ❌ Download fail: {e}")
        return False

# ── scene video ───────────────────────────────────────────────────────────────

def get_video(query, sid):
    try:
        r = requests.get("https://pixabay.com/api/videos/", params={
            "key": KEY, "q": query, "per_page": 5,
            "min_width": 1280, "video_type": "film"
        }, timeout=20).json()

        hits = r.get("hits", [])
        if not hits:
            return False

        videos = hits[0].get("videos", {})
        url = None
        for quality in ["large", "medium", "small", "tiny"]:
            if quality in videos and videos[quality].get("url"):
                url = videos[quality]["url"]
                break

        if not url:
            return False

        path = f"output/media/scene_{sid}.mp4"
        ok = download(url, path, timeout=120)
        if ok:
            print(f"  ✅ Scene {sid}: video  [{query}]")
        return ok
    except Exception as e:
        print(f"  ⚠️ Video fail scene {sid}: {e}")
        return False

# ── scene image ───────────────────────────────────────────────────────────────

def get_image(query, sid, meme=False):
    try:
        for img_type in (["illustration"] if meme else ["photo", "illustration"]):
            r = requests.get("https://pixabay.com/api/", params={
                "key": KEY, "q": query, "per_page": 5,
                "image_type": img_type, "min_width": 1280,
                "safesearch": "true"
            }, timeout=20).json()
            hits = r.get("hits", [])
            if hits:
                break

        if not hits:
            return False

        url = hits[0].get("largeImageURL") or hits[0].get("webformatURL")
        if not url:
            return False

        path = f"output/media/scene_{sid}.jpg"
        ok = download(url, path, timeout=30)
        if ok:
            label = "meme" if meme else "image"
            print(f"  ✅ Scene {sid}: {label}  [{query}]")
        return ok
    except Exception as e:
        print(f"  ⚠️ Image fail scene {sid}: {e}")
        return False

# ── background music from Pixabay ─────────────────────────────────────────────

def get_bg_music():
    music_path = "assets/bg_music.mp3"
    if os.path.exists(music_path) and os.path.getsize(music_path) > 10000:
        print("  ⏩ BG music already exists")
        return

    mood = script.get("background_music_mood", "epic")
    mood_queries = {
        "epic":         "epic cinematic",
        "calm":         "calm ambient relaxing",
        "happy":        "happy upbeat",
        "mysterious":   "mysterious dark ambient",
        "dramatic":     "dramatic orchestral",
        "fun":          "fun cheerful",
        "sad":          "sad emotional piano",
        "motivational": "motivational inspiring"
    }
    query = mood_queries.get(mood, "cinematic background")

    got = False
    try:
        r = requests.get("https://pixabay.com/api/music/", params={
            "key": KEY, "q": query, "per_page": 5
        }, timeout=20)
        if r.status_code == 200:
            hits = r.json().get("hits", [])
            for hit in hits:
                audio_url = (
                    hit.get("audio", {}).get("url") or
                    hit.get("url") or
                    hit.get("previewURL")
                )
                if audio_url:
                    got = download(audio_url, music_path, timeout=90)
                    if got:
                        print(f"  ✅ BG music: {mood} mood")
                        break
    except Exception as e:
        print(f"  ⚠️ Music API: {e}")

    if not got:
        # Silent fallback — pipeline will not break
        subprocess.run([
            "ffmpeg", "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "1300", "-q:a", "9",
            "-acodec", "libmp3lame",
            "-y", music_path
        ], capture_output=True)
        print("  ⚠️ BG music unavailable — silent fallback used")

# ── run ───────────────────────────────────────────────────────────────────────

print("🎵 Downloading background music...")
get_bg_music()

print("\n🖼️  Downloading scene media...")
for scene in script["scenes"]:
    sid   = scene["id"]
    query = scene.get("pixabay_query", "nature cinematic")
    meme  = scene.get("is_meme", False)

    if os.path.exists(f"output/media/scene_{sid}.mp4"):
        print(f"  ⏩ Scene {sid}: already have video")
        continue
    if os.path.exists(f"output/media/scene_{sid}.jpg"):
        print(f"  ⏩ Scene {sid}: already have image")
        continue

    got = False
    if not meme:
        got = get_video(query, sid)
    if not got:
        get_image(query, sid, meme=meme)

    time.sleep(0.3)

print("\n✅ All media downloaded!")