import os
import google_auth_oauthlib.flow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )

    credentials = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(credentials.to_json())

    print("Login complete, token.json created!")

if __name__ == "__main__":
    main()