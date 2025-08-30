#!/usr/bin/env python3
"""
Test script for corrected OAuth 1.0a Yahoo! Fantasy API
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from dotenv import load_dotenv
from yahoo_connect import YahooFantasyAPI

def test_oauth1():
    """Test the corrected OAuth 1.0a implementation"""
    print("🏈 Testing Yahoo! Fantasy API with OAuth 1.0a...")
    print("=" * 55)
    
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
        print("\n🔌 Initializing Yahoo! API client (OAuth 1.0a)...")
        api = YahooFantasyAPI()
        print("✅ API client initialized successfully")
        
        # Test authentication
        print("\n🌐 Testing OAuth 1.0a authentication...")
        if api.authenticate():
            print("✅ OAuth 1.0a authentication successful!")
            
            # Test basic API call
            print("\n📡 Testing basic API call...")
            result = api.discover_league_info()
            if result:
                print("✅ API call successful!")
                print(f"   Status: {result.get('status', 'unknown')}")
                print(f"   Data length: {len(result.get('data', ''))} characters")
                return True
            else:
                print("❌ API call failed")
                return False
        else:
            print("❌ OAuth 1.0a authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oauth1()
    if success:
        print("\n🎉 Yahoo! API OAuth 1.0a test PASSED!")
        print("Your credentials are working with the correct OAuth implementation!")
    else:
        print("\n💥 Yahoo! API OAuth 1.0a test FAILED!")
        print("Please check your credentials and try again.")
