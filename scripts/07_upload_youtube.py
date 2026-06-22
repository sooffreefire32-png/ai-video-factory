import os, json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

# ✅ SIRF upload scope — analytics wala hata diya
creds = Credentials(
    token=None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    token_uri="https://oauth2.googleapis.com/token"
)
creds.refresh(Request())

yt = build("youtube", "v3", credentials=creds)

VIDEO = "output/final/final_video.mp4"
THUMB = "output/thumbnail.jpg"

req = yt.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title":           script["title"],
            "description":     script["description"],
            "tags":            script["tags"],
            "categoryId":      "22",
            "defaultLanguage": "en"
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids":             False
        }
    },
    media_body=MediaFileUpload(
        VIDEO,
        mimetype="video/mp4",
        chunksize=10 * 1024 * 1024,
        resumable=True
    )
)

print("📤 Uploading...")
response = None
while response is None:
    status, response = req.next_chunk()
    if status:
        print(f"   {int(status.progress()*100)}%", end="\r")

video_id = response["id"]
print(f"\n✅ Uploaded: https://youtube.com/watch?v={video_id}")

if os.path.exists(THUMB):
    yt.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(THUMB, mimetype="image/jpeg")
    ).execute()
    print("✅ Thumbnail set!")

with open("output/video_id.txt", "w") as f:
    f.write(video_id)

print(f"\n🎉 DONE! https://youtube.com/watch?v={video_id}")