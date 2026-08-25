import os
import json
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from app.schemas.context_analysis import (
    ContextChangeResult
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# ANALYZE CONTEXT CHANGE
# ============================================================

def analyze_context_change(
    previous_context: str,
    current_transcript: str,
    previous_meeting_id: Optional[int] = None
):
    """
    Compare a previous meeting with the current meeting.

    The purpose of this function is to detect changes such as:

    - deadline changed
    - task owner changed
    - decision changed

    IMPORTANT:
    This function DOES NOT update the database.

    It only detects a possible change.

    The user must confirm the change before the Task
    is updated.
    """

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are a meeting context continuity assistant.

Your job is to compare a previous meeting with a new meeting.

Look for important changes involving:

1. Deadline changes
2. Task owner / assignee changes
3. Important decision changes

Only report a change when there is clear evidence.

Do NOT invent information.

Previous meeting:

{previous_context}


Current meeting:

{current_transcript}


Return ONLY valid JSON.

Use exactly this structure:

{{
    "change_type": "deadline | assignee | decision",
    "task": "task or decision affected",
    "previous_value": "old value or null",
    "new_value": "new value or null",
    "evidence": "sentence from the current meeting proving the change",
    "previous_meeting_id": {previous_meeting_id if previous_meeting_id else "null"}
}}

If there is NO important change, return:

{{
    "change_type": "none",
    "task": "",
    "previous_value": null,
    "new_value": null,
    "evidence": "",
    "previous_meeting_id": null
}}
"""

    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        response_text = response.text.strip()

        print("\n===== GEMINI CONTEXT RESPONSE =====")
        print(response_text)

        # ----------------------------------------------------
        # Remove markdown if Gemini accidentally returns it
        # ----------------------------------------------------

        if response_text.startswith("```json"):
            response_text = response_text[7:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # ----------------------------------------------------
        # Convert JSON → Python dictionary
        # ----------------------------------------------------

        result = json.loads(response_text)

        # ----------------------------------------------------
        # Validate required fields
        # ----------------------------------------------------

        if "change_type" not in result:
            result["change_type"] = "none"

        if "task" not in result:
            result["task"] = ""

        if "previous_value" not in result:
            result["previous_value"] = None

        if "new_value" not in result:
            result["new_value"] = None

        if "evidence" not in result:
            result["evidence"] = ""

        if "previous_meeting_id" not in result:
            result["previous_meeting_id"] = previous_meeting_id

        return result

    # ========================================================
    # GEMINI ERROR
    # ========================================================

    except errors.APIError as e:

        print("===== GEMINI API ERROR =====")
        print(e)

        raise Exception(
            f"Gemini context analysis failed: {e}"
        )

    # ========================================================
    # INVALID JSON
    # ========================================================

    except json.JSONDecodeError as e:

        print("===== INVALID GEMINI JSON =====")
        print(e)

        raise Exception(
            "Gemini returned invalid context analysis JSON."
        )