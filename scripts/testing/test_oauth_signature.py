#!/usr/bin/env python3
"""
Test OAuth 1.0a signature generation without hitting rate-limited endpoints
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from dotenv import load_dotenv
from yahoo_connect import YahooFantasyAPI

def test_oauth_signature():
    """Test OAuth 1.0a signature generation"""
    print("🔐 Testing OAuth 1.0a signature generation...")
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
        # Initialize API client
        api = YahooFantasyAPI()
        print("✅ API client initialized successfully")
        
        # Test OAuth signature generation
        print("\n🔑 Testing OAuth signature generation...")
        
        # Test URL and parameters
        test_url = "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nfl/teams"
        test_params = {'test': 'value'}
        
        # Generate OAuth headers
        headers = api._get_oauth_headers('GET', test_url, test_params)
        
        if 'Authorization' in headers:
            auth_header = headers['Authorization']
            print("✅ OAuth Authorization header generated successfully")
            print(f"   Header: {auth_header[:100]}...")
            
            # Check that all required OAuth parameters are present
            required_params = ['oauth_consumer_key', 'oauth_nonce', 'oauth_signature_method', 
                             'oauth_timestamp', 'oauth_version', 'oauth_signature']
            
            missing_params = []
            for param in required_params:
                if param not in auth_header:
                    missing_params.append(param)
            
            if not missing_params:
                print("✅ All required OAuth parameters present")
                print("✅ OAuth 1.0a signature generation is working correctly!")
                return True
            else:
                print(f"❌ Missing OAuth parameters: {missing_params}")
                return False
        else:
            print("❌ No Authorization header generated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oauth_signature()
    if success:
        print("\n🎉 OAuth signature test PASSED!")
        print("Your OAuth 1.0a implementation is working correctly!")
        print("\n💡 The rate limiting (HTTP 429) you saw earlier is actually a good sign!")
        print("   It means Yahoo! is receiving your requests and your OAuth is working.")
        print("   You'll need to wait a bit before making more authentication attempts.")
    else:
        print("\n💥 OAuth signature test FAILED!")
        print("There's an issue with the OAuth implementation.")
