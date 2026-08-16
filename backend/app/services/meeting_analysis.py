import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import errors


# Load variables from .env
load_dotenv()


# Create Gemini client using your API key
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_meeting(transcript: str):
    """
    Send a meeting transcript to Gemini.

    Gemini returns:
    - summary
    - action_items
    """

    prompt = f"""
You are an AI meeting assistant.

Analyze the following meeting transcript.

Return ONLY valid JSON using exactly this structure:

{{
    "summary": "short summary of the meeting",
    "action_items": [
        {{
            "description": "specific task",
            "assignee": "person responsible or null",
            "deadline": "YYYY-MM-DD or null"
        }}
    ]
}}

Important:
- Do not add markdown.
- Do not add ```json.
- Return only JSON.
- If there are no action items, return an empty array.

Rules:
- Return ONLY JSON.
- Do not use markdown.
- Do not use ```json.
- If there are no action items, return an empty array.
- NEVER invent a deadline.
- If the year is not explicitly mentioned, return null for the deadline.
- Only return a deadline when it is clearly stated in the transcript.

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

        # Convert JSON text into Python dictionary
        result = json.loads(response_text)

        return result

    except errors.APIError as e:

        # Gemini API error, such as 503
        print(f"Gemini API error: {e}")

        raise Exception(
            "Gemini is temporarily unavailable. Please try again."
        )

    except json.JSONDecodeError:

        # Gemini returned something that wasn't valid JSON
        print("Gemini returned invalid JSON.")

        raise Exception(
            "Gemini returned an invalid analysis response."
        )