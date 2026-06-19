from github_ai import ask_ai

def score_topic(topic):

    prompt = f"""
Score this YouTube idea 1-10:

- curiosity
- emotional hook
- viral potential in USA audience
- mystery factor

Topic: {topic}

Return only JSON:
{
 "score": 0-40,
 "reason": ""
}
"""

    result = ask_ai(prompt)
    return result