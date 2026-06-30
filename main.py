from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from scheduler import start_scheduler, run_digest

# Stores the latest digest text in memory (not used for replies yet,
# kept for when inbound messaging gets added later)
latest_digest = ""


def save_digest(text: str):
    global latest_digest
    latest_digest = text


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
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
