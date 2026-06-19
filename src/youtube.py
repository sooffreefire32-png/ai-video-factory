from googleapiclient.discovery import build

def upload(video):

    youtube = build("youtube", "v3", developerKey="YOUTUBE_API")

    youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "AI Mystery Documentary",
                "description": "Auto generated video",
                "tags": ["mystery", "ai", "documentary"]
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=video
    ).execute()