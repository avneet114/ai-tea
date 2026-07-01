import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sources.youtube import get_latest_transcript
from sources.rss import get_rss_stories
from sources.tldr import get_tldr_stories
from digest import generate_digest
from messenger import send_imessage

MY_PHONE = os.getenv("MY_PHONE")

scheduler = AsyncIOScheduler()


async def run_digest():
    """Fetch all sources, generate digest, send via iMessage."""
    print("[digest] Fetching sources...")

    all_stories = []

    # TLDR AI is primary — scrape today's newsletter first
    try:
        tldr_stories = await get_tldr_stories()
        print(f"[digest] TLDR AI: {len(tldr_stories)} stories")
        all_stories.extend(tldr_stories)
    except Exception as e:
        print(f"[digest] TLDR error: {e}")

    # If TLDR had nothing (weekend / scrape failed), fall back to RSS + YouTube
    if not all_stories:
        print("[digest] TLDR empty — falling back to RSS + YouTube")
        rss_stories = get_rss_stories()
        all_stories.extend(rss_stories)
        print(f"[digest] RSS fallback: {len(rss_stories)} stories")

        try:
            yt = await get_latest_transcript()
            if yt:
                all_stories.append(yt)
                print(f"[digest] YouTube: got transcript for '{yt['title']}'")
        except Exception as e:
            print(f"[digest] YouTube error: {e}")
    else:
        # Still grab YouTube even on TLDR days — good for extra context
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
