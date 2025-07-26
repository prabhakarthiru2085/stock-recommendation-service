// Dashboard JavaScript for Stock Recommendation Service
document.addEventListener('DOMContentLoaded', function() {
    // Add enter key support for company input
    document.getElementById('companyInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeStock();
        }
    });
});

async function analyzeStock() {
    const companyName = document.getElementById('companyInput').value.trim();
    
    if (!companyName) {
        alert('Please enter a company name');
        return;
    }
    
    // Show loading, hide results and errors
    showLoading();
    hideResults();
    hideError();
    
    try {
        console.log(`Analyzing stock for: ${companyName}`);
        
        // Make API call to get recommendation
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                company_name: companyName
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const recommendationData = await response.json();
        console.log('Recommendation data:', recommendationData);
        
        // Get detailed company data
        const detailResponse = await fetch(`/company/${encodeURIComponent(companyName)}/data`);
        let detailData = null;
        
        if (detailResponse.ok) {
            detailData = await detailResponse.json();
            console.log('Detail data:', detailData);
        }
        
        // Hide loading and show results
        hideLoading();
        populateResults(recommendationData, detailData);
        showResults();
        
    } catch (error) {
        console.error('Error analyzing stock:', error);
        hideLoading();
        showError(`Failed to analyze ${companyName}. Please check the company name and try again.`);
    }
}

function populateResults(recommendationData, detailData) {
    // Populate recommendation section
    populateRecommendation(recommendationData);
    
    // Populate detailed data sections
    if (detailData && detailData.data) {
        populateCompanyOverview(detailData.data);
        populateFinancialRatios(detailData.data);
        populateQuarterlyResults(detailData.data);
        populateShareholdingPattern(detailData.data);
    }
    
    // Populate analysis scores
    populateAnalysisScores(recommendationData);
}

function populateRecommendation(data) {
    // Update company name
    document.getElementById('companyName').textContent = data.company_name;
    
    // Update recommendation badge
    const recommendationBadge = document.getElementById('recommendationBadge');
    const recommendationText = document.getElementById('recommendationText');
    
    recommendationText.textContent = data.recommendation;
    
    // Remove existing classes and add appropriate color class
    recommendationBadge.className = 'recommendation-badge';
    recommendationBadge.classList.add(data.recommendation.toLowerCase());
    
    // Update confidence score
    const confidenceScore = Math.round(data.confidence_score * 100);
    document.getElementById('confidenceScore').textContent = `${confidenceScore}%`;
    
    // Update confidence progress bar
    const confidenceProgress = document.getElementById('confidenceProgress');
    confidenceProgress.style.width = `${confidenceScore}%`;
    
    // Update reasoning list
    const reasoningList = document.getElementById('reasoningList');
    reasoningList.innerHTML = '';
    
    if (data.reasoning && data.reasoning.length > 0) {
        data.reasoning.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            reasoningList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No detailed reasoning available';
        reasoningList.appendChild(li);
    }
}

function populateCompanyOverview(data) {
    const basicData = data.basic_data || {};
    
    // Helper function to format currency
    const formatCurrency = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        if (isNaN(num)) return '-';
        
        if (num >= 10000000) {
            return `₹${(num / 10000000).toFixed(2)} Cr`;
        } else if (num >= 100000) {
            return `₹${(num / 100000).toFixed(2)} L`;
        } else {
            return `₹${num.toLocaleString()}`;
        }
    };
    
    // Helper function to format percentage
    const formatPercent = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        return isNaN(num) ? '-' : `${num.toFixed(2)}%`;
    };
    
    // Helper function to format ratio
    const formatRatio = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        return isNaN(num) ? '-' : num.toFixed(2);
    };
    
    // Update overview fields
    document.getElementById('currentPrice').textContent = formatCurrency(basicData.current_price);
    document.getElementById('marketCap').textContent = formatCurrency(basicData.market_cap);
    document.getElementById('peRatio').textContent = formatRatio(basicData.price_earnings || basicData.pe_ratio);
    document.getElementById('pbRatio').textContent = formatRatio(basicData.price_to_book || basicData.pb_ratio);
    document.getElementById('dividendYield').textContent = formatPercent(basicData.dividend_yield);
    document.getElementById('bookValue').textContent = formatCurrency(basicData.book_value);
}

