#!/bin/bash
# stop.sh - Stop the Project Management app Docker container
# Usage: ./scripts/stop.sh
#
# This script stops and removes the Docker container for the Project Management MVP.
# The database file (kanban.db) is preserved.

set -e

echo "==================================="
echo "Project Management MVP - Stopping"
echo "==================================="

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found."
    exit 1
fi

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Stop the container
echo "🛑 Stopping container..."
docker-compose down

echo ""
echo "==================================="
echo "✅ App Stopped Successfully"
echo "==================================="
echo "Database file preserved: kanban.db"
echo "To start again: ./scripts/start.sh"
echo "==================================="
