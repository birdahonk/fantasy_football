#!/usr/bin/env python3
"""
Simple Yahoo! OAuth scope test - no complex imports
"""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

def main():
    print("🔍 Simple Yahoo! OAuth Scope Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('YAHOO_CLIENT_ID')
    if not client_id:
        print("❌ YAHOO_CLIENT_ID not found in .env file")
        return
    
    print(f"✅ Client ID: {client_id[:10]}...")
    
    # Test the basic scope that should work
    scope = 'fspt-r'
    redirect_uri = "https://tools.birdahonk.com/fantasy/oauth/callback/"
    base_auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
    
    print(f"\n🧪 Testing scope: '{scope}'")
    print(f"🔗 Redirect URI: {redirect_uri}")
    
    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope
    }
    
    auth_url = f"{base_auth_url}?{urlencode(auth_params)}"
    print(f"\n🌐 Auth URL: {auth_url}")
    
    # Try to open browser
    try:
        print("\n🚀 Opening browser...")
        webbrowser.open(auth_url)
        print("✅ Browser opened successfully!")
        print("\n📝 Check your browser for:")
        print("   - Success: URL with '?code=AUTHORIZATION_CODE'")
        print("   - Error: URL with '?error=invalid_scope'")
        print("\n🔄 Come back here and tell me what you see!")
        
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"📋 Copy this URL manually: {auth_url}")

if __name__ == "__main__":
    main()
