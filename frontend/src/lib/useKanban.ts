import { useCallback, useEffect, useState } from "react";
import { createId, moveCard as moveCardLocal, type BoardData, type Card, type Column } from "./kanban";
import type { KanbanUpdate } from "./useAIChat";

type ApiCard = {
  id: number;
  title: string;
  details: string;
  position: number;
};

type ApiColumn = {
  id: number;
  title: string;
  position: number;
  cards: ApiCard[];
};

type ApiBoard = {
  id: number;
  name: string;
  description?: string | null;
  columns: ApiColumn[];
};

const toCardId = (id: number) => String(id);

const mapBoard = (payload: ApiBoard): BoardData => {
  const cards: Record<string, Card> = {};
  const columns = payload.columns.map((column) => {
    const cardIds = column.cards.map((card) => {
      const cardId = toCardId(card.id);
      cards[cardId] = {
        id: cardId,
        title: card.title,
        details: card.details ?? "",
      };
      return cardId;
    });

    return {
      id: toCardId(column.id),
      title: column.title,
      cardIds,
    };
  });

  return { columns, cards };
};

const getColumnId = (columns: Column[], itemId: string) => {
  if (columns.some((column) => column.id === itemId)) {
    return itemId;
  }

  return columns.find((column) => column.cardIds.includes(itemId))?.id ?? null;
};

const getMovePosition = (columns: Column[], activeId: string, overId: string) => {
  const targetColumnId = getColumnId(columns, overId);
  if (!targetColumnId) {
    return null;
  }

  const targetColumn = columns.find((column) => column.id === targetColumnId);
  if (!targetColumn) {
    return null;
  }

  if (!targetColumn.cardIds.includes(overId)) {
    return null;
  }

  const overIndex = targetColumn.cardIds.indexOf(overId);
  return overIndex + 0.5;
};

const fetchJson = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `${response.status} ${response.statusText}`);
  }

  return response.json();
};

const applyKanbanUpdatesToBoard = (board: BoardData, updates: KanbanUpdate[]) => {
  const nextBoard: BoardData = {
    cards: { ...board.cards },
    columns: board.columns.map((column) => ({ ...column, cardIds: [...column.cardIds] })),
  };

  const findColumn = (columnId?: number | string) => {
    if (columnId === undefined || columnId === null) {
      return null;
    }
    const id = String(columnId);
    return nextBoard.columns.find((column) => column.id === id) ?? null;
  };

  const findCardId = (cardId?: number | string) => {
    if (cardId === undefined || cardId === null) {
      return null;
    }
    return String(cardId);
  };

  const removeCardFromColumns = (cardId: string) => {
    nextBoard.columns = nextBoard.columns.map((column) => ({
      ...column,
      cardIds: column.cardIds.filter((id) => id !== cardId),
    }));
  };

  updates.forEach((update) => {
    const cardId = findCardId(update.card_id);
    const columnId = update.column_id !== undefined ? String(update.column_id) : undefined;

    switch (update.action) {
      case "create_card": {
        if (!columnId || !update.title) {
          return;
        }

        const targetColumn = findColumn(columnId);
        if (!targetColumn) {
          return;
        }

        const newId = createId("ai-card");
        nextBoard.cards[newId] = {
          id: newId,
          title: update.title,
          details: update.details ?? "",
        };
        targetColumn.cardIds = [...targetColumn.cardIds, newId];
        return;
      }

      case "rename_column": {
        if (!columnId || !update.title) {
          return;
        }

        const targetColumn = findColumn(columnId);
        if (!targetColumn) {
          return;
        }

        targetColumn.title = update.title;
        return;
      }

      case "move_card": {
        if (!cardId || !columnId) {
          return;
        }

        const targetColumn = findColumn(columnId);
        if (!targetColumn) {
          return;
        }

        if (!nextBoard.cards[cardId]) {
          return;
        }

        removeCardFromColumns(cardId);

        const position = Number.isFinite(update.position)
          ? Math.max(0, Math.min(targetColumn.cardIds.length, Math.round(update.position!)))
          : targetColumn.cardIds.length;

        targetColumn.cardIds = [
          ...targetColumn.cardIds.slice(0, position),
          cardId,
          ...targetColumn.cardIds.slice(position),
        ];
        return;
      }

      case "update_card": {
        if (!cardId || !nextBoard.cards[cardId]) {
          return;
        }

        const card = nextBoard.cards[cardId];
        if (update.title) {
          card.title = update.title;
        }
        if (update.details) {
          card.details = update.details;
        }
        return;
      }

      case "delete_card": {
        if (!cardId || !nextBoard.cards[cardId]) {
          return;
        }

        delete nextBoard.cards[cardId];
        removeCardFromColumns(cardId);
        return;
      }

      default:
        return;
    }
  });

  return nextBoard;
};

