import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_youtube_service():
    creds = Credentials.from_authorized_user_info(
        json.loads(open("token.json").read()),
        SCOPES
    )
    return build("youtube", "v3", credentials=creds)

def get_channel_id(youtube):
    response = youtube.channels().list(
        part="snippet",
        mine=True
    ).execute()
    return response["items"][0]["id"]

def get_audience_activity(youtube, channel_id):
    # This is a placeholder. Real YouTube Analytics API requires a different service and scope.
    # For simplicity, we'll return a dummy optimal time.
    # In a real scenario, you'd use the YouTube Analytics API to get viewer activity by hour/day.
    # Example: https://developers.google.com/youtube/analytics/v1/reference/reports/query
    print("Fetching audience activity (placeholder for now)...")
    # For demonstration, let's assume 6 PM UTC is a good time.
    return {"hour": 18, "timezone": "UTC"}

if __name__ == "__main__":
    # This part would be run during OAuth setup to get the token.json
    # For now, assume token.json exists with necessary scopes.
    try:
        youtube = get_youtube_service()
        channel_id = get_channel_id(youtube)
        activity = get_audience_activity(youtube, channel_id)
        print(f"Optimal upload time: {activity['hour']}:00 {activity['timezone']}")
    except Exception as e:
        print(f"Error getting YouTube Analytics: {e}")
        print("Please ensure you have authenticated with the correct scopes and token.json is available.")
