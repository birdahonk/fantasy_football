#!/usr/bin/env python3
"""
Generate Fresh OAuth 2.0 Authorization URL
Quick script to get a new authorization code
"""

import os
from urllib.parse import urlencode
from dotenv import load_dotenv

def main():
    """Generate fresh OAuth 2.0 authorization URL"""
    
    # Load environment variables
    load_dotenv()
    
    # OAuth 2.0 endpoints
    auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
    
    # Client credentials
    client_id = os.getenv('YAHOO_CLIENT_ID')
    redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'https://tools.birdahonk.com/fantasy/oauth/callback')
    scopes = os.getenv('YAHOO_SCOPES', 'fspt-w')
    
    print("🚀 Generate Fresh OAuth 2.0 Authorization URL")
    print("=" * 60)
    
    # Build authorization URL
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scopes,
        'state': 'fantasy_football_app'
    }
    
    auth_url_full = f"{auth_url}?{urlencode(params)}"
    
    print("🔐 Fresh OAuth 2.0 Authorization URL:")
    print(f"🌐 {auth_url_full}")
    print()
    print("📝 Instructions:")
    print("1. Copy the URL above")
    print("2. Open it in your browser")
    print("3. Complete the authentication")
    print("4. Copy the new authorization code from the callback URL")
    print("5. Run exchange_oauth2_code.py with the new code")
    print()
    print("💡 Since you're already authenticated, this should be quick!")

if __name__ == "__main__":
    main()
