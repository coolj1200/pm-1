import json
import os
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from fastapi import HTTPException

from backend.services.ai import call_openrouter, call_openrouter_structured, parse_json_body


class DummyUrlopenResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_call_openrouter_raises_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(HTTPException) as exc_info:
        call_openrouter("What is 2+2?")

    assert exc_info.value.status_code == 401
    assert "not configured" in exc_info.value.detail.lower()


def test_call_openrouter_parses_openrouter_response(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    response_payload = {"choices": [{"message": {"content": "4"}}]}
    fake_response = DummyUrlopenResponse(json.dumps(response_payload).encode("utf-8"))
    monkeypatch.setattr(
        "backend.services.ai.urllib.request.urlopen",
        lambda request, timeout: fake_response,
    )

    result = call_openrouter("What is 2+2?")

    assert result == "4"


def test_parse_json_body_extracts_json_from_text():
    text = 'Answer: {"response": "4", "kanban_updates": []}'
    result = parse_json_body(text)

    assert result == {"response": "4", "kanban_updates": []}


def test_call_openrouter_structured_parses_json(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    response_text = 'Here is your JSON:\n{"response": "OK", "kanban_updates": [{"action": "create_card", "title": "New task"}]}'
    fake_response = DummyUrlopenResponse(response_text.encode("utf-8"))
    monkeypatch.setattr(
        "backend.services.ai.urllib.request.urlopen",
        lambda request, timeout: fake_response,
    )

    board_state = {"id": 1, "name": "My Board", "columns": []}
    result = call_openrouter_structured(board_state, "Create a card", [])

    assert result == {
        "response": "OK",
        "kanban_updates": [{"action": "create_card", "title": "New task"}],
    }
