# YouTube Automation Setup Guide

This guide will help you set up and run your automated YouTube channel using GitHub Actions.

## 1. Prerequisites

Ensure you have the following secrets added to your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret Name | Description |
| :--- | :--- |
| `GH_TOKEN` | Your GitHub Personal Access Token (PAT) with `repo` and `workflow` scopes. |
| `GEMINI_API_KEY` | Your Google Gemini API Key for script, title, and thumbnail generation. |
| `PIXABAY_API_KEY` | Your Pixabay API Key for downloading stock images and videos. |
| `GOOGLE_CLIENT_ID` | Your Google Cloud Console Project Client ID. |
| `GOOGLE_CLIENT_SECRET` | Your Google Cloud Console Project Client Secret. |
| `GOOGLE_REFRESH_TOKEN` | A valid Google OAuth refresh token with YouTube upload permissions. |

## 2. YouTube OAuth Setup

To upload videos, you need a `token.json` file or a `GOOGLE_REFRESH_TOKEN`. Since this runs in GitHub Actions, using a refresh token is the most reliable method.

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a project and enable the **YouTube Data API v3**.
3.  Configure the **OAuth consent screen** and add yourself as a test user.
4.  Create **OAuth 2.0 Client IDs** (Desktop app).
5.  Use a script or a tool like [Google OAuth Playground](https://developers.google.com/oauthplayground/) to get a refresh token with the scope `https://www.googleapis.com/auth/youtube.upload`.

## 3. Repository Structure

-   `src/main.py`: The main script that orchestrates the entire process.
-   `src/tts.py`: Generates voiceover using `gTTS` (Free).
-   `src/flow_ai.py`: Fetches stock assets from Pixabay or generates images with Gemini.
-   `src/editor.py`: Renders the final video using `moviepy`.
-   `src/youtube_upload.py`: Uploads the video and thumbnail to YouTube.
-   `assets/character.mp4`: Your main character video (5 seconds).

## 4. How to Run

1.  Go to your GitHub repository.
2.  Click on the **Actions** tab.
3.  Select **AI Viral Video System** from the left sidebar.
4.  Click **Run workflow**.
5.  (Optional) Enter a specific topic or leave it blank for the AI to choose a viral one.
6.  Click **Run workflow** again.

The system will now:
1.  Generate a viral mystery topic.
2.  Write a 20-minute script.
3.  Download stock footage and images.
4.  Create a voiceover.
5.  Assemble the video with your character.
6.  Generate a thumbnail and metadata.
7.  Upload everything to YouTube at the optimal time.

## 5. Customization

-   **Video Length**: You can adjust the `VIDEO_MIN_DURATION_SECONDS` in `src/main.py`.
-   **Voice Language**: Change the `lang` parameter in `generate_voice` in `src/main.py`.
-   **Niche**: Update the `channel_niche` in `src/topic.py` to target different content.

Enjoy your automated YouTube journey!
