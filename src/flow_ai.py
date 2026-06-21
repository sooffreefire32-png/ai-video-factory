import os
import requests
import base64
import re
from pixabay_api import search_pixabay, download_asset

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def clean_query(text):
    # Remove special characters and limit to 5-7 words for Pixabay
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    return " ".join(words[:6])

def generate_image_with_gemini(prompt, output_path):
    # Use Gemini 1.5 Flash to generate an image description if needed, 
    # but for actual image generation, we need the correct Imagen endpoint.
    # Since direct Imagen API access is often restricted, we'll try the most common one.
    
    print(f"Attempting image generation for: {prompt}")
    
    # Correct endpoint for Imagen 3 on Vertex AI / Generative AI
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={GEMINI_API_KEY}"
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            image_b64 = data["predictions"][0]["bytesBase64Encoded"]
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_b64))
            return True
        else:
            print(f"Imagen failed ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"Error in image generation: {e}")
        return False

def get_visual_asset(prompt, output_path, asset_type="photo"):
    search_query = clean_query(prompt)
    print(f"Searching Pixabay for {asset_type}: {search_query}")
    hits = search_pixabay(search_query, type=asset_type, per_page=1)

    if hits:
        asset_url = None
        if asset_type == "photo":
            asset_url = hits[0].get("largeImageURL")
        elif asset_type == "video":
            videos = hits[0].get("videos", {})
            # Try to get the best quality video
            video_data = videos.get("large") or videos.get("medium") or videos.get("small")
            asset_url = video_data.get("url") if video_data else None

        if asset_url and download_asset(asset_url, output_path):
            return True
    
    print(f"No suitable {asset_type} found on Pixabay. Falling back to Gemini image generation.")
    return generate_image_with_gemini(prompt, output_path)
