#!/usr/bin/env python3
"""
Simple test script to verify the stock recommendation service
"""

import requests
import json
import time

# Service configuration
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Is it running?")
        return False

def test_recommendation(company_name):
    """Test stock recommendation for a company"""
    print(f"\n📊 Testing recommendation for: {company_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommend",
            json={"company_name": company_name},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendation: {data['recommendation']}")
            print(f"📈 Confidence Score: {data['confidence_score']:.2f}")
            print("💡 Key Reasons:")
            for reason in data['reasoning'][:3]:  # Show first 3 reasons
                print(f"   • {reason}")
            return True
        elif response.status_code == 404:
            print(f"❌ Company '{company_name}' not found")
            return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this is normal for first requests)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_company_data(company_name):
    """Test raw company data endpoint"""
    print(f"\n🔍 Testing raw data for: {company_name}")
    
    try:
        response = requests.get(f"{BASE_URL}/company/{company_name}/data", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Raw data retrieved successfully")
            print(f"📊 Data sections available: {list(data['data'].keys())}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Stock Recommendation Service Test")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Service is not running. Please start it first:")
        print("   python run.py")
        return
    
    # Test companies (mix of large and smaller companies)
    test_companies = [
        "Infosys",
        "TCS", 
        "HDFC Bank",
        "Reliance"
    ]
    
    successful_tests = 0
    total_tests = len(test_companies)
    
    for company in test_companies:
        print(f"\n{'='*20} {company} {'='*20}")
        
        # Test recommendation
        if test_recommendation(company):
            successful_tests += 1
            
        # Add small delay between requests
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Test Summary:")
    print(f"   Successful: {successful_tests}/{total_tests}")
    print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Service is working correctly.")
    elif successful_tests > 0:
        print("⚠️  Some tests passed. Service is partially working.")
    else:
        print("❌ No tests passed. Please check the service.")
    
    # Test cache stats
    print(f"\n🗄️ Testing cache stats...")
    try:
        response = requests.get(f"{BASE_URL}/cache/stats")
        if response.status_code == 200:
            cache_data = response.json()
            print(f"✅ Cache contains {cache_data['cached_companies']} companies")
        else:
            print("❌ Could not retrieve cache stats")
    except Exception as e:
        print(f"❌ Cache stats error: {e}")

if __name__ == "__main__":
    main()