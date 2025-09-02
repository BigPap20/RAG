#!/usr/bin/env python3
"""
scraper.py
Core scraping functionality extracted from the original project.
Provides web scraping and Hugging Face model data retrieval functionality.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

# Configuration
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; arm64 Mac OS X 14_5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
)

# Hugging Face specific configurations
HF_LIST_URL = "https://huggingface.co/models?sort=likes"
HF_API_BASE = "https://huggingface.co/api/models"
MODEL_HREF_RE = re.compile(r"^/([A-Za-z0-9][A-Za-z0-9_.-]*)/([A-Za-z0-9][A-Za-z0-9_.-]*)$")

# Banned top-level organizations for HF scraping
BAD_ORGS = {
    "models", "datasets", "spaces", "docs", "search", "organizations", "settings",
    "pricing", "login", "join", "new", "collections", "tasks", "events", "api",
    "blog", "about", "terms", "privacy", "contact", "people"
}

# Optional Hugging Face Hub client
try:
    from huggingface_hub import HfApi, login
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False


class WebScraper:
    """General web scraping functionality."""
    
    def __init__(self, timeout: int = 20, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        })
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a general URL and return structured data.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict containing scraped data with keys: 'url', 'title', 'text', 'status'
        """
        result = {
            "url": url,
            "title": "",
            "text": "",
            "status": "error",
            "error": None
        }
        
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Extract title
                    title_tag = soup.find("title")
                    result["title"] = title_tag.get_text().strip() if title_tag else ""
                    
                    # Extract main text content
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    result["text"] = soup.get_text().strip()
                    result["status"] = "success"
                    return result
                else:
                    result["error"] = f"HTTP {response.status_code}"
            except requests.RequestException as e:
                result["error"] = str(e)
                if attempt < self.retries - 1:
                    time.sleep(2 * (attempt + 1))
        
        return result


class HuggingFaceScraper:
    """Specialized scraper for Hugging Face models."""
    
    def __init__(self, timeout: int = 20, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        })
    
    def scrape_models(self, limit: int = 20) -> List[str]:
        """
        Scrape model IDs from Hugging Face models page.
        
        Args:
            limit: Maximum number of model IDs to return
            
        Returns:
            List of model IDs in format 'org/model'
        """
        for attempt in range(self.retries):
            try:
                response = self.session.get(HF_LIST_URL, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    ids = []
                    for a in soup.select("a[href]"):
                        href = a.get("href", "")
                        href = href.split("?", 1)[0].split("#", 1)[0]  # Remove query/fragment
                        
                        m = MODEL_HREF_RE.match(href)
                        if not m:
                            continue
                            
                        org, name = m.group(1), m.group(2)
                        if org in BAD_ORGS:
                            continue
                            
                        # Extra safety checks
                        if "%" in org or "%" in name or "@" in org or "@" in name:
                            continue
                            
                        ids.append(f"{org}/{name}")
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_ids = []
                    for model_id in ids:
                        if (model_id not in seen and 
                            not model_id.startswith("search/") and 
                            "%" not in model_id):
                            seen.add(model_id)
                            unique_ids.append(model_id)
                    
                    return unique_ids[:limit]
                    
            except requests.RequestException:
                if attempt < self.retries - 1:
                    time.sleep(2 * (attempt + 1))
        
        return []
    
    def get_models_via_api(self, limit: int = 20) -> List[str]:
        """
        Get model IDs using Hugging Face Hub API as fallback.
        
        Args:
            limit: Maximum number of model IDs to return
            
        Returns:
            List of model IDs
        """
        if not HAS_HF_HUB:
            return []
        
        try:
            api = HfApi()
            models = api.list_models(sort="likes", direction=-1, limit=limit)
            return [m.modelId for m in models]
        except Exception:
            return []
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: Model ID in format 'org/model'
            
        Returns:
            Dict containing model information
        """
        result = {
            "model_id": model_id,
            "likes": 0,
            "downloads": 0,
            "status": "error",
            "error": None
        }
        
        try:
            # Try direct API call first
            response = self.session.get(f"{HF_API_BASE}/{model_id}", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                result.update({
                    "likes": data.get("likes", 0),
                    "downloads": data.get("downloads", 0),
                    "status": "success",
                    "tags": data.get("tags", []),
                    "pipeline_tag": data.get("pipeline_tag", ""),
                    "created_at": data.get("created_at", ""),
                    "last_modified": data.get("lastModified", ""),
                })
                return result
            else:
                result["error"] = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            result["error"] = str(e)
        
        return result
    
    def enrich_models(self, model_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Enrich a list of model IDs with detailed information.
        
        Args:
            model_ids: List of model IDs to enrich
            
        Returns:
            List of enriched model data dictionaries
        """
        enriched_models = []
        
        for model_id in model_ids:
            info = self.get_model_info(model_id)
            if info["status"] == "success":
                enriched_models.append(info)
        
        return enriched_models


def create_context_from_models(models: List[Dict[str, Any]], topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Create enriched context from model data, optionally filtered by topic.
    
    Args:
        models: List of model data dictionaries
        topic: Optional topic to filter models by
        
    Returns:
        Dict containing processed context data
    """
    if topic:
        # Filter models by topic (search in tags and pipeline_tag)
        filtered_models = []
        topic_lower = topic.lower()
        
        for model in models:
            tags = [tag.lower() for tag in model.get("tags", [])]
            pipeline_tag = model.get("pipeline_tag", "").lower()
            
            if (topic_lower in pipeline_tag or 
                any(topic_lower in tag for tag in tags) or
                topic_lower in model.get("model_id", "").lower()):
                filtered_models.append(model)
        
        models = filtered_models
    
    # Calculate summary statistics
    total_models = len(models)
    total_likes = sum(model.get("likes", 0) for model in models)
    total_downloads = sum(model.get("downloads", 0) for model in models)
    
    # Get top models by likes
    top_models = sorted(models, key=lambda x: x.get("likes", 0), reverse=True)[:10]
    
    # Get unique pipeline tags
    pipeline_tags = set()
    for model in models:
        if model.get("pipeline_tag"):
            pipeline_tags.add(model.get("pipeline_tag"))
    
    context = {
        "topic": topic or "all",
        "total_models": total_models,
        "total_likes": total_likes,
        "total_downloads": total_downloads,
        "average_likes": total_likes / total_models if total_models > 0 else 0,
        "average_downloads": total_downloads / total_models if total_models > 0 else 0,
        "top_models": top_models,
        "pipeline_tags": list(pipeline_tags),
        "models": models
    }
    
    return context