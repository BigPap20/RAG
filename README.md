# RAG Scraper

A backend service for web scraping and Hugging Face model data retrieval, designed for integration with OutloudOS and other frontend applications.

## What it does

This project provides a FastAPI-based backend service that:

1. **Web Scraping**: Scrapes content from any URL and extracts text and metadata
2. **Hugging Face Integration**: Retrieves and enriches data about machine learning models from Hugging Face
3. **Context Generation**: Creates enriched, filtered context about models based on topics
4. **API Access**: Provides clean REST API endpoints for easy integration

## Project Structure

```
/scraper/
    scraper.py          # Core scraping and data processing logic
    api.py              # FastAPI endpoints
    requirements.txt    # Python dependencies
    __init__.py         # Package initialization

/streamlit_app/
    app.py              # Optional Streamlit UI (original interface)

README.md               # This file
requirements.txt        # Global project dependencies
```

## Installation

### Backend API

1. Navigate to the scraper directory:
```bash
cd scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Streamlit App (Optional)

If you want to use the original Streamlit interface:

1. Install Streamlit and other dependencies:
```bash
pip install streamlit pandas
```

## Running the API

### Start the FastAPI server:

```bash
# From the project root
python -m uvicorn scraper.api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Root Information
```
GET /
```
Returns basic API information and available endpoints.

### 2. Web Scraping
```
GET /scrape?url={url}&format={json|text}
```
Scrapes content from any URL.

**Parameters:**
- `url` (required): URL to scrape
- `format` (optional): Response format - "json" (default) or "text"

**Example:**
```bash
curl "http://localhost:8000/scrape?url=https://example.com"
```

**Response:**
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "text": "Example Domain This domain is for use in illustrative examples...",
  "status": "success"
}
```

### 3. Enriched Context
```
GET /context?topic={topic}&limit={limit}
```
Returns enriched context about Hugging Face models, optionally filtered by topic.

**Parameters:**
- `topic` (optional): Filter models by topic (searches tags, pipeline_tag, model name)
- `limit` (optional): Maximum number of models to include (default: 20, max: 100)

**Example:**
```bash
curl "http://localhost:8000/context?topic=text-generation&limit=10"
```

**Response:**
```json
{
  "topic": "text-generation",
  "total_models": 8,
  "total_likes": 1250,
  "total_downloads": 50000,
  "average_likes": 156.25,
  "average_downloads": 6250.0,
  "top_models": [...],
  "pipeline_tags": ["text-generation", "text2text-generation"],
  "models": [...]
}
```

### 4. Model Data
```
GET /models?limit={limit}&enrich={true|false}
```
Returns Hugging Face model data.

**Parameters:**
- `limit` (optional): Maximum number of models (default: 20, max: 100)
- `enrich` (optional): Include detailed model information (default: true)

**Example:**
```bash
curl "http://localhost:8000/models?limit=5&enrich=true"
```

### 5. Health Check
```
GET /health
```
Returns service health status.

## Running the Streamlit App (Optional)

To use the original Streamlit interface:

```bash
cd streamlit_app
streamlit run app.py
```

The Streamlit app will be available at `http://localhost:8501`

## Integration Examples

### Python Integration
```python
import requests

# Scrape a webpage
response = requests.get("http://localhost:8000/scrape?url=https://example.com")
data = response.json()
print(data["text"])

# Get model context
response = requests.get("http://localhost:8000/context?topic=nlp&limit=10")
context = response.json()
print(f"Found {context['total_models']} NLP models")
```

### ASP.NET Integration
```csharp
using System.Net.Http;
using System.Text.Json;

var client = new HttpClient();
var response = await client.GetAsync("http://localhost:8000/context?topic=vision");
var jsonString = await response.Content.ReadAsStringAsync();
var context = JsonSerializer.Deserialize<dynamic>(jsonString);
```

### JavaScript/Frontend Integration
```javascript
// Fetch model context
fetch('http://localhost:8000/context?topic=audio&limit=15')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total_models} audio models`);
    console.log('Top models:', data.top_models);
  });
```

## Development

### Testing the API

Test endpoints manually:
```bash
# Test basic scraping
curl "http://localhost:8000/scrape?url=https://httpbin.org/html"

# Test health check
curl "http://localhost:8000/health"

# Test model data (this may fail without internet access)
curl "http://localhost:8000/models?limit=3&enrich=false"
```

### Environment Variables

Optional environment variables:
- `HUGGINGFACE_HUB_TOKEN`: Hugging Face API token for authenticated requests

### Error Handling

The API includes comprehensive error handling:
- HTTP 400: Bad request (invalid URL, parameters)
- HTTP 503: Service unavailable (Hugging Face API issues)
- HTTP 500: Internal server error

## Notes

- This refactor is designed for local development and easy integration
- The API includes fallback mechanisms when web scraping fails
- All scraping respects rate limits and includes proper error handling
- The original Streamlit UI is preserved in `/streamlit_app` for optional use