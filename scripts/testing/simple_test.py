#!/usr/bin/env python3
"""
Simple test script to verify Yahoo! API credentials are loaded
This tests basic setup without starting OAuth flow
"""

import os
from dotenv import load_dotenv

def simple_test():
    """Simple test of environment variables and basic setup"""
    print("🏈 Simple Yahoo! API Credential Test...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    client_id = os.getenv('YAHOO_CLIENT_ID')
    client_secret = os.getenv('YAHOO_CLIENT_SECRET')
    
    print(f"✅ Client ID: {client_id[:10]}..." if client_id else "❌ Client ID: Missing")
    print(f"✅ Client Secret: {client_secret[:10]}..." if client_secret else "❌ Client Secret: Missing")
    
    if not client_id or not client_secret:
        print("\n❌ Please add your Yahoo! API credentials to .env file:")
        print("YAHOO_CLIENT_ID=your_actual_client_id")
        print("YAHOO_CLIENT_SECRET=your_actual_client_secret")
        return False
    
    print("\n✅ Credentials are loaded successfully!")
    print("✅ Basic setup is working!")
    
    # Test basic API endpoint
    print("\n🌐 Testing basic API endpoint...")
    import requests
    
    try:
        # Test if we can reach Yahoo! API (without authentication)
        response = requests.get("https://fantasysports.yahooapis.com/fantasy/v2/game/nfl", timeout=10)
        print(f"✅ Yahoo! API endpoint reachable (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Error reaching Yahoo! API: {str(e)}")
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🎉 Basic test PASSED!")
        print("Your credentials are loaded and Yahoo! API is reachable!")
    else:
        print("\n💥 Basic test FAILED!")
        print("Please check your setup and try again.")
