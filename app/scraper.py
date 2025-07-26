import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin, quote
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenerScraper:
    def __init__(self):
        self.base_url = "https://www.screener.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content"""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def _close_selenium(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def search_company(self, company_name: str) -> Optional[str]:
        """Search for company and return the company URL"""
        try:
            search_url = f"{self.base_url}/api/company/search/?q={quote(company_name)}"
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Return the URL of the first match
                    company_url = data[0].get('url', '')
                    if company_url:
                        return urljoin(self.base_url, company_url)
            
            return None
        except Exception as e:
            logger.error(f"Error searching for company {company_name}: {e}")
            return None
    
    def scrape_company_data(self, company_name: str) -> Dict[str, Any]:
        """Main method to scrape all company data"""
        try:
            company_url = self.search_company(company_name)
            if not company_url:
                logger.error(f"Company {company_name} not found")
                return {}
            
            logger.info(f"Found company URL: {company_url}")
            
            # Scrape basic page data
            basic_data = self._scrape_basic_data(company_url)
            
            # Scrape additional sections
            quarterly_data = self._scrape_quarterly_results(company_url)
            ratios_data = self._scrape_financial_ratios(company_url)
            shareholding_data = self._scrape_shareholding_pattern(company_url)
            
            return {
                'company_name': company_name,
                'company_url': company_url,
                'basic_data': basic_data,
                'quarterly_results': quarterly_data,
                'financial_ratios': ratios_data,
                'shareholding_pattern': shareholding_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping data for {company_name}: {e}")
            return {}
    
    def _scrape_basic_data(self, url: str) -> Dict[str, Any]:
        """Scrape basic company information"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {}
            
            # Company name and sector
            company_name = soup.find('h1')
            if company_name:
                data['name'] = company_name.get_text(strip=True)
            
            # Current price
            price_element = soup.find('span', class_='number')
            if price_element:
                price_text = price_element.get_text(strip=True).replace('₹', '').replace(',', '')
                try:
                    data['current_price'] = float(price_text)
                except ValueError:
                    pass
            
            # Key ratios table
            ratios_section = soup.find('div', {'id': 'top-ratios'})
            if ratios_section:
                ratio_items = ratios_section.find_all('li', class_='flex flex-space-between')
                for item in ratio_items:
                    name_elem = item.find('span', class_='name')
                    value_elem = item.find('span', class_='number')
                    
                    if name_elem and value_elem:
                        name = name_elem.get_text(strip=True).lower().replace(' ', '_')
                        value_text = value_elem.get_text(strip=True).replace('₹', '').replace(',', '').replace('%', '')
                        
                        try:
                            if value_text and value_text != '-':
                                data[name] = float(value_text)
                        except ValueError:
                            data[name] = value_text
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping basic data from {url}: {e}")
            return {}
    
    def _scrape_quarterly_results(self, url: str) -> List[Dict[str, Any]]:
        """Scrape quarterly results data"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Find quarterly results table
            quarterly_section = soup.find('section', {'id': 'quarters'})
            if quarterly_section:
                table = quarterly_section.find('table')
                if table:
                    headers = []
                    header_row = table.find('thead')
                    if header_row:
                        for th in header_row.find_all('th'):
                            headers.append(th.get_text(strip=True))
                    
                    tbody = table.find('tbody')
                    if tbody:
                        for row in tbody.find_all('tr'):
                            cells = row.find_all('td')
                            if len(cells) >= len(headers):
                                quarter_data = {}
                                for i, cell in enumerate(cells[:len(headers)]):
                                    if i < len(headers):
                                        value = cell.get_text(strip=True).replace('₹', '').replace(',', '')
                                        try:
                                            if value and value != '-':
                                                quarter_data[headers[i]] = float(value)
                                            else:
                                                quarter_data[headers[i]] = value
                                        except ValueError:
                                            quarter_data[headers[i]] = value
                                
                                if quarter_data:
                                    results.append(quarter_data)
            
            return results[:8]  # Return last 8 quarters
            
        except Exception as e:
            logger.error(f"Error scraping quarterly results: {e}")
            return []
    
    def _scrape_financial_ratios(self, url: str) -> Dict[str, Any]:
        """Scrape financial ratios"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            ratios = {}
            
            # Find ratios section
            ratios_section = soup.find('section', {'id': 'ratios'})
            if ratios_section:
                ratio_rows = ratios_section.find_all('tr')
                for row in ratio_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        name = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True).replace('%', '').replace(',', '')
                        
                        try:
                            if value and value != '-':
                                ratios[name.lower().replace(' ', '_')] = float(value)
                        except ValueError:
                            ratios[name.lower().replace(' ', '_')] = value
            
            return ratios
            
        except Exception as e:
            logger.error(f"Error scraping financial ratios: {e}")
            return {}
    
    def _scrape_shareholding_pattern(self, url: str) -> Dict[str, Any]:
        """Scrape shareholding pattern data"""
        try:
            # Navigate to investors tab
            investors_url = url.rstrip('/') + '/investors/'
            response = self.session.get(investors_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            shareholding = {}
            
            # Find shareholding table
            shareholding_section = soup.find('section', {'id': 'shareholding'})
            if shareholding_section:
                table = shareholding_section.find('table')
                if table:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            category = cells[0].get_text(strip=True)
                            percentage = cells[1].get_text(strip=True).replace('%', '')
                            
                            try:
                                if percentage and percentage != '-':
                                    shareholding[category.lower().replace(' ', '_')] = float(percentage)
                            except ValueError:
                                pass
            
            return shareholding
            
        except Exception as e:
            logger.error(f"Error scraping shareholding pattern: {e}")
            return {}
    
    def __del__(self):
        """Cleanup"""
        self._close_selenium()