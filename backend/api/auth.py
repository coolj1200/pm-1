"""Authentication endpoints for the project management app."""

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel

router = APIRouter()

SESSIONS: dict[str, dict[str, str]] = {}
VALID_USER = "user"
VALID_PASSWORD = "password"


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user: Optional[str]


def get_current_user(session_token: Optional[str] = Cookie(None)) -> dict[str, str]:
    if not session_token or session_token not in SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return SESSIONS[session_token]


@router.get("/api/auth/session", response_model=UserResponse)
def get_session(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in SESSIONS:
        return {"user": None}
    return {"user": SESSIONS[session_token]["username"]}


@router.post("/api/auth/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response):
    if payload.username != VALID_USER or payload.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = str(uuid4())
    SESSIONS[token] = {"username": payload.username}
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        path="/",
        samesite="lax",
    )
    return {"user": payload.username}


@router.post("/api/auth/logout", response_model=UserResponse)
def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token and session_token in SESSIONS:
        del SESSIONS[session_token]

    response.delete_cookie("session_token", path="/")
    return {"user": None}
