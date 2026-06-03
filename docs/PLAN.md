# Project Execution Plan

## Guiding testing policy
- Aim for meaningful coverage; do not add tests only to hit an exact threshold.
- Target ~80% coverage where it is sensible and valuable, but prioritize high-quality tests over raw numbers.
- If a part is already well-tested and additional tests would add low value, keep coverage lower.

## Part 1: Planning & Frontend Documentation

### Objective
Understand the existing frontend codebase, create a detailed execution plan with checklists and success criteria for all subsequent parts, and get user approval before proceeding.

### Substeps
- [x] Review existing frontend code structure and components
- [x] Document frontend architecture in frontend/AGENTS.md
- [ ] Create detailed substeps for Parts 2-10 with checklists
- [ ] Define tests and success criteria for each part
- [ ] Present plan to user for review and approval

### Tests & Success Criteria
- **Success**: frontend/AGENTS.md created and describes current components, state management, and testing setup
- **Success**: Enriched PLAN.md includes detailed substeps, checkboxes, and success criteria for all 10 parts
- **Success**: User reviews and approves the plan before proceeding

---

## Part 2: Docker & Backend Scaffolding ✅

### Objective
Set up Docker infrastructure, create a basic FastAPI backend, and verify "hello world" example works with both static HTML and API calls.

### Substeps
- [x] Create Dockerfile in project root with Python 3.12, uv package manager
- [x] Create backend/main.py with FastAPI app
- [x] Create backend/requirements.txt with FastAPI, uvicorn, sqlalchemy, python-dotenv, openai
- [x] Create backend/.env template (with OPENROUTER_API_KEY placeholder)
- [x] Create docker-compose.yml to build and run the container
- [x] Write scripts/start.sh and scripts/stop.sh for Mac/Linux/PC
- [x] Create backend/api/health.py endpoint returning {"status": "ok"}
- [x] Serve static HTML hello world at GET /
- [x] Verify API call from static HTML to /api/health works (fetch + display response)
- [x] Add comprehensive comments to scripts explaining usage

### Tests & Success Criteria
- ✅ **Success**: Docker image builds without errors
- ✅ **Success**: Container starts and serves static HTML at http://localhost:8000
- ✅ **Success**: curl http://localhost:8000/ returns HTML
- ✅ **Success**: curl http://localhost:8000/api/health returns {"status": "ok"}
- ✅ **Success**: Browser can call /api/health from static HTML and display response (static page includes JS test)
- ✅ **Success**: start.sh and stop.sh scripts work on macOS (PC/Linux skipped as per requirements)

---

## Part 3: Serve Built Frontend

### Objective
Build the Next.js frontend and serve it from FastAPI, so the Kanban board displays at /.

### Substeps
- [x] Update Docker build to run `cd frontend && npm install && npm run build`
- [x] Copy frontend build output to a backend-accessible location
- [x] Configure FastAPI to serve Next.js static files and handle client-side routing
- [x] Test that GET / renders the Kanban board (no login yet)
- [x] Run frontend unit tests: npm run test:unit passes
- [x] Run frontend E2E tests: npm run test:e2e passes
- [ ] Add backend unit test structure (pytest with fixtures)
- [ ] Create backend integration test for static file serving

### Tests & Success Criteria
- **Success**: npm run test:unit passes (frontend/src/lib/kanban.test.ts, components tests)
- **Success**: npm run test:e2e passes (basic Kanban board E2E test)
- **Success**: GET http://localhost:8000/ returns full Kanban board HTML
- **Success**: Kanban board renders in browser with 5 columns and sample cards
- **Success**: Drag-and-drop works in browser
- **Success**: Backend can handle 10+ concurrent requests without errors
- **Success**: Backend unit tests exist and pass (pytest)

---

## Part 4: Authentication Layer

### Objective
Add login/logout flow so users must authenticate with hardcoded credentials ("user" / "password") to see the Kanban.

### Substeps
- [x] Create frontend component: LoginForm.tsx with email/password fields
- [x] Create frontend authentication context (AuthProvider) to manage session state
- [x] Add GET /api/auth/session endpoint to check if user is logged in
- [x] Add POST /api/auth/login endpoint accepting {username, password} → {token, user}
- [x] Add POST /api/auth/logout endpoint clearing session
- [x] Implement middleware to protect /api/kanban routes (check session)
- [x] Update frontend page.tsx to show login or Kanban based on auth state
- [x] Add logout button to Kanban header
- [ ] Create LoginForm.test.tsx unit tests
- [ ] Create E2E tests for login/logout flow
- [ ] Add backend unit tests for auth endpoints

### Tests & Success Criteria
- **Success**: npm run test:unit passes (LoginForm tests, auth context tests)
- **Success**: npm run test:e2e passes (login, see Kanban, logout, redirect to login)
- **Success**: curl without session → 401 Unauthorized on /api/kanban
- **Success**: POST /api/auth/login with "user"/"password" → returns token
- **Success**: POST /api/auth/login with wrong credentials → 401
- **Success**: Logout clears session and redirects to login page
- **Success**: Session persists across page reloads
- **Success**: Backend auth tests pass (pytest)

