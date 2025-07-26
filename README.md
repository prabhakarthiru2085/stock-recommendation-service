# Indian Stock Recommendation Service

A Python-based backend service that provides intelligent stock recommendations (Buy/Sell/Hold) for Indian companies based on comprehensive financial analysis of data scraped from Screener.in.

## 🚀 Features

- **Company Search**: Accept Indian company names and find matching stocks
- **Comprehensive Data Collection**: Scrapes multiple data sections from Screener.in:
  - Company Overview & Analysis
  - Quarterly Results
  - Financial Ratios (ROE, ROCE, Debt-to-Equity, etc.)
  - Balance Sheet & Cash Flow data
  - Shareholding Patterns
  - Recent Announcements
- **AI-Powered Analysis**: Rule-based analysis engine that evaluates:
  - Financial Health (30% weight)
  - Growth Trends (25% weight) 
  - Valuation Metrics (20% weight)
  - Profitability Ratios (15% weight)
  - Corporate Governance (10% weight)
- **REST API**: FastAPI-based endpoints for easy integration
- **Caching**: In-memory caching for improved performance
- **Error Handling**: Comprehensive error handling and validation

## 📋 Requirements

- Python 3.8+
- Chrome/Chromium browser (for Selenium)
- Internet connection for web scraping

## 🛠 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd stock-recommendation-service
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env file as needed
```

## 🚀 Running the Service

### Method 1: Using the run script (Recommended)
```bash
python run.py
```

### Method 2: Using uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at: `http://localhost:8000`

## 📖 API Documentation

Once the service is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### 1. Get Stock Recommendation
```http
POST /recommend
Content-Type: application/json

{
    "company_name": "Infosys"
}
```

**Response**:
```json
{
    "company_name": "Infosys",
    "recommendation": "Buy",
    "confidence_score": 0.78,
    "reasoning": [
        "Strong ROE of 24.5%",
        "Excellent revenue growth of 18.2%",
        "Healthy promoter holding of 45.3%"
    ],
    "key_metrics": {
        "overall_score": 0.78,
        "financial_health_score": 0.85,
        "growth_score": 0.72
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Get Raw Company Data
```http
GET /company/{company_name}/data
```

#### 3. Health Check
```http
GET /health
```

#### 4. Cache Management
```http
GET /cache/stats
DELETE /cache
```

## 🧠 Analysis Engine

The recommendation engine uses a weighted scoring system:

### Scoring Weights:
- **Financial Health (30%)**: Debt ratios, liquidity, interest coverage
- **Growth Trends (25%)**: Revenue and profit growth over quarters
- **Valuation (20%)**: P/E ratio, P/B ratio, dividend yield
- **Profitability (15%)**: ROE, ROCE, profit margins
- **Governance (10%)**: Promoter holding, institutional investment

### Recommendation Logic:
- **Score ≥ 0.75**: **BUY** recommendation
- **Score ≤ 0.35**: **SELL** recommendation  
- **0.35 < Score < 0.75**: **HOLD** recommendation

## 🔧 Configuration

Key configuration options in `config/settings.py`:

```python
# Server Configuration
HOST = "0.0.0.0"
PORT = 8000

# Scraping Configuration
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1.0

# Cache Configuration
CACHE_TTL = 3600  # 1 hour
MAX_CACHE_SIZE = 1000
```

## 📊 Example Usage

```python
import requests

# Get recommendation
response = requests.post(
    "http://localhost:8000/recommend",
    json={"company_name": "TCS"}
)

recommendation = response.json()
print(f"Recommendation: {recommendation['recommendation']}")
print(f"Confidence: {recommendation['confidence_score']}")
```

## ⚠️ Important Notes

### Rate Limiting
- The service implements rate limiting to respect Screener.in's servers
- Default: 1 request per second
- Configurable via `RATE_LIMIT_DELAY` setting

### Data Accuracy
- Data is scraped in real-time from Screener.in
- Recommendations are based on publicly available information
- This is for educational/analysis purposes only
- **Not financial advice** - consult professionals for investment decisions

### Legal Compliance
- Respects robots.txt and implements ethical scraping practices
- Uses appropriate delays between requests
- For educational and research purposes

## 🐛 Troubleshooting

### Common Issues:

1. **Chrome Driver Issues**:
```bash
# The service auto-downloads ChromeDriver, but if issues persist:
pip install --upgrade webdriver-manager
```

2. **Company Not Found**:
- Try exact company name as listed on Screener.in
- Check spelling and use common abbreviations

3. **Scraping Failures**:
- Check internet connection
- Verify Screener.in is accessible
- Check logs for detailed error messages

## 🔮 Future Enhancements

- [ ] Machine Learning model integration
- [ ] Redis caching for production use
- [ ] Database storage for historical analysis
- [ ] Real-time notifications
- [ ] Portfolio analysis features
- [ ] Technical analysis indicators
- [ ] Sector comparison tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please ensure compliance with Screener.in's terms of service and applicable laws.

## ⚡ Performance

- Average response time: 5-15 seconds (depends on data complexity)
- Concurrent requests: Supported with rate limiting
- Memory usage: ~50-100MB base + cache

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Create an issue in the repository