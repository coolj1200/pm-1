# Frontend: Project Management Kanban MVP

## Overview

A React 19 + Next.js 16 + TypeScript frontend for a Project Management Kanban board. Features drag-and-drop card management across 5 fixed columns (Backlog, Discovery, In Progress, Review, Done) with the ability to rename columns, add/edit/delete cards, and display card details.

## Architecture

### Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css          # Global styles, Tailwind directives
│   │   ├── layout.tsx           # Root layout with meta tags
│   │   └── page.tsx             # Home page, renders KanbanBoard
│   ├── components/
│   │   ├── KanbanBoard.tsx       # Main board component (state management, drag-drop orchestration)
│   │   ├── KanbanColumn.tsx      # Column wrapper with rename + add card functionality
│   │   ├── KanbanCard.tsx        # Individual card with edit/delete actions
│   │   ├── KanbanCardPreview.tsx # Drag overlay preview for active card
│   │   ├── NewCardForm.tsx       # Modal form for adding new cards
│   │   ├── KanbanBoard.test.tsx  # Unit tests for KanbanBoard component
│   │   ├── KanbanCard.test.tsx   # (implied) Unit tests for KanbanCard
│   ├── lib/
│   │   ├── kanban.ts            # Core data structure, state logic (moveCard, createId, etc.)
│   │   └── kanban.test.ts       # Unit tests for kanban utilities
│   └── test/
│       ├── setup.ts             # Vitest configuration (JSDOM setup, mocks)
│       └── vitest.d.ts          # Type definitions for Vitest globals
├── tests/
│   └── kanban.spec.ts           # E2E tests (Playwright)
├── package.json                 # Dependencies, scripts
├── tsconfig.json                # TypeScript configuration
├── vitest.config.ts             # Vitest (unit test) configuration
├── playwright.config.ts         # Playwright (E2E test) configuration
├── postcss.config.mjs           # PostCSS configuration (Tailwind)
├── next.config.ts               # Next.js configuration
└── eslint.config.mjs            # ESLint configuration
```

## Key Components

### KanbanBoard (src/components/KanbanBoard.tsx)
- **Role**: Main component orchestrating the entire board
- **State**: `board` (BoardData with columns and cards), `activeCardId` (for drag overlay)
- **Key Props**: None (all state local)
- **Key Methods**:
  - `handleDragStart`: Sets active card for drag overlay
  - `handleDragEnd`: Calls moveCard utility and updates columns
  - `handleRenameColumn`: Updates column title
  - `handleAddCard`: Creates new card, appends to column
  - `handleDeleteCard`: Removes card from board and column
- **Styling**: Uses Tailwind CSS with custom gradient overlays
- **Dependencies**: dnd-kit (drag-drop), KanbanColumn, KanbanCardPreview

### KanbanColumn (src/components/KanbanColumn.tsx)
- **Role**: Renders a single column with cards and header
- **Props**: `column`, `cards` (lookup object), `isOver` (dnd-kit), handlers
- **Features**: 
  - Column title with rename button
  - "Add card" button
  - Droppable zone for cards
  - List of KanbanCard children

### KanbanCard (src/components/KanbanCard.tsx)
- **Role**: Renders a single card
- **Props**: `card`, `handlers` (delete, etc.)
- **Features**: 
  - Card title and details
  - Delete button
  - Draggable (dnd-kit)
  - Expandable/collapsible details

### KanbanCardPreview (src/components/KanbanCardPreview.tsx)
- **Role**: Visual feedback during drag
- **Props**: `card` or null
- **Purpose**: Shows a semi-transparent copy of the card being dragged

### NewCardForm (src/components/NewCardForm.tsx)
- **Role**: Modal form for creating new cards
- **Props**: `columnId`, `onSubmit`, `onCancel`
- **Features**: Input fields for title and details

## State & Data Model

### BoardData Type (src/lib/kanban.ts)
```typescript
type BoardData = {
  columns: Column[];
  cards: Record<string, Card>;
};

