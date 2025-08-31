#!/usr/bin/env python3
"""
Safe API Test - Minimal connection check
Only tests basic connectivity, no OAuth attempts
"""

import requests
import time

def test_basic_connectivity():
    """Test basic API connectivity without authentication"""
    print("🔍 Testing basic Yahoo! Fantasy Sports API connectivity...")
    print("⚠️  This is a SAFE test - NO OAuth attempts")
    print()
    
    # Test the most basic endpoint that doesn't require authentication
    test_url = "https://fantasysports.yahooapis.com/fantasy/v2/game/nfl"
    
    try:
        print(f"📡 Testing endpoint: {test_url}")
        print("⏳ Making single request...")
        
        # Single, simple request
        response = requests.get(test_url, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("✅ API is responding (401 = Unauthorized, which is expected)")
            print("✅ Rate limits appear to have reset")
            print("✅ Basic connectivity is working")
        elif response.status_code == 429:
            print("⏳ Still rate limited (429)")
            print("⏳ Need to wait longer for OAuth endpoints to reset")
        else:
            print(f"📊 Unexpected status: {response.status_code}")
            
        print()
        print("🔒 This test did NOT attempt OAuth authentication")
        print("🔒 It only checked basic API connectivity")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Safe API Test - Starting...")
    print("=" * 50)
    
    test_basic_connectivity()
    
    print("=" * 50)
    print("🏁 Safe API Test - Complete")
    print("💡 If you see '401 Unauthorized', the API is ready for OAuth testing")
    print("💡 If you see '429 Rate Limited', wait longer before OAuth attempts")
