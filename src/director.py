import random

def create_timeline(scenes, character_video_path, character_video_duration):
    timeline = []
    current_time = 0

    for i, scene_content in enumerate(scenes):
        # Estimate scene duration (e.g., 5-8 seconds per scene as per user prompt)
        # This is a rough estimate and will be refined during actual video rendering
        scene_duration = random.randint(5, 8)

        timeline.append({
            "type": "scene_image",
            "content": scene_content, # This will be used to generate an image
            "duration": scene_duration,
            "start_time": current_time
        })
        current_time += scene_duration

        # Add character video periodically or strategically
        # User wants character video to be shown more if needed
        # For now, let's add it every few scenes or at key moments
        if i % 3 == 0 and i != 0: # Add character video every 3 scenes, but not at the very beginning
            timeline.append({
                "type": "character_video",
                "path": character_video_path,
                "duration": character_video_duration,
                "start_time": current_time
            })
            current_time += character_video_duration

        # Placeholder for potential effects or transitions between scenes
        # This can be further developed to include specific effect types
        # timeline.append({"type": "transition", "duration": 1, "start_time": current_time})
        # current_time += 1

    return timeline
