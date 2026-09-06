"""
Development-only verification of the MCP assistant path.

Does not query PostgreSQL from the assistant layer.
Uses the MCP stdio client, then POST /assistant/chat.
"""

import asyncio
import json
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "scripts"))

from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.auth_service import create_access_token  # noqa: E402
from app.services.mcp_client import retrieve_meeting_context  # noqa: E402
from seed_demo_mcp_memory import seed  # noqa: E402


DEMO_QUESTION = (
    "Who was responsible for the API follow-up from our previous meeting?"
)


def first_user_id() -> int:
    db = SessionLocal()
    try:
        user = db.query(User).order_by(User.id.asc()).first()
        if not user:
            raise SystemExit("No user found. Register a user first.")
        return user.id
    finally:
        db.close()


async def verify_mcp_protocol(user_id: int) -> None:
    print("\n===== TEST: MCP PROTOCOL get_meeting_context =====")
    context = await retrieve_meeting_context(
        user_id=user_id,
        query=DEMO_QUESTION,
        limit=5,
    )
    blob = json.dumps(context, default=str).lower()
    print("payload_type", type(context).__name__)
    print("meeting_count", len(context) if isinstance(context, list) else "n/a")
    print("has_sarah", "sarah" in blob)
    print("has_api_followup", "api follow-up" in blob)
    print("has_deadline", "2026-09-05" in blob)

    if not isinstance(context, list) or "sarah" not in blob:
        raise SystemExit(
            "MCP context did not include the seeded Sarah / API follow-up task."
        )

    print("\n===== TEST: USER ISOLATION (MCP) =====")
    other = await retrieve_meeting_context(
        user_id=999999,
        query=DEMO_QUESTION,
        limit=5,
    )
    other_blob = json.dumps(other, default=str).lower()
    print("other_count", len(other) if isinstance(other, list) else type(other).__name__)
    print("other_has_sarah", "sarah" in other_blob)
    if "sarah" in other_blob:
        raise SystemExit(
            "MCP returned another user's task to user_id=999999."
        )


def verify_http(user_id: int) -> None:
    token = create_access_token(user_id)
    other_token = create_access_token(999999)

    questions = [
        DEMO_QUESTION,
        "What was the deadline for the API follow-up?",
        "What did we discuss in our previous meeting?",
        "What did we decide about the Mars office?",
    ]

    with TestClient(app) as client:
        print("\n===== TEST: POST /assistant/chat =====")
        for question in questions:
            print(f"\nQ: {question}")
            response = client.post(
                "/assistant/chat",
                json={"message": question},
                headers={"Authorization": f"Bearer {token}"},
            )
            print("status:", response.status_code)
            print("body:", response.text)
            if response.status_code != 200:
                raise SystemExit("Assistant chat request failed.")

        print("\n===== TEST: USER ISOLATION (HTTP) =====")
        response = client.post(
            "/assistant/chat",
            json={"message": DEMO_QUESTION},
            headers={"Authorization": f"Bearer {other_token}"},
        )
        print("status:", response.status_code)
        print("body:", response.text)
        if response.status_code == 200:
            reply = response.json().get("reply", "").lower()
            if "sarah" in reply:
                raise SystemExit(
                    "Assistant leaked Sarah from another user's MCP context."
                )


def main() -> None:
    seed(email=None)
    user_id = first_user_id()
    if "--http-only" not in sys.argv:
        asyncio.run(verify_mcp_protocol(user_id))
    verify_http(user_id)
    print("\n===== MCP ASSISTANT VERIFICATION COMPLETE =====")


if __name__ == "__main__":
    main()
