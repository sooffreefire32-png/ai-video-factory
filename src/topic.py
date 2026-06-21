import json
import random
import os
import requests

def get_topic(selected_topic=None):
    if selected_topic and selected_topic.strip():
        return selected_topic

    # List of high RPM mystery topics for USA/UK audience
    high_rpm_topics = [
        "The mysterious disappearance of Flight MH370",
        "The secret history of Area 51 and reverse engineering",
        "Unsolved mysteries of the Bermuda Triangle",
        "The hidden truth behind the Great Pyramids",
        "The Voynich Manuscript: An unbreakable code",
        "The mystery of the Dyatlov Pass incident",
        "Lost civilizations: The search for Atlantis",
        "The dark secrets of the Vatican archives",
        "The mystery of the Roanoke colony disappearance",
        "The unsolved identity of Jack the Ripper"
    ]

    # Try to get a viral topic from AI
    try:
        from github_ai import ask_ai
        prompt = "Suggest one highly viral and intriguing mystery topic for a 20-minute YouTube documentary aimed at a USA audience. Provide only the topic name."
        topic = ask_ai(prompt)
        if topic and "AI_ERROR" not in topic and len(topic) < 100:
            return topic.strip().strip('"')
    except Exception as e:
        print(f"Error generating topic: {e}")

    return random.choice(high_rpm_topics)
