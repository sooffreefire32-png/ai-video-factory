import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import pickle

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    credentials = None
    token_path = "token.pickle"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # This part is for initial authorization, which is hard in GitHub Actions.
            # We'll rely on a pre-generated refresh token.
            raise Exception("No valid credentials found. Please ensure GOOGLE_REFRESH_TOKEN is set.")

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(video_path, title, description, tags, category_id="28", privacy_status="public"):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=video_path
    )

    response = insert_request.execute()
    print(f"Video uploaded. ID: {response.get("id")}")
    return response.get("id")


if __name__ == "__main__":
    # This part is for generating the initial refresh token locally.
    # In GitHub Actions, we'll use the GOOGLE_REFRESH_TOKEN directly.
    # This block won't run in the GitHub Action environment.
    if not os.path.exists("client_secret.json"):
        print("Please download client_secret.json from Google Cloud Console.")
        print("Visit https://console.developers.google.com/apis/credentials")
        print("Create OAuth 2.0 Client IDs -> Desktop app. Download JSON and rename to client_secret.json")
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", SCOPES)
        credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
        print("Refresh Token:", credentials.refresh_token)

    # Example usage (will be called by the workflow)
    # upload_video("output/final_video.mp4", "My AI Generated Video", "This video was made by AI!", ["AI", "YouTube", "Automation"])
