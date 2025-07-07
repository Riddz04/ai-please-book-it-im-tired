#!/usr/bin/env python3
"""
Standalone script to start the Streamlit frontend
"""
import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])