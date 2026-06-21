import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_title_description_tags(topic, script):
    prompt = f"""
    Based on the following video topic and script, generate a compelling YouTube video title, a detailed description, and relevant tags. The target audience is USA/UK and other high-RPM countries, so use English and focus on intriguing, mystery-exposing content. The channel is \'svifi mystery\'.

    Topic: {topic}

    Script:
    {script}

    Provide the output in JSON format with the following keys: \'title\', \'description\', \'tags\' (a list of strings).
    Ensure the title is catchy, the description is informative and includes keywords, and tags are highly relevant.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {\"Content-Type\": \"application/json\"}
    payload = {
        \"contents\": [{
            \"parts\": [{\"text\": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_text = response.json()[\"candidates\"][0][\"content\"][\"parts\"][0][\"text\"]
        # Attempt to parse JSON, sometimes Gemini might return extra text
        try:
            data = json.loads(response_text)
            return data[\"title\"], data[\"description\"], data[\"tags\"]
        except json.JSONDecodeError:
            print(f\"Failed to decode JSON from Gemini: {response_text}\")
            # Fallback to a simpler parsing or default values
            title_start = response_text.find(\"title\": \") + len(\"title\": \")
            title_end = response_text.find("\n", title_start)
            title = response_text[title_start:title_end].strip().strip("\\\"\\\',\")
            description = \"A mysterious video from svifi mystery channel.\"
            tags = [\"mystery\", \"svifi mystery\", topic.lower().replace(" ", "-")]
            return title, description, tags

    except requests.exceptions.RequestException as e:
        print(f\"Error generating title, description, tags with Gemini: {e}\")
        return f\"Mystery Video: {topic}\", \"A mysterious video from svifi mystery channel.\", [\"mystery\", \"svifi mystery\", topic.lower().replace(" ", "-")]
