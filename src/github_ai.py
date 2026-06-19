import os
import requests

def ask_ai(prompt):

    # GH API style (GitHub token based inference)
    url = "https://api.github.com/marketplace/models"

    headers = {
        "Authorization": f"Bearer {os.getenv('GH_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    # NOTE: real GH inference endpoint depends on your enabled model access
    res = requests.post(url, json=payload, headers=headers)

    try:
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "AI_ERROR"