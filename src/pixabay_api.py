import os
import requests

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def search_pixabay(query, type="photo", min_width=1920, min_height=1080, per_page=3):
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": type if type == "photo" else "all", # Pixabay uses image_type for photos, videos for videos
        "video_type": "all" if type == "video" else None,
        "min_width": min_width,
        "min_height": min_height,
        "per_page": per_page,
        "safesearch": True,
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data.get("hits", [])
    except requests.exceptions.RequestException as e:
        print(f"Error searching Pixabay: {e}")
        return []

def download_asset(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {url} to {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading asset from {url}: {e}")
        return False

# Example Usage (for testing)
if __name__ == "__main__":
    # Set a dummy API key for local testing
    os.environ["PIXABAY_API_KEY"] = "YOUR_PIXABAY_API_KEY"

    print("Searching for photos...")
    photos = search_pixabay("mystery forest", type="photo", per_page=1)
    if photos:
        print(f"Found {len(photos)} photos.")
        photo_url = photos[0]["largeImageURL"]
        download_asset(photo_url, "test_photo.jpg")
    else:
        print("No photos found.")

    print("\nSearching for videos...")
    videos = search_pixabay("dark alley", type="video", per_page=1)
    if videos:
        print(f"Found {len(videos)} videos.")
        # Pixabay video URLs are nested differently
        video_url = videos[0]["videos"]["large"]["url"]
        download_asset(video_url, "test_video.mp4")
    else:
        print("No videos found.")