function populateFinancialRatios(data) {
    const basicData = data.basic_data || {};
    const ratiosData = data.financial_ratios || {};
    
    // Helper function to format percentage
    const formatPercent = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        return isNaN(num) ? '-' : `${num.toFixed(2)}%`;
    };
    
    // Helper function to format ratio
    const formatRatio = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        return isNaN(num) ? '-' : num.toFixed(2);
    };
    
    // Update financial ratios
    document.getElementById('roe').textContent = formatPercent(ratiosData.roe || basicData.roe);
    document.getElementById('roce').textContent = formatPercent(ratiosData.roce || basicData.roce);
    document.getElementById('debtToEquity').textContent = formatRatio(ratiosData.debt_to_equity || basicData.debt_to_equity);
    document.getElementById('currentRatio').textContent = formatRatio(ratiosData.current_ratio || basicData.current_ratio);
    document.getElementById('interestCoverage').textContent = formatRatio(ratiosData.interest_coverage || basicData.interest_coverage);
    document.getElementById('assetTurnover').textContent = formatRatio(ratiosData.asset_turnover || basicData.asset_turnover);
}

function populateQuarterlyResults(data) {
    const quarterlyResults = data.quarterly_results || [];
    const tableBody = document.querySelector('#quarterlyTable tbody');
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (quarterlyResults.length === 0) {
        const row = tableBody.insertRow();
        const cell = row.insertCell(0);
        cell.colSpan = 6;
        cell.textContent = 'No quarterly data available';
        cell.style.textAlign = 'center';
        cell.style.color = '#7f8c8d';
        return;
    }
    
    // Helper function to format currency in crores
    const formatCrores = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        if (isNaN(num)) return '-';
        return (num / 10000000).toFixed(2); // Convert to crores
    };
    
    // Helper function to format growth percentage
    const formatGrowth = (value) => {
        if (!value || value === '-') return '-';
        const num = parseFloat(value);
        if (isNaN(num)) return '-';
        const formatted = num.toFixed(2);
        return num >= 0 ? `+${formatted}%` : `${formatted}%`;
    };
    
    // Populate quarterly data (show last 4 quarters)
    quarterlyResults.slice(0, 4).forEach(quarter => {
        const row = tableBody.insertRow();
        
        // Quarter
        const quarterCell = row.insertCell(0);
        quarterCell.textContent = quarter.Quarter || quarter.quarter || '-';
        
        // Revenue
        const revenueCell = row.insertCell(1);
        revenueCell.textContent = formatCrores(quarter.Sales || quarter.revenue);
        
        // Net Profit
        const profitCell = row.insertCell(2);
        profitCell.textContent = formatCrores(quarter['Net Profit'] || quarter.net_profit);
        
        // EPS
        const epsCell = row.insertCell(3);
        const eps = quarter.EPS || quarter.eps;
        epsCell.textContent = eps ? `₹${parseFloat(eps).toFixed(2)}` : '-';
        
        // Revenue Growth
        const revenueGrowthCell = row.insertCell(4);
        revenueGrowthCell.textContent = formatGrowth(quarter['Sales Growth'] || quarter.revenue_growth);
        
        // Profit Growth
        const profitGrowthCell = row.insertCell(5);
        profitGrowthCell.textContent = formatGrowth(quarter['Profit Growth'] || quarter.profit_growth);
        
        // Add color coding for growth
        const revenueGrowthValue = parseFloat(quarter['Sales Growth'] || quarter.revenue_growth || 0);
        const profitGrowthValue = parseFloat(quarter['Profit Growth'] || quarter.profit_growth || 0);
        
        if (revenueGrowthValue > 0) {
            revenueGrowthCell.style.color = '#27ae60';
        } else if (revenueGrowthValue < 0) {
            revenueGrowthCell.style.color = '#e74c3c';
        }
        
        if (profitGrowthValue > 0) {
            profitGrowthCell.style.color = '#27ae60';
        } else if (profitGrowthValue < 0) {
            profitGrowthCell.style.color = '#e74c3c';
        }
    });
}

