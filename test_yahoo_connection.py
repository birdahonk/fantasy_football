#!/usr/bin/env python3
"""
Test script to verify Yahoo! Fantasy API connection
Run this to test your API credentials and basic connectivity
"""

import os
from dotenv import load_dotenv
from scripts.yahoo_connect import YahooFantasyAPI

def test_yahoo_connection():
    """Test basic Yahoo! API connectivity"""
    print("🏈 Testing Yahoo! Fantasy API Connection...")
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
    
    try:
        # Initialize API client
        print("\n🔌 Initializing Yahoo! API client...")
        api = YahooFantasyAPI()
        print("✅ API client initialized successfully")
        
        # Test basic connectivity
        print("\n🌐 Testing API connectivity...")
        if api.authenticate():
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_yahoo_connection()
    if success:
        print("\n🎉 Yahoo! API connection test PASSED!")
        print("Your credentials are working and ready for fantasy football data!")
    else:
        print("\n💥 Yahoo! API connection test FAILED!")
        print("Please check your credentials and try again.")
