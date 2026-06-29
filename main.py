import os
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from scheduler import start_scheduler, run_digest
from chat import reply_to_message
from messenger import send_imessage

MY_PHONE  = os.getenv("MY_PHONE")
CLAW_KEY  = os.getenv("CLAW_API_KEY")
CLAW_WS   = "wss://claw-messenger.onrender.com"

# Store latest digest so Boba has context when you reply
latest_digest = ""


def save_digest(text: str):
    global latest_digest
    latest_digest = text


async def on_reply(from_number: str, body: str):
    """When Avneet texts back, Boba replies."""
    if from_number != MY_PHONE:
        return
    print(f"[boba] Got reply: {body}")
    response = reply_to_message(body, recent_digest=latest_digest)
    await send_imessage(MY_PHONE, response)
    print(f"[boba] Replied!")


async def listen_for_replies():
    """Connect to Claw Messenger WebSocket and listen for inbound messages."""
    try:
        import websockets
    except ImportError:
        print("[boba] websockets not installed, skipping reply listener")
        return

    ws_url = f"{CLAW_WS}?api_key={CLAW_KEY}"
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                print("[boba] listening for your replies...")
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                        from_number = msg.get("from") or msg.get("phone_number")
                        body = msg.get("text") or msg.get("body", "")
                        if from_number and body:
                            await on_reply(from_number, body)
                    except Exception as e:
                        print(f"[boba] parse error: {e}")
        except Exception as e:
            print(f"[boba] ws disconnected: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    asyncio.create_task(listen_for_replies())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health():
    return {"status": "ok", "project": "ai-tea", "friend": "boba"}


@app.post("/trigger/digest")
async def trigger_digest():
    """Manually trigger Boba's morning digest."""
    await run_digest()
    return {"ok": True}
