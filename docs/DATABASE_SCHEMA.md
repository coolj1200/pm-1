# Database Schema

This project uses SQLite for local persistence. The schema supports:
- multiple users
- one or more boards per user
- multiple columns per board
- multiple cards per column

## Tables

### users
- `id` integer primary key
- `username` unique text, not null
- `password_hash` text, not null
- `is_active` boolean, not null, default true
- `created_at` datetime, not null

### boards
- `id` integer primary key
- `user_id` integer not null, foreign key to `users.id`
- `name` text, not null
- `description` text, nullable
- `created_at` datetime, not null
- `updated_at` datetime, not null

Indexes
- `user_id` is indexed for fast user-specific board queries

### columns
- `id` integer primary key
- `board_id` integer not null, foreign key to `boards.id`
- `title` text, not null
- `position` float, not null, default 0.0
- `created_at` datetime, not null
- `updated_at` datetime, not null

Indexes
- `board_id` is indexed for fast column loading by board

### cards
- `id` integer primary key
- `board_id` integer not null, foreign key to `boards.id`
- `column_id` integer not null, foreign key to `columns.id`
- `title` text, not null
- `details` text, nullable
- `position` float, not null, default 0.0
- `created_at` datetime, not null
- `updated_at` datetime, not null

Indexes
- `board_id` and `column_id` are indexed for fast card queries and card movement.

## SQL sample

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL
);

CREATE TABLE boards (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE columns (
  id INTEGER PRIMARY KEY,
  board_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  position REAL NOT NULL DEFAULT 0.0,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  FOREIGN KEY(board_id) REFERENCES boards(id)
);

CREATE TABLE cards (
  id INTEGER PRIMARY KEY,
  board_id INTEGER NOT NULL,
  column_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  details TEXT,
  position REAL NOT NULL DEFAULT 0.0,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  FOREIGN KEY(board_id) REFERENCES boards(id),
  FOREIGN KEY(column_id) REFERENCES columns(id)
);
```

## Sample JSON response

```json
{
  "board": {
    "id": 1,
    "name": "Product Roadmap",
    "description": "Main planning board",
    "columns": [
      {
        "id": 10,
        "title": "Backlog",
        "position": 0,
        "cards": [
          {
            "id": 101,
            "title": "User research",
            "details": "Collect customer interview notes.",
            "position": 0
          }
        ]
      },
      {
        "id": 11,
        "title": "In Progress",
        "position": 1,
        "cards": []
      }
    ]
  }
}
```

## Notes

- `position` is a lightweight ordering field to preserve column and card order.
- `board_id` is stored on cards for faster board-scoped card queries and to validate relationships.
