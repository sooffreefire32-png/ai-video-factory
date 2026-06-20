import os
import json
import requests
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings

# Set the path to the ImageMagick binary (required by MoviePy for some text effects)
# change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"}) # Assuming ImageMagick is installed

# --- Configuration ---
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CHARACTER_VIDEO_PATH = "assets/character.mp4"
OUTPUT_DIR = "output"

# --- Gemini TTS API Interaction ---
# This is a placeholder. Actual Gemini TTS API might require specific client libraries or different endpoint.
# For now, we'll simulate a TTS call.
def generate_tts_audio(text: str, voice_id: str = "en-US-Neural2-D") -> str:
    # In a real scenario, this would call Gemini TTS API
    # For demonstration, we'll create a dummy audio file
    audio_filename = f"temp_audio_{hash(text)}.mp3"
    # Simulate audio generation (e.g., using gTTS or a placeholder)
    # from gtts import gTTS
    # tts = gTTS(text=text, lang='en', slow=False)
    # tts.save(audio_filename)
    # For now, just create an empty file
    with open(audio_filename, "w") as f: # Dummy file
        f.write("dummy audio content")
    return audio_filename

# --- Pixabay API Interaction ---
def search_pixabay(query: str, media_type: str = "video", min_width: int = 1280, min_height: int = 720) -> list:
    if not PIXABAY_API_KEY: return []
    url = f"https://pixabay.com/api/{media_type}/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "lang": "en",
        "image_type": "photo" if media_type == "image" else None,
        "video_type": "film" if media_type == "video" else None,
        "min_width": min_width,
        "min_height": min_height,
        "per_page": 10
    }
    try:
        response = requests.get(url, params={k: v for k, v in params.items() if v is not None})
        response.raise_for_status()
        hits = response.json().get("hits", [])
        if media_type == "video":
            return [hit["videos"]["large"]["url"] for hit in hits if "videos" in hit and "large" in hit["videos"]]
        elif media_type == "image":
            return [hit["largeImageURL"] for hit in hits]
    except Exception as e:
        print(f"Error searching Pixabay for {query}: {e}")
    return []

def download_media(url: str, filename: str) -> str:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filename
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

