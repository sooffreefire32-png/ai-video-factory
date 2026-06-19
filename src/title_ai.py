from github_ai import ask_ai

def generate_title(topic):

    prompt = f"""
Create viral YouTube title:

Topic: {topic}

Rules:
- emotional hook
- curiosity gap
- no boring words
- USA audience style

Return 3 titles only.
"""

    return ask_ai(prompt)