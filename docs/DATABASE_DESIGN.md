# Database Design

This design focuses on a simple, normalized schema that supports the Kanban app and future growth.

## Goals

- Keep the schema easy to understand and maintain.
- Support multiple users with separate boards.
- Keep board state persistent and queryable.
- Make card and column ordering explicit and stable.
- Use SQLite for local development and simple deployment.

## Design decisions

### User model
A separate `users` table allows the app to support multiple sign-ins later.

- `username` is unique.
- `password_hash` is stored so credentials can be validated securely.
- `is_active` supports future account soft-deactivation.

### Board model
The `boards` table links a board to a user and stores board metadata.

- One user can own many boards.
- Board metadata includes `name` and `description`.
- `created_at` and `updated_at` support future audit and sync behavior.

### Column model
Columns live under boards and are ordered by `position`.

- `board_id` ensures each column belongs to a board.
- `position` is a floating-point field to allow reordering without renumbering every row.

### Card model
Cards belong to both a board and a column.

- `column_id` defines the current column.
- `board_id` makes it easier to query cards for an entire board.
- `position` preserves order within a column.
- `details` stores optional card text.

## Normalization and integrity

- The schema is normalized to 3NF: each table has a single responsibility.
- Foreign keys maintain referential integrity.
- Cascade deletes keep the board hierarchy consistent when a user, board, or column is removed.

## Migration strategy

For the MVP, `backend/database.py` uses SQLAlchemy `Base.metadata.create_all(engine)`.

- This is sufficient for local development and initial deployment.
- If schema changes are needed later, Alembic can be introduced for managed migrations.

## Storage location

The SQLite database is stored at `backend/database.db`.

- The file is created automatically on startup if it does not exist.
- This keeps persistence local, simple, and easy to inspect.

## Future extensions

- Add a `BoardPermission` table if shared boards are required.
- Add a `ConversationMessage` table for AI chat history.
- Add a `tags` table for card labels and filtering.
- Add `priority` or `due_date` fields to cards for richer workflows.