---

## Part 5: Database Schema Design

### Objective
Propose and document a database schema for the Kanban system, supporting users, boards, columns, and cards.

### Substeps
- [ ] Design SQLAlchemy ORM models: User, Board, Column, Card
- [ ] Define relationships: User → Board → Columns → Cards
- [x] Plan migration strategy (Alembic or simple schema creation)
- [x] Create docs/DATABASE_SCHEMA.md documenting the schema
- [x] Create docs/DATABASE_DESIGN.md explaining design decisions (normalization, indexing, etc.)
- [x] Include sample SQL schema in docs
- [x] Include sample JSON structure for API responses
- [x] Present schema and design to user for approval

### Tests & Success Criteria
- **Success**: docs/DATABASE_SCHEMA.md exists and describes all tables/fields
- **Success**: docs/DATABASE_DESIGN.md explains why this schema was chosen
- **Success**: Schema supports multiple users with separate boards
- **Success**: Schema supports multiple columns per board
- **Success**: Schema supports multiple cards per column
- **Success**: User approves schema design

---

## Part 6: Backend Kanban API

### Objective
Implement backend API routes to read and persist Kanban board state, using SQLite database that auto-creates on startup.

### Substeps
- [x] Create backend/models.py with SQLAlchemy ORM models (User, Board, Column, Card)
- [x] Create backend/database.py with SQLite initialization and session management
- [x] Create backend/database.py to auto-create database if missing
- [x] Create backend/api/kanban.py with routes:
  - GET /api/kanban → fetch user's board with all columns and cards
  - POST /api/kanban/cards → create new card
  - PUT /api/kanban/cards/{id} → update card title/details
  - DELETE /api/kanban/cards/{id} → delete card
  - PUT /api/kanban/columns/{id} → rename column
  - PUT /api/kanban/cards/{id}/move → move card to different column
- [x] Add comprehensive input validation and error handling
- [ ] Add backend unit tests for all routes (pytest with fixtures, mocked database)
- [x] Add integration tests against real SQLite (test DB file)
- [x] Ensure database file is created at startup if missing
- [ ] Add logging for database operations

### Tests & Success Criteria
- **Success**: Backend unit tests pass (target around 80% coverage only when sensible)
- **Success**: Integration tests pass (test database CRUD operations)
- **Success**: GET /api/kanban returns board JSON with correct structure
- **Success**: POST /api/kanban/cards creates card and returns 201
- **Success**: PUT /api/kanban/cards/{id} updates card and returns 200
- **Success**: DELETE /api/kanban/cards/{id} deletes card and returns 204
- **Success**: Invalid input returns 400 Bad Request with error message
- **Success**: Unauthorized user (no session) returns 401
- **Success**: SQLite database auto-creates on startup
- **Success**: All API responses include appropriate error messages

---

## Part 7: Frontend ↔ Backend Integration

### Objective
Have the frontend use the backend API so the Kanban board is persistent across sessions.

### Substeps
- [x] Update KanbanBoard.tsx to fetch board on mount: GET /api/kanban
- [x] Update KanbanBoard.tsx handleDragEnd to call backend: PUT /api/kanban/cards/{id}/move
- [x] Update KanbanBoard.tsx handleAddCard to call backend: POST /api/kanban/cards
- [x] Update KanbanBoard.tsx handleDeleteCard to call backend: DELETE /api/kanban/cards/{id}
- [x] Update KanbanBoard.tsx handleRenameColumn to call backend: PUT /api/kanban/columns/{id}
- [x] Add loading/error states in UI for all API calls
- [x] Add optimistic updates (show change immediately, rollback on error)
- [x] Create useKanban.ts hook to encapsulate API logic
- [ ] Add comprehensive error handling and user feedback
- [ ] Create unit tests for useKanban hook (mocked fetch)
- [ ] Create E2E tests for full flow (login → add card → verify persists on reload)
- [ ] Create backend integration tests verifying data persistence

### Tests & Success Criteria
- **Success**: npm run test:unit passes (useKanban hook, component tests)
- **Success**: npm run test:e2e passes (login → add card → reload page → card persists)
- **Success**: npm run test:e2e passes (drag card → reload page → card position persists)
- **Success**: DELETE card removes from UI and database
- **Success**: Rename column persists across reload
- **Success**: Create new card increments card count in database
- **Success**: UI shows loading state during API calls
- **Success**: UI shows error message if API call fails (with retry button)
- **Success**: Optimistic updates work (card moves immediately, reverts if error)
- **Success**: Multiple users see their own separate boards
- **Success**: Backend integration tests pass

---

## Part 8: AI Connectivity

### Objective
Verify the backend can successfully call OpenRouter API with a simple "2+2" test.

### Substeps
- [ ] Ensure OPENROUTER_API_KEY is set in .env
- [ ] Create backend/services/ai.py with OpenRouter client initialization
- [ ] Create POST /api/ai/test endpoint that sends "What is 2+2?" to AI
- [ ] Parse response and return to frontend
- [ ] Add error handling (invalid API key, network timeout, etc.)
- [ ] Create backend unit test mocking OpenRouter API call
- [ ] Create backend integration test against real OpenRouter API (marked as @pytest.mark.slow)
- [ ] Log AI requests and responses for debugging
- [ ] Document OpenRouter integration in docs/AI_INTEGRATION.md

### Tests & Success Criteria
- **Success**: POST /api/ai/test returns {"response": "4"} (or similar)
- **Success**: Backend unit tests pass (mocked OpenRouter)
- **Success**: Integration test passes (calls real OpenRouter, checks for "4" in response)
- **Success**: Invalid API key returns 401 with clear error message
- **Success**: Network timeout returns 503 with retry guidance
- **Success**: Response time < 10 seconds for simple queries
- **Success**: docs/AI_INTEGRATION.md explains setup and costs

---

## Part 9: AI with Kanban Context & Structured Outputs

### Objective
Extend backend to always call AI with Kanban board context + user question + conversation history. AI responds with structured outputs (response text + optional Kanban updates).

### Substeps
- [ ] Create AI response schema with pydantic: {response: str, kanban_updates?: [...]}
- [ ] Extend POST /api/ai/test to accept message and history parameters
- [ ] Create POST /api/ai/chat endpoint accepting {message, history}
- [ ] Fetch current board state and include in AI prompt
- [ ] Pass Kanban JSON + message + history to OpenRouter with structured outputs
- [ ] Parse structured response and return to frontend
- [ ] Create database schema for conversation history (ConversationMessage table)
- [ ] Store each message and AI response in database
- [ ] Create backend unit tests for AI response parsing
- [ ] Create backend unit tests for Kanban update validation (AI shouldn't corrupt board)
- [ ] Create integration tests for full flow
- [ ] Add logging of full AI interactions for debugging

### Tests & Success Criteria
- **Success**: POST /api/ai/chat returns {response: string, kanban_updates: [...]}
- **Success**: AI response references correct board context (column/card names)
- **Success**: Kanban updates from AI are validated (can't create invalid updates)
- **Success**: Conversation history persists in database
- **Success**: Backend rejects invalid kanban_updates with 400 error
- **Success**: AI refuses certain dangerous updates with explanation
- **Success**: Unit tests pass (target around 80% coverage of AI logic only when sensible)
- **Success**: Integration tests pass (end-to-end AI + board interaction)
- **Success**: Response time < 20 seconds for typical AI queries

---

## Part 10: AI Chat Sidebar UI

### Objective
Add a beautiful sidebar AI chat widget to the UI, allowing the LLM to update the Kanban in real-time with live UI refresh.

### Substeps
- [ ] Create AIChatSidebar.tsx component with message list and input
- [ ] Create useAIChat.ts hook for API integration and state management
- [ ] Add sidebar to KanbanBoard.tsx (split layout: board + chat)
- [ ] Display loading indicator while waiting for AI response
- [ ] Show error messages with retry button if AI call fails
- [ ] When AI returns kanban_updates, apply them to frontend state
- [ ] Trigger real-time UI refresh when Kanban changes from AI (animate transitions)
- [ ] Add user message → AI response in chat history
- [ ] Add timestamp to each message in sidebar
- [ ] Persist conversation history (localStorage for MVP)
- [ ] Add "Clear conversation" button
- [ ] Style sidebar to match design scheme (color scheme from AGENTS.md)
- [ ] Make sidebar collapsible/resizable
- [ ] Create AIChatSidebar.test.tsx unit tests
- [ ] Create E2E tests for full AI chat flow (ask → AI updates → see board update)
- [ ] Add accessibility (ARIA labels, keyboard navigation)

### Tests & Success Criteria
- **Success**: npm run test:unit passes (AIChatSidebar, useAIChat tests)
- **Success**: npm run test:e2e passes (open chat → send message → see AI response)
- **Success**: npm run test:e2e passes (AI updates card → see Kanban refresh)
- **Success**: Chat messages persist locally until cleared
- **Success**: Sidebar is responsive (works on mobile, tablet, desktop)
- **Success**: Sidebar smooth animations when expanding/collapsing
- **Success**: Error states handled gracefully (show message, offer retry)
- **Success**: Kanban updates from AI apply instantly with visual feedback
- **Success**: Accessibility tests pass (keyboard navigation works)
- **Success**: All unit and E2E tests pass
- **Success**: Manual QA: full AI chat workflow works end-to-end

---

## Overall Success Criteria
- All 10 parts complete with tests passing
- Docker container builds and runs cleanly
- Production build size optimized (Next.js standalone)
- All API endpoints documented
- Code follows project standards (no overengineering, clear naming, comments)
- README in project root explains setup and running