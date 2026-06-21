import os
import json
from topic import get_topic
from scenes import generate_script, split_scenes
from director import create_timeline
from flow_ai import generate_image
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
def run_workflow():
    # 1. Get Topic (and allow user selection in workflow_dispatch)
    topic = get_topic() # This will be enhanced to allow selection
    print(f"Generating video for topic: {topic}")

    # 2. Generate Script (ensure it's long enough for 20 mins)
    # We'll generate script in chunks if needed to reach target duration
    full_script = ""
    current_duration = 0
    while current_duration < VIDEO_MIN_DURATION_SECONDS:
        script_chunk = generate_script(topic) # This needs to be smarter about generating more content
        full_script += script_chunk + "\n\n"
        # Estimate duration based on words per minute and TTS speed
        # Assuming ~150 words per minute, and 20 min video needs ~3000 words
        current_duration = (len(full_script.split()) / 150) * 60
        print(f"Current script length: {len(full_script.split())} words, estimated duration: {current_duration/60:.2f} minutes")

    # 3. Split Script into Scenes
    scenes = split_scenes(full_script)

    # 4. Create Timeline with Images and Character Video
    timeline = create_timeline(scenes, CHARACTER_VIDEO_PATH, CHARACTER_VIDEO_DURATION)

    # 5. Generate Images for Scenes
    os.makedirs("output/images", exist_ok=True)
    generated_images = []
    image_count = 0
    for item in timeline:
        if item["type"] == "image":
            path = f"output/images/{image_count}.png"
            generate_image(item["content"], path)
            generated_images.append(path)
            image_count += 1

    # 6. Generate Voiceover
    voiceover_path = "output/voice.mp3"
    generate_voice(full_script, voiceover_path, lang='en') # Ensure English language

    # 7. Pick Background Music
    music_path = pick_music(full_script) # This needs to be implemented to pick actual music

    # 8. Render Video
    final_video_path = "output/video.mp4"
    render_video(generated_images, voiceover_path, music_path, timeline, final_video_path, CHARACTER_VIDEO_PATH)

    # 9. Generate Title, Description, Tags
    title, description, tags = generate_title_description_tags(topic, full_script)

    # 10. Generate Thumbnail
    thumbnail_path = "output/thumbnail.png"
    generate_thumbnail(topic, CHARACTER_VIDEO_PATH, thumbnail_path) # Needs to use character video

    # 11. Get Optimal Upload Time
    youtube_service = get_youtube_service()
    # channel_id = get_channel_id(youtube_service) # Uncomment if needed for real analytics
    optimal_time_info = get_audience_activity(youtube_service, "") # Placeholder channel_id
    print(f"Optimal upload time: {optimal_time_info['hour']}:00 {optimal_time_info['timezone']}")

    # 12. Upload Video to YouTube
    upload_video(final_video_path, title, description, tags, thumbnail_path, optimal_time_info)

    print("DONE: Video created and uploaded successfully!")

if __name__ == "__main__":
    run_workflow()