type Column = {
  id: string;
  title: string;
  cardIds: string[];
};

type Card = {
  id: string;
  title: string;
  details: string;
};
```

**Design**: Normalized structure with cards in a lookup table and columns referencing card IDs. This allows efficient updates and prevents duplication.

### Initial Data (src/lib/kanban.ts)
5 hardcoded columns (Backlog, Discovery, In Progress, Review, Done) with 8 sample cards distributed across them.

## Utilities (src/lib/kanban.ts)

- `initialData`: Sample board state
- `createId(prefix)`: Generates unique IDs with format `{prefix}-{timestamp}`
- `moveCard(columns, activeId, overId)`: Core drag-drop logic; moves card from one column to another
- Card/Column lookup helpers (implied)

## Testing Strategy

### Unit Tests (Vitest + React Testing Library)
- **Location**: `src/components/*.test.tsx`, `src/lib/*.test.ts`
- **Coverage**: Component rendering, user interactions (clicks, drag-drop), state updates, utility functions
- **Setup**: `src/test/setup.ts` configures JSDOM, mocks dnd-kit
- **Run**: `npm run test:unit` or `npm run test:unit:watch`

### E2E Tests (Playwright)
- **Location**: `tests/kanban.spec.ts`
- **Coverage**: Full user workflow (drag card, rename column, add/delete card in real browser)
- **Run**: `npm run test:e2e`

## Drag-and-Drop Implementation

Uses **@dnd-kit** (modern React drag-drop library):
- `DndContext`: Wraps the board and provides drag state
- `PointerSensor`: Activates drag when pointer moves 6px (prevents accidental drags)
- `DragOverlay`: Shows card preview while dragging
- `closestCorners`: Collision detection strategy
- `useSensor`, `useSensors`: Hooks to configure pointer behavior

## Styling

- **Framework**: Tailwind CSS 4 (utility-first)
- **Extras**: Gradient overlays for visual depth
- **Color Scheme** (from project AGENTS.md):
  - Accent Yellow: `#ecad0a`
  - Blue Primary: `#209dd7`
  - Purple Secondary: `#753991`
  - Dark Navy: `#032147`
  - Gray Text: `#888888`

## Scripts

- `npm run dev`: Start Next.js dev server (hot-reload on http://localhost:3000)
- `npm run build`: Build static Next.js site (.next/standalone)
- `npm run start`: Serve built site
- `npm run lint`: Run ESLint
- `npm run test:unit`: Run Vitest unit tests
- `npm run test:unit:watch`: Run Vitest in watch mode
- `npm run test:e2e`: Run Playwright E2E tests
- `npm run test:all`: Run all tests

## Dependencies

**Production**:
- `next@16.1.6`: React framework
- `react@19.2.3`, `react-dom@19.2.3`: UI library
- `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`: Drag-drop
- `clsx@2.1.1`: Conditional className utility
- `tailwindcss@4`: CSS framework

**Development**:
- `typescript@5`: Type safety
- `vitest@3.2.4`, `@vitest/coverage-v8`: Unit testing
- `@playwright/test@1.58.0`: E2E testing
- `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`: Testing utilities
- `eslint@9`, `eslint-config-next`: Linting
- `@tailwindcss/postcss@4`, `postcss`: CSS processing
- `jsdom@27.0.1`: DOM for tests

## Current Limitations (MVP)

- **No Backend**: Board state is local (in-memory), not persisted
- **No Authentication**: Anyone can view/edit the board
- **No AI Integration**: No LLM chat or Kanban automation
- **No Multi-user**: Single hardcoded board for all users
- **No Database**: No persistent storage

## Next Steps (Part 3+)

1. Backend (FastAPI) to persist board state
2. Authentication layer (login/logout)
3. Database schema and API routes
4. Connect frontend to backend API
5. AI chat sidebar with Kanban updates
