from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging
from app.models import RecommendationRequest, StockRecommendation
from app.scraper import ScreenerScraper
from app.analyzer import StockAnalyzer
import asyncio
from typing import Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Indian Stock Recommendation Service",
    description="AI-powered stock recommendations based on Screener.in data analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
scraper = ScreenerScraper()
analyzer = StockAnalyzer()

# In-memory cache for demo purposes (use Redis in production)
cache: Dict[str, StockRecommendation] = {}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api")
async def root():
    """API health check endpoint"""
    return {
        "message": "Indian Stock Recommendation Service is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "stock-recommendation-service",
        "components": {
            "scraper": "operational",
            "analyzer": "operational",
            "api": "operational"
        }
    }

@app.post("/recommend", response_model=StockRecommendation)
async def get_stock_recommendation(request: RecommendationRequest):
    """
    Get stock recommendation for an Indian company
    
    Args:
        request: RecommendationRequest containing company name
        
    Returns:
        StockRecommendation: Buy/Sell/Hold recommendation with analysis
    """
    try:
        company_name = request.company_name.strip()
        
        if not company_name:
            raise HTTPException(status_code=400, detail="Company name cannot be empty")
        
        # Check cache first
        cache_key = company_name.lower()
        if cache_key in cache:
            logger.info(f"Returning cached recommendation for {company_name}")
            return cache[cache_key]
        
        logger.info(f"Processing recommendation request for: {company_name}")
        
        # Scrape company data
        logger.info("Scraping company data from Screener.in...")
        company_data = scraper.scrape_company_data(company_name)
        
        if not company_data or not company_data.get('basic_data'):
            raise HTTPException(
                status_code=404, 
                detail=f"Company '{company_name}' not found or data unavailable"
            )
        
        # Analyze the data
        logger.info("Analyzing company data...")
        recommendation = analyzer.analyze_stock(company_data)
        
        # Cache the result
        cache[cache_key] = recommendation
        
        logger.info(f"Generated {recommendation.recommendation} recommendation for {company_name}")
        return recommendation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing recommendation for {company_name}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/company/{company_name}/data")
async def get_company_data(company_name: str):
    """
    Get raw company data from Screener.in (for debugging/analysis)
    
    Args:
        company_name: Name of the Indian company
        
    Returns:
        Raw scraped data from Screener.in
    """
    try:
        if not company_name.strip():
            raise HTTPException(status_code=400, detail="Company name cannot be empty")
        
        logger.info(f"Fetching raw data for: {company_name}")
        
        company_data = scraper.scrape_company_data(company_name)
        
        if not company_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Company '{company_name}' not found"
            )
        
        return {
            "company_name": company_name,
            "data": company_data,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching data for {company_name}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.delete("/cache")
async def clear_cache():
    """Clear the recommendation cache"""
    global cache
    cache.clear()
    return {"message": "Cache cleared successfully"}

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "cached_companies": len(cache),
        "companies": list(cache.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)