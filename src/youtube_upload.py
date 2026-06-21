import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_credentials():
    if os.path.exists("token.json"):
        return Credentials.from_authorized_user_info(
            json.loads(open("token.json").read()),
            SCOPES
        )
    else:
        # Use refresh token from environment variables
        return Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=SCOPES
        )

def upload_video(file_path, title, description, tags, thumbnail_path, optimal_time_info=None):
    try:
        creds = get_credentials()
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "publishAt": None
            }
        }

        if optimal_time_info:
            now = datetime.utcnow()
            publish_time = now.replace(hour=optimal_time_info["hour"], minute=0, second=0, microsecond=0)
            if publish_time < now:
                publish_time += timedelta(days=1)
            
            scheduled_time = publish_time.isoformat() + ".000Z"
            body["status"]["publishAt"] = scheduled_time
            print(f"Scheduling video for upload at: {scheduled_time}")

        media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media_body
        )
        response = request.execute()
        print("Uploaded Video ID:", response["id"])

        if thumbnail_path and os.path.exists(thumbnail_path):
            thumbnail_media = MediaFileUpload(thumbnail_path, resumable=True)
            youtube.thumbnails().set(
                videoId=response["id"],
                media_body=thumbnail_media
            ).execute()
            print("Thumbnail uploaded successfully.")
    except Exception as e:
        print(f"Error in YouTube upload: {e}")

if __name__ == "__main__":
    print("This script is intended to be called by main.py")
