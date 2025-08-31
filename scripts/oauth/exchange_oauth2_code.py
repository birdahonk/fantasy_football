#!/usr/bin/env python3
"""
Exchange OAuth 2.0 Authorization Code for Access Tokens
Simple script to complete the OAuth 2.0 flow
"""

import os
import json
import requests
from dotenv import load_dotenv

def exchange_code_for_tokens(authorization_code):
    """Exchange authorization code for access and refresh tokens"""
    
    # Load environment variables
    load_dotenv()
    
    # OAuth 2.0 token endpoint
    token_url = "https://api.login.yahoo.com/oauth2/get_token"
    
    # Client credentials
    client_id = os.getenv('YAHOO_CLIENT_ID')
    client_secret = os.getenv('YAHOO_CLIENT_SECRET')
    redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'https://tools.birdahonk.com/fantasy/oauth/callback')
    
    print("🔐 Exchanging OAuth 2.0 authorization code for tokens...")
    print(f"📱 Client ID: {client_id}")
    print(f"🔗 Redirect URI: {redirect_uri}")
    print(f"🔑 Authorization Code: {authorization_code[:10]}...")
    print()
    
    # Prepare the token exchange request
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id
    }
    
    # Include client secret if available
    if client_secret:
        data['client_secret'] = client_secret
        print("✅ Client secret included")
    else:
        print("⚠️  No client secret found")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'FantasyFootballApp/1.0'
    }
    
    print("\n📡 Making token exchange request...")
    print(f"🌐 URL: {token_url}")
    print(f"📋 Data: {data}")
    print()
    
    try:
        response = requests.post(token_url, data=data, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Response Body: {response.text}")
        print()
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("🎉 SUCCESS! Tokens received:")
            print(f"🔑 Access Token: {token_data.get('access_token', 'N/A')[:20]}...")
            print(f"🔄 Refresh Token: {token_data.get('refresh_token', 'N/A')[:20]}...")
            print(f"📝 Token Type: {token_data.get('token_type', 'N/A')}")
            print(f"⏰ Expires In: {token_data.get('expires_in', 'N/A')} seconds")
            print(f"📋 Scope: {token_data.get('scope', 'N/A')}")
            
            # Save tokens to file
            tokens_file = "config/yahoo_oauth2_tokens.json"
            os.makedirs(os.path.dirname(tokens_file), exist_ok=True)
            
            with open(tokens_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"\n💾 Tokens saved to: {tokens_file}")
            return True
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📝 Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

def main():
    """Main function"""
    print("🚀 OAuth 2.0 Token Exchange")
    print("=" * 50)
    
    # Use the authorization code from the callback
    authorization_code = "6q52fybnqheg5x7gwwnh848hacjupqay"
    
    print(f"🔑 Using authorization code: {authorization_code}")
    print()
    
    success = exchange_code_for_tokens(authorization_code)
    
    print("=" * 50)
    if success:
        print("🏁 Token exchange completed successfully!")
        print("🎉 You now have OAuth 2.0 access tokens!")
        print("🚀 Ready to make API calls to Yahoo Fantasy Sports!")
    else:
        print("🏁 Token exchange failed")
        print("📝 Check the error details above")

if __name__ == "__main__":
    main()
