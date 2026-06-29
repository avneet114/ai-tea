from typing import Optional
from datetime import datetime, timedelta, timezone
import feedparser

FEEDS = {
    "OpenAI":        "https://openai.com/blog/rss.xml",
    "Anthropic":     "https://www.anthropic.com/rss.xml",
    "Google DeepMind": "https://blog.google/technology/ai/rss/",
    "Meta AI":       "https://ai.meta.com/blog/rss/",
    "Hugging Face":  "https://huggingface.co/blog/feed.xml",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI":  "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica":  "https://feeds.arstechnica.com/arstechnica/technology-lab",
}

HOURS_LOOKBACK = 36  # slightly wider than 24h to handle timezone edge cases


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
    return text[:300] if text else ""
