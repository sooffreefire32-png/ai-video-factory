import os

from topic import get_topic
from scenes import generate_script, split_scenes
from director import create_timeline
from flow_ai import generate_image
from tts import generate_voice
from music import pick_music
from editor import render_video

topic = get_topic()

script = generate_script(topic)

scenes = split_scenes(script)

timeline = create_timeline(scenes)

os.makedirs("output/images", exist_ok=True)

images = []
i = 0

for item in timeline:
    if item["type"] == "image":
        path = f"output/images/{i}.png"
        generate_image(item["content"], path)
        images.append(path)
        i += 1

generate_voice(script, "output/voice.mp3")

music = pick_music(script)

render_video(images, "output/voice.mp3", music)

print("DONE")