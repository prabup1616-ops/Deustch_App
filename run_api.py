"""
FastAPI Server Launcher for Goethe B1 Master API.
Run this script to start the Uvicorn ASGI server with live reload.
Command: python run_api.py
Docs available at: http://localhost:8000/docs
"""

import os
import sys
import uvicorn

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

if __name__ == "__main__":
    print("🚀 Starting Goethe-Zertifikat B1 FastAPI Server on http://localhost:8000")
    print("📖 Interactive Swagger API Docs: http://localhost:8000/docs")
    print("📘 ReDoc API Documentation: http://localhost:8000/redoc")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
