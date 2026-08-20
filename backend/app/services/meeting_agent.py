import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def create_meeting_agent(
    transcript: str,
    context: str
):
    """
    Analyze the current meeting using
    context retrieved from MCP.
    """

    prompt = f"""
You are an AI Meeting Agent.

CURRENT MEETING:
{transcript}

CONTEXT FROM MCP:
{context}

Use the MCP context to understand previous
discussions when relevant.

Extract:

1. Meeting summary
2. Action items
3. Assignees
4. Deadlines

Do not invent information.

Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text