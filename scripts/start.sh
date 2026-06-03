#!/bin/bash
# start.sh - Start the Project Management app in a Docker container
# Usage: ./scripts/start.sh
# 
# This script builds and starts the Docker container for the Project Management MVP.
# The app will be available at http://localhost:8000
#
# Make sure you have:
# - Docker installed and running
# - OPENROUTER_API_KEY set in backend/.env (optional for testing)

set -e

echo "==================================="
echo "Project Management MVP - Starting"
echo "==================================="

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "📁 Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# Load environment variables from .env if it exists
if [ -f "backend/.env" ]; then
    echo "📋 Loading environment from backend/.env"
    export $(grep -v '^#' backend/.env | xargs)
fi

# Build and start the container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting container..."
docker-compose up -d

# Wait for the container to be ready
echo "⏳ Waiting for app to be ready..."
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ App is ready!"
        break
    fi
    echo "   Attempt $((RETRY_COUNT + 1))/$MAX_RETRIES..."
    sleep 1
    ((RETRY_COUNT++))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  App may still be starting. Check logs with: docker-compose logs"
fi

echo ""
echo "==================================="
echo "✨ App Started Successfully!"
echo "==================================="
echo "🌐 Open in browser: http://localhost:8000"
echo "📊 Health check:   http://localhost:8000/api/health"
echo ""
echo "Available commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop app:     ./scripts/stop.sh"
echo "  Restart:      docker-compose restart"
echo "==================================="
