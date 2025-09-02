#!/usr/bin/env python3
"""
api.py
FastAPI endpoints for the scraper backend service.
Provides REST API access to scraping and model enrichment functionality.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from scraper.scraper import WebScraper, HuggingFaceScraper, create_context_from_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Scraper API",
    description="Backend API for web scraping and Hugging Face model data retrieval",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize scrapers
web_scraper = WebScraper()
hf_scraper = HuggingFaceScraper()

# Cache for model data to avoid repeated API calls
model_cache = {}
cache_ttl = 300  # 5 minutes


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "Scrape content from a URL",
            "/context": "Get enriched model context by topic",
            "/models": "Get Hugging Face model data",
            "/docs": "API documentation"
        }
    }


@app.get("/scrape")
async def scrape_url(
    url: str = Query(..., description="URL to scrape"),
    format: str = Query("json", description="Response format: 'json' or 'text'")
):
    """
    Scrape content from a URL and return raw scraped text/JSON.
    
    Args:
        url: The URL to scrape
        format: Response format ('json' or 'text')
        
    Returns:
        Scraped content in the requested format
    """
    try:
        logger.info(f"Scraping URL: {url}")
        result = web_scraper.scrape_url(url)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=400,
                detail=f"Failed to scrape URL: {result.get('error', 'Unknown error')}"
            )
        
        if format.lower() == "text":
            return result["text"]
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/context")
async def get_context(
    topic: Optional[str] = Query(None, description="Topic to filter models by"),
    limit: int = Query(20, description="Maximum number of models to include", ge=1, le=100)
):
    """
    Get enriched/cleaned context about Hugging Face models, optionally filtered by topic.
    
    Args:
        topic: Optional topic to filter models by (searches in tags, pipeline_tag, and model name)
        limit: Maximum number of models to include in the context
        
    Returns:
        Enriched context data with model statistics and filtered results
    """
    try:
        logger.info(f"Getting context for topic: {topic}, limit: {limit}")
        
        # Get fresh model data
        model_ids = hf_scraper.scrape_models(limit=limit)
        
        # Fallback to API if scraping returns empty results
        if not model_ids:
            logger.info("Scraping returned no results, falling back to API")
            model_ids = hf_scraper.get_models_via_api(limit=limit)
        
        if not model_ids:
            raise HTTPException(
                status_code=503,
                detail="Unable to retrieve model data from Hugging Face"
            )
        
        # Enrich models with detailed information
        enriched_models = hf_scraper.enrich_models(model_ids)
        
        if not enriched_models:
            raise HTTPException(
                status_code=503,
                detail="Unable to enrich model data"
            )
        
        # Create context
        context = create_context_from_models(enriched_models, topic)
        
        logger.info(f"Generated context with {context['total_models']} models")
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/models")
async def get_models(
    limit: int = Query(20, description="Maximum number of models to return", ge=1, le=100),
    enrich: bool = Query(True, description="Whether to enrich models with detailed information")
):
    """
    Get Hugging Face model data.
    
    Args:
        limit: Maximum number of models to return
        enrich: Whether to include detailed model information
        
    Returns:
        List of model data
    """
    try:
        logger.info(f"Getting {limit} models, enrich: {enrich}")
        
        # Get model IDs
        model_ids = hf_scraper.scrape_models(limit=limit)
        
        # Fallback to API if scraping fails
        if not model_ids:
            logger.info("Scraping failed, using API fallback")
            model_ids = hf_scraper.get_models_via_api(limit=limit)
        
        if not model_ids:
            raise HTTPException(
                status_code=503,
                detail="Unable to retrieve model data from Hugging Face"
            )
        
        if enrich:
            # Return enriched model data
            models = hf_scraper.enrich_models(model_ids)
            return {"models": models, "count": len(models)}
        else:
            # Return just the model IDs
            return {"model_ids": model_ids, "count": len(model_ids)}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RAG Scraper API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)