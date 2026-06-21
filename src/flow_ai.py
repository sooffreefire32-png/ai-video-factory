import os
import requests
import base64
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
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print("Gemini image generation failed")
            print(response.text)
            return False
        data = response.json()
        image_b64 = data["predictions"][0]["bytesBase64Encoded"]
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_b64))
        print(f"Generated image with Gemini: {output_path}")
        return True
    except Exception as e:
        print(f"Error in Gemini image generation: {e}")
        return False

def get_visual_asset(prompt, output_path, asset_type="photo"):
    # Limit prompt length for Pixabay search
    search_query = " ".join(prompt.split()[:5])
    print(f"Searching Pixabay for {asset_type}: {search_query}")
    hits = search_pixabay(search_query, type=asset_type, per_page=1)

    if hits:
        asset_url = None
        if asset_type == "photo":
            asset_url = hits[0].get("largeImageURL")
        elif asset_type == "video":
            # Pixabay video URLs are nested differently
            videos = hits[0].get("videos", {})
            large_video = videos.get("large", {})
            asset_url = large_video.get("url")

        if asset_url and download_asset(asset_url, output_path):
            return True
    
    print(f"No suitable {asset_type} found on Pixabay. Falling back to Gemini image generation.")
    # Fallback to Gemini for image generation
    return generate_image_with_gemini(prompt, output_path)
