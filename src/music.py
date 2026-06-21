import os
import requests
from pixabay_api import search_pixabay, download_asset

def pick_music(script, output_dir="output/music"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Use keywords from the script to search for relevant music
    keywords = []
    if "mystery" in script.lower():
        keywords.append("mystery")
    if "suspense" in script.lower():
        keywords.append("suspense")
    if "dark" in script.lower():
        keywords.append("dark")
    if "cinematic" in script.lower():
        keywords.append("cinematic")
    
    search_query = " ".join(keywords) if keywords else "cinematic mystery"

    print(f"Searching Pixabay for music: {search_query}")
    # Pixabay API for music is not directly available through the main API endpoint for images/videos.
    # We need to simulate a search or use a different approach for music.
    # For now, let's assume we have a way to get a music URL or a local asset.
    # A more robust solution would involve scraping Pixabay music or using a dedicated music API.

    # Placeholder: For now, we will return a dummy music path. 
    # In a real implementation, you would download a suitable track.
    # For demonstration, let's assume a default music file exists or is downloaded.
    dummy_music_path = os.path.join(output_dir, "background_music.mp3")
    # You would replace this with actual download logic from a source like Pixabay or a similar free music site.
    # For example, if Pixabay had a direct music API:
    # music_hits = search_pixabay(search_query, type="music", per_page=1)
    # if music_hits:
    #     music_url = music_hits[0]["url"]
    #     download_asset(music_url, dummy_music_path)
    # else:
    #     print("No music found on Pixabay. Using a default.")

    # For now, let's create a dummy file if it doesn't exist for testing purposes
    if not os.path.exists(dummy_music_path):
        # Create a silent MP3 file for testing if no actual music is downloaded
        from pydub import AudioSegment
        silent_audio = AudioSegment.silent(duration=60 * 1000) # 1 minute of silence
        silent_audio.export(dummy_music_path, format="mp3")
        print(f"Created a dummy silent music file at {dummy_music_path}")

    return dummy_music_path
