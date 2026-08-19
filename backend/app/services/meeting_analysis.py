import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import errors


# Load variables from .env
load_dotenv()


# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_meeting(
    transcript: str,
    previous_context: list | None = None
):
    """
    Analyze a meeting transcript using Gemini.

    previous_context contains information from
    previous meetings for the same user.

    Returns:
        summary
        action_items
    """

    # If there are no previous meetings,
    # use an empty list.
    if previous_context is None:
        previous_context = []


    # --------------------------------------------------
    # Build previous meeting context
    # --------------------------------------------------

    context_text = ""

    for meeting in previous_context:

        context_text += f"""
Previous Meeting ID: {meeting["meeting_id"]}
Title: {meeting["title"]}
Summary: {meeting["summary"]}
Transcript: {meeting["transcript"]}

--------------------------------
"""


    # If there is no previous context
    if not context_text:

        context_text = "No previous meeting context is available."


    # --------------------------------------------------
    # Gemini prompt
    # --------------------------------------------------

    prompt = f"""
You are an AI meeting assistant.

You are analyzing a NEW meeting.

You also have access to PREVIOUS MEETING CONTEXT.

Use previous meetings only when they are relevant
to the current meeting.

==============================
PREVIOUS MEETING CONTEXT
==============================

{context_text}


==============================
CURRENT MEETING
==============================

{transcript}


==============================
TASK
==============================

Analyze the current meeting.

Identify:
1. A short summary.
2. Real action items assigned to people.
3. Deadlines when explicitly mentioned.


Return ONLY valid JSON using exactly this structure:

{{
    "summary": "short summary of the current meeting",
    "action_items": [
        {{
            "description": "specific task that must be completed",
            "assignee": "person responsible or null",
            "deadline": "YYYY-MM-DD or null"
        }}
    ]
}}


==============================
RULES
==============================

1. Return ONLY JSON.

2. Do NOT use markdown.

3. Do NOT use ```json.

4. Do NOT invent tasks.

5. Do NOT invent people.

6. Do NOT invent deadlines.

7. Only use information from the current meeting
   or relevant previous meeting context.

8. If nobody is assigned a task,
   return an empty action_items array.

9. If a person says:
   "I will do..."
   "I will finish..."
   "I'll handle..."
   treat it as an action item.

10. If someone assigns another person a task,
    treat it as an action item.

11. If the deadline does not include a year,
    return null.

12. Only return a deadline when it is clearly
    stated in the conversation.

13. Previous meetings provide context only.
    Do not create tasks from old meetings unless
    the current meeting refers to them.


Return the JSON now.
"""


    # --------------------------------------------------
    # Send request to Gemini
    # --------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # Get Gemini response
        response_text = response.text.strip()


        print("===== GEMINI ANALYSIS RESPONSE =====")
        print(response_text)


        # --------------------------------------------------
        # Remove markdown if Gemini accidentally adds it
        # --------------------------------------------------

        if response_text.startswith("```json"):

            response_text = response_text[7:]


        if response_text.endswith("```"):

            response_text = response_text[:-3]


        response_text = response_text.strip()


        # --------------------------------------------------
        # Convert JSON string to Python dictionary
        # --------------------------------------------------

        result = json.loads(response_text)


        # --------------------------------------------------
        # Make sure required fields exist
        # --------------------------------------------------

        if "summary" not in result:

            result["summary"] = ""


        if "action_items" not in result:

            result["action_items"] = []


        return result


    # --------------------------------------------------
    # Gemini API error
    # --------------------------------------------------

    except errors.APIError as e:

        print(f"Gemini API error: {e}")

        raise Exception(
            f"Gemini analysis failed: {e}"
        )


    # --------------------------------------------------
    # Invalid JSON error
    # --------------------------------------------------

    except json.JSONDecodeError as e:

        print("Gemini returned invalid JSON.")

        print(f"JSON error: {e}")

        raise Exception(
            "Gemini returned invalid JSON."
        )