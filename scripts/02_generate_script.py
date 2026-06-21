import os, json, re
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
TOPIC    = os.environ.get("TOPIC", "Amazing Facts")
LANGUAGE = os.environ.get("LANGUAGE", "en")

retention = {"insights": "Create engaging content with strong hooks."}
if os.path.exists("output/retention_insights.json"):
    retention = json.load(open("output/retention_insights.json"))

prompt = f"""You are a top YouTube video scriptwriter.

TOPIC: {TOPIC}
LANGUAGE: {LANGUAGE}
TARGET DURATION: 20 minutes (1200 seconds total)
PREVIOUS VIDEO INSIGHTS: {retention.get('insights','')}

Create a complete, engaging YouTube video script.
Return ONLY raw valid JSON — no markdown, no backticks, no explanation.

{{
  "title": "Catchy YouTube title max 60 chars",
  "description": "Full YouTube description with timestamps 400 words",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10"],
  "thumbnail_prompt": "Vivid detailed image prompt for YouTube thumbnail eye-catching bright colors",
  "background_music_mood": "epic",
  "scenes": [
    {{
      "id": 1,
      "type": "hook",
      "duration": 30,
      "narration": "Full narration text spoken by presenter (~70 words for 30s)",
      "pixabay_query": "space galaxy stars",
      "text_overlay": "SHOCKING SPACE FACTS",
      "use_character": true,
      "effect": "zoom_in",
      "is_meme": false
    }}
  ]
}}

RULES:
- Exactly 40 scenes
- Scenes 1-3: strong hook, shocking fact or question
- Scenes 4-37: main content, vary pace
- Scenes 38-39: summary
- Scene 40: CTA/subscribe
- Every 5th scene set is_meme=true (uses meme-style visuals)
- use_character: true for talking scenes, false for pure visual scenes
- effect options: zoom_in, zoom_out, fade, slide_left, slide_right, none
- Each duration between 25-35 seconds
- Total durations must sum to ~1200"""

response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=prompt
)

text = response.text.strip()
# Strip markdown fences if present
text = re.sub(r'^```json\s*', '', text)
text = re.sub(r'^```\s*', '', text)
text = re.sub(r'\s*```$', '', text)
text = text.strip()

script = json.loads(text)

os.makedirs("output", exist_ok=True)
with open("output/script.json", "w") as f:
    json.dump(script, f, indent=2, ensure_ascii=False)

total_dur = sum(s.get("duration", 30) for s in script["scenes"])
print(f"✅ Script: {script['title']}")
print(f"✅ Scenes: {len(script['scenes'])} | Total: {total_dur}s")