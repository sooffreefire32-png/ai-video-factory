from github_ai import ask_ai

def thumbnail_prompt(topic):

    prompt = f"""
Create YouTube thumbnail prompt:

Topic: {topic}

Rules:
- shocking expression
- mystery background
- cinematic lighting
- high contrast

Return image generation prompt only.
"""

    return ask_ai(prompt)