# AI Integration

This project uses OpenRouter to power backend AI connectivity.

## Configuration

- The OpenRouter API key is stored in `backend/.env` as:

```env
OPENROUTER_API_KEY=sk-...
```

- The backend loads this value with `python-dotenv` during startup.

## Endpoints

### POST /api/ai/test

A simple connectivity endpoint.

Request body:

```json
{
  "message": "What is 2+2?",
  "history": [
    {"role": "user", "content": "Hello"}
  ]
}
```

Response body:

```json
{
  "response": "4"
}
```

### POST /api/ai/chat

This endpoint sends the current user board state, a message, and an optional history list to OpenRouter.

Request body:

```json
{
  "message": "Create a new card in Backlog",
  "history": [
    {"role": "user", "content": "Please add a new task"}
  ]
}
```

Response body:

```json
{
  "response": "I created a new card for you.",
  "kanban_updates": [
    {
      "action": "create_card",
      "title": "New task",
      "column_id": 1
    }
  ]
}
```

## Behavior

- `POST /api/ai/chat` includes the current board state in the prompt.
- The backend stores both user messages and AI responses in the database via the `conversation_messages` table.
- The AI is instructed to return valid JSON only, with a top-level `response` field and optional `kanban_updates`.

## Error handling

- Missing or invalid API key returns `401`.
- OpenRouter network failures return `503`.
- Invalid or malformed AI responses return `502`.

## Model

- The backend uses `gpt-oss-120b(free)` for OpenRouter calls.
- The request uses `temperature: 0` for deterministic responses.
