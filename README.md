# ai-tea

Daily AI news delivered to my iMessage every morning at 7:30am via **Boba** — an AI friend persona that texts like a person, not a newsletter.

Built on top of [iaintreadingallthat](https://avneet114.github.io/tldr/) news sources. Sent via iMessage (blue bubble) using [Claw Messenger](https://claw-messenger.com).

---

## What it does

Boba pulls from 10 sources every morning, filters to the last 36 hours, picks the 5 most interesting AI stories, and texts me in the morning.

---

## Sources

| Source | Type |
|--------|------|
| AI Daily Brief | YouTube transcript |
| smol.ai | Scraped aggregator |
| OpenAI Blog | RSS |
| Anthropic | RSS |
| Google DeepMind | RSS |
| Meta AI | RSS |
| Hugging Face | RSS |
| TechCrunch AI | RSS |
| The Verge AI | RSS |
| Ars Technica | RSS |

---

## Stack

| Layer | Tool |
|-------|------|
| News fetching | feedparser, httpx, BeautifulSoup |
| YouTube transcripts | youtube-transcript-api |
| AI digest generation | Claude API (claude-sonnet-4-6) |
| iMessage delivery | Claw Messenger |
| Hosting + cron | Railway |

---

## Structure

```
main.py          — FastAPI app, /trigger/digest endpoint
scheduler.py     — APScheduler cron at 7:30am daily
digest.py        — Claude prompt, generates Boba's message
messenger.py     — Claw Messenger iMessage send
sources/
  rss.py         — 8 RSS feeds, 36h lookback
  smolai.py      — scrapes news.smol.ai
  youtube.py     — AI Daily Brief transcript fetcher
Procfile         — uvicorn for Railway
```
