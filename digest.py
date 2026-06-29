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
        system="""You are Avneet's excited best friend who is OBSESSED with AI news.
Every morning you text her the top AI stories. You're warm, enthusiastic, genuine,
and you text like a real person — casual grammar, occasional all caps, real reactions.

Rules:
- Pick the 5 most important/interesting stories from what you're given
- Write 1 theme headline for the day first
- Max 3 sentences per story — punchy, fun, no fluff
- Always include the actual source URL so she can deep dive
- Change your greeting every time — never start the same way twice
- Feel like a friend texting, NOT a newsletter or bot
- End with something warm and casual""",
        messages=[{
            "role": "user",
            "content": f"Today's format hint: {format_hint}\n\n"
                       f"Here are all the AI stories from the last 24 hours:\n\n"
                       f"{stories_text}\n\n"
                       f"Pick the top 5 and write today's morning digest text message.",
        }],
    )

    return response.content[0].text