# --- Video Editing Logic ---
def create_video(timeline_map: list, script: str, output_filename: str = "final_video.mp4"):
    final_clips = []
    current_time = 0
    audio_clips = []

    # Load main character video once
    main_character_clip = None
    if os.path.exists(CHARACTER_VIDEO_PATH):
        main_character_clip = VideoFileClip(CHARACTER_VIDEO_PATH)

    for event in timeline_map:
        start = event.get("time_start", current_time)
        end = event.get("time_end", start + 5) # Default 5 seconds if not specified
        duration = end - start

        clip = None
        audio_narration = None

        if event["type"] == "narration":
            # Generate TTS audio for narration
            tts_file = generate_tts_audio(event["content"], event.get("tts_voice_id"))
            if os.path.exists(tts_file):
                audio_narration = AudioFileClip(tts_file)
                duration = audio_narration.duration # Sync clip duration to narration
                # Create a blank video clip for narration, or use a static image
                clip = ColorClip(size=(1920, 1080), color=(0,0,0), duration=duration)
                clip = clip.set_audio(audio_narration)
                audio_clips.append(audio_narration.set_start(start))

        elif event["type"] == "main_character_video":
            if main_character_clip:
                # Loop or trim the main character video
                if duration > main_character_clip.duration:
                    clip = concatenate_videoclips([main_character_clip] * int(duration / main_character_clip.duration + 1)).subclip(0, duration)
                else:
                    clip = main_character_clip.subclip(0, duration)
                
                # Apply placement (simple for now, can be more complex)
                if event.get("character_placement") == "full_screen":
                    clip = clip.resize(newsize=(1920, 1080))
                elif event.get("character_placement") == "top_left":
                    clip = clip.resize(width=640).set_position(("left", "top"))
                # Add more complex positioning as needed

        elif event["type"] == "stock_video":
            search_term = event["content"]
            video_urls = search_pixabay(search_term, media_type="video")
            if video_urls:
                downloaded_video = download_media(video_urls[0], f"temp_video_{hash(search_term)}.mp4")
                if downloaded_video:
                    clip = VideoFileClip(downloaded_video).subclip(0, duration).resize(newsize=(1920, 1080))

        elif event["type"] == "stock_image":
            search_term = event["content"]
            image_urls = search_pixabay(search_term, media_type="image")
            if image_urls:
                downloaded_image = download_media(image_urls[0], f"temp_image_{hash(search_term)}.jpg")
                if downloaded_image:
                    clip = ImageClip(downloaded_image, duration=duration).resize(newsize=(1920, 1080))

        elif event["type"] == "text_overlay":
            # This will be overlaid on top of existing clips, handled later
            pass

        elif event["type"] == "background_music":
            # This will be added as a separate audio track, handled later
            pass

        elif event["type"] == "meme":
            # Search for meme images/videos and integrate
            search_term = event["content"] + " meme"
            image_urls = search_pixabay(search_term, media_type="image")
            if image_urls:
                downloaded_meme = download_media(image_urls[0], f"temp_meme_{hash(search_term)}.jpg")
                if downloaded_meme:
                    meme_clip = ImageClip(downloaded_meme, duration=duration).resize(width=500).set_position(("center", "center"))
                    # This meme clip needs to be composited onto another clip
                    # For simplicity, we'll just add it as a standalone for now if no other clip exists
                    if clip is None: clip = ColorClip(size=(1920, 1080), color=(0,0,0), duration=duration).set_opacity(0)
                    clip = CompositeVideoClip([clip, meme_clip.set_start(0)])

        if clip:
            final_clips.append(clip.set_start(start))
            current_time = end

    if not final_clips:
        print("No clips generated for the video.")
        return

    # Concatenate all video clips
    final_video = CompositeVideoClip(final_clips, size=(1920, 1080))

    # Add background music (simple overlay for now)
    bg_music_events = [e for e in timeline_map if e["type"] == "background_music"]
    if bg_music_events:
        # For simplicity, just take the first background music suggestion and loop it
        # In a real scenario, you'd search for royalty-free music and mix it properly
        # For now, let's assume a generic background music file exists or is generated
        bg_music_file = "assets/background_music.mp3" # Placeholder
        if os.path.exists(bg_music_file):
            bg_music = AudioFileClip(bg_music_file).volumex(0.3) # Lower volume
            bg_music = bg_music.audio_loop(duration=final_video.duration)
            final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, bg_music]))

    # Add text overlays
    text_overlay_clips = []
    for event in timeline_map:
        if event["type"] == "text_overlay":
            text_clip = TextClip(event["content"], fontsize=70, color=\
white", stroke_color="black", stroke_width=2, duration=event["time_end"] - event["time_start"])
            text_clip = text_clip.set_start(event["time_start"]).set_position(("center", "bottom"))
            text_overlay_clips.append(text_clip)

    if text_overlay_clips:
        final_video = CompositeVideoClip([final_video] + text_overlay_clips)

    # Write the final video file
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    final_video.write_videofile(os.path.join(OUTPUT_DIR, output_filename), fps=24, codec="libx264")

# --- Main execution for testing ---
if __name__ == "__main__":
    # Example timeline map (this would come from ai_director.py)
    sample_timeline = [
        {"time_start": 0, "time_end": 10, "type": "narration", "content": "Welcome to the future of AI content creation!"},
        {"time_start": 10, "time_end": 20, "type": "main_character_video", "character_placement": "full_screen"},
        {"time_start": 20, "time_end": 30, "type": "stock_video", "content": "robots working"},
        {"time_start": 30, "time_end": 40, "type": "stock_image", "content": "futuristic city"},
        {"time_start": 40, "time_end": 50, "type": "text_overlay", "content": "AI is changing everything!"},
        {"time_start": 0, "time_end": 50, "type": "background_music", "content": "upbeat tech music"},
        {"time_start": 50, "time_end": 60, "type": "meme", "content": "mind blown"}
    ]
    sample_script = "This is a sample script for testing purposes."

    print("Starting video creation...")
    create_video(sample_timeline, sample_script, output_filename="test_video.mp4")
    print("Video creation finished.")