function populateShareholdingPattern(data) {
    const shareholding = data.shareholding_pattern || {};
    
    // Helper function to update shareholding bar
    const updateShareholdingBar = (barId, percentId, value) => {
        const bar = document.getElementById(barId);
        const percent = document.getElementById(percentId);
        
        const percentage = parseFloat(value) || 0;
        bar.style.width = `${percentage}%`;
        percent.textContent = `${percentage.toFixed(1)}%`;
    };
    
    // Update shareholding pattern
    updateShareholdingBar('promoterBar', 'promoterPercent', 
        shareholding.promoters || shareholding.promoter_holding || 0);
    
    updateShareholdingBar('publicBar', 'publicPercent', 
        shareholding.public || shareholding.public_holding || 0);
    
    updateShareholdingBar('institutionalBar', 'institutionalPercent', 
        shareholding.institutional_investors || shareholding.institutional_holding || 0);
}

function populateAnalysisScores(data) {
    const keyMetrics = data.key_metrics || {};
    
    // Helper function to update score bar
    const updateScoreBar = (barId, scoreId, value) => {
        const bar = document.getElementById(barId);
        const scoreElement = document.getElementById(scoreId);
        
        const score = parseFloat(value) || 0;
        const percentage = Math.min(score * 100, 100); // Convert to percentage, max 100%
        
        bar.style.width = `${percentage}%`;
        scoreElement.textContent = score.toFixed(2);
        
        // Color coding based on score
        if (score >= 0.75) {
            bar.style.background = 'linear-gradient(90deg, #27ae60, #2ecc71)';
        } else if (score >= 0.5) {
            bar.style.background = 'linear-gradient(90deg, #f39c12, #e67e22)';
        } else {
            bar.style.background = 'linear-gradient(90deg, #e74c3c, #c0392b)';
        }
    };
    
    // Update analysis scores
    updateScoreBar('financialBar', 'financialScore', keyMetrics.financial_health_score);
    updateScoreBar('growthBar', 'growthScore', keyMetrics.growth_score);
    updateScoreBar('valuationBar', 'valuationScore', keyMetrics.valuation_score);
    updateScoreBar('profitabilityBar', 'profitabilityScore', keyMetrics.profitability_score);
    updateScoreBar('governanceBar', 'governanceScore', keyMetrics.governance_score);
}

// Utility functions
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('analyzeBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('analyzeBtn').innerHTML = '<i class="fas fa-search"></i> Analyze Stock';
}

function showResults() {
    document.getElementById('resultsSection').classList.remove('hidden');
    // Smooth scroll to results
    document.getElementById('resultsSection').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

function hideResults() {
    document.getElementById('resultsSection').classList.add('hidden');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').classList.remove('hidden');
    // Smooth scroll to error
    document.getElementById('errorSection').scrollIntoView({ 
        behavior: 'smooth',
        block: 'center'
    });
}

function hideError() {
    document.getElementById('errorSection').classList.add('hidden');
}

// Function to clear the search and results
function clearSearch() {
    document.getElementById('companyInput').value = '';
    hideResults();
    hideError();
}

// Function to try a sample company
function trySampleCompany(companyName) {
    document.getElementById('companyInput').value = companyName;
    analyzeStock();
}

// Add some sample company buttons (you can call this from HTML if needed)
function addSampleButtons() {
    const searchContainer = document.querySelector('.search-container');
    const samplesDiv = document.createElement('div');
    samplesDiv.innerHTML = `
        <div style="text-align: center; margin-top: 20px;">
            <p style="color: #7f8c8d; margin-bottom: 10px;">Try these popular stocks:</p>
            <button onclick="trySampleCompany('Infosys')" class="sample-btn">Infosys</button>
            <button onclick="trySampleCompany('TCS')" class="sample-btn">TCS</button>
            <button onclick="trySampleCompany('HDFC Bank')" class="sample-btn">HDFC Bank</button>
            <button onclick="trySampleCompany('Reliance')" class="sample-btn">Reliance</button>
        </div>
    `;
    
    // Add CSS for sample buttons
    const style = document.createElement('style');
    style.textContent = `
        .sample-btn {
            margin: 5px;
            padding: 8px 15px;
            background: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 20px;
            color: #2c3e50;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        .sample-btn:hover {
            background: #3498db;
            color: white;
            border-color: #3498db;
        }
    `;
    document.head.appendChild(style);
    
    searchContainer.appendChild(samplesDiv);
}

// Call this when page loads if you want sample buttons
// addSampleButtons();