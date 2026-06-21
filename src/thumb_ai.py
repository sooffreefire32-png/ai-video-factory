import os
import requests
import base64

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_thumbnail(topic, character_video_path, output_path):
    # For now, we\'ll generate a simple image-based thumbnail using Gemini
    # A more advanced approach would involve overlaying the character video onto a generated background
    prompt = f\"Create a captivating YouTube thumbnail for a mystery video about \\\"{topic}\\\". The thumbnail should be dark, mysterious, and include elements related to the topic. Also, incorporate a stylized representation of a mysterious character, similar to the one in {character_video_path}. The character should be central and intriguing. Aspect ratio 16:9.\"

    url = f\"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}\"
    payload = {
        \"instances\": [
            {
                \"prompt\": prompt
            }
        ],
        \"parameters\": {
            \"sampleCount\": 1
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(\"Gemini thumbnail generation failed\")
        print(response.text)
        return False
    data = response.json()
    image_b64 = data[\"predictions\"][0][\"bytesBase64Encoded\"]
    with open(output_path, \"wb\") as f:
        f.write(base64.b64decode(image_b64))
    print(f\"Generated thumbnail with Gemini: {output_path}\")
    return True
