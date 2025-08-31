#!/usr/bin/env python3
"""
Test Yahoo Fantasy Sports API with OAuth 2.0
Verify our authentication is working and we can retrieve data
"""

import os
import json
import requests
from dotenv import load_dotenv

def test_fantasy_api():
    """Test the Yahoo Fantasy Sports API with OAuth 2.0 tokens"""
    
    # Load environment variables
    load_dotenv()
    
    # Load OAuth 2.0 tokens
    tokens_file = "config/yahoo_oauth2_tokens.json"
    
    if not os.path.exists(tokens_file):
        print("❌ OAuth 2.0 tokens not found. Please run exchange_oauth2_code.py first.")
        return False
    
    try:
        with open(tokens_file, 'r') as f:
            tokens = json.load(f)
        
        access_token = tokens.get('access_token')
        token_type = tokens.get('token_type', 'Bearer')
        
        if not access_token:
            print("❌ No access token found in tokens file")
            return False
        
        print("🚀 Testing Yahoo Fantasy Sports API with OAuth 2.0")
        print("=" * 60)
        print(f"🔑 Access Token: {access_token[:20]}...")
        print(f"📝 Token Type: {token_type}")
        print()
        
        # Test 1: Get NFL game info
        print("📡 Test 1: Getting NFL game information...")
        headers = {
            'Authorization': f"{token_type} {access_token}",
            'User-Agent': 'FantasyFootballApp/1.0',
            'Accept': 'application/json'
        }
        
        # Test basic NFL game endpoint
        url = "https://fantasysports.yahooapis.com/fantasy/v2/game/nfl"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            print("✅ SUCCESS! API call worked!")
            
            try:
                data = response.json()
                print(f"📊 Response Data: {json.dumps(data, indent=2)[:500]}...")
                
                # Check if we got fantasy content
                if 'fantasy_content' in data:
                    print("🎉 FANTASY CONTENT RECEIVED!")
                    print("🏈 Yahoo Fantasy Sports API is working perfectly!")
                    return True
                else:
                    print("⚠️  Response received but no fantasy_content found")
                    print(f"📝 Full response: {data}")
                    return False
                    
            except json.JSONDecodeError:
                print("⚠️  Response received but not valid JSON")
                print(f"📝 Raw response: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📝 Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Main function"""
    print("🏈 Yahoo Fantasy Sports API Test")
    print("=" * 50)
    
    success = test_fantasy_api()
    
    print("=" * 50)
    if success:
        print("🏁 API test completed successfully!")
        print("🎉 OAuth 2.0 is working perfectly!")
        print("🚀 Ready to build your Fantasy Football app!")
    else:
        print("🏁 API test failed")
        print("📝 Check the error details above")

if __name__ == "__main__":
    main()
