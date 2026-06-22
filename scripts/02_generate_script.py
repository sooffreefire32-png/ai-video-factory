import os, json, re, requests, urllib.request, urllib.parse

GH_TOKEN         = os.environ["GH_TOKEN"]
YOUTUBE_DATA_KEY = os.environ["YOUTUBE_DATA_API_KEY"]
TOPIC            = os.environ.get("TOPIC", "Amazing Facts")

def gh_call(prompt, max_tokens=8000):
    data = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.85
    }).encode()
    req = urllib.request.Request(
        "https://models.inference.ai.azure.com/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GH_TOKEN}"
        }
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())
    text = result["choices"][0]["message"]["content"].strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def get_trending(topic):
    try:
        q   = urllib.parse.quote(topic)
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={q}&type=video&order=viewCount"
            f"&maxResults=10&relevanceLanguage=en&regionCode=US"
            f"&key={YOUTUBE_DATA_KEY}"
        )
        r = requests.get(url, timeout=15).json()
        return [i["snippet"]["title"] for i in r.get("items", [])]
    except Exception as e:
        print(f"⚠️ Trending: {e}")
        return []

trending     = get_trending(TOPIC)
trending_str = "\n".join(f"- {t}" for t in trending[:8]) or "No data"

retention = {"insights": "Strong hook first 30s, pattern interrupt every 2 min, CTA at end."}
if os.path.exists("output/retention_insights.json"):
    retention = json.load(open("output/retention_insights.json"))

SCENE_TEMPLATE = """{{
  "id": {id},
  "narration": "Minimum 70 words of natural spoken English narration for this scene...",
  "media_queries": ["specific query 1", "specific query 2", "specific query 3", "specific query 4", "specific query 5", "specific query 6"],
  "text_overlay": "SHORT OVERLAY",
  "use_character": true,
  "effect": "zoom_in",
  "is_meme": false
}}"""

# ── Batch 1: metadata + scenes 1-20 ──────────────────────────────────────────

print("🤖 Batch 1: metadata + scenes 1-20...")

prompt1 = f"""YouTube scriptwriter and SEO expert.

TOPIC: {TOPIC}
LANGUAGE: English ONLY
TRENDING: {trending_str}
INSIGHTS: {retention.get('insights', '')}
TARGET: High RPM countries — USA, UK, Canada, Australia, Germany

Return ONLY raw JSON (no markdown):
{{
  "title": "Power English title 60 chars with high-search US/UK keywords",
  "description": "400 word SEO description with timestamps and keywords for US/UK",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10"],
  "thumbnail_prompt": "Dramatic vivid YouTube thumbnail, bright colors, cinematic, no text",
  "background_music_mood": "epic",
  "scenes": [
    /* scenes 1 through 20 */
    {{
      "id": 1,
      "narration": "MINIMUM 70 WORDS of natural spoken English. Full sentences. Engaging and conversational. This is what the voice will say for 30 seconds.",
      "media_queries": ["cinematic query 1", "query 2", "query 3", "query 4", "query 5", "query 6"],
      "text_overlay": "SHOCKING HOOK",
      "use_character": true,
      "effect": "zoom_in",
      "is_meme": false
    }}
  ]
}}

STRICT RULES for 20 scenes:
- Scenes 1-3: shocking hook that stops scrolling
- Scenes 4-20: main content with facts and stories  
- Each narration: MINIMUM 70 words, natural spoken English
- media_queries: 6 SPECIFIC Pixabay search queries for that scene
- effect: zoom_in/zoom_out/slide_left/slide_right/none (vary them)
- use_character: true for talking scenes, false for pure visual
- is_meme: true ONLY for scenes 5, 10, 15, 20
- text_overlay: 3-5 impactful words"""

text1   = gh_call(prompt1, max_tokens=8000)
part1   = json.loads(text1)
scenes1 = part1["scenes"]
print(f"✅ Batch 1: {len(scenes1)} scenes")

# ── Batch 2: scenes 21-40 ─────────────────────────────────────────────────────

print("🤖 Batch 2: scenes 21-40...")

prompt2 = f"""Continue YouTube video script about: {TOPIC}
Video title: {part1['title']}
Scenes 1-20 are done. Generate scenes 21 through 40.

Return ONLY raw JSON array (no object wrapper, just the array):
[
  {{
    "id": 21,
    "narration": "MINIMUM 70 words natural spoken English for this scene...",
    "media_queries": ["query1","query2","query3","query4","query5","query6"],
    "text_overlay": "OVERLAY",
    "use_character": true,
    "effect": "zoom_out",
    "is_meme": false
  }}
]

RULES:
- Scenes 21-37: detailed content, facts, stories, explanations
- Scenes 38-39: summary and recap of key points
- Scene 40: strong subscribe CTA
- is_meme: true ONLY for scenes 25, 30, 35
- Each narration: MINIMUM 70 words, natural spoken English
- media_queries: 6 specific Pixabay search terms
- Vary effects: zoom_in/zoom_out/slide_left/slide_right/none"""

text2   = gh_call(prompt2, max_tokens=7000)
scenes2 = json.loads(text2)
print(f"✅ Batch 2: {len(scenes2)} scenes")

# ── Merge + fix IDs ───────────────────────────────────────────────────────────

all_scenes = scenes1 + scenes2
for i, s in enumerate(all_scenes):
    s["id"] = i + 1

script = {
    "title":                  part1["title"],
    "description":            part1["description"],
    "tags":                   part1["tags"],
    "thumbnail_prompt":       part1["thumbnail_prompt"],
    "background_music_mood":  part1.get("background_music_mood", "epic"),
    "scenes":                 all_scenes
}

os.makedirs("output", exist_ok=True)
with open("output/script.json", "w", encoding="utf-8") as f:
    json.dump(script, f, indent=2, ensure_ascii=False)

avg_words = sum(len(s.get("narration","").split()) for s in all_scenes) // max(len(all_scenes), 1)
est_dur   = len(all_scenes) * 30

print(f"\n✅ Title      : {script['title']}")
print(f"✅ Scenes     : {len(all_scenes)}")
print(f"✅ Est. dur   : ~{est_dur//60} min")
print(f"✅ Avg words  : {avg_words} per scene")
print(f"✅ Tags       : {', '.join(script['tags'][:5])}")