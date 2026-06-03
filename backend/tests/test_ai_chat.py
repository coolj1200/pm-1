import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.api.ai import AiChatRequest, ChatHistoryItem, ai_chat
from backend.api.kanban import BoardResponse
from backend.models import ConversationMessage


class FakeDB:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass


class DummyBoard:
    id = 1


def test_ai_chat_stores_user_and_assistant_messages(monkeypatch):
    monkeypatch.setattr(
        "backend.api.ai.get_or_create_user_and_board",
        lambda db, username: (None, DummyBoard()),
    )

    board_response = BoardResponse(id=1, name="My Board", description=None, columns=[])
    monkeypatch.setattr("backend.api.ai.board_to_response", lambda board, db: board_response)
    monkeypatch.setattr(
        "backend.api.ai.call_openrouter_structured",
        lambda board_state, user_message, history: {
            "response": "OK",
            "kanban_updates": [{"action": "create_card", "title": "New task"}],
        },
    )

    db = FakeDB()
    payload = AiChatRequest(
        message="Create a new task",
        history=[ChatHistoryItem(role="user", content="Please add a task")],
    )

    response = ai_chat(payload, current_user={"username": "user"}, db=db)

    assert response == {
        "response": "OK",
        "kanban_updates": [{"action": "create_card", "title": "New task"}],
    }
    assert len(db.added) == 2
    assert isinstance(db.added[0], ConversationMessage)
    assert isinstance(db.added[1], ConversationMessage)
    assert db.added[0].role == "user"
    assert db.added[1].role == "assistant"
