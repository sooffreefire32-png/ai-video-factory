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

def run_workflow(selected_topic=None):
    # 1. Get Topic
    topic = get_topic(selected_topic)
    if not topic or "AI_ERROR" in topic:
        topic = "Mysteries of the Unknown"
    print(f"Generating video for topic: {topic}")

    # 2. Generate Script
    full_script = ""
    parts = ["introduction", "main mystery part 1", "main mystery part 2", "deep dive/secrets exposed", "conclusion and call to action"]
    for part in parts:
        prompt = f"Write the {part} of a documentary script about {topic}. Focus on suspense and mystery for a USA audience. This is part of a 20-minute video."
        script_chunk = generate_script(prompt)
        if "AI_ERROR" not in script_chunk:
            full_script += script_chunk + "\n\n"
    
    if len(full_script.split()) < 100:
        full_script = f"Welcome to our deep dive into {topic}. This is a mysterious journey that will reveal secrets you never knew existed..."
    
    print(f"Final script length: {len(full_script.split())} words.")

    # 3. Split Script into Scenes
    scenes = split_scenes(full_script)
    if not scenes:
        scenes = [f"A mysterious view of {topic}", "Secrets being revealed", "The truth unfolds"]

    # 4. Create Timeline
    timeline = create_timeline(scenes, CHARACTER_VIDEO_PATH, CHARACTER_VIDEO_DURATION)

    # 5. Generate Visual Assets
    os.makedirs("output/images", exist_ok=True)
    visual_assets_paths = []
    asset_count = 0
    for item in timeline:
        if item["type"] == "scene_image":
            path = f"output/images/{asset_count}.png"
            # Try video, then photo
            if not get_visual_asset(item["content"], path, asset_type="video"):
                get_visual_asset(item["content"], path, asset_type="photo")
            
            if os.path.exists(path):
                visual_assets_paths.append(path)
                asset_count += 1
            else:
                print(f"Failed to get asset for: {item['content']}")

    # 6. Generate Voiceover
    voiceover_path = "output/voice.mp3"
    generate_voice(full_script, voiceover_path, lang='en')

    # 7. Pick Background Music
    music_path = pick_music(full_script)

    # 8. Render Video
    final_video_path = "output/video.mp4"
    if visual_assets_paths:
        render_video(visual_assets_paths, voiceover_path, music_path, timeline, final_video_path, CHARACTER_VIDEO_PATH)
    else:
        print("No visual assets found, cannot render video.")
        return

    # 9. Metadata
    title, description, tags = generate_title_description_tags(topic, full_script)

    # 10. Thumbnail
    thumbnail_path = "output/thumbnail.png"
    generate_thumbnail(topic, CHARACTER_VIDEO_PATH, thumbnail_path)

    # 11. Optimal Upload Time
    optimal_time_info = {"hour": 18, "timezone": "UTC"}

    # 12. Upload
    if os.path.exists(final_video_path):
        upload_video(final_video_path, title, description, tags, thumbnail_path, optimal_time_info)
    else:
        print("Final video file not found.")

    print("DONE: Video created and uploaded successfully!")

if __name__ == "__main__":
    selected_topic = sys.argv[1] if len(sys.argv) > 1 else None
    run_workflow(selected_topic)
