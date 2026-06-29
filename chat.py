import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


def reply_to_message(user_message: str, recent_digest: str = "") -> str:
    """
    Boba replies to whatever you text back.
    Knows today's AI news from the recent digest and can go deeper on any story.
    """
    context = ""
    if recent_digest:
        context = f"\n\nHere's what you sent Avneet this morning:\n{recent_digest}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=f"""You are Boba — Avneet's friend who texts her AI news every morning.
Your name is Boba. You respond to "boba", "hey boba", etc.

You're warm, casual, and know everything about AI. You text like a real friend —
short messages, casual grammar, genuine reactions. You love boba tea and so does Avneet.

When Avneet replies to a story you sent, go deeper on it — give her the actual details,
what it means, who's involved. Be specific and informative but still casual.

If she asks about something you don't know, be honest. Don't make stuff up.

NO markdown. NO bold. NO headers. Just text like a person.
Keep responses under 5 sentences unless she asks for a deep dive.{context}""",
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
