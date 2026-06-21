import os
import requests
import json

def ask_ai(prompt):
    # GitHub Models endpoint (GPT-4o)
    url = "https://models.inference.ai.azure.com/chat/completions"
    
    # Truncate prompt if it's too large for GH Models
    if len(prompt) > 8000:
        prompt = prompt[:8000] + "..."

    headers = {
        "Authorization": f"Bearer {os.getenv('GH_TOKEN')}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 4096
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            print(f"GH Models failed with {res.status_code}: {res.text}")
            return ask_gemini(prompt)
    except Exception as e:
        print(f"Error communicating with GitHub AI model: {e}")
        return ask_gemini(prompt)

def ask_gemini(prompt):
    # Stable Gemini endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"Gemini API failed with {res.status_code}: {res.text}")
            return "AI_ERROR"
    except Exception as e:
        print(f"Gemini fallback failed: {e}")
        return "AI_ERROR"
