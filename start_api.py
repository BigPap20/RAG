#!/usr/bin/env python3
"""
start_api.py
Simple script to start the FastAPI server
"""

import uvicorn
import sys
import os

# Add the current directory to the path so we can import the scraper module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting RAG Scraper API...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "scraper.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )