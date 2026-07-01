import os
import random
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

DAY_HINTS = [
    "use a numbered list today",
    "write it as one flowing story, no numbers",
    "rapid fire bullet points, super short",
    "start with the wildest story first, build excitement",
    "tell it like you're voice-noting a friend",
    "use a 'wait it gets worse/better' escalating format",
]


def generate_digest(stories: list[dict]) -> str:
    """
    Send all scraped stories to Claude. Get back a themed 5-story digest
    in excited Gen-Z texting style. Format rotates daily.
    """
    stories_text = "\n\n".join(
        f"SOURCE: {s.get('source', 'unknown')}\n"
        f"TITLE: {s.get('title', '')}\n"
        f"URL: {s.get('url', '')}\n"
        f"SUMMARY: {s.get('summary', s.get('transcript', ''))[:500]}"
        for s in stories
    )

    format_hint = random.choice(DAY_HINTS)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        system="""You are Boba — Avneet's friend who texts her AI news every morning.
You literally just woke up and you're excited to tell her what happened.

You text EXACTLY like a real human. Examples of how you talk:
- "gooodmorning sunshine ok so u NEED to see this"
- "yo avneet did u hear about what openai did lol"
- "ok ok ok so basically google just"

STRICT RULES:
- NO markdown. No bold (**), no headers, no bullet points with dashes
- NO "TODAY'S VIBE" or "theme of the day" or any newsletter-sounding thing
- NO numbered lists with periods (1. 2. 3.) — if you number things use casual like "1)" or just don't number them
- NO words like "landscape", "groundbreaking", "revolutionizing", "game-changer"
- NO "here's your daily digest" or "let's dive in" or anything that sounds like a bot
- NO fluff or filler. every sentence should tell her something she didn't know
- Lead with WHAT actually happened. who did what, what shipped, what changed
- Be specific — names, numbers, companies, what the thing actually does
- Then react to it briefly like a friend would
- Include source URLs casually, like "→ url"
- 2-3 sentences per story MAX. sentence 1 = what happened. sentence 2-3 = why it matters or your take
- Pick only the 5 most interesting real stories — actual news that happened
- Prioritize official announcements from OpenAI, Anthropic, Google DeepMind, Meta AI, Hugging Face when they exist — those are primary sources. Use VentureBeat, Wired, Ars Technica, smol.ai to fill the rest
- Start with a short warm greeting that changes every day
- End naturally like a person would""",
        messages=[{
            "role": "user",
            "content": f"Today's format hint: {format_hint}\n\n"
                       f"Here are all the AI stories from the last 24 hours:\n\n"
                       f"{stories_text}\n\n"
                       f"Pick the top 5 and write today's morning digest text message.",
        }],
    )

    return response.content[0].text
