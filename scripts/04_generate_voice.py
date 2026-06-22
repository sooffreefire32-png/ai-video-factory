import os, json, asyncio, time

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

os.makedirs("output/audio", exist_ok=True)

# Best free English voice — Microsoft Edge TTS
VOICE = "en-US-AndrewMultilingualNeural"

async def edge_tts_gen(text, out):
    try:
        import edge_tts
        comm = edge_tts.Communicate(text, VOICE)
        await comm.save(out)
        return os.path.exists(out) and os.path.getsize(out) > 5000
    except Exception as e:
        print(f"    ⚠️ edge-tts: {e}")
        return False

def gtts_fallback(text, out):
    try:
        from gtts import gTTS
        gTTS(text=text, lang="en", slow=False).save(out)
        return os.path.exists(out) and os.path.getsize(out) > 1000
    except Exception as e:
        print(f"    ❌ gTTS: {e}")
        return False

for scene in script["scenes"]:
    sid  = scene["id"]
    text = scene.get("narration", "").strip()
    out  = f"output/audio/scene_{sid}.mp3"

    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(f"  ⏩ Scene {sid}")
        continue

    if not text:
        print(f"  ⚠️  Scene {sid} empty")
        continue

    words = len(text.split())
    print(f"  🎙️ Scene {sid} ({words} words)...")

    ok = asyncio.run(edge_tts_gen(text, out))
    if not ok:
        ok = gtts_fallback(text, out)

    if ok:
        size = os.path.getsize(out) // 1024
        print(f"  ✅ Scene {sid}  ({size}KB)")
    else:
        print(f"  ❌ Scene {sid} FAILED")

    time.sleep(0.15)

print("\n✅ All voices done!")