"""FastAPI application for ScrAI simulation control."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import actors, llm, simulations, streams


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle."""
    # Startup: initialize runtime singleton
    from .dependencies import get_runtime_manager
    runtime_manager = get_runtime_manager()
    await runtime_manager.initialize()
    
    yield
    
    # Shutdown: cleanup
    await runtime_manager.shutdown()


app = FastAPI(
    title="ScrAI API",
    description="Simulation control and management API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(simulations.router, prefix="/api")
app.include_router(llm.router, prefix="/api")
app.include_router(streams.router, prefix="/api")
app.include_router(actors.router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
