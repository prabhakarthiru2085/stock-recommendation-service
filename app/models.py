from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RecommendationType(str, Enum):
    BUY = "Buy"
    SELL = "Sell"
    HOLD = "Hold"

class CompanyOverview(BaseModel):
    name: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

class QuarterlyResult(BaseModel):
    quarter: str
    revenue: Optional[float] = None
    net_profit: Optional[float] = None
    eps: Optional[float] = None
    growth_revenue: Optional[float] = None
    growth_profit: Optional[float] = None

class FinancialRatios(BaseModel):
    roe: Optional[float] = None
    roce: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    asset_turnover: Optional[float] = None

class ShareholdingPattern(BaseModel):
    promoter_holding: Optional[float] = None
    public_holding: Optional[float] = None
    institutional_holding: Optional[float] = None

class CompanyData(BaseModel):
    company_name: str
    overview: Optional[CompanyOverview] = None
    quarterly_results: List[QuarterlyResult] = []
    financial_ratios: Optional[FinancialRatios] = None
    shareholding_pattern: Optional[ShareholdingPattern] = None
    announcements: List[str] = []
    credit_ratings: List[str] = []
    raw_data: Dict[str, Any] = {}

class StockRecommendation(BaseModel):
    company_name: str
    recommendation: RecommendationType
    confidence_score: float = Field(ge=0, le=1)
    reasoning: List[str]
    key_metrics: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class RecommendationRequest(BaseModel):
    company_name: str