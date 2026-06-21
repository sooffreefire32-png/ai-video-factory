import os, json, requests, time

KEY = os.environ["PIXABAY_API_KEY"]

with open("output/script.json") as f:
    script = json.load(f)

os.makedirs("output/media", exist_ok=True)

def download(url, path, timeout=60):
    r = requests.get(url, timeout=timeout, stream=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

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
        download(url, path)
        print(f"  ✅ Scene {sid}: video ({query})")
        return True
    except Exception as e:
        print(f"  ⚠️ Video fail scene {sid}: {e}")
        return False

def get_image(query, sid, meme=False):
    try:
        image_type = "illustration" if meme else "photo"
        r = requests.get("https://pixabay.com/api/", params={
            "key": KEY, "q": query, "per_page": 5,
            "image_type": image_type, "min_width": 1280,
            "safesearch": "true"
        }, timeout=20).json()

        hits = r.get("hits", [])
        if not hits:
            # retry as photo
            r = requests.get("https://pixabay.com/api/", params={
                "key": KEY, "q": query, "per_page": 3,
                "image_type": "photo", "safesearch": "true"
            }, timeout=20).json()
            hits = r.get("hits", [])

        if not hits:
            return False

        url = hits[0].get("largeImageURL") or hits[0].get("webformatURL")
        if not url:
            return False

        path = f"output/media/scene_{sid}.jpg"
        download(url, path, timeout=30)
        label = "meme-style" if meme else "image"
        print(f"  ✅ Scene {sid}: {label} ({query})")
        return True
    except Exception as e:
        print(f"  ⚠️ Image fail scene {sid}: {e}")
        return False

for scene in script["scenes"]:
    sid   = scene["id"]
    query = scene.get("pixabay_query", "nature landscape")
    meme  = scene.get("is_meme", False)

    # Already downloaded?
    if os.path.exists(f"output/media/scene_{sid}.mp4"):
        continue
    if os.path.exists(f"output/media/scene_{sid}.jpg"):
        continue

    # Try video first (skip for meme scenes)
    got = False
    if not meme:
        got = get_video(query, sid)

    if not got:
        get_image(query, sid, meme=meme)

    time.sleep(0.4)  # Pixabay rate limit

print("✅ Media download complete!")