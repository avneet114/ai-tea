import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from scheduler import start_scheduler, run_digest


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health():
    return {"status": "ok", "project": "ai-tea"}


@app.post("/trigger/digest")
async def trigger_digest():
    """Manually trigger the daily digest — for testing without waiting for cron."""
    await run_digest()
    return {"ok": True}
