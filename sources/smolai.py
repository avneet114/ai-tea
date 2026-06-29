import httpx
from bs4 import BeautifulSoup


SMOL_URL = "https://news.smol.ai/"


async def get_smolai_stories() -> list[dict]:
    """
    Scrape today's top AI stories from smol.ai.
    Returns list of {"title": ..., "url": ..., "summary": ..., "source": "smol.ai"}
    """
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(SMOL_URL, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        })
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    stories = []

    for item in soup.select("a[href]"):
        title = item.get_text(strip=True)
        url = item.get("href", "")

        if not title or len(title) < 15 or not url.startswith("http"):
            continue
        if "smol.ai" in url or "github.com/smol-ai" in url:
            continue

        stories.append({
            "title": title,
            "url": url,
            "summary": "",
            "source": "smol.ai",
        })

    # Deduplicate by URL
    seen = set()
    unique = []
    for s in stories:
        if s["url"] not in seen:
            seen.add(s["url"])
            unique.append(s)

    return unique[:20]
