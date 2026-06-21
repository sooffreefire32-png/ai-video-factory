import os
import requests
import random

def pick_music(script, output_dir="output/music"):
    os.makedirs(output_dir, exist_ok=True)
    dummy_music_path = os.path.join(output_dir, "background_music.mp3")
    
    # In a real scenario, you'd download from Pixabay or another source.
    # For now, we'll create a silent file if it doesn't exist.
    if not os.path.exists(dummy_music_path):
        try:
            from pydub import AudioSegment
            silent_audio = AudioSegment.silent(duration=60 * 1000) # 1 minute
            silent_audio.export(dummy_music_path, format="mp3")
            print(f"Created a dummy silent music file at {dummy_music_path}")
        except Exception as e:
            print(f"Failed to create silent music: {e}")
            # If pydub fails, we'll just return None and handle it in the editor
            return None

    return dummy_music_path
