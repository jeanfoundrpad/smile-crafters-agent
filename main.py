"""
Smile Crafters AI Agent — FastAPI Server
Receives webhooks from messaging platforms and replies via the agent.

To run locally:
    uvicorn main:app --reload --port 8000

To test:
    curl -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{"contact_id": "test123", "message": "How much are veneers?"}'
"""

import random
import time
import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent import get_reply

app = FastAPI(title="Smile Crafters AI Agent")


# ── Request/Response models ───────────────────────────────────────────────────

class ChatRequest(BaseModel):
    contact_id: str       # Unique ID for this lead (from your CRM or platform)
    message: str          # The user's incoming message
    platform: str = "test"  # "instagram", "whatsapp", "facebook", "website", etc.


class ChatResponse(BaseModel):
    reply: str
    images: list[str] = []   # URLs of images to send (if any)
    delay_seconds: float = 0  # How long to wait before sending (human feel)


# ── Human delay logic ─────────────────────────────────────────────────────────

def calculate_delay(reply_text: str) -> float:
    """
    Simulate a human reading and typing delay.
    Returns seconds to wait before sending the reply.
    """
    read_time = random.uniform(3, 8)                  # Time to "read" the message
    type_time = len(reply_text) * 0.04                # ~40ms per character
    jitter = random.uniform(0, 4)
    total = read_time + type_time + jitter
    return min(total, 45)                             # Cap at 45 seconds


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "Smile Crafters agent is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main endpoint. Receives a message, runs it through the agent, returns a reply.

    This endpoint is called by:
    - Your test curl commands
    - ManyChat webhook (for Instagram/Facebook)
    - 360Dialog webhook (for WhatsApp)
    - Voiceflow webhook (for website chat)
    """
    print(f"\n[{req.platform}] {req.contact_id}: {req.message}")

    # Run agent (synchronous call wrapped in async)
    reply_text, image_urls = await asyncio.to_thread(
        get_reply, req.contact_id, req.message
    )

    delay = calculate_delay(reply_text)
    print(f"[Agent] Reply ({delay:.1f}s delay): {reply_text[:80]}...")

    return ChatResponse(
        reply=reply_text,
        images=image_urls,
        delay_seconds=round(delay, 1)
    )


# ── Platform-specific webhook handlers ───────────────────────────────────────
# These normalize each platform's webhook format into our standard ChatRequest.
# Wire these up in ManyChat / 360Dialog / Voiceflow as webhook URLs.

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Receives WhatsApp messages via 360Dialog webhook."""
    body = await request.json()
    # 360Dialog webhook format
    for msg in body.get("messages", []):
        contact_id = msg.get("from")
        text = msg.get("text", {}).get("body", "")
        if contact_id and text:
            reply, images = await asyncio.to_thread(get_reply, contact_id, text)
            delay = calculate_delay(reply)
            # TODO: Send reply back via 360Dialog API
            # POST https://waba.360dialog.io/v1/messages
            print(f"[WhatsApp → {contact_id}] (after {delay}s): {reply}")
    return {"status": "ok"}


@app.post("/webhook/instagram")
async def instagram_webhook(request: Request):
    """Receives Instagram DMs via ManyChat or Meta API webhook."""
    body = await request.json()
    # Meta/ManyChat webhook format
    for entry in body.get("entry", []):
        for msg_event in entry.get("messaging", []):
            contact_id = msg_event.get("sender", {}).get("id")
            text = msg_event.get("message", {}).get("text", "")
            if contact_id and text:
                reply, images = await asyncio.to_thread(get_reply, contact_id, text)
                delay = calculate_delay(reply)
                # TODO: Send reply back via Meta Graph API
                print(f"[Instagram → {contact_id}] (after {delay}s): {reply}")
    return {"status": "ok"}


@app.post("/webhook/facebook")
async def facebook_webhook(request: Request):
    """Receives Facebook Messenger messages."""
    # Facebook uses the same format as Instagram
    return await instagram_webhook(request)
