import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sources.youtube import get_latest_transcript
from sources.smolai import get_smolai_stories
from sources.rss import get_rss_stories
from digest import generate_digest
from messenger import send_imessage

MY_PHONE = os.getenv("MY_PHONE")

scheduler = AsyncIOScheduler()


async def run_digest():
    """Fetch all sources, generate digest, send via iMessage."""
    print("[digest] Fetching sources...")

    # Gather all stories from all sources
    all_stories = []

    # RSS feeds (sync)
    rss_stories = get_rss_stories()
    all_stories.extend(rss_stories)
    print(f"[digest] RSS: {len(rss_stories)} stories")

    # smol.ai (async)
    try:
        smol_stories = await get_smolai_stories()
        all_stories.extend(smol_stories)
        print(f"[digest] smol.ai: {len(smol_stories)} stories")
    except Exception as e:
        print(f"[digest] smol.ai error: {e}")

    # YouTube transcript (async)
    try:
        yt = await get_latest_transcript()
        if yt:
            all_stories.append(yt)
            print(f"[digest] YouTube: got transcript for '{yt['title']}'")
    except Exception as e:
        print(f"[digest] YouTube error: {e}")

    if not all_stories:
        print("[digest] No stories found, skipping.")
        return

    print(f"[digest] Total: {len(all_stories)} stories → sending to Claude...")
    message = generate_digest(all_stories)
    print(f"[digest] Digest generated ({len(message)} chars), sending iMessage...")

    await send_imessage(MY_PHONE, message)
    print("[digest] Sent!")


@scheduler.scheduled_job("cron", hour=7, minute=30)
async def daily_digest():
    await run_digest()


def start_scheduler():
    scheduler.start()
