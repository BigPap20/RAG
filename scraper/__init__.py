"""
RAG Scraper Package
Backend service for web scraping and Hugging Face model data retrieval.
"""

from .scraper import WebScraper, HuggingFaceScraper, create_context_from_models
from .api import app

__version__ = "1.0.0"
__all__ = ["WebScraper", "HuggingFaceScraper", "create_context_from_models", "app"]