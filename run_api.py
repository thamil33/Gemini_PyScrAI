#!/usr/bin/env python3
"""Development server for ScrAI API."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "scrai.api.app:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info",
    )
