import os
import requests
from pixabay_api import search_pixabay, download_asset

# Fallback to Gemini for image generation if Pixabay fails or no suitable asset is found
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_image_with_gemini(prompt, output_path):
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
        print("Gemini image generation failed")
        print(response.text)
        return False
    data = response.json()
    image_b64 = data["predictions"][0]["bytesBase64Encoded"]
    import base64
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_b64))
    print(f"Generated image with Gemini: {output_path}")
    return True

def get_visual_asset(prompt, output_path, asset_type="photo"):
    print(f"Searching Pixabay for {asset_type}: {prompt}")
    hits = search_pixabay(prompt, type=asset_type, per_page=1)

    if hits:
        asset_url = None
        if asset_type == "photo":
            asset_url = hits[0]["largeImageURL"]
        elif asset_type == "video":
            # Pixabay video URLs are nested differently
            asset_url = hits[0]["videos"]["large"]["url"]

        if asset_url and download_asset(asset_url, output_path):
            return True
    
    print(f"No suitable {asset_type} found on Pixabay or download failed. Falling back to Gemini image generation.")
    # Fallback to Gemini for image generation if Pixabay fails or no video is found
    if asset_type == "photo":
        return generate_image_with_gemini(prompt, output_path)
    else:
        print("Cannot generate video with Gemini. Skipping asset.")
        return False
