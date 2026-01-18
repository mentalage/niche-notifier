"""FastAPI Application Entry Point.

Notify Niche Web API for managing RSS feeds and viewing articles.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routers import feeds, categories, articles

app = FastAPI(
    title="Notify Niche API",
    description="RSS Feed Management and Discord Notification Preview API",
    version="1.0.0"
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feeds.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(articles.router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Notify Niche API is running"}


@app.get("/api/health")
async def health_check():
    """API health check."""
    return {"status": "healthy"}
