import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sources.youtube import get_latest_transcript
from sources.rss import get_rss_stories
from digest import generate_digest
from messenger import send_imessage

MY_PHONE = os.getenv("MY_PHONE")

scheduler = AsyncIOScheduler()


async def run_digest():
    """Fetch all sources, generate digest, send via iMessage."""
    print("[digest] Fetching sources...")

    all_stories = []

    # RSS feeds — includes smol.ai, newsletters, Anthropic
    rss_stories = get_rss_stories()
    all_stories.extend(rss_stories)
    print(f"[digest] RSS: {len(rss_stories)} stories")

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

    # Save so Boba has context when you reply
    from main import save_digest
    save_digest(message)

    await send_imessage(MY_PHONE, message)
    print("[digest] Sent!")


@scheduler.scheduled_job("cron", hour=7, minute=30)
async def daily_digest():
    await run_digest()


def start_scheduler():
    scheduler.start()
