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
- ~3000 words
"""
    return ask_ai(prompt)

def split_scenes(script):
    prompt = f"""
Split this script into short cinematic scenes (5–8 sec each). 
Provide each scene description on a new line. 
Do not include any other text or numbers.

Script:
{script}
"""
    result = ask_ai(prompt)
    # Clean up the result to get a list of scenes
    scenes = [s.strip() for s in result.split("\n") if s.strip()]
    # Filter out common AI prefix/suffix lines if they exist
    scenes = [s for s in scenes if not s.lower().startswith("here are") and not s.lower().startswith("scene")]
    return scenes
