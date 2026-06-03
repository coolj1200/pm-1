"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .api.health import router as health_router
from .api.auth import router as auth_router
from .api.kanban import router as kanban_router
from .api.ai import router as ai_router
from .database import init_db

app = FastAPI(title="Project Management API")

# Initialize the SQLite database and tables on startup
app.add_event_handler("startup", init_db)

# Include API routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(kanban_router)
app.include_router(ai_router)

# Frontend build output directory
frontend_build_dir = Path(__file__).parent.parent / "frontend_build"
next_dir = frontend_build_dir / "_next"
public_dir = frontend_build_dir / "public"

if next_dir.exists():
    app.mount("/_next", StaticFiles(directory=next_dir), name="_next")

if public_dir.exists():
    app.mount("/public", StaticFiles(directory=public_dir), name="public")


def get_frontend_file(path: str) -> Path:
    candidate = (frontend_build_dir / path).resolve()
    if frontend_build_dir.resolve() in candidate.parents or candidate == frontend_build_dir.resolve():
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


@app.get("/")
def root():
    """Serve the exported frontend index page."""
    index_file = frontend_build_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")

    static_dir = Path(__file__).parent / "static"
    fallback_file = static_dir / "index.html"
    if fallback_file.exists():
        return FileResponse(fallback_file, media_type="text/html")

    return {"message": "Hello World"}


@app.get("/{path:path}")
def catch_all(path: str):
    """Serve frontend assets and fallback to the exported index page."""
    if path.startswith("api/"):
        return {"error": "Not found"}, 404

    frontend_file = get_frontend_file(path)
    if frontend_file:
        return FileResponse(frontend_file)

    index_file = frontend_build_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")

    return {"error": "Not found"}, 404


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

