import os, json, re, requests, urllib.request, urllib.parse

GH_TOKEN         = os.environ["GH_TOKEN"]
YOUTUBE_DATA_KEY = os.environ["YOUTUBE_DATA_API_KEY"]
TOPIC            = os.environ.get("TOPIC", "Amazing Facts")

def get_trending(topic):
    try:
        q   = urllib.parse.quote(topic)
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={q}&type=video&order=viewCount"
            f"&maxResults=10&relevanceLanguage=en"
            f"&regionCode=US&key={YOUTUBE_DATA_KEY}"
        )
        r      = requests.get(url, timeout=15).json()
        titles = [i["snippet"]["title"] for i in r.get("items", [])]
        print(f"✅ Trending: {len(titles)} titles")
        return titles
    except Exception as e:
        print(f"⚠️ Trending failed: {e}")
        return []

trending     = get_trending(TOPIC)
trending_str = "\n".join(f"- {t}" for t in trending[:8]) or "No data"

retention = {"insights": "Strong hook first 30s, CTA at end."}
if os.path.exists("output/retention_insights.json"):
    retention = json.load(open("output/retention_insights.json"))

prompt = f"""You are a world-class YouTube scriptwriter and SEO expert.

TOPIC: {TOPIC}
LANGUAGE: English ONLY
TARGET DURATION: exactly 20 minutes = 1200 seconds total

TRENDING TITLES:
{trending_str}

PREVIOUS VIDEO INSIGHTS: {retention.get('insights', '')}

SEO TARGET: High RPM countries — USA, UK, Canada, Australia, Germany.

CRITICAL NARRATION RULE:
- Each scene duration is 30 seconds
- At normal speaking pace (130 words per minute), 30 seconds = 65 words
- So each narration MUST be AT LEAST 60-70 words
- Write full detailed sentences, not bullet points
- The narrator speaks slowly and clearly for English learners too

Return ONLY raw valid JSON — no markdown, no backticks.

{{
  "title": "Power title max 60 chars with high-search keywords",
  "description": "Full SEO description 400 words with timestamps and US/UK keywords",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10"],
  "thumbnail_prompt": "Ultra vivid eye-catching YouTube thumbnail bright colors bold text space",
  "background_music_mood": "epic",
  "scenes": [
    {{
      "id": 1,
      "type": "hook",
      "duration": 30,
      "narration": "Write AT LEAST 65 words of full spoken English narration here. This is what the voice will say out loud. Make it engaging, natural, conversational. Do not use bullet points. Write complete flowing sentences that take exactly 30 seconds to speak at a normal pace.",
      "pixabay_query": "cinematic space galaxy stars",
      "text_overlay": "YOU WON'T BELIEVE THIS",
      "use_character": true,
      "effect": "zoom_in",
      "is_meme": false
    }}
  ]
}}

RULES:
- Exactly 40 scenes — each 30 seconds = total 1200 seconds = 20 minutes
- Each narration: minimum 60 words, maximum 80 words
- Scenes 1-3: shocking hook that stops scrolling
- Scenes 4-37: detailed engaging content, facts, stories, explanations
- Scenes 38-39: recap and summary
- Scene 40: strong subscribe CTA
- Every 5th scene (5,10,15,20,25,30,35): is_meme=true
- use_character true for talking scenes, false for pure visual scenes
- effect: zoom_in / zoom_out / slide_left / slide_right / none
- narration: natural spoken English only, no symbols, no hashtags"""

data = json.dumps({
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 12000,
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

print("🤖 Generating 20-min script via GitHub Models...")
with urllib.request.urlopen(req, timeout=180) as resp:
    result = json.loads(resp.read())

text = result["choices"][0]["message"]["content"].strip()
text = re.sub(r'^```json\s*', '', text)
text = re.sub(r'^```\s*',     '', text)
text = re.sub(r'\s*```$',     '', text)
text = text.strip()

script = json.loads(text)

# Validate word count per scene
short_scenes = []
for scene in script["scenes"]:
    words = len(scene.get("narration", "").split())
    if words < 50:
        short_scenes.append(f"Scene {scene['id']}: {words} words")

if short_scenes:
    print(f"⚠️ Short narrations: {short_scenes[:5]}")

os.makedirs("output", exist_ok=True)
with open("output/script.json", "w", encoding="utf-8") as f:
    json.dump(script, f, indent=2, ensure_ascii=False)

total = sum(s.get("duration", 30) for s in script["scenes"])
avg_words = sum(len(s.get("narration","").split()) for s in script["scenes"]) // len(script["scenes"])
print(f"✅ Title     : {script['title']}")
print(f"✅ Scenes    : {len(script['scenes'])}")
print(f"✅ Total dur : {total}s = {total//60} min")
print(f"✅ Avg words : {avg_words} per scene")