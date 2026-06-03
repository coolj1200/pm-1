"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
def health_check():
    """Check if the backend is running."""
    return {"status": "ok"}
