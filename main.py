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
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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


@app.get("/demo", response_class=HTMLResponse)
def demo_chat():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smile Crafters — AI Assistant</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .chat-window { width: 420px; height: 680px; background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; }
    .chat-header { background: #1a1a2e; color: white; padding: 16px 20px; }
    .chat-header h2 { font-size: 16px; }
    .chat-header span { font-size: 12px; color: #aaa; display: block; margin-top: 2px; }
    .chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
    .msg { max-width: 82%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
    .msg.user { background: #1a1a2e; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
    .msg.bot { background: #f1f1f1; color: #222; align-self: flex-start; border-bottom-left-radius: 4px; }
    .msg.typing { color: #999; font-style: italic; background: #f1f1f1; align-self: flex-start; }
    .chat-input { display: flex; padding: 12px; border-top: 1px solid #eee; gap: 8px; }
    .chat-input input { flex: 1; padding: 10px 14px; border: 1px solid #ddd; border-radius: 24px; font-size: 14px; outline: none; }
    .chat-input button { background: #1a1a2e; color: white; border: none; border-radius: 24px; padding: 10px 18px; cursor: pointer; font-size: 14px; }
    .chat-input button:disabled { background: #999; cursor: not-allowed; }
    @media (max-width: 480px) { .chat-window { width: 100%; height: 100vh; border-radius: 0; } }
  </style>
</head>
<body>
<div class="chat-window">
  <div class="chat-header">
    <h2>Smile Crafters</h2>
    <span>Beverly Hills Premier Dental — AI Assistant</span>
  </div>
  <div class="chat-messages" id="messages">
    <div class="msg bot">Hi there! Welcome to Smile Crafters. How can I help you today?</div>
  </div>
  <div class="chat-input">
    <input type="text" id="userInput" placeholder="Type a message..." onkeydown="if(event.key==='Enter') sendMessage()" />
    <button id="sendBtn" onclick="sendMessage()">Send</button>
  </div>
</div>
<script>
  const contactId = "demo_" + Math.random().toString(36).substr(2, 9);

  async function sendMessage() {
    const input = document.getElementById("userInput");
    const btn = document.getElementById("sendBtn");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";
    btn.disabled = true;

    const typingEl = addMessage("Typing...", "typing");

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contact_id: contactId, message: text, platform: "demo" })
      });
      const data = await res.json();
      const delay = Math.min((data.delay_seconds || 2) * 1000, 8000);
      await new Promise(r => setTimeout(r, delay));
      typingEl.remove();
      addMessage(data.reply, "bot");
    } catch (err) {
      typingEl.remove();
      addMessage("Sorry, something went wrong. Please try again.", "bot");
    }

    btn.disabled = false;
    input.focus();
  }

  function addMessage(text, type) {
    const el = document.createElement("div");
    el.className = "msg " + type;
    el.textContent = text;
    const container = document.getElementById("messages");
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
    return el;
  }
</script>
</body>
</html>"""


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
