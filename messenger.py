import os
import httpx

CLAW_API_KEY = os.getenv("CLAW_API_KEY")
CLAW_BASE    = "https://claw-messenger.onrender.com"


async def send_imessage(to: str, text: str):
    """Send an iMessage via Claw Messenger API."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{CLAW_BASE}/api/agent/send-message",
            headers={
                "Authorization": f"Bearer {CLAW_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "phone_number": to,
                "text": text,
                "service": "iMessage",
                "claim_route": True,
            },
        )
        resp.raise_for_status()
        return resp.json()
