"""OpenRouter AI service integration."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv(Path(__file__).parent.parent / ".env")

OPENROUTER_API_URL = "https://openrouter.ai/v1/chat/completions"
OPENROUTER_MODEL = "gpt-oss-120b(free)"
OPENROUTER_TIMEOUT_SECONDS = 10


def get_openrouter_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenRouter API key is not configured",
        )
    return api_key


def parse_json_body(raw_text: str) -> dict:
    start = raw_text.find("{")
    if start == -1:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter response did not contain JSON",
        )

    depth = 0
    in_string = False
    escape = False
    for index, char in enumerate(raw_text[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = raw_text[start : index + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    break

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="OpenRouter response did not contain a valid JSON object",
    )


def call_openrouter(prompt: str) -> str:
    api_key = get_openrouter_api_key()
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    request_body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_API_URL,
        data=request_body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=OPENROUTER_TIMEOUT_SECONDS) as response:
            raw_response = response.read().decode("utf-8")
            data = json.loads(raw_response)
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OpenRouter API key is invalid",
            )
        if 500 <= exc.code < 600:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenRouter service returned an error",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenRouter request failed with status {exc.code}",
        )
    except urllib.error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenRouter network error: {exc.reason}",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter returned invalid JSON",
        )

    choices = data.get("choices")
    if not choices or not isinstance(choices, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter returned unexpected response format",
        )

    first_choice = choices[0]
    message = first_choice.get("message") or {}
    content = message.get("content")
    if not content or not isinstance(content, str):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter response did not include a valid message",
        )

    return content.strip()


def call_openrouter_structured(board_state: dict, user_message: str, history: list[dict]) -> dict:
    api_key = get_openrouter_api_key()
    system_instructions = (
        "You are a Kanban board assistant. "
        "Receive the current board state, prior messages, and the user's current question. "
        "Return only valid JSON with these keys:"
        " 'response' (string), and optional 'kanban_updates' (array). "
        "Do not include any markdown, explanations, or text outside the JSON object."
    )
    user_payload = {
        "board_state": board_state,
        "history": history,
        "question": user_message,
        "instructions": (
            "Produce a JSON object with the exact keys 'response' and optional 'kanban_updates'. "
            "The 'kanban_updates' array should contain zero or more update objects with fields like 'action', 'card_id', 'column_id', 'title', 'details', and 'position'."
        ),
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        "temperature": 0,
    }
    request_body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_API_URL,
        data=request_body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=OPENROUTER_TIMEOUT_SECONDS) as response:
            raw_response = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OpenRouter API key is invalid",
            )
        if 500 <= exc.code < 600:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenRouter service returned an error",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenRouter request failed with status {exc.code}",
        )
    except urllib.error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenRouter network error: {exc.reason}",
        )

    parsed = parse_json_body(raw_response)
    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter returned a non-object response",
        )

    if "response" not in parsed or not isinstance(parsed["response"], str):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter structured response must include a string 'response' field",
        )

    return parsed
