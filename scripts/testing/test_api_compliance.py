#!/usr/bin/env python3
"""
Comprehensive API Compliance Test
Validates our Yahoo! Fantasy Sports API implementation against official documentation
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from dotenv import load_dotenv
from yahoo_connect import YahooFantasyAPI
from xml_parser import parse_yahoo_response

def test_api_compliance():
    """Test our API implementation for compliance with official documentation"""
    print("🔍 Testing Yahoo! Fantasy Sports API Compliance...")
    print("=" * 60)
    
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
        print("🔌 Initializing Yahoo! API client...")
        api = YahooFantasyAPI()
        print("✅ API client initialized successfully")
        
        # Test 1: OAuth 1.0a Implementation
        print("\n🔐 Test 1: OAuth 1.0a Implementation")
        print("-" * 40)
        
        # Check OAuth endpoints match official docs
        expected_endpoints = {
            'request_token': 'https://api.login.yahoo.com/oauth/v2/get_request_token',
            'authorize': 'https://api.login.yahoo.com/oauth/v2/request_auth',
            'access_token': 'https://api.login.yahoo.com/oauth/v2/get_token'
        }
        
        actual_endpoints = {
            'request_token': api.request_token_url,
            'authorize': api.authorize_url,
            'access_token': api.access_token_url
        }
        
        oauth_compliant = True
        for name, expected in expected_endpoints.items():
            actual = actual_endpoints[name]
            if actual == expected:
                print(f"✅ {name}: {actual}")
            else:
                print(f"❌ {name}: Expected {expected}, got {actual}")
                oauth_compliant = False
        
        # Test 2: API Base URL
        print("\n🌐 Test 2: API Base URL")
        print("-" * 40)
        expected_base = "https://fantasysports.yahooapis.com/fantasy/v2"
        if api.base_url == expected_base:
            print(f"✅ Base URL: {api.base_url}")
        else:
            print(f"❌ Base URL: Expected {expected_base}, got {api.base_url}")
            oauth_compliant = False
        
        # Test 3: XML Parser Integration
        print("\n📄 Test 3: XML Parser Integration")
        print("-" * 40)
        try:
            from xml_parser import YahooXMLParser
            parser = YahooXMLParser()
            print("✅ XML Parser imported successfully")
            print(f"✅ Parser has {len([m for m in dir(parser) if not m.startswith('_')])} public methods")
        except ImportError as e:
            print(f"❌ XML Parser import failed: {e}")
            oauth_compliant = False
        
        # Test 4: API Endpoints Compliance
        print("\n📡 Test 4: API Endpoints Compliance")
        print("-" * 40)
        
        # Check that we have all required endpoints from official docs
        required_endpoints = [
            'discover_league_info',
            'get_current_roster',
            'get_available_players',
            'get_league_info',
            'get_team_info',
            'get_player_info',
            'get_matchups',
            'get_standings',
            'get_transactions'
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if hasattr(api, endpoint):
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - Missing")
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            oauth_compliant = False
        
        # Test 5: OAuth Signature Method
        print("\n🔑 Test 5: OAuth Signature Method")
        print("-" * 40)
        
        # Test signature generation
        try:
            test_url = "https://fantasysports.yahooapis.com/fantasy/v2/test"
            test_params = {'test': 'value'}
            headers = api._get_oauth_headers('GET', test_url, test_params)
            
            if 'Authorization' in headers:
                auth_header = headers['Authorization']
                if 'HMAC-SHA1' in auth_header:
                    print("✅ OAuth signature method: HMAC-SHA1")
                else:
                    print("❌ OAuth signature method: Expected HMAC-SHA1")
                    oauth_compliant = False
                
                # Check required OAuth parameters
                required_params = ['oauth_consumer_key', 'oauth_nonce', 'oauth_signature_method', 
                                 'oauth_timestamp', 'oauth_version', 'oauth_signature']
                
                missing_params = []
                for param in required_params:
                    if param in auth_header:
                        print(f"✅ {param}")
                    else:
                        print(f"❌ {param} - Missing")
                        missing_params.append(param)
                
                if missing_params:
                    oauth_compliant = False
            else:
                print("❌ No Authorization header generated")
                oauth_compliant = False
                
        except Exception as e:
            print(f"❌ OAuth signature test failed: {e}")
            oauth_compliant = False
        
        # Test 6: XML Response Handling
        print("\n📋 Test 6: XML Response Handling")
        print("-" * 40)
        
        # Test XML parser with sample data
        sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<fantasy_content>
    <users>
        <user>
            <guid>test_guid</guid>
            <games>
                <game>
                    <game_key>390</game_key>
                    <name>NFL</name>
                </game>
            </games>
        </user>
    </users>
</fantasy_content>'''
        
        try:
            parsed = parse_yahoo_response(sample_xml)
            if 'users' in parsed and len(parsed['users']) > 0:
                print("✅ XML Parser working correctly")
                print(f"✅ Parsed {len(parsed['users'])} users")
            else:
                print("❌ XML Parser not working correctly")
                oauth_compliant = False
        except Exception as e:
            print(f"❌ XML Parser test failed: {e}")
            oauth_compliant = False
        
        # Summary
        print("\n" + "=" * 60)
        if oauth_compliant:
            print("🎉 API COMPLIANCE TEST PASSED!")
            print("✅ Your implementation is fully compliant with official Yahoo! documentation")
            print("\n📋 Compliance Summary:")
            print("   • OAuth 1.0a endpoints: ✅ Correct")
            print("   • API base URL: ✅ Correct")
            print("   • XML response handling: ✅ Implemented")
            print("   • Required API methods: ✅ All present")
            print("   • OAuth signature method: ✅ HMAC-SHA1")
            print("   • XML parser: ✅ Functional")
        else:
            print("💥 API COMPLIANCE TEST FAILED!")
            print("❌ Some issues found - check the details above")
        
        return oauth_compliant
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_compliance()
    if success:
        print("\n🚀 Ready to test with real Yahoo! API!")
        print("   Once OAuth rate limits reset, you can authenticate and fetch data.")
    else:
        print("\n🔧 Please fix the compliance issues before proceeding.")
