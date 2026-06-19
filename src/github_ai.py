import requests
import os

def ask_ai(prompt):

    url = "https://models.github.ai/inference"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_MODEL_TOKEN')}"
    }

    data = {
        "model": "gpt-4.1",
        "messages": [{"role": "user", "content": prompt}]
    }

    r = requests.post(url, json=data, headers=headers)

    return r.json()["choices"][0]["message"]["content"]