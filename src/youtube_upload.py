import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video():
    creds = Credentials.from_authorized_user_info(
        json.loads(open("token.json").read()),
        SCOPES
    )

    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "AI Generated Mystery Video",
                "description": "Auto uploaded AI video",
                "tags": ["AI", "mystery", "automation"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body="output/video.mp4"
    )

    response = request.execute()
    print("Uploaded Video ID:", response["id"])

if __name__ == "__main__":
    upload_video()