import os
import requests
import json

def ask_ai(prompt):
    # Correct GitHub Models API endpoint
    url = "https://models.inference.ai.azure.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('GH_TOKEN')}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": "gpt-4o", # Default model for GitHub Models
        "temperature": 0.7,
        "max_tokens": 4096
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error communicating with GitHub AI model: {e}")
        # Fallback to Gemini if GH fails
        return ask_gemini(prompt)

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini fallback failed: {e}")
        return "AI_ERROR"
