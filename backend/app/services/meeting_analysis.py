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


def analyze_meeting(transcript: str):
    """
    Analyze a meeting transcript using Gemini.

    Returns:
        summary
        action_items
    """

    prompt = f"""
You are an AI meeting assistant.

Analyze the following meeting transcript and identify
real action items assigned to people.

Return ONLY valid JSON using this exact structure:

{{
    "summary": "short summary of the meeting",
    "action_items": [
        {{
            "description": "specific task that must be completed",
            "assignee": "person responsible or null",
            "deadline": "YYYY-MM-DD or null"
        }}
    ]
}}

Rules:

1. Return ONLY JSON.
2. Do NOT use markdown.
3. Do NOT use ```json.
4. Do NOT invent tasks.
5. Do NOT invent people.
6. Do NOT invent deadlines.
7. If nobody is assigned a task, return an empty action_items array.
8. If a person says "I will do...", treat it as an action item.
9. If someone assigns another person a task, treat it as an action item.
10. If the deadline does not include a year, return null.
11. Only use information that exists in the transcript.

Meeting transcript:

{transcript}
"""

    try:

        # Send transcript to Gemini
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        # Get Gemini response
        response_text = response.text.strip()

        print("===== GEMINI ANALYSIS RESPONSE =====")
        print(response_text)

        # Remove markdown if Gemini accidentally returns it
        if response_text.startswith("```json"):
            response_text = response_text[7:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Convert JSON into Python dictionary
        result = json.loads(response_text)

        # Make sure required fields exist
        if "summary" not in result:
            result["summary"] = ""

        if "action_items" not in result:
            result["action_items"] = []

        return result

    except errors.APIError as e:

        print(f"Gemini API error: {e}")

        raise Exception(
            f"Gemini analysis failed: {e}"
        )

    except json.JSONDecodeError as e:

        print("Gemini returned invalid JSON.")
        print(f"JSON error: {e}")

        raise Exception(
            "Gemini returned invalid JSON."
        )