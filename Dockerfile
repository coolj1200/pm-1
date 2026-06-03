# Build stage: compile frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend .
RUN npm run build

# Runtime stage: Python FastAPI backend
FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy backend code and requirements
COPY backend/requirements.txt .
RUN uv pip install --system -r requirements.txt
COPY backend /app/backend

# Copy exported frontend from builder stage
COPY --from=frontend-builder /app/frontend/out /app/frontend_build

WORKDIR /app

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
