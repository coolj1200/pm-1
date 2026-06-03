"""AI endpoints for chat and connectivity tests."""

import json
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel

from ..database import get_db
from ..models import ConversationMessage
from ..services.ai import call_openrouter, call_openrouter_structured
from .auth import get_current_user
from .kanban import board_to_response, get_or_create_user_and_board

router = APIRouter()


class ChatHistoryItem(BaseModel):
    role: str
    content: str

    model_config = {"extra": "ignore"}


class AiTestRequest(BaseModel):
    message: Optional[str] = "What is 2+2?"
    history: Optional[List[ChatHistoryItem]] = []


class AiTestResponse(BaseModel):
    response: str


class KanbanUpdate(BaseModel):
    action: str
    card_id: Optional[int] = None
    column_id: Optional[int] = None
    title: Optional[str] = None
    details: Optional[str] = None
    position: Optional[float] = None

    model_config = {"extra": "ignore"}


class AiChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatHistoryItem]] = []


class AiChatResponse(BaseModel):
    response: str
    kanban_updates: Optional[List[KanbanUpdate]] = None


@router.post("/api/ai/test", response_model=AiTestResponse)
def ai_test(payload: Optional[AiTestRequest] = Body(default=None)):
    if payload is None or not isinstance(payload, AiTestRequest):
        payload = AiTestRequest()

    prompt = payload.message or "What is 2+2?"
    if payload.history:
        history_text = "\n".join(
            f"{item.role}: {item.content}" for item in payload.history
        )
        prompt = f"{history_text}\n\nQuestion: {prompt}"

    ai_output = call_openrouter(prompt)
    return {"response": ai_output}


@router.post("/api/ai/chat", response_model=AiChatResponse)
def ai_chat(
    payload: AiChatRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Any = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    board_state = board_to_response(board, db).model_dump()

    history_data = [item.model_dump() for item in payload.history or []]
    structured_response = call_openrouter_structured(
        board_state=board_state,
        user_message=payload.message,
        history=history_data,
    )

    db.add(
        ConversationMessage(
            board_id=board.id,
            role="user",
            content=payload.message,
        )
    )
    db.add(
        ConversationMessage(
            board_id=board.id,
            role="assistant",
            content=json.dumps(structured_response),
        )
    )
    db.commit()

    return {
        "response": structured_response["response"],
        "kanban_updates": structured_response.get("kanban_updates"),
    }
