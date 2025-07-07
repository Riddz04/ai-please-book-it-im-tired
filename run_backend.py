#!/usr/bin/env python3
"""
Alternative backend runner with proper path setup
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",  # Use import string instead of app object
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )