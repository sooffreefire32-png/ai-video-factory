import requests
import os

def generate_voice(text, path):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"

    payload = {
        "contents": [{
            "parts": [{"text": text}]
        }]
    }

    r = requests.post(url, json=payload)

    voice_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]

    with open(path.replace(".mp3", ".txt"), "w") as f:
        f.write(voice_text)