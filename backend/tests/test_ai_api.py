import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.api.ai import AiTestRequest, ai_test


def test_ai_test_endpoint_returns_default_prompt(monkeypatch):
    monkeypatch.setattr("backend.api.ai.call_openrouter", lambda prompt: "4")

    response = ai_test()

    assert response == {"response": "4"}


def test_ai_test_endpoint_accepts_message_body(monkeypatch):
    monkeypatch.setattr("backend.api.ai.call_openrouter", lambda prompt: prompt)

    response = ai_test(AiTestRequest(message="Hello AI"))

    assert response == {"response": "Hello AI"}
