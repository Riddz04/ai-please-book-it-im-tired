#!/usr/bin/env python3
"""
Standalone script to start the FastAPI backend server
"""
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",  # Use import string for reload mode
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )