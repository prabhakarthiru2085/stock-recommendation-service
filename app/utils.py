import re
import logging
from typing import Optional, Union, List
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

def clean_numeric_value(value: str) -> Optional[float]:
    """Clean and convert string numeric values to float"""
    if not value or value == '-' or value.lower() == 'n/a':
        return None
        
    try:
        # Remove common formatting characters
        cleaned = re.sub(r'[₹,\s%]', '', str(value))
        
        # Handle special cases like 'Cr' (Crores), 'L' (Lakhs)
        if cleaned.endswith('Cr'):
            return float(cleaned[:-2]) * 10000000  # Convert crores to actual value
        elif cleaned.endswith('L'):
            return float(cleaned[:-1]) * 100000    # Convert lakhs to actual value
        
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def normalize_company_name(name: str) -> str:
    """Normalize company name for consistent processing"""
    if not name:
        return ""
    
    # Remove common suffixes and clean up
    name = name.strip()
    suffixes_to_remove = ['Ltd', 'Limited', 'Ltd.', 'Limited.', 'Pvt', 'Pvt.', 'Private']
    
    for suffix in suffixes_to_remove:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    
    return name

def validate_company_name(name: str) -> bool:
    """Validate if company name is acceptable"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Check for suspicious patterns
    if re.match(r'^[0-9]+$', name.strip()):  # Only numbers
        return False
    
    return True

def extract_percentage(value: str) -> Optional[float]:
    """Extract percentage value from string"""
    if not value:
        return None
    
    try:
        # Remove % and convert to float
        cleaned = value.replace('%', '').strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> Optional[float]:
    """Safely divide two numbers, return None if division by zero"""
    try:
        if denominator == 0:
            return None
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return None

def rate_limit(calls_per_second: float = 1.0):
    """Decorator to rate limit function calls"""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = asyncio.get_event_loop().time() - last_called[0]
            min_interval = 1.0 / calls_per_second
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            
            last_called[0] = asyncio.get_event_loop().time()
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def calculate_score_confidence(individual_scores: List[float], weights: List[float]) -> float:
    """Calculate confidence based on available data completeness"""
    if not individual_scores or not weights:
        return 0.0
    
    # Count non-zero scores (indicating available data)
    available_data_points = sum(1 for score in individual_scores if score != 0.5)  # 0.5 is neutral/no data
    total_data_points = len(individual_scores)
    
    # Base confidence on data completeness
    data_completeness = available_data_points / total_data_points
    
    return min(data_completeness, 1.0)

def format_currency(amount: Optional[float], currency: str = "₹") -> str:
    """Format currency amount with proper formatting"""
    if amount is None:
        return "N/A"
    
    if amount >= 10000000:  # Crores
        return f"{currency}{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # Lakhs
        return f"{currency}{amount/100000:.2f} L"
    else:
        return f"{currency}{amount:,.2f}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."