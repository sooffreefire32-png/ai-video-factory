import json, random

TOPICS = [
    "A man disappeared from a moving train",
    "A town erased from maps overnight",
    "A phone call from future",
    "CIA secret experiment gone wrong",
    "Airport where planes vanish"
]

def get_topic():

    try:
        used = json.load(open("used.json"))
    except:
        used = []

    available = [t for t in TOPICS if t not in used]

    if not available:
        used = []
        available = TOPICS

    topic = random.choice(available)

    used.append(topic)
    json.dump(used, open("used.json", "w"))

    return topic