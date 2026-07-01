import httpx
from bs4 import BeautifulSoup

TLDR_URL = "https://tldr.tech/api/latest/ai"


async def get_tldr_stories() -> list[dict]:
    """
    Scrape today's TLDR AI newsletter from tldr.tech/api/latest/ai.
    Each story is an <article> tag containing a link with utm_source=tldrai
    and a summary paragraph.
    Returns list of {"title", "url", "summary", "source"}.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(TLDR_URL, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        }, follow_redirects=True)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    stories = []

    for article in soup.find_all("article"):
        link = article.find("a", href=True)
        if not link:
            continue

        href = link.get("href", "")
        title = link.get_text(strip=True)

        # Only real stories have utm_source=tldrai and "(X minute read)"
        if "utm_source=tldrai" not in href or "minute read" not in title.lower():
            continue

        # Strip the "(X minute read)" suffix from title
        clean_title = title.rsplit("(", 1)[0].strip()

        # Summary is all text in the article minus the link text
        full_text = article.get_text(strip=True)
        summary = full_text.replace(title, "").strip()[:500]

        # Clean utm params from URL
        url = href.split("?")[0]

        stories.append({
            "title": clean_title,
            "url": url,
            "summary": summary,
            "source": "TLDR AI",
        })

    return stories
