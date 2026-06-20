import os
import json
import requests

# --- Configuration ---
GH_TOKEN = os.getenv("GH_TOKEN")

# --- GitHub Models API Interaction ---
def generate_content_with_github_models(prompt: str, max_tokens: int = 4000) -> str:
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "model": "gpt-4o", # Using gpt-4o as specified in the initial request
        "messages": [
            {"role": "system", "content": "You are an AI video director and scriptwriter. Your goal is to create engaging, high-retention YouTube video scripts (20 minutes long) and detailed editing timeline maps. Focus on topics that appeal to USA/UK audiences for high RPM. Ensure the script is in English. Incorporate elements that maximize viewer retention. Provide a structured JSON output with the script and a timeline map."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    response = requests.post("https://api.github.com/copilot_internal/v2/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# --- Script Generation and Timeline Mapping Logic ---
def generate_video_plan(video_topic: str, previous_video_data: dict = None) -> dict:
    # Placeholder for previous video analysis (views, retention)
    # In a real scenario, this would involve fetching data from YouTube Analytics
    # and feeding it into the prompt for the AI to learn from.
    analysis_feedback = ""
    if previous_video_data:
        analysis_feedback = f"\n\nPrevious video performance data: {json.dumps(previous_video_data)}\nAnalyze this data and suggest improvements for viewer retention and engagement in the new script."

    prompt = f"""Create a detailed 20-minute YouTube video script and an editing timeline map for a video about: '{video_topic}'.

**Script Requirements:**
-   Target Audience: USA/UK (English language only).
-   Length: Approximately 20 minutes of spoken content.
-   Engagement: Maximize viewer retention, use hooks, clear explanations, and a strong call to action.
-   Tone: Engaging, informative, and professional.

**Timeline Map Requirements:**
-   Provide a JSON array of events, each with:
    -   `time_start`: (float) Start time in seconds.
    -   `time_end`: (float) End time in seconds.
    -   `type`: (string) e.g., "narration", "main_character_video", "stock_video", "stock_image", "text_overlay", "background_music", "meme".
    -   `content`: (string) Specific text for narration, description of stock footage/image, text for overlay, music name, meme description.
    -   `character_placement`: (string, optional) e.g., "top_left", "center", "full_screen" for main_character_video.
    -   `tts_voice_id`: (string, optional) ID of the TTS voice to use for narration.

**Important Note for AI:**
-   Ensure the main character video (from `assets/character.mp4`) is used strategically. If it needs to be longer than 5 seconds, indicate its placement and duration, and the editor will loop/trim it.
-   Integrate background music throughout the video.
-   Suggest relevant memes or visual gags.
-   The output MUST be a single JSON object with two keys: `script` (string) and `timeline_map` (array of objects).""" + analysis_feedback

    # Call GitHub Models to generate the script and timeline
    raw_response = generate_content_with_github_models(prompt)

    # Attempt to parse the JSON response
    try:
        # Sometimes the model wraps JSON in markdown code blocks
        if raw_response.startswith("```json") and raw_response.endswith("```"):
            raw_response = raw_response[7:-3].strip()
        plan = json.loads(raw_response)
        return plan
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from AI: {e}")
        print(f"Raw AI response: {raw_response}")
        # Fallback if JSON parsing fails
        return {"script": raw_response, "timeline_map": []}

# --- Main execution for testing ---
if __name__ == "__main__":
    # Example usage (replace with actual topic and previous data)
    topic = "The Future of AI in Content Creation"
    # previous_data = {"video_id": "abc", "views": 10000, "retention_rate": "60%"}
    previous_data = None # For initial test

    if not GH_TOKEN:
        print("Error: GH_TOKEN environment variable not set.")
        print("Please set GH_TOKEN with your GitHub Personal Access Token (or GitHub Models Token).")
    else:
        print(f"Generating video plan for: {topic}")
        video_plan = generate_video_plan(topic, previous_data)
        print("\n--- Generated Script ---")
        print(video_plan.get("script", "No script generated."))
        print("\n--- Timeline Map ---")
        print(json.dumps(video_plan.get("timeline_map", []), indent=2))