export const useKanban = () => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshBoard = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const payload = await fetchJson<ApiBoard>("/api/kanban");
      setBoard(mapBoard(payload));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load board");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshBoard();
  }, [refreshBoard]);

  const renameColumn = useCallback(
    async (columnId: string, title: string) => {
      if (!board) {
        return;
      }

      setError(null);
      const previousBoard = board;
      setBoard((current) =>
        current
          ? {
              ...current,
              columns: current.columns.map((column) =>
                column.id === columnId ? { ...column, title } : column
              ),
            }
          : current
      );

      try {
        await fetchJson<ApiColumn>(`/api/kanban/columns/${columnId}`, {
          method: "PUT",
          body: JSON.stringify({ title }),
        });
      } catch (err) {
        setBoard(previousBoard);
        setError(err instanceof Error ? err.message : "Unable to rename column");
      }
    },
    [board]
  );

  const addCard = useCallback(
    async (columnId: string, title: string, details: string) => {
      if (!board) {
        return;
      }

      setError(null);
      const previousBoard = board;
      const tempId = createId("temp-card");
      const tempCard: Card = { id: tempId, title, details };

      setBoard((current) =>
        current
          ? {
              ...current,
              cards: { ...current.cards, [tempId]: tempCard },
              columns: current.columns.map((column) =>
                column.id === columnId
                  ? { ...column, cardIds: [...column.cardIds, tempId] }
                  : column
              ),
            }
          : current
      );

      try {
        const card = await fetchJson<ApiCard>("/api/kanban/cards", {
          method: "POST",
          body: JSON.stringify({ column_id: Number(columnId), title, details }),
        });

        const actualId = toCardId(card.id);
        setBoard((current) => {
          if (!current) {
            return current;
          }

          const updatedCards = { ...current.cards };
          delete updatedCards[tempId];
          updatedCards[actualId] = {
            id: actualId,
            title: card.title,
            details: card.details ?? "",
          };

          return {
            ...current,
            cards: updatedCards,
            columns: current.columns.map((column) => ({
              ...column,
              cardIds: column.cardIds.map((id) => (id === tempId ? actualId : id)),
            })),
          };
        });
      } catch (err) {
        setBoard(previousBoard);
        setError(err instanceof Error ? err.message : "Unable to add card");
      }
    },
    [board]
  );

  const deleteCard = useCallback(
    async (cardId: string) => {
      if (!board) {
        return;
      }

      setError(null);
      const previousBoard = board;
      setBoard((current) =>
        current
          ? {
              ...current,
              cards: Object.fromEntries(
                Object.entries(current.cards).filter(([id]) => id !== cardId)
              ),
              columns: current.columns.map((column) => ({
                ...column,
                cardIds: column.cardIds.filter((id) => id !== cardId),
              })),
            }
          : current
      );

      try {
        await fetchJson<void>(`/api/kanban/cards/${cardId}`, {
          method: "DELETE",
        });
      } catch (err) {
        setBoard(previousBoard);
        setError(err instanceof Error ? err.message : "Unable to delete card");
      }
    },
    [board]
  );

  const moveCard = useCallback(
    async (activeId: string, overId: string) => {
      if (!board) {
        return;
      }

      setError(null);
      const previousBoard = board;
      const nextBoard = {
        ...board,
        columns: moveCardLocal(board.columns, activeId, overId),
      };
      setBoard(nextBoard);

      try {
        const targetColumnId = getColumnId(board.columns, overId);
        if (!targetColumnId) {
          throw new Error("Invalid column or card target");
        }

        const position = getMovePosition(board.columns, activeId, overId);
        await fetchJson<ApiCard>(`/api/kanban/cards/${activeId}/move`, {
          method: "PUT",
          body: JSON.stringify({
            column_id: Number(targetColumnId),
            position,
          }),
        });
      } catch (err) {
        setBoard(previousBoard);
        setError(err instanceof Error ? err.message : "Unable to move card");
      }
    },
    [board]
  );

  const applyKanbanUpdates = useCallback(
    (updates: KanbanUpdate[] | undefined) => {
      if (!updates?.length || !board) {
        return;
      }

      setBoard((current) => {
        if (!current) {
          return current;
        }
        return applyKanbanUpdatesToBoard(current, updates);
      });
    },
    [board]
  );

  return {
    board,
    loading,
    error,
    refreshBoard,
    renameColumn,
    addCard,
    deleteCard,
    moveCard,
    applyKanbanUpdates,
  };
};
