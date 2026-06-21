import os, json, subprocess

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

with open("output/script.json") as f:
    script = json.load(f)

os.makedirs("output/audio", exist_ok=True)

def gemini_tts(text, out_mp3):
    """Gemini 2.0 Flash TTS"""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(
            model="gemini-2.0-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                )
            )
        )
        audio_bytes = resp.candidates[0].content.parts[0].inline_data.data
        wav = out_mp3.replace(".mp3", ".wav")
        with open(wav, "wb") as f:
            f.write(audio_bytes)
        subprocess.run([
            "ffmpeg", "-i", wav, "-q:a", "0",
            out_mp3, "-y", "-loglevel", "quiet"
        ])
        os.remove(wav)
        return True
    except Exception as e:
        print(f"  ⚠️ Gemini TTS fail: {e}")
        return False

def gtts_fallback(text, out_mp3, lang="en"):
    """gTTS fallback — always free"""
    try:
        from gtts import gTTS
        gTTS(text=text, lang=lang, slow=False).save(out_mp3)
        return True
    except Exception as e:
        print(f"  ❌ gTTS also failed: {e}")
        return False

lang = "en" if script.get("language", "en") == "en" else "ur"

for scene in script["scenes"]:
    sid  = scene["id"]
    text = scene.get("narration", "")
    out  = f"output/audio/scene_{sid}.mp3"

    if os.path.exists(out):
        print(f"  ⏩ Skip scene {sid} (exists)")
        continue

    if not text.strip():
        print(f"  ⚠️ Scene {sid} empty narration")
        continue

    ok = gemini_tts(text, out)
    if not ok:
        ok = gtts_fallback(text, out, lang)

    if ok:
        print(f"  ✅ Voice scene {sid}")
    else:
        print(f"  ❌ Voice failed scene {sid}")

print("✅ All voices done!")