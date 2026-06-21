import os
import requests
import json

def ask_ai(prompt, model_endpoint="https://api.github.com/marketplace/models"):
    """
    Sends a prompt to a GitHub-hosted AI model (as per user's GH_TOKEN context).
    This function is generalized to handle various AI tasks including script generation,
    editing decisions, and potentially analytics interpretation.
    """
    headers = {
        "Authorization": f"Bearer {os.getenv(\'GH_TOKEN\')}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # NOTE: The actual GitHub inference endpoint and payload might vary
        # based on the specific AI model the user has access to via their GH_TOKEN.
        # This is a placeholder based on the initial `github_ai.py`.
        res = requests.post(model_endpoint, json=payload, headers=headers)
        res.raise_for_status() # Raise an exception for HTTP errors
        
        # Assuming the response structure for content generation
        response_data = res.json()
        if "choices" in response_data and response_data["choices"]:
            return response_data["choices"][0]["message"]["content"]
        elif "generated_text" in response_data: # Some models might return directly
            return response_data["generated_text"]
        else:
            print(f"Unexpected AI response format: {response_data}")
            return "AI_ERROR: Unexpected response format"

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with GitHub AI model: {e}")
        return "AI_ERROR: Request failed"
    except Exception as e:
        print(f"An unexpected error occurred in ask_ai: {e}")
        return "AI_ERROR: General error"

def analyze_video_performance(video_id, metrics=None):
    """
    Placeholder for analyzing YouTube video performance using a GitHub-hosted AI model.
    This would involve passing video analytics data to the AI for insights.
    """
    if metrics is None:
        metrics = ["views", "watch_time_minutes", "average_view_duration", "subscribers_gained"]
    
    prompt = f"Analyze the YouTube video with ID {video_id} based on metrics: {', '.join(metrics)}. Provide insights on what worked well and suggestions for improvement for future videos, focusing on increasing retention and views for a USA/UK audience."
    print(f"Sending analytics prompt to AI: {prompt}")
    # This assumes the ask_ai function can handle analytical prompts and return structured advice.
    return ask_ai(prompt, model_endpoint="https://api.github.com/some/analytics/model") # Hypothetical analytics endpoint

def get_editing_suggestions(script_content, visual_assets, character_video_info):
    """
    Placeholder for getting advanced video editing suggestions from a GitHub-hosted AI model.
    This would involve passing script, available assets, and character video info to the AI.
    """
    prompt = f"""
    Given the following video script and available visual assets, provide detailed editing instructions to create a professional, animated-vibe mystery video targeting a USA/UK audience. 
    The video should be at least 20 minutes long. 
    
    Script: {script_content}
    Visual Assets (descriptions/paths): {visual_assets}
    Main Character Video: {character_video_info} (use this for dynamic placement and animation vibe)
    
    Focus on:
    - Seamless transitions and effects (not simple cuts)
    - Dynamic placement of the main character video to enhance storytelling (copy/trim as needed)
    - Background music and sound effects selection (AI should choose)
    - Integration of memes or viral elements if appropriate for the mystery niche
    - Ensuring a full animation feel, not just static images.
    
    Return editing instructions in a structured format (e.g., JSON or detailed steps).
    """
    print("Sending editing suggestions prompt to AI...")
    return ask_ai(prompt, model_endpoint="https://api.github.com/some/editing/model") # Hypothetical editing endpoint
