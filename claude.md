# Product 3: AI News → iMessage Daily Digest

**What it does:** Every morning you get an iMessage with 1 headline theme + 5 top AI news
stories from the last 24 hours, written like your excited best friend texting you. Format
changes daily so it never feels stale.

---

## Sources

### a. YouTube — AI Daily Brief
- Channel: https://www.youtube.com/@AIDailyBrief/videos
- Pull transcript from latest video using `youtube-transcript-api`
- Extract key stories mentioned in the episode

### b. smol.ai News
- Site: https://news.smol.ai/
- Aggregates top AI news from Twitter/X, Discord, Reddit, Hacker News
- Scrape or RSS the daily top stories

### c. Official Sources & Tech Press
- **OpenAI Blog** — openai.com/blog
- **Anthropic News** — anthropic.com/news
- **Google DeepMind Blog** — deepmind.google/blog
- **Meta AI Blog** — ai.meta.com/blog
- **Hugging Face Blog** — huggingface.co/blog
- **TechCrunch AI** — techcrunch.com/category/artificial-intelligence/
- **The Verge AI** — theverge.com/ai-artificial-intelligence
- **ArXiv cs.AI** — arxiv.org/list/cs.AI/recent

### Freshness Rule
Only include stories published or trending in the **last 24 hours**. No recycled news.
Filter by publish date on RSS items. For YouTube, only use transcripts from videos
uploaded in the last 24 hours. For smol.ai, scrape today's page only.

---

## Tone & Style: Excited Avneet

Write like an excited friend who just woke up and can't wait to tell you what happened.
Warm, enthusiastic, uses all caps occasionally, casual grammar, genuine excitement.

**Key rules:**
- Greeting changes every morning — never the same opener twice in a week
- Format/structure varies daily — sometimes numbered, sometimes just flowing text, sometimes uses reactions
- Max 3 sentences per story, keep it punchy
- Always include the source link so they can deep dive
- Feel like a friend texting, not a newsletter

**Example greetings (rotate, invent new ones):**
- "gooodmorning sunshines the world says hello and AI said hold my beer"
- "OKAY WAKE UP bc today is actually wild in AI"
- "rise n shine!! the robots were busy while u slept"
- "hey hey hey guess what happened overnight"
- "good morning beautiful people the AI timeline is UNHINGED today"

**Example formats (rotate daily):**

Format A — numbered casual:
```
gooodmorning sunshines!! the world says hello 🌞

today's theme: google woke up and chose violence

1. ok so google literally just dropped gemini 2.5 and it's FAST
   like scary fast. benchmarks are insane → deepmind.google/blog/gemini-2-5

2. did u see openai is charging $200/month now for pro??
   the timeline is losing it honestly → techcrunch.com/2025/...

3. anthropic published a paper on AI honesty and it's actually
   really interesting → anthropic.com/news/...

4. someone fine-tuned llama on their PHONE and it works???
   → huggingface.co/blog/...

5. the verge did a whole thing on AI replacing designers and
   designers are NOT happy about it → theverge.com/...

that's your morning briefing!! reply if u wanna deep dive on any of these
```

Format B — story style:
```
OKAY so wake up bc today is ACTUALLY crazy

so basically google and openai are literally beefing rn?? google dropped
gemini 2.5 (→ deepmind.google/...) and then openai fired back with a
tweet saying theirs is better and the whole timeline went insane

ALSO anthropic (our faves) just shipped... [continues naturally]

anyway go read the links if u want the full tea ☕
```

Format C — rapid fire:
```
rise n shine!! quick hits from the AI world:

• GPT-5 DROPPED (not a drill) → openai.com/blog/gpt-5
• zuck said llama 5 is coming in weeks??? → ai.meta.com/...
• that viral AI video tool everyone's posting? acquired by adobe → techcrunch.com/...
• deepmind solved another protein thing → deepmind.google/...
• huggingface hit 1M models on the hub 🤯 → huggingface.co/...

ok go be productive now ily 💛
```

---

## Architecture

```
Daily cron (7:30 AM) — runs on Railway
      │
      ├── YouTube: latest AI Daily Brief transcript (last 24h only)
      ├── smol.ai: scrape today's stories
      ├── TechCrunch + The Verge: RSS (last 24h)
      └── Official blogs: RSS (last 24h)
      │
      ▼
  Combine all stories → deduplicate → sort by recency
      │
      ▼
  Claude API (claude-sonnet-4-6)
      │  System prompt: "You are Avneet's excited best friend.
      │   Pick the 5 biggest AI stories from the last 24 hours.
      │   Write a theme headline + 5 items. Change your format
      │   and greeting every day. Max 3 sentences per item.
      │   Include source links. Be warm, fun, genuine."
      │
      ▼
  Claw Messenger API → blue bubble on iPhone at 8 AM
```

---

## Stack

| Layer | Tool | Cost |
|---|---|---|
| YouTube transcripts | youtube-transcript-api | Free |
| smol.ai scraping | httpx + BeautifulSoup | Free |
| Tech press + official blogs | RSS via feedparser | Free |
| AI summarization | Claude API | ~$0.05/day |
| iMessage delivery | Claw Messenger | Already subscribed |
| Hosting + cron | Railway | Free tier |

**Total: ~$1.50/month**

---

## File Structure

```
/product3
  main.py            # FastAPI app + /trigger/digest endpoint
  sources/
    youtube.py       # Pull AI Daily Brief transcript (last 24h)
    smolai.py        # Scrape smol.ai today's stories
    rss.py           # TechCrunch, The Verge, official blogs (last 24h)
  digest.py          # Claude: pick top 5, write excited genz digest
  messenger.py       # Claw Messenger iMessage send
  scheduler.py       # 7:30 AM daily cron
  .env
  requirements.txt
```

---

## Build Order

1. `sources/youtube.py` — pull latest AI Daily Brief transcript
2. `sources/smolai.py` — scrape smol.ai top stories
3. `sources/rss.py` — TechCrunch, The Verge, official blog RSS feeds (24h filter)
4. `digest.py` — Claude picks top 5, writes excited genz digest, rotates format
5. `messenger.py` — Claw Messenger send (copy from product2)
6. `scheduler.py` — wire it all, cron at 7:30 AM
7. `main.py` — FastAPI with `/trigger/digest` for testing
8. Deploy to Railway
