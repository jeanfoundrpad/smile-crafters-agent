"""
Tool definitions and implementations for the Smile Crafters agent.
Replace the stub implementations with real Calendly/CRM API calls.
"""

import os

# ── Tool definitions sent to Claude ─────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "check_availability",
        "description": "Check available appointment slots for a consultation. Call this when the user expresses interest in booking or asks about scheduling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "consultation_type": {
                    "type": "string",
                    "enum": ["virtual", "in_person"],
                    "description": "Whether the user wants a virtual or in-person consultation."
                }
            },
            "required": ["consultation_type"]
        }
    },
    {
        "name": "book_consultation",
        "description": "Book a consultation appointment for the lead.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Lead's full name."},
                "phone": {"type": "string", "description": "Lead's phone number."},
                "email": {"type": "string", "description": "Lead's email address."},
                "slot": {"type": "string", "description": "The appointment slot, e.g. 'Tuesday March 31 at 2:00 PM'."},
                "consultation_type": {
                    "type": "string",
                    "enum": ["virtual", "in_person"],
                    "description": "Type of consultation."
                }
            },
            "required": ["slot", "consultation_type"]
        }
    },
    {
        "name": "send_image",
        "description": "Send an image to the lead. Use this when the user asks to see photos, before/after results, smile transformations, or pricing/promotion info. Send up to 2-3 images when relevant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_key": {
                    "type": "string",
                    "enum": [
                        "veneer_closeup_after",
                        "veneer_process_wax",
                        "veneer_side_profile",
                        "veneer_side_angles",
                        "veneer_full_smile",
                        "veneer_full_arch",
                        "veneer_before_after",
                        "veneer_arch_final"
                    ],
                    "description": "Which image to send. Use veneer_before_after for dramatic before/after transformation. Use veneer_full_smile or veneer_closeup_after for beautiful final results. Use veneer_process_wax or veneer_side_profile to show the process. Send 2-3 images when a user asks to see results."
                }
            },
            "required": ["image_key"]
        }
    },
    {
        "name": "update_lead_stage",
        "description": "Update the lead's stage in the CRM pipeline.",
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string", "description": "The lead's unique contact ID."},
                "stage": {
                    "type": "string",
                    "enum": ["new", "warm", "hot", "booked", "lost"],
                    "description": "The new pipeline stage."
                },
                "notes": {"type": "string", "description": "Optional notes about the lead."}
            },
            "required": ["contact_id", "stage"]
        }
    }
]

# ── Image library ─────────────────────────────────────────────────────────────
# Images are extracted from the client's PDF (6 real before/after photos).
# TODO: Upload the files in the /images folder to Cloudinary (free) and
#       paste the resulting URLs here. Steps:
#       1. Go to cloudinary.com → sign up free
#       2. Upload all 6 files from smile_crafters_agent/images/
#       3. Copy each URL and paste below

IMAGE_LIBRARY = {
    "veneer_closeup_after":    "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958376/Close-up_lips_white_veneers_mi3er3.jpg",
    "veneer_process_wax":      "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958462/Wax_model_on_black_background_ocz5bn.jpg",
    "veneer_side_profile":     "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958469/Side_profile_temporaries_i0d6e5.jpg",
    "veneer_side_angles":      "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958479/Wax_Two_side-angle_shots_rlhlrn.jpg",
    "veneer_full_smile":       "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958498/Full_smile_red_lips_cpccg4.jpg",
    "veneer_full_arch":        "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958504/Full_upper_lower_arch_smile_cmy4rq.jpg",
    "veneer_before_after":     "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958511/Before_and_after_Smiles_bb5lo9.jpg",
    "veneer_arch_final":       "https://res.cloudinary.com/dhdianxeq/image/upload/v1774958517/Clean_full_arch_final_g9mogu.jpg",
}

# ── Tool implementations ──────────────────────────────────────────────────────

def check_availability(consultation_type: str) -> dict:
    """
    Returns available appointment slots.
    TODO: Replace with real Calendly API call:
    GET https://api.calendly.com/event_type_available_times
    """
    # Stub response — replace with Calendly API
    slots = [
        "Tuesday April 1 at 10:00 AM",
        "Tuesday April 1 at 2:00 PM",
        "Wednesday April 2 at 11:00 AM",
        "Thursday April 3 at 3:00 PM",
    ]
    return {
        "available_slots": slots,
        "consultation_type": consultation_type,
        "duration": "15 minutes",
        "cost": "Free"
    }


def book_consultation(slot: str, consultation_type: str, name: str = None,
                      phone: str = None, email: str = None) -> dict:
    """
    Books a consultation appointment.
    TODO: Replace with real Calendly API call:
    POST https://api.calendly.com/scheduled_events
    """
    # Stub response — replace with Calendly API
    return {
        "success": True,
        "confirmation_number": "SC-2024-001",
        "slot": slot,
        "type": consultation_type,
        "message": f"Appointment confirmed for {slot}. A confirmation will be sent shortly."
    }


def send_image(image_key: str) -> dict:
    """
    Returns the URL of the requested image.
    The calling code (main.py) is responsible for actually sending
    this image via the platform API (WhatsApp, IG, etc.).
    """
    url = IMAGE_LIBRARY.get(image_key)
    if not url:
        return {"success": False, "error": f"Image '{image_key}' not found."}
    return {
        "success": True,
        "image_key": image_key,
        "url": url
    }


def update_lead_stage(contact_id: str, stage: str, notes: str = None) -> dict:
    """
    Updates the lead's CRM stage.
    TODO: Replace with real CRM API call (GoHighLevel, Airtable, etc.)
    """
    print(f"[CRM] Contact {contact_id} → stage: {stage} | notes: {notes}")
    return {"success": True, "contact_id": contact_id, "stage": stage}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Routes Claude's tool call to the correct function and returns a result string."""
    import json

    if tool_name == "check_availability":
        result = check_availability(**tool_input)
    elif tool_name == "book_consultation":
        result = book_consultation(**tool_input)
    elif tool_name == "send_image":
        result = send_image(**tool_input)
    elif tool_name == "update_lead_stage":
        result = update_lead_stage(**tool_input)
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result)
