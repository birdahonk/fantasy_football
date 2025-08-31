#!/usr/bin/env python3
"""
Minimal test to check if Yahoo! API rate limits have reset
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from dotenv import load_dotenv
import requests

def test_minimal_api():
    """Test if we can reach Yahoo! API without hitting rate limits"""
    print("🔍 Testing minimal Yahoo! API connectivity...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    client_id = os.getenv('YAHOO_CLIENT_ID')
    client_secret = os.getenv('YAHOO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Yahoo! API credentials in .env file")
        return False
    
    try:
        print("🌐 Testing basic API endpoint reachability...")
        
        # Test a simple endpoint that doesn't require OAuth
        # This will help us see if rate limits have reset
        test_url = "https://fantasysports.yahooapis.com/fantasy/v2/game/nfl"
        
        print(f"   Testing: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("✅ API is reachable! 401 is expected without OAuth token")
            print("✅ Rate limits appear to have reset!")
            return True
        elif response.status_code == 429:
            print("⏳ Still rate limited - need to wait longer")
            return False
        else:
            print(f"📡 Unexpected response: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_minimal_api()
    if success:
        print("\n🎉 Minimal API test PASSED!")
        print("Rate limits appear to have reset - ready to try OAuth!")
    else:
        print("\n⏳ Still need to wait for rate limits to reset")
        print("Try again in another 10-15 minutes")
