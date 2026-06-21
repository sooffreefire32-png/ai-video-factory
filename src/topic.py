import json
import random
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TOPICS = [
    "A man disappeared from a moving train",
    "A town erased from maps overnight",
    "A phone call from future",
    "CIA secret experiment gone wrong",
    "Airport where planes vanish"
]

def get_viral_topic_from_gemini(channel_niche="mystery and exposing secrets", language="English", target_audience="USA, UK, high-RPM countries"):
    prompt = f"""
    Generate a highly viral and engaging YouTube video topic for a channel focused on {channel_niche}. 
    The topic should be in {language} and appeal to a {target_audience} audience. 
    It should be a mystery or a secret being exposed. 
    Provide only the topic title, without any additional text or formatting.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error generating viral topic with Gemini: {e}")
        return random.choice(TOPICS) # Fallback to predefined topics

def get_topic(selected_topic=None):
    if selected_topic:
        return selected_topic
    
    # Placeholder for analyzing previous video performance
    # In a real scenario, you would call youtube_analytics.py functions here
    # and use the insights to inform topic generation.
    print("Analyzing previous video performance for topic generation (placeholder)...")

    # Try to get a viral topic from Gemini
    viral_topic = get_viral_topic_from_gemini()
    if viral_topic:
        return viral_topic
    
    # Fallback to predefined topics if Gemini fails
    try:
        with open("used.json", "r") as f:
            used = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        used = []
    
    available = [t for t in TOPICS if t not in used]
    if not available:
        used = []
        available = TOPICS
    
    topic = random.choice(available)
    used.append(topic)
    
    with open("used.json", "w") as f:
        json.dump(used, f)
    
    return topic
