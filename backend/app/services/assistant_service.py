import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app.services.mcp_client import (
    MCPClientError,
    retrieve_meeting_context,
)


BACKEND_DIR = Path(__file__).resolve().parents[2]

load_dotenv(dotenv_path=BACKEND_DIR / ".env")


class AssistantError(Exception):
    """Raised when the assistant cannot produce a grounded reply."""


def _format_mcp_context(context) -> str:
    if not context:
        return "No previous meeting context was found."

    if isinstance(context, str):
        return context

    return json.dumps(context, indent=2, default=str)


def _build_prompt(context_text: str, user_message: str) -> str:
    return f"""
You are an AI meeting assistant.

The following information was retrieved from the user's previous meetings
through MCP.

Use this context to answer the user's question.

Do not invent information.

If the context does not contain the answer, say that you could not
find enough information in the user's previous meetings.

Retrieved MCP context:
{context_text}

USER QUESTION:
{user_message}
""".strip()


def _generate_reply(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise AssistantError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=api_key)

    # Prefer the same model used by meeting analysis, then the
    # transcription model already used in this project.
    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    last_error = None

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
        except Exception as exc:
            print(f"===== GEMINI MODEL ERROR ({model}) =====")
            print(exc)
            last_error = exc
            continue

        text = (response.text or "").strip()

        if text:
            return text

        last_error = AssistantError(
            "Gemini returned an empty assistant reply."
        )

    if isinstance(last_error, AssistantError):
        raise last_error

    raise AssistantError(
        "I retrieved your meeting context, but the assistant could "
        "not generate a reply. Please try again."
    ) from last_error


async def answer_user_question(
    user_id: int,
    message: str
) -> str:
    """
    Retrieve meeting/task context through MCP, then ask Gemini
    to answer using only that context.
    """

    try:
        context = await retrieve_meeting_context(
            user_id=user_id,
            query=message,
            limit=5,
        )
    except MCPClientError as exc:
        print("===== ASSISTANT MCP ERROR =====")
        print(exc)
        raise AssistantError(
            "I couldn't retrieve your previous meeting context "
            "right now. Please try again."
        ) from exc

    context_text = _format_mcp_context(context)
    prompt = _build_prompt(context_text, message)

    try:
        return await asyncio.to_thread(
            _generate_reply,
            prompt
        )
    except AssistantError:
        raise
    except Exception as exc:
        print("===== ASSISTANT GEMINI ERROR =====")
        print(exc)
        raise AssistantError(
            "I retrieved your meeting context, but the assistant could "
            "not generate a reply. Please try again."
        ) from exc
