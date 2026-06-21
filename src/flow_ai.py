import os
import requests
import base64
from pixabay_api import search_pixabay, download_asset

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_image_with_gemini(prompt, output_path):
    # Correct endpoint for Gemini Image Generation (Imagen)
    # Note: Imagen access might be restricted. Using a more common endpoint.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Since direct Imagen API might be tricky, we'll try to use the most stable one
    # If the user has a specific Imagen API setup, this might need adjustment
    # For now, let's use a placeholder or a stable version
    
    # Placeholder for actual image generation if Imagen is not available
    print(f"Attempting image generation for: {prompt}")
    
    # Using the Imagen 3 model name as per common docs, but with error handling
    url_imagen = f"https://generativelanguage.googleapis.com/v1beta/projects/unused/locations/unused/publishers/google/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    
    try:
        response = requests.post(url_imagen, json=payload)
        if response.status_code == 200:
            data = response.json()
            image_b64 = data["predictions"][0]["bytesBase64Encoded"]
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_b64))
            return True
        else:
            print(f"Imagen failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error in image generation: {e}")
        return False

def get_visual_asset(prompt, output_path, asset_type="photo"):
    search_query = " ".join(prompt.split()[:5])
    print(f"Searching Pixabay for {asset_type}: {search_query}")
    hits = search_pixabay(search_query, type=asset_type, per_page=1)

    if hits:
        asset_url = None
        if asset_type == "photo":
            asset_url = hits[0].get("largeImageURL")
        elif asset_type == "video":
            videos = hits[0].get("videos", {})
            large_video = videos.get("large", {})
            asset_url = large_video.get("url")

        if asset_url and download_asset(asset_url, output_path):
            return True
    
    print(f"No suitable {asset_type} found on Pixabay. Falling back to Gemini image generation.")
    return generate_image_with_gemini(prompt, output_path)
