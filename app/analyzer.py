import logging
from typing import Dict, List, Any, Optional, Tuple
from app.models import StockRecommendation, RecommendationType, CompanyData, FinancialRatios
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self):
        self.weights = {
            'financial_health': 0.30,
            'growth_trends': 0.25,
            'valuation': 0.20,
            'profitability': 0.15,
            'governance': 0.10
        }
    
    def analyze_stock(self, company_data: Dict[str, Any]) -> StockRecommendation:
        """Main analysis method that returns stock recommendation"""
        try:
            company_name = company_data.get('company_name', 'Unknown')
            
            # Perform individual analyses
            financial_score, financial_reasons = self._analyze_financial_health(company_data)
            growth_score, growth_reasons = self._analyze_growth_trends(company_data)
            valuation_score, valuation_reasons = self._analyze_valuation(company_data)
            profitability_score, profitability_reasons = self._analyze_profitability(company_data)
            governance_score, governance_reasons = self._analyze_governance(company_data)
            
            # Calculate weighted overall score
            overall_score = (
                financial_score * self.weights['financial_health'] +
                growth_score * self.weights['growth_trends'] +
                valuation_score * self.weights['valuation'] +
                profitability_score * self.weights['profitability'] +
                governance_score * self.weights['governance']
            )
            
            # Determine recommendation based on overall score
            recommendation = self._determine_recommendation(overall_score)
            
            # Combine all reasoning
            all_reasons = (
                financial_reasons + growth_reasons + valuation_reasons + 
                profitability_reasons + governance_reasons
            )
            
            # Key metrics summary
            key_metrics = {
                'overall_score': round(overall_score, 2),
                'financial_health_score': round(financial_score, 2),
                'growth_score': round(growth_score, 2),
                'valuation_score': round(valuation_score, 2),
                'profitability_score': round(profitability_score, 2),
                'governance_score': round(governance_score, 2)
            }
            
            return StockRecommendation(
                company_name=company_name,
                recommendation=recommendation,
                confidence_score=min(overall_score, 1.0),
                reasoning=all_reasons,
                key_metrics=key_metrics
            )
            
        except Exception as e:
            logger.error(f"Error analyzing stock data: {e}")
            return StockRecommendation(
                company_name=company_name,
                recommendation=RecommendationType.HOLD,
                confidence_score=0.0,
                reasoning=[f"Analysis failed: {str(e)}"],
                key_metrics={}
            )
    
    def _analyze_financial_health(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze financial health metrics"""
        score = 0.5  # Start with neutral
        reasons = []
        
        try:
            basic_data = data.get('basic_data', {})
            ratios = data.get('financial_ratios', {})
            
            # Debt-to-Equity ratio analysis
            debt_to_equity = ratios.get('debt_to_equity') or basic_data.get('debt_to_equity')
            if debt_to_equity is not None:
                if debt_to_equity < 0.5:
                    score += 0.15
                    reasons.append("Low debt-to-equity ratio indicates strong financial position")
                elif debt_to_equity > 1.0:
                    score -= 0.15
                    reasons.append("High debt-to-equity ratio raises concerns about financial stability")
            
            # Current ratio analysis
            current_ratio = ratios.get('current_ratio') or basic_data.get('current_ratio')
            if current_ratio is not None:
                if current_ratio > 1.5:
                    score += 0.1
                    reasons.append("Good current ratio indicates healthy liquidity")
                elif current_ratio < 1.0:
                    score -= 0.1
                    reasons.append("Low current ratio may indicate liquidity concerns")
            
            # Interest coverage analysis
            interest_coverage = ratios.get('interest_coverage') or basic_data.get('interest_coverage')  
            if interest_coverage is not None:
                if interest_coverage > 5:
                    score += 0.1
                    reasons.append("Strong interest coverage indicates ability to service debt")
                elif interest_coverage < 2:
                    score -= 0.15
                    reasons.append("Weak interest coverage raises debt servicing concerns")
            
        except Exception as e:
            logger.error(f"Error in financial health analysis: {e}")
            reasons.append("Limited financial health data available")
        
        return max(0, min(1, score)), reasons
    
    def _analyze_growth_trends(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze growth trends from quarterly data"""
        score = 0.5
        reasons = []
        
        try:
            quarterly_results = data.get('quarterly_results', [])
            
            if len(quarterly_results) >= 4:
                # Analyze revenue growth
                revenue_growth = self._calculate_growth_trend(quarterly_results, 'Sales')
                if revenue_growth is not None:
                    if revenue_growth > 15:
                        score += 0.2
                        reasons.append(f"Strong revenue growth of {revenue_growth:.1f}%")
                    elif revenue_growth > 5:
                        score += 0.1
                        reasons.append(f"Moderate revenue growth of {revenue_growth:.1f}%")
                    elif revenue_growth < -5:
                        score -= 0.15
                        reasons.append(f"Declining revenue trend of {revenue_growth:.1f}%")
                
                # Analyze profit growth
                profit_growth = self._calculate_growth_trend(quarterly_results, 'Net Profit')
                if profit_growth is not None:
                    if profit_growth > 20:
                        score += 0.15
                        reasons.append(f"Excellent profit growth of {profit_growth:.1f}%")
                    elif profit_growth > 10:
                        score += 0.1
                        reasons.append(f"Good profit growth of {profit_growth:.1f}%")
                    elif profit_growth < -10:
                        score -= 0.2
                        reasons.append(f"Concerning profit decline of {profit_growth:.1f}%")
            
            else:
                reasons.append("Insufficient quarterly data for growth trend analysis")
        
        except Exception as e:
            logger.error(f"Error in growth analysis: {e}")
            reasons.append("Limited growth data available")
        
        return max(0, min(1, score)), reasons
    
    def _analyze_valuation(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze valuation metrics"""
        score = 0.5
        reasons = []
        
        try:
            basic_data = data.get('basic_data', {})
            
            # P/E ratio analysis
            pe_ratio = basic_data.get('price_earnings') or basic_data.get('pe_ratio')
            if pe_ratio is not None and pe_ratio > 0:
                if pe_ratio < 15:
                    score += 0.15
                    reasons.append(f"Attractive P/E ratio of {pe_ratio:.1f}")
                elif pe_ratio < 25:
                    score += 0.05
                    reasons.append(f"Reasonable P/E ratio of {pe_ratio:.1f}")
                elif pe_ratio > 40:
                    score -= 0.1
                    reasons.append(f"High P/E ratio of {pe_ratio:.1f} may indicate overvaluation")
            
            # P/B ratio analysis
            pb_ratio = basic_data.get('price_to_book') or basic_data.get('pb_ratio')
            if pb_ratio is not None and pb_ratio > 0:
                if pb_ratio < 1.5:
                    score += 0.1
                    reasons.append(f"Attractive P/B ratio of {pb_ratio:.1f}")
                elif pb_ratio > 3:
                    score -= 0.05
                    reasons.append(f"High P/B ratio of {pb_ratio:.1f}")
            
            # Dividend yield analysis
            dividend_yield = basic_data.get('dividend_yield')
            if dividend_yield is not None and dividend_yield > 0:
                if dividend_yield > 2:
                    score += 0.05
                    reasons.append(f"Good dividend yield of {dividend_yield:.1f}%")
        
        except Exception as e:
            logger.error(f"Error in valuation analysis: {e}")
            reasons.append("Limited valuation data available")
        
        return max(0, min(1, score)), reasons
    
    def _analyze_profitability(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze profitability metrics"""
        score = 0.5
        reasons = []
        
        try:
            basic_data = data.get('basic_data', {})
            ratios = data.get('financial_ratios', {})
            
            # ROE analysis
            roe = ratios.get('roe') or basic_data.get('roe')
            if roe is not None:
                if roe > 20:
                    score += 0.2
                    reasons.append(f"Excellent ROE of {roe:.1f}%")
                elif roe > 15:
                    score += 0.15
                    reasons.append(f"Good ROE of {roe:.1f}%")
                elif roe < 10:
                    score -= 0.1
                    reasons.append(f"Below average ROE of {roe:.1f}%")
            
            # ROCE analysis
            roce = ratios.get('roce') or basic_data.get('roce')
            if roce is not None:
                if roce > 20:
                    score += 0.15
                    reasons.append(f"Strong ROCE of {roce:.1f}%")
                elif roce > 15:
                    score += 0.1
                    reasons.append(f"Good ROCE of {roce:.1f}%")
                elif roce < 10:
                    score -= 0.1
                    reasons.append(f"Low ROCE of {roce:.1f}%")
            
            # Profit margin analysis
            profit_margin = basic_data.get('net_profit_margin')
            if profit_margin is not None:
                if profit_margin > 15:
                    score += 0.1
                    reasons.append(f"High profit margin of {profit_margin:.1f}%")
                elif profit_margin < 5:
                    score -= 0.05
                    reasons.append(f"Low profit margin of {profit_margin:.1f}%")
        
        except Exception as e:
            logger.error(f"Error in profitability analysis: {e}")
            reasons.append("Limited profitability data available")
        
        return max(0, min(1, score)), reasons
    
    def _analyze_governance(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze governance and management quality"""
        score = 0.5
        reasons = []
        
        try:
            shareholding = data.get('shareholding_pattern', {})
            
            # Promoter holding analysis
            promoter_holding = shareholding.get('promoters') or shareholding.get('promoter_holding')
            if promoter_holding is not None:
                if 40 <= promoter_holding <= 75:
                    score += 0.1
                    reasons.append(f"Healthy promoter holding of {promoter_holding:.1f}%")
                elif promoter_holding > 80:
                    score -= 0.05
                    reasons.append(f"Very high promoter holding of {promoter_holding:.1f}% may limit liquidity")
                elif promoter_holding < 25:
                    score -= 0.1
                    reasons.append(f"Low promoter holding of {promoter_holding:.1f}% may indicate lack of confidence")
            
            # Institutional holding analysis
            institutional_holding = shareholding.get('institutional_investors') or shareholding.get('institutional_holding')
            if institutional_holding is not None and institutional_holding > 20:
                score += 0.05
                reasons.append(f"Good institutional holding of {institutional_holding:.1f}%")
        
        except Exception as e:
            logger.error(f"Error in governance analysis: {e}")
            reasons.append("Limited governance data available")
        
        return max(0, min(1, score)), reasons
    
    def _calculate_growth_trend(self, quarterly_data: List[Dict], metric: str) -> Optional[float]:
        """Calculate growth trend for a specific metric"""
        try:
            values = []
            for quarter in quarterly_data[:4]:  # Last 4 quarters
                value = quarter.get(metric)
                if value is not None and isinstance(value, (int, float)):
                    values.append(value)
            
            if len(values) >= 2:
                # Calculate YoY growth if we have enough data
                recent_avg = np.mean(values[:2])  # Most recent 2 quarters
                older_avg = np.mean(values[-2:])  # Older 2 quarters
                
                if older_avg != 0:
                    growth = ((recent_avg - older_avg) / older_avg) * 100
                    return growth
            
            return None
        except Exception as e:
            logger.error(f"Error calculating growth trend for {metric}: {e}")
            return None
    
    def _determine_recommendation(self, score: float) -> RecommendationType:
        """Determine recommendation based on overall score"""
        if score >= 0.75:
            return RecommendationType.BUY
        elif score <= 0.35:
            return RecommendationType.SELL
        else:
            return RecommendationType.HOLD