import requests
import os

def generate_image(prompt, path):

    url = "https://api.flow.ai/v1/images/generate"

    headers = {
        "Authorization": f"Bearer {os.getenv('FLOW_API_KEY')}"
    }

    data = {
        "prompt": f"""
Cinematic documentary evidence style.
CCTV / investigation / crime scene look.
NO fantasy or space.

Scene: {prompt}
""",
        "width": 1024,
        "height": 576
    }

    r = requests.post(url, json=data, headers=headers)

    img_url = r.json()["image_url"]

    img = requests.get(img_url).content

    with open(path, "wb") as f:
        f.write(img)