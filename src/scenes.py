from github_ai import ask_ai

def generate_script(topic):

    prompt = f"""
Write a 20-minute documentary script.

Topic: {topic}

Rules:
- emotional hook
- suspense storytelling
- cinematic tone
- no mention of visuals
- 3000 words
"""

    return ask_ai(prompt)


def split_scenes(script):

    prompt = f"""
Split this into short cinematic scenes (5–8 sec):

{script}
"""

    result = ask_ai(prompt)

    return result.split("\n")