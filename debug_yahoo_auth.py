#!/usr/bin/env python3
"""
Debug script to test Yahoo! OAuth scopes and identify the correct one
This will help us understand what scope Yahoo! expects for Fantasy Sports API
"""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

def test_yahoo_scopes():
    """Test different OAuth scopes to find the correct one"""
    print("🔍 Debugging Yahoo! OAuth Scopes...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('YAHOO_CLIENT_ID')
    if not client_id:
        print("❌ YAHOO_CLIENT_ID not found in .env file")
        return
    
    print(f"✅ Client ID: {client_id[:10]}...")
    
    # Test different scopes
    scopes_to_test = [
        'fspt-r',      # Fantasy Sports Read
        'fspt-w',      # Fantasy Sports Read/Write
        'fspt-rw',     # Alternative Fantasy Sports scope
        '',            # No scope (let Yahoo! decide)
        'openid',      # OpenID Connect
        'email',       # Email access
        'profile'      # Profile access
    ]
    
    base_auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
    redirect_uri = "https://tools.birdahonk.com/fantasy/oauth/callback/"
    
    print(f"\n🔗 Redirect URI: {redirect_uri}")
    print(f"🌐 Base Auth URL: {base_auth_url}")
    
    print("\n🧪 Testing different OAuth scopes:")
    print("-" * 40)
    
    for i, scope in enumerate(scopes_to_test, 1):
        scope_display = scope if scope else "(no scope)"
        print(f"{i}. Testing scope: '{scope_display}'")
        
        auth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
        }
        
        if scope:
            auth_params['scope'] = scope
        
        auth_url = f"{base_auth_url}?{urlencode(auth_params)}"
        print(f"   Auth URL: {auth_url}")
        
        # Ask user if they want to test this scope
        test_this = input(f"   Test scope '{scope_display}'? (y/n): ").strip().lower()
        
        if test_this == 'y':
            print(f"   🌐 Opening browser for scope: '{scope_display}'")
            try:
                webbrowser.open(auth_url)
                print(f"   ✅ Browser opened for scope: '{scope_display}'")
                print(f"   📝 Check the URL in your browser for any error messages")
                print(f"   🔄 Come back here when you're done testing this scope")
                
                input(f"   Press Enter when you've tested scope '{scope_display}'...")
                
            except Exception as e:
                print(f"   ❌ Error opening browser: {e}")
                print(f"   📋 Copy this URL manually: {auth_url}")
        
        print()  # Empty line for readability
    
    print("🎯 Scope testing complete!")
    print("📋 Check your browser for which scopes work and which give errors")
    print("🔍 Look for error messages in the URL like 'error=invalid_scope'")

if __name__ == "__main__":
    test_yahoo_scopes()
