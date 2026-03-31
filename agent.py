"""
Smile Crafters AI Agent — Core Logic
Handles multi-turn conversations using Claude with tool use.
"""

import os
import anthropic
from system_prompt import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, execute_tool

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# In-memory conversation store: { contact_id: [messages] }
# In production, replace with a database (Redis, Postgres, etc.)
conversations: dict[str, list] = {}


def get_reply(contact_id: str, user_message: str) -> tuple[str, list[str]]:
    """
    Send a user message and get Claude's reply.

    Returns:
        (text_reply, image_urls) — the text response and any images to send
    """
    # Load or create conversation history for this contact
    if contact_id not in conversations:
        conversations[contact_id] = []

    history = conversations[contact_id]
    history.append({"role": "user", "content": user_message})

    image_urls = []
    final_text = ""

    # Agentic loop — keeps going until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=history,
        )

        # Collect any text blocks from this response turn
        for block in response.content:
            if block.type == "text":
                final_text = block.text

        # If Claude is done (no more tool calls), break
        if response.stop_reason == "end_turn":
            history.append({"role": "assistant", "content": response.content})
            break

        # Claude wants to use tools
        if response.stop_reason == "tool_use":
            history.append({"role": "assistant", "content": response.content})

            # Execute each tool Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Tool] {block.name}({block.input})")
                    result = execute_tool(block.name, block.input)

                    # If it's send_image, capture the URL to return to caller
                    if block.name == "send_image":
                        import json
                        result_data = json.loads(result)
                        if result_data.get("success") and result_data.get("url"):
                            image_urls.append(result_data["url"])

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            history.append({"role": "user", "content": tool_results})
            # Loop again — Claude will process the tool results and respond

        else:
            # Unexpected stop reason — break to avoid infinite loop
            break

    # Save updated history
    conversations[contact_id] = history

    return final_text, image_urls


def reset_conversation(contact_id: str):
    """Clear conversation history for a contact (e.g. after a booking)."""
    conversations.pop(contact_id, None)
