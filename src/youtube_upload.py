import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video(file_path, title, description, tags, thumbnail_path, optimal_time_info=None):
    creds = Credentials.from_authorized_user_info(
        json.loads(open("token.json").read()),
        SCOPES
    )
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # Category for 'Howto & Style' or 'Science & Technology'
        },
        "status": {
            "privacyStatus": "public",
            "publishAt": None # This will be set if optimal_time_info is provided
        }
    }

    # Set scheduled publish time if optimal_time_info is available
    if optimal_time_info:
        # Format: YYYY-MM-DDTHH:MM:SS.000Z
        now = datetime.utcnow()
        publish_time = now.replace(hour=optimal_time_info["hour"], minute=0, second=0, microsecond=0)
        # If the optimal time has already passed today, schedule for tomorrow
        if publish_time < now:
            publish_time += timedelta(days=1)
        
        scheduled_time = publish_time.isoformat() + ".000Z"
        body["status"]["publishAt"] = scheduled_time
        print(f"Scheduling video for upload at: {scheduled_time}")

    # Upload video file
    media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media_body
    )
    response = request.execute()
    print("Uploaded Video ID:", response["id"])

    # Upload thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        thumbnail_media = MediaFileUpload(thumbnail_path, resumable=True)
        youtube.thumbnails().set(
            videoId=response["id"],
            media_body=thumbnail_media
        ).execute()
        print("Thumbnail uploaded successfully.")

if __name__ == "__main__":
    print("This script is intended to be called by main.py")
