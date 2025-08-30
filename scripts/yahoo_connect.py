#!/usr/bin/env python3
"""
Yahoo Fantasy API connection and data fetching
Handles OAuth 1.0a authentication, league discovery, and data retrieval
Based on official Yahoo! Fantasy Sports API documentation
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode, parse_qs, urlparse
import webbrowser
from pathlib import Path
import logging
import hmac
import hashlib
import base64
import secrets

# Import local utilities
try:
    from utils import log_api_call, load_config, save_config, ensure_directories
except ImportError:
    # Fallback for when running from root directory
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import log_api_call, load_config, save_config, ensure_directories

# Configure logging
logger = logging.getLogger(__name__)

class YahooFantasyAPI:
    """Yahoo Fantasy Sports API client using OAuth 1.0a"""
    
    def __init__(self):
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Missing required Yahoo API environment variables: YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET")
        
        self.base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.request_token_url = "https://api.login.yahoo.com/oauth/v2/get_request_token"
        self.authorize_url = "https://api.login.yahoo.com/oauth/v2/request_auth"
        self.access_token_url = "https://api.login.yahoo.com/oauth/v2/get_token"
        
        self.access_token = None
        self.access_secret = None
        self.access_session_handle = None
        
        # Load existing tokens if available
        self._load_tokens()
        
        # Ensure directories exist
        ensure_directories()
    
    def _load_tokens(self) -> None:
        """Load saved tokens from config"""
        config = load_config('yahoo_tokens')
        if config:
            self.access_token = config.get('access_token')
            self.access_secret = config.get('access_secret')
            self.access_session_handle = config.get('session_handle')
            logger.info("Loaded existing Yahoo tokens from config")
    
    def _save_tokens(self) -> None:
        """Save tokens to config"""
        config = {
            'access_token': self.access_token,
            'access_secret': self.access_secret,
            'session_handle': self.access_session_handle
        }
        save_config('yahoo_tokens', config)
        logger.info("Saved Yahoo tokens to config")
    
    def _generate_oauth_signature(self, method: str, url: str, params: Dict[str, str], 
                                 token_secret: str = "") -> str:
        """Generate OAuth 1.0a signature"""
        # Sort parameters alphabetically
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Create signature base string
        signature_base = f"{method}&{requests.utils.quote(url, safe='')}&{requests.utils.quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{requests.utils.quote(self.client_secret, safe='')}&{requests.utils.quote(token_secret, safe='')}"
        
        # Generate HMAC-SHA1 signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_oauth_headers(self, method: str, url: str, params: Dict[str, str], 
                           token_secret: str = "") -> Dict[str, str]:
        """Generate OAuth 1.0a headers"""
        timestamp = str(int(time.time()))
        nonce = secrets.token_urlsafe(32)
        
        oauth_params = {
            'oauth_consumer_key': self.client_id,
            'oauth_nonce': nonce,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': timestamp,
            'oauth_version': '1.0'
        }
        
        # Add token if available
        if self.access_token:
            oauth_params['oauth_token'] = self.access_token
        
        # Combine all parameters for signature
        all_params = {**params, **oauth_params}
        signature = self._generate_oauth_signature(method, url, all_params, token_secret)
        oauth_params['oauth_signature'] = signature
        
        # Create Authorization header
        auth_header = 'OAuth ' + ', '.join([f'{k}="{requests.utils.quote(v, safe="")}"' for k, v in oauth_params.items()])
        
        return {'Authorization': auth_header}
    
    def authenticate(self) -> bool:
        """Complete OAuth 1.0a authentication flow"""
        if self.access_token and self.access_secret:
            logger.info("Using existing valid tokens")
            return True
        
        logger.info("Starting new OAuth 1.0a authentication flow")
        return self._new_authentication()
    
    def _new_authentication(self) -> bool:
        """Start new OAuth 1.0a flow"""
        try:
            # Step 1: Get request token
            logger.info("Getting request token...")
            request_token = self._get_request_token()
            if not request_token:
                return False
            
            # Step 2: Get user authorization
            logger.info("Getting user authorization...")
            if not self._get_user_authorization(request_token):
                return False
            
            # Step 3: Exchange for access token
            logger.info("Exchanging for access token...")
            return self._get_access_token(request_token)
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _get_request_token(self) -> Optional[str]:
        """Get request token from Yahoo!"""
        try:
            # For request token, we don't include oauth_callback in the signature
            # Only include it in the request body
            params = {}
            
            headers = self._get_oauth_headers('POST', self.request_token_url, params)
            
            # Add oauth_callback to the request body, not to the signature
            data = {'oauth_callback': 'oob'}  # Out-of-band callback for desktop apps
            
            response = requests.post(self.request_token_url, data=data, headers=headers)
            log_api_call(self.request_token_url, response.elapsed.total_seconds(), response.status_code)
            
            if response.status_code == 200:
                # Parse response (format: oauth_token=TOKEN&oauth_token_secret=SECRET)
                response_data = parse_qs(response.text)
                request_token = response_data.get('oauth_token', [None])[0]
                request_token_secret = response_data.get('oauth_token_secret', [None])[0]
                
                if request_token and request_token_secret:
                    self.request_token_secret = request_token_secret
                    logger.info("Successfully obtained request token")
                    return request_token
            
            logger.error(f"Failed to get request token: {response.status_code} - {response.text}")
            logger.error(f"Response headers: {dict(response.headers)}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting request token: {e}")
            return None
    
    def _get_user_authorization(self, request_token: str) -> bool:
        """Get user authorization for the request token"""
        try:
            auth_url = f"{self.authorize_url}?oauth_token={request_token}"
            print(f"\n🔐 Yahoo Fantasy API Authentication Required")
            print(f"Please visit this URL in your browser:\n{auth_url}\n")
            
            # Try to open browser automatically
            try:
                webbrowser.open(auth_url)
                print("🌐 Browser opened automatically. Please complete authentication.")
            except:
                print("🌐 Please copy and paste the URL above into your browser.")
            
            # Wait for user to complete authentication
            self.verifier = input("\nEnter the verification code from Yahoo: ").strip()
            
            if not self.verifier:
                logger.error("No verification code provided")
                return False
            
            logger.info("User authorization completed")
            return True
            
        except Exception as e:
            logger.error(f"Error getting user authorization: {e}")
            return False
    
    def _get_access_token(self, request_token: str) -> bool:
        """Exchange request token for access token"""
        try:
            params = {
                'oauth_token': request_token,
                'oauth_verifier': self.verifier
            }
            
            headers = self._get_oauth_headers('POST', self.access_token_url, params, self.request_token_secret)
            
            response = requests.post(self.access_token_url, data=params, headers=headers)
            log_api_call(self.access_token_url, response.elapsed.total_seconds(), response.status_code)
            
            if response.status_code == 200:
                # Parse response
                response_data = parse_qs(response.text)
                self.access_token = response_data.get('oauth_token', [None])[0]
                self.access_secret = response_data.get('oauth_token_secret', [None])[0]
                self.access_session_handle = response_data.get('oauth_session_handle', [None])[0]
                
                if all([self.access_token, self.access_secret]):
                    self._save_tokens()
                    logger.info("Successfully obtained access tokens")
                    return True
            
            logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return False
    
    def make_request(self, endpoint: str, method: str = 'GET', params: Dict[str, str] = None) -> Optional[Dict]:
        """Make authenticated request to Yahoo! Fantasy API"""
        if not self.authenticate():
            logger.error("Authentication required")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            if params is None:
                params = {}
            
            headers = self._get_oauth_headers(method, url, params, self.access_secret)
            
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            else:
                response = requests.post(url, data=params, headers=headers)
            
            log_api_call(url, response.elapsed.total_seconds(), response.status_code)
            
            if response.status_code == 200:
                # Parse XML response (Yahoo! returns XML)
                # For now, return raw text, we can add XML parsing later
                return {'status': 'success', 'data': response.text}
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return None
    
    def discover_league_info(self) -> Optional[Dict]:
        """Discover user's fantasy leagues and teams"""
        endpoint = "users;use_login=1/games;game_keys=nfl/teams"
        return self.make_request(endpoint)
    
    def get_current_roster(self, team_key: str) -> Optional[Dict]:
        """Get current roster for a specific team"""
        endpoint = f"team/{team_key}/roster"
        return self.make_request(endpoint)
    
    def get_available_players(self, league_key: str, position: str = None) -> Optional[Dict]:
        """Get available free agents in a league"""
        endpoint = f"league/{league_key}/players;status=FA"
        if position:
            endpoint += f";position={position}"
        return self.make_request(endpoint)

def main():
    """Test the Yahoo Fantasy API connection"""
    try:
        print("🏈 Testing Yahoo Fantasy API Connection...")
        
        api = YahooFantasyAPI()
        
        # Test authentication
        if api.authenticate():
            print("✅ Authentication successful!")
            
            # Test league discovery
            league_info = api.discover_league_info()
            if league_info:
                print(f"✅ League discovered: {league_info['status']}")
                print(f"   Data: {league_info['data']}")
                
                # Test roster retrieval
                roster = api.get_current_roster("1234567890") # Replace with actual team_key
                if roster:
                    print(f"✅ Roster retrieved: {roster['status']}")
                    print(f"   Data: {roster['data']}")
                    
                    # Show first few players
                    print("\n📋 Sample roster:")
                    # The original script had roster parsing, but the new one doesn't.
                    # For now, we'll just print the raw data.
                    print(f"   Raw Data: {roster['data']}")
                    
                else:
                    print("❌ Failed to retrieve roster")
            else:
                print("❌ Failed to discover league")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main test failed: {e}")

if __name__ == "__main__":
    main()
