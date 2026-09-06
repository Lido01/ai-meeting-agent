from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.assistant_service import (
    AssistantError,
    answer_user_question,
)


router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"]
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user_id: int = Depends(get_current_user)
):
    """
    Answer a question using MCP-retrieved meeting and task context.

    The authenticated JWT user ID is passed to MCP.
    The frontend cannot supply a different user_id.
    """

    try:
        reply = await answer_user_question(
            user_id=current_user_id,
            message=payload.message.strip(),
        )
    except AssistantError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return ChatResponse(reply=reply)
