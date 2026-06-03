"""Kanban board API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Board, Card, Column, User
from .auth import get_current_user

router = APIRouter()


class CardRequest(BaseModel):
    column_id: int
    title: str
    details: Optional[str] = None


class UpdateCardRequest(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None


class MoveCardRequest(BaseModel):
    column_id: int
    position: Optional[float] = None


class ColumnRequest(BaseModel):
    title: str


class CardResponse(BaseModel):
    id: int
    title: str
    details: Optional[str]
    position: float


class ColumnResponse(BaseModel):
    id: int
    title: str
    position: float
    cards: list[CardResponse]


class BoardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    columns: list[ColumnResponse]


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.scalar(select(User).where(User.username == username))


def get_or_create_user_and_board(db: Session, username: str) -> tuple[User, Board]:
    user = get_user_by_username(db, username)
    if user is None:
        user = User(username=username, password_hash="password", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    board = db.scalar(select(Board).where(Board.user_id == user.id))
    if board is None:
        board = Board(user_id=user.id, name="My Board")
        db.add(board)
        db.commit()
        db.refresh(board)

        default_titles = ["Backlog", "Discovery", "In Progress", "Review", "Done"]
        for position, title in enumerate(default_titles):
            column = Column(board_id=board.id, title=title, position=float(position))
            db.add(column)

        db.commit()
        db.refresh(board)

    return user, board


def board_to_response(board: Board, db: Session) -> BoardResponse:
    columns = db.scalars(
        select(Column).where(Column.board_id == board.id).order_by(Column.position)
    ).all()

    column_responses: list[ColumnResponse] = []
    for column in columns:
        cards = db.scalars(
            select(Card).where(Card.column_id == column.id).order_by(Card.position)
        ).all()
        card_responses = [
            CardResponse(
                id=card.id,
                title=card.title,
                details=card.details,
                position=card.position,
            )
            for card in cards
        ]
        column_responses.append(
            ColumnResponse(
                id=column.id,
                title=column.title,
                position=column.position,
                cards=card_responses,
            )
        )

    return BoardResponse(
        id=board.id,
        name=board.name,
        description=board.description,
        columns=column_responses,
    )


def validate_board_column(board: Board, column_id: int, db: Session) -> Column:
    column = db.scalar(select(Column).where(Column.id == column_id, Column.board_id == board.id))
    if column is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column not found for this board",
        )
    return column


def validate_board_card(board: Board, card_id: int, db: Session) -> Card:
    card = db.scalar(select(Card).where(Card.id == card_id, Card.board_id == board.id))
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found for this board",
        )
    return card


@router.get("/api/kanban", response_model=BoardResponse)
def read_board(
    current_user: dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    return board_to_response(board, db)


@router.post("/api/kanban/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(
    payload: CardRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    column = validate_board_column(board, payload.column_id, db)

    max_position = db.scalar(
        select(func.max(Card.position)).where(Card.column_id == column.id)
    )
    position = float(max_position or 0.0) + 1.0

    card = Card(
        board_id=board.id,
        column_id=column.id,
        title=payload.title,
        details=payload.details,
        position=position,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return CardResponse(
        id=card.id,
        title=card.title,
        details=card.details,
        position=card.position,
    )


@router.put("/api/kanban/cards/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    payload: UpdateCardRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    card = validate_board_card(board, card_id, db)

    if payload.title is not None:
        card.title = payload.title
    if payload.details is not None:
        card.details = payload.details

    db.add(card)
    db.commit()
    db.refresh(card)
    return CardResponse(
        id=card.id,
        title=card.title,
        details=card.details,
        position=card.position,
    )


@router.delete("/api/kanban/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    card = validate_board_card(board, card_id, db)
    db.delete(card)
    db.commit()


@router.put("/api/kanban/columns/{column_id}", response_model=ColumnResponse)
def rename_column(
    column_id: int,
    payload: ColumnRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    column = validate_board_column(board, column_id, db)
    column.title = payload.title
    db.add(column)
    db.commit()
    db.refresh(column)

    cards = db.scalars(
        select(Card).where(Card.column_id == column.id).order_by(Card.position)
    ).all()
    return ColumnResponse(
        id=column.id,
        title=column.title,
        position=column.position,
        cards=[
            CardResponse(
                id=card.id,
                title=card.title,
                details=card.details,
                position=card.position,
            )
            for card in cards
        ],
    )


@router.put("/api/kanban/cards/{card_id}/move", response_model=CardResponse)
def move_card(
    card_id: int,
    payload: MoveCardRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, board = get_or_create_user_and_board(db, current_user["username"])
    card = validate_board_card(board, card_id, db)
    target_column = validate_board_column(board, payload.column_id, db)

    card.column_id = target_column.id
    card.position = payload.position if payload.position is not None else float(
        db.scalar(select(func.max(Card.position)).where(Card.column_id == target_column.id)) or 0.0
    ) + 1.0
    db.add(card)
    db.commit()
    db.refresh(card)

    return CardResponse(
        id=card.id,
        title=card.title,
        details=card.details,
        position=card.position,
    )
