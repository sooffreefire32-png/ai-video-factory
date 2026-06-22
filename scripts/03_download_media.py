import os, json, requests, subprocess, time

KEY = os.environ["PIXABAY_API_KEY"]

with open("output/script.json") as f:
    script = json.load(f)

os.makedirs("output/media", exist_ok=True)
os.makedirs("assets",       exist_ok=True)

def download(url, path, timeout=90):
    try:
        r = requests.get(url, timeout=timeout, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=16384):
                f.write(chunk)
        return os.path.getsize(path) > 5000
    except Exception as e:
        print(f"    ❌ {e}")
        return False

def get_video(query, out):
    try:
        r = requests.get("https://pixabay.com/api/videos/", params={
            "key": KEY, "q": query, "per_page": 5, "video_type": "film"
        }, timeout=15).json()
        hits = r.get("hits", [])
        if not hits:
            return False
        videos = hits[0].get("videos", {})
        for q in ["medium", "small", "large", "tiny"]:
            if q in videos and videos[q].get("url"):
                return download(videos[q]["url"], out, timeout=60)
        return False
    except:
        return False

def get_image(query, out, illus=False):
    try:
        for img_type in (["illustration"] if illus else ["photo", "illustration"]):
            r = requests.get("https://pixabay.com/api/", params={
                "key": KEY, "q": query, "per_page": 5,
                "image_type": img_type, "min_width": 1280,
                "safesearch": "true"
            }, timeout=15).json()
            hits = r.get("hits", [])
            if hits:
                url = hits[0].get("largeImageURL") or hits[0].get("webformatURL")
                if url:
                    return download(url, out, timeout=30)
        return False
    except:
        return False

def get_bg_music():
    path = "assets/bg_music.mp3"
    if os.path.exists(path) and os.path.getsize(path) > 50000:
        print("  ⏩ BG music exists")
        return
    mood = script.get("background_music_mood", "epic")
    mood_map = {
        "epic": "epic cinematic",
        "calm": "calm ambient",
        "happy": "happy upbeat",
        "mysterious": "mysterious dark ambient",
        "dramatic": "dramatic orchestral",
        "motivational": "motivational inspiring"
    }
    query = mood_map.get(mood, "cinematic background")
    got   = False
    try:
        r = requests.get("https://pixabay.com/api/music/", params={
            "key": KEY, "q": query, "per_page": 5
        }, timeout=20)
        if r.status_code == 200:
            for hit in r.json().get("hits", []):
                url = hit.get("audio", {}).get("url") or hit.get("url")
                if url:
                    got = download(url, path, timeout=120)
                    if got:
                        print(f"  ✅ BG music: {mood}")
                        break
    except Exception as e:
        print(f"  ⚠️ Music API: {e}")

    if not got:
        subprocess.run([
            "ffmpeg", "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "1300", "-q:a", "9",
            "-acodec", "libmp3lame", "-y", path
        ], capture_output=True)
        print("  ⚠️ Silent fallback music")

print("🎵 Background music...")
get_bg_music()

print("\n🖼️  Scene media (6 clips per scene)...")
for scene in script["scenes"]:
    sid     = scene["id"]
    queries = scene.get("media_queries", [])

    # Fallback if old format
    if not queries:
        queries = [scene.get("pixabay_query", "cinematic nature")] * 6

    # Ensure 6 queries by cycling
    while len(queries) < 6:
        queries.append(queries[0])

    is_meme  = scene.get("is_meme", False)
    got_count = 0

    for clip_idx, query in enumerate(queries[:6]):
        vp = f"output/media/scene_{sid}_clip_{clip_idx}.mp4"
        ip = f"output/media/scene_{sid}_clip_{clip_idx}.jpg"

        if os.path.exists(vp) or os.path.exists(ip):
            got_count += 1
            continue

        got = False
        if not is_meme:
            got = get_video(query, vp)
        if not got:
            got = get_image(query, ip, illus=is_meme)
        if not got:
            get_image("cinematic nature landscape", ip)

        if got:
            got_count += 1
        time.sleep(0.25)

    print(f"  ✅ Scene {sid}: {got_count}/6 clips")

print("\n✅ All media downloaded!")