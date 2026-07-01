from typing import Optional
from datetime import datetime, timedelta, timezone
import feedparser

FEEDS = {
    # X/Twitter recaps — catches viral AI news before press does
    "smol.ai":         "https://news.smol.ai/rss.xml",
    "Ben's Bites":     "https://www.bensbites.com/feed",
    "TLDR AI":         "https://tldr.tech/ai/rss",
    "The Rundown AI":  "https://www.therundown.ai/feed",
    # Anthropic only official source
    "Anthropic":       "https://www.anthropic.com/rss.xml",
}

HOURS_LOOKBACK = 48  # wide enough to catch daily newsletters that publish late


def get_rss_stories() -> list[dict]:
    """
    Fetch stories from RSS feeds published in the last 36 hours.
    Returns list of {"title": ..., "url": ..., "summary": ..., "source": ...}
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)
    stories = []

    for source_name, feed_url in FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                published = _parse_date(entry)
                if published and published < cutoff:
                    continue

                stories.append({
                    "title":   entry.get("title", "").strip(),
                    "url":     entry.get("link", ""),
                    "summary": _clean_summary(entry.get("summary", "")),
                    "source":  source_name,
                })
        except Exception as e:
            print(f"[rss] Error fetching {source_name}: {e}")

    return stories


def _parse_date(entry) -> Optional[datetime]:
    """Try to parse the published date from an RSS entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = entry.get(field)
        if parsed:
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except Exception:
                pass
    return None


def _clean_summary(raw: str) -> str:
    """Strip HTML tags from summary."""
    from bs4 import BeautifulSoup
    text = BeautifulSoup(raw, "html.parser").get_text(strip=True)
    return text[:800] if text else ""
