import os, json, subprocess, time
from google import genai
from google.genai import types

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
client     = genai.Client(api_key=GEMINI_KEY)

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

os.makedirs("output/audio", exist_ok=True)

def gemini_tts(text, out_mp3):
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"   # clear English voice
                        )
                    )
                )
            )
        )
        audio_data = resp.candidates[0].content.parts[0].inline_data.data
        wav = out_mp3.replace(".mp3", ".wav")
        with open(wav, "wb") as f:
            f.write(audio_data)
        subprocess.run([
            "ffmpeg", "-i", wav,
            "-q:a", "0", out_mp3,
            "-y", "-loglevel", "quiet"
        ])
        os.remove(wav)
        return True
    except Exception as e:
        print(f"    ⚠️ Gemini TTS fail: {e}")
        return False

def gtts_fallback(text, out_mp3):
    try:
        from gtts import gTTS
        gTTS(text=text, lang="en", slow=False).save(out_mp3)
        return True
    except Exception as e:
        print(f"    ❌ gTTS fail: {e}")
        return False

for scene in script["scenes"]:
    sid  = scene["id"]
    text = scene.get("narration", "").strip()
    out  = f"output/audio/scene_{sid}.mp3"

    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(f"  ⏩ Scene {sid} exists")
        continue

    if not text:
        print(f"  ⚠️  Scene {sid} empty")
        continue

    print(f"  🎙️ Scene {sid}...")
    ok = gemini_tts(text, out)
    if not ok:
        ok = gtts_fallback(text, out)

    if ok:
        size = os.path.getsize(out)
        print(f"  ✅ Scene {sid}  ({size//1024}KB)")
    else:
        print(f"  ❌ Scene {sid} FAILED")

    time.sleep(0.5)   # Gemini rate limit

print("\n✅ All voices done!")