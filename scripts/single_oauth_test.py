#!/usr/bin/env python3
"""
Single OAuth 1.0a Test - Makes exactly ONE attempt and stops
This script is designed to test OAuth authentication without triggering rate limits
"""

import os
import sys
from dotenv import load_dotenv

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yahoo_connect import YahooFantasyAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Make exactly ONE OAuth attempt and report results"""
    print("🚀 Single OAuth 1.0a Test - ONE ATTEMPT ONLY")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if we have the required environment variables
    if not os.getenv('YAHOO_CLIENT_ID'):
        print("❌ Error: YAHOO_CLIENT_ID not found in environment")
        print("Please set YAHOO_CLIENT_ID in your .env file")
        return False
    
    if not os.getenv('YAHOO_CLIENT_SECRET'):
        print("❌ Error: YAHOO_CLIENT_SECRET not found in environment")
        print("Please set YAHOO_CLIENT_SECRET in your .env file")
        return False
    
    print("✅ Environment variables loaded")
    print("📡 Making ONE OAuth request token attempt...")
    print("⚠️  This script will make exactly ONE attempt and then stop")
    print()
    
    try:
        # Create API instance
        api = YahooFantasyAPI()
        
        print("🔐 Starting OAuth 1.0a flow...")
        print("📝 This will open your browser for Yahoo authentication")
        print("⚠️  The authenticate() method will check for existing tokens first")
        print()
        
        # Make exactly ONE authentication attempt
        success = api.authenticate()
        
        if success:
            print("🎉 SUCCESS! OAuth 1.0a authentication completed!")
            print("✅ You now have valid access tokens")
            print("🚀 Ready to make API calls to Yahoo Fantasy Sports")
            return True
        else:
            print("❌ OAuth 1.0a authentication failed")
            print("📊 Check the logs above for specific error details")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error during OAuth test: {e}")
        logger.exception("OAuth test failed with exception")
        return False

if __name__ == "__main__":
    print("🔒 Single OAuth Test - ONE ATTEMPT ONLY")
    print("⚠️  This script will NOT retry or make multiple attempts")
    print("=" * 60)
    
    success = main()
    
    print("=" * 60)
    if success:
        print("🏁 Test completed successfully!")
    else:
        print("🏁 Test completed with errors")
    
    print("📝 Check the logs above for detailed information")
    print("💡 If you see rate limiting, wait longer before testing again")
