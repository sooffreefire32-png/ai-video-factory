import os, json
from datetime import datetime, timedelta

def analyze():
    last_id_path = "data/last_video_id.txt"
    default = {
        "has_previous": False,
        "insights": (
            "First video — use strong hook in first 30 seconds, "
            "add pattern interrupts every 2 minutes, "
            "clear CTA at end."
        ),
        "avg_retention": 0,
        "weak_points": []
    }

    if not os.path.exists(last_id_path):
        _save(default)
        return

    video_id = open(last_id_path).read().strip()
    if not video_id:
        _save(default)
        return

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = Credentials(
            token=None,
            refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
            client_id=os.environ["YOUTUBE_CLIENT_ID"],
            client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/yt-analytics.readonly"
            ]
        )
        creds.refresh(Request())
        analytics = build("youtubeAnalytics", "v2", credentials=creds)

        end_date   = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        resp = analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="averageViewDuration,averageViewPercentage,views",
            dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id}",
            sort="elapsedVideoTimeRatio"
        ).execute()

        rows = resp.get("rows", [])
        if not rows:
            _save(default)
            return

        retentions = [float(r[2]) for r in rows]
        avg = sum(retentions) / len(retentions)

        # Find biggest drop points
        weak = []
        for i in range(1, len(rows)):
            drop = float(rows[i-1][2]) - float(rows[i][2])
            if drop > 8:
                time_pct = int(float(rows[i][0]) * 100)
                weak.append(f"{time_pct}% mark (drop: {drop:.1f}%)")

        tips = []
        if weak:
            tips.append(f"Viewers dropped at: {', '.join(weak[:3])} — add hooks/cuts there.")
        if avg < 30:
            tips.append("Low retention — shorten scenes, faster pacing needed.")
        elif avg > 50:
            tips.append("Good retention — continue similar style, add more depth.")

        result = {
            "has_previous": True,
            "video_id": video_id,
            "avg_retention": round(avg, 1),
            "weak_points": weak,
            "insights": " ".join(tips) if tips else "Good performance — maintain current style."
        }
        _save(result)
        print(f"✅ Retention: {avg:.1f}% | Weak points: {weak[:3]}")

    except Exception as e:
        print(f"⚠️ Analytics error (non-fatal): {e}")
        default["insights"] += f" (Analytics unavailable: {str(e)[:60]})"
        _save(default)

def _save(data):
    os.makedirs("output", exist_ok=True)
    with open("output/retention_insights.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    analyze()