import os
import json
import sys
from topic import get_topic
from scenes import generate_script, split_scenes
from director import create_timeline
from flow_ai import get_visual_asset
from tts import generate_voice
from music import pick_music
from editor import render_video
from youtube_upload import upload_video
from youtube_analytics import get_audience_activity, get_youtube_service
from thumb_ai import generate_thumbnail
from title_ai import generate_title_description_tags

# --- Configuration ---
VIDEO_MIN_DURATION_SECONDS = 20 * 60  # 20 minutes
CHARACTER_VIDEO_PATH = "assets/character.mp4"
CHARACTER_VIDEO_DURATION = 5 # seconds

# --- Main Workflow ---
def run_workflow(selected_topic=None):
    # 1. Get Topic (High RPM targeted for USA/UK)
    topic = get_topic(selected_topic)
    print(f"Generating video for topic: {topic}")

    # 2. Generate Script (ensure it's long enough for 20 mins)
    # Target ~3000-3500 words for 20 minutes at ~150-170 wpm
    full_script = ""
    target_word_count = 3500
    print(f"Generating script for target word count: {target_word_count}")
    
    # Generate script in parts to maintain quality and length
    parts = ["introduction", "main mystery part 1", "main mystery part 2", "deep dive/secrets exposed", "conclusion and call to action"]
    for part in parts:
        prompt = f"Write the {part} of a documentary script about {topic}. Focus on suspense and mystery for a USA audience. This is part of a 20-minute video."
        script_chunk = generate_script(prompt)
        full_script += script_chunk + "\n\n"
    
    current_word_count = len(full_script.split())
    print(f"Final script length: {current_word_count} words.")

    # 3. Split Script into Scenes
    scenes = split_scenes(full_script)

    # 4. Create Timeline with Images and Character Video
    timeline = create_timeline(scenes, CHARACTER_VIDEO_PATH, CHARACTER_VIDEO_DURATION)

    # 5. Generate Visual Assets (Pixabay + Gemini fallback)
    os.makedirs("output/images", exist_ok=True)
    visual_assets_paths = []
    asset_count = 0
    for item in timeline:
        if item["type"] == "scene_image":
            path = f"output/images/{asset_count}.png"
            # Try to get a video first for professional feel, then photo
            if not get_visual_asset(item["content"], path, asset_type="video"):
                get_visual_asset(item["content"], path, asset_type="photo")
            visual_assets_paths.append(path)
            asset_count += 1

    # 6. Generate Voiceover
    voiceover_path = "output/voice.mp3"
    generate_voice(full_script, voiceover_path, lang='en')

    # 7. Pick Background Music
    music_path = pick_music(full_script)

    # 8. Render Video
    final_video_path = "output/video.mp4"
    render_video(visual_assets_paths, voiceover_path, music_path, timeline, final_video_path, CHARACTER_VIDEO_PATH)

    # 9. Generate Title, Description, Tags (Using Gemini)
    title, description, tags = generate_title_description_tags(topic, full_script)

    # 10. Generate Thumbnail
    thumbnail_path = "output/thumbnail.png"
    generate_thumbnail(topic, CHARACTER_VIDEO_PATH, thumbnail_path)

    # 11. Get Optimal Upload Time
    try:
        youtube_service = get_youtube_service()
        optimal_time_info = get_audience_activity(youtube_service, "")
    except:
        optimal_time_info = {"hour": 18, "timezone": "UTC"} # Fallback

    # 12. Upload Video to YouTube
    upload_video(final_video_path, title, description, tags, thumbnail_path, optimal_time_info)

    print("DONE: Video created and uploaded successfully!")

if __name__ == "__main__":
    # Allow topic selection from command line arguments (passed from GitHub Action)
    selected_topic = sys.argv[1] if len(sys.argv) > 1 else None
    run_workflow(selected_topic)
