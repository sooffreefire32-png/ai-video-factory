import os, json, re, requests, urllib.request, urllib.parse

GH_TOKEN         = os.environ["GH_TOKEN"]
YOUTUBE_DATA_KEY = os.environ["YOUTUBE_DATA_API_KEY"]
TOPIC            = os.environ.get("TOPIC", "Amazing Facts")

# ── Trending topics from YouTube ──────────────────────────────────────────────

def get_trending(topic):
    try:
        q   = urllib.parse.quote(topic)
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={q}&type=video&order=viewCount"
            f"&maxResults=10&relevanceLanguage=en"
            f"&regionCode=US"
            f"&key={YOUTUBE_DATA_KEY}"
        )
        r     = requests.get(url, timeout=15).json()
        items = r.get("items", [])
        titles = [i["snippet"]["title"] for i in items]
        print(f"✅ Trending: {len(titles)} titles found")
        return titles
    except Exception as e:
        print(f"⚠️ Trending failed: {e}")
        return []

trending     = get_trending(TOPIC)
trending_str = "\n".join(f"- {t}" for t in trending[:8]) or "No data"

# ── Retention insights ────────────────────────────────────────────────────────

retention = {"insights": "Strong hook first 30s, CTA at end."}
if os.path.exists("output/retention_insights.json"):
    retention = json.load(open("output/retention_insights.json"))

# ── GitHub Models — Script + SEO ──────────────────────────────────────────────

prompt = f"""You are a world-class YouTube scriptwriter and SEO expert.

TOPIC: {TOPIC}
LANGUAGE: English only
TARGET: 20 minutes (~1200 seconds total)

TRENDING TITLES FOR INSPIRATION:
{trending_str}

PREVIOUS VIDEO INSIGHTS: {retention.get('insights', '')}

Your goal: maximize views from HIGH RPM countries (USA, UK, Canada, Australia, Germany).
SEO strategy:
- Title must include power words that rank in English search
- Tags must include long-tail keywords searched in USA/UK
- Description must have timestamps and keywords naturally
- Hook must make English-speaking audience stop scrolling

Return ONLY raw valid JSON — no markdown, no backticks, no explanation.

{{
  "title": "Powerful English title max 60 chars with high-RPM keywords",
  "description": "Full SEO description 400 words with timestamps, keywords for US/UK audience",
  "tags": [
    "tag1 long tail",
    "tag2 specific niche",
    "tag3",
    "tag4",
    "tag5",
    "tag6",
    "tag7",
    "tag8",
    "tag9",
    "tag10"
  ],
  "thumbnail_prompt": "Eye-catching vivid YouTube thumbnail description bright colors bold",
  "background_music_mood": "epic",
  "scenes": [
    {{
      "id": 1,
      "type": "hook",
      "duration": 30,
      "narration": "Full English narration ~70 words that hooks US/UK viewers instantly",
      "pixabay_query": "cinematic space galaxy",
      "text_overlay": "YOU WON'T BELIEVE THIS",
      "use_character": true,
      "effect": "zoom_in",
      "is_meme": false
    }}
  ]
}}

STRICT RULES:
- Exactly 40 scenes
- Language: English ONLY
- Scenes 1-3: shocking hook for English audience
- Scenes 4-37: engaging main content, vary pace
- Scenes 38-39: summary
- Scene 40: subscribe CTA
- Every 5th scene: is_meme=true
- use_character: true for talking scenes, false for pure visual
- effect: zoom_in / zoom_out / slide_left / slide_right / none
- Each scene 25-35 seconds
- Total ~1200 seconds
- narration must be natural spoken English"""

data = json.dumps({
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 8000,
    "temperature": 0.85
}).encode()

req = urllib.request.Request(
    "https://models.inference.ai.azure.com/chat/completions",
    data=data,
    headers={
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {GH_TOKEN}"
    }
)

print("🤖 Generating script via GitHub Models (GPT-4o)...")
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())

text = result["choices"][0]["message"]["content"].strip()
text = re.sub(r'^```json\s*', '', text)
text = re.sub(r'^```\s*',     '', text)
text = re.sub(r'\s*```$',     '', text)
text = text.strip()

script = json.loads(text)

os.makedirs("output", exist_ok=True)
with open("output/script.json", "w", encoding="utf-8") as f:
    json.dump(script, f, indent=2, ensure_ascii=False)

total = sum(s.get("duration", 30) for s in script["scenes"])
print(f"✅ Title : {script['title']}")
print(f"✅ Scenes: {len(script['scenes'])}  |  Total: {total}s  ({total//60}min)")
print(f"✅ Tags  : {', '.join(script['tags'][:5])}")