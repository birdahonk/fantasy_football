#!/usr/bin/env python3
"""
Test multiple Yahoo! OAuth scopes to find the correct one
"""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

def test_scope(scope_name, scope_value):
    """Test a specific OAuth scope"""
    print(f"\n🧪 Testing scope: '{scope_name}' = '{scope_value}'")
    
    load_dotenv()
    client_id = os.getenv('YAHOO_CLIENT_ID')
    if not client_id:
        print("❌ YAHOO_CLIENT_ID not found")
        return False
    
    redirect_uri = "https://tools.birdahonk.com/fantasy/oauth/callback/"
    base_auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
    
    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
    }
    
    if scope_value:
        auth_params['scope'] = scope_value
    
    auth_url = f"{base_auth_url}?{urlencode(auth_params)}"
    print(f"🔗 Auth URL: {auth_url}")
    
    # Ask user if they want to test this
    test_this = input(f"   Test scope '{scope_name}'? (y/n/q to quit): ").strip().lower()
    
    if test_this == 'q':
        return 'quit'
    elif test_this != 'y':
        return False
    
    try:
        print(f"   🚀 Opening browser for '{scope_name}'...")
        webbrowser.open(auth_url)
        print(f"   ✅ Browser opened for '{scope_name}'")
        print(f"   📝 Complete the OAuth flow and check the final URL")
        print(f"   🔍 Look for success (?code=...) or error (?error=...)")
        
        input(f"   Press Enter when done testing '{scope_name}'...")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   📋 Copy this URL manually: {auth_url}")
        return False

def main():
    print("🔍 Yahoo! OAuth Scope Testing - Multiple Options")
    print("=" * 55)
    
    # List of scopes to test
    scopes_to_test = [
        ("No Scope", ""),
        ("Fantasy Sports Read", "fspt-r"),
        ("Fantasy Sports Write", "fspt-w"),
        ("Fantasy Sports RW", "fspt-rw"),
        ("OpenID Connect", "openid"),
        ("Email Access", "email"),
        ("Profile Access", "profile"),
        ("Basic Fantasy", "fantasy"),
        ("Sports Access", "sports"),
        ("Read Access", "read"),
        ("Write Access", "write")
    ]
    
    print("📋 Available scopes to test:")
    for i, (name, value) in enumerate(scopes_to_test, 1):
        display_value = value if value else "(empty)"
        print(f"   {i:2d}. {name:20} = '{display_value}'")
    
    print("\n🚀 Starting scope testing...")
    print("💡 Test each scope and tell me what happens!")
    
    for name, value in scopes_to_test:
        result = test_scope(name, value)
        if result == 'quit':
            print("\n🛑 Testing stopped by user")
            break
        elif result:
            print(f"   ✅ Completed testing '{name}'")
        else:
            print(f"   ⏭️  Skipped testing '{name}'")
    
    print("\n🎯 Scope testing complete!")
    print("📋 Tell me which scope worked (gave you a code) or which gave errors")

if __name__ == "__main__":
    main()
