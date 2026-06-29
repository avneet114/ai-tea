import re
from typing import Optional
import httpx
from youtube_transcript_api import YouTubeTranscriptApi

CHANNEL_URL = "https://www.youtube.com/@AIDailyBrief/videos"


async def get_latest_transcript() -> Optional[dict]:
    """
    Fetch the latest AI Daily Brief video and return its transcript.
    Returns {"title": ..., "transcript": ..., "url": ..., "source": ...} or None.
    """
    video = await _get_latest_video_id()
    if not video:
        print("[youtube] No recent video found")
        return None

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video["id"])
        full_text = " ".join(seg["text"] for seg in transcript_list)
        return {
            "title": video["title"],
            "transcript": full_text[:8000],
            "url": f"https://youtube.com/watch?v={video['id']}",
            "source": "AI Daily Brief (YouTube)",
        }
    except Exception as e:
        print(f"[youtube] Transcript error: {e}")
        return None


async def _get_latest_video_id() -> Optional[dict]:
    """Scrape the channel page for the most recent video."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(CHANNEL_URL, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept-Language": "en-US,en;q=0.9",
        })
        html = resp.text

    pattern = r'"videoId":"([^"]+)".*?"text":"([^"]*)"'
    matches = re.findall(pattern, html)
    if not matches:
        return None

    seen = set()
    for vid_id, title in matches:
        if vid_id not in seen and len(title) > 10:
            return {"id": vid_id, "title": title}
    return None
