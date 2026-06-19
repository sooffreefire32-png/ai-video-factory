import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_image(prompt, output_path):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"

    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1
        }
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print("Image generation failed")
        print(response.text)
        return

    data = response.json()

    image_b64 = data["predictions"][0]["bytesBase64Encoded"]

    import base64

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_b64))

    print(f"Saved: {output_path}")