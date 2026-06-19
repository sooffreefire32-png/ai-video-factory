import random

def create_timeline(scenes):

    timeline = []

    for i, s in enumerate(scenes):

        timeline.append({
            "type": "image",
            "content": s,
            "duration": 5
        })

        if i == 0 or i % 4 == 0:
            timeline.append({
                "type": "character",
                "content": "assets/character.mp4",
                "duration": 5
            })

    return timeline