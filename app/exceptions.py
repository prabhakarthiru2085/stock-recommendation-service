class StockRecommendationException(Exception):
    """Base exception for stock recommendation service"""
    pass

class CompanyNotFoundError(StockRecommendationException):
    """Raised when company is not found on Screener.in"""
    pass

class ScrapingError(StockRecommendationException):
    """Raised when scraping fails"""
    pass

class AnalysisError(StockRecommendationException):
    """Raised when analysis fails"""
    pass

class ValidationError(StockRecommendationException):
    """Raised when input validation fails"""
    pass

class RateLimitError(StockRecommendationException):
    """Raised when rate limit is exceeded"""
    pass