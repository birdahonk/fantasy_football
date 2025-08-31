#!/usr/bin/env python3
"""
Simple OAuth 2.0 Test Script
Tests the new OAuth 2.0 client without triggering rate limits
"""

import os
import sys
from dotenv import load_dotenv

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from oauth2_client import YahooOAuth2Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test OAuth 2.0 client"""
    print("🚀 Testing Yahoo OAuth 2.0 Client")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['YAHOO_CLIENT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ Environment variables loaded")
    print(f"📱 Client ID: {os.getenv('YAHOO_CLIENT_ID')}")
    print(f"🔗 Redirect URI: {os.getenv('YAHOO_REDIRECT_URI', 'https://tools.birdahonk.com/fantasy/oauth/callback')}")
    print(f"📋 Scopes: {os.getenv('YAHOO_SCOPES', 'fspt-w')}")
    print()
    
    try:
        # Create OAuth 2.0 client
        client = YahooOAuth2Client()
        
        # Check if already authenticated
        if client.is_authenticated():
            print("✅ Already authenticated with OAuth 2.0")
            print("🎯 Testing API call...")
            
            # Test a simple API call
            result = client.make_request("game/nfl")
            if result and result['status'] == 'success':
                print("✅ API call successful!")
                print("🎉 OAuth 2.0 is working correctly!")
                return True
            else:
                print("❌ API call failed")
                return False
        else:
            print("🔐 Starting OAuth 2.0 authentication...")
            print("⚠️  This will open your browser for Yahoo authentication")
            print()
            
            if client.authenticate():
                print("✅ OAuth 2.0 authentication successful!")
                print("🎯 Testing API call...")
                
                # Test API call after authentication
                result = client.make_request("game/nfl")
                if result and result['status'] == 'success':
                    print("✅ API call successful!")
                    print("🎉 OAuth 2.0 is working correctly!")
                    return True
                else:
                    print("❌ API call failed")
                    return False
            else:
                print("❌ OAuth 2.0 authentication failed")
                return False
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("OAuth 2.0 test failed with exception")
        return False

if __name__ == "__main__":
    print("🔒 OAuth 2.0 Test - Single Attempt")
    print("⚠️  This script will make ONE OAuth 2.0 attempt")
    print("=" * 50)
    
    success = main()
    
    print("=" * 50)
    if success:
        print("🏁 Test completed successfully!")
        print("🎉 OAuth 2.0 is working and ready for use!")
    else:
        print("🏁 Test completed with errors")
        print("📝 Check the logs above for detailed information")
    
    print("\n💡 If OAuth 2.0 works, we can migrate away from OAuth 1.0a")
    print("💡 If it fails, we know the issue is with Yahoo's OAuth endpoints in general")
