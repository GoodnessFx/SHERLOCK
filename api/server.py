from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os
import logging
from core.config import settings
from api.routes import edges, track_record, markets, health, feed
from api.websocket import router as ws_router, log_broadcaster

logger = logging.getLogger(__name__)

# FastAPI instance
app = FastAPI(
    title="SHERLOCK API",
    description="The autonomous prediction intelligence network that never sleeps.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(edges.router, prefix="/api", tags=["edges"])
app.include_router(track_record.router, prefix="/api", tags=["track_record"])
app.include_router(markets.router, prefix="/api", tags=["markets"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(feed.router, prefix="/api", tags=["feed"])
app.include_router(ws_router, tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    """
    Actions on API startup.
    """
    logger.info("Starting up SHERLOCK API...")
    # Start the log broadcaster in the background
    asyncio.create_task(log_broadcaster())

@app.get("/")
async def root():
    return {
        "project": "SHERLOCK",
        "tagline": "The autonomous prediction intelligence network that never sleeps.",
        "status": "online",
        "api_docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
