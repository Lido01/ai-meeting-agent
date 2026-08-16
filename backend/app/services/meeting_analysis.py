import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_meeting(transcript: str):
    """
    Send transcript to Gemini and extract:
    - summary
    - action items
    """

    prompt = f"""
You are an AI meeting assistant.

Analyze this meeting transcript.

Return ONLY valid JSON using this structure:

{{
    "summary": "short meeting summary",
    "action_items": [
        {{
            "description": "task description",
            "assignee": "person responsible",
            "deadline": "YYYY-MM-DD or null"
        }}
    ]
}}

Meeting transcript:
{transcript}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    # Convert Gemini JSON text into Python data
    result = json.loads(response.text)

    return result