#!/usr/bin/env python3
"""
Yahoo OAuth 2.0 Client for Fantasy Sports API
Uses Authorization Code Grant flow as per Yahoo's OAuth 2.0 documentation
"""

import os
import json
import time
import webbrowser
import requests
from urllib.parse import urlencode, parse_qs
from typing import Dict, Optional, Tuple
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooOAuth2Client:
    """OAuth 2.0 client for Yahoo APIs using Authorization Code Grant flow"""
    
    def __init__(self):
        load_dotenv()
        
        # OAuth 2.0 endpoints
        self.auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
        
        # Client credentials
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        self.redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'https://tools.birdahonk.com/fantasy/oauth/callback')
        self.scopes = os.getenv('YAHOO_SCOPES', 'fspt-w')  # Fantasy Sports read/write - this worked!
        
        # Token storage
        self.tokens_file = "config/yahoo_oauth2_tokens.json"
        self.access_token = None
        self.refresh_token = None
        self.token_type = None
        self.expires_at = None
        self.scope = None
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
        
        # Load existing tokens if available
        self._load_tokens()
    
    def _load_tokens(self) -> None:
        """Load existing OAuth 2.0 tokens from file"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r') as f:
                    tokens = json.load(f)
                
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
                self.token_type = tokens.get('token_type', 'Bearer')
                self.expires_at = tokens.get('expires_at')
                self.scope = tokens.get('scope')
                
                logger.info("Loaded existing OAuth 2.0 tokens")
            else:
                logger.info("No existing OAuth 2.0 tokens found")
                
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
    
    def _save_tokens(self) -> None:
        """Save OAuth 2.0 tokens to file"""
        try:
            tokens = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'token_type': self.token_type,
                'expires_at': self.expires_at,
                'scope': self.scope,
                'created_at': int(time.time())
            }
            
            with open(self.tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            logger.info("OAuth 2.0 tokens saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if we have valid access tokens"""
        if not self.access_token:
            return False
        
        # Check if token is expired (with 5 minute buffer)
        if self.expires_at and time.time() > (self.expires_at - 300):
            logger.info("Access token expired, attempting refresh")
            return self.refresh_access_token()
        
        return True
    
    def get_authorization_url(self) -> str:
        """Generate the authorization URL for OAuth 2.0 flow"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scopes,
            'state': 'fantasy_football_app'
        }
        
        # Debug logging
        logger.info(f"OAuth 2.0 parameters: {params}")
        logger.info(f"Redirect URI being sent: {self.redirect_uri}")
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url
    
    def authenticate(self) -> bool:
        """Complete OAuth 2.0 authentication flow"""
        if not self.client_id:
            logger.error("YAHOO_CLIENT_ID not set in environment")
            return False
        
        if self.is_authenticated():
            logger.info("Already authenticated with valid tokens")
            return True
        
        try:
            # Step 1: Get authorization URL and open browser
            auth_url = self.get_authorization_url()
            print(f"\n🔐 Yahoo OAuth 2.0 Authentication Required")
            print(f"Please visit this URL in your browser:\n{auth_url}\n")
            
            # Try to open browser automatically
            try:
                webbrowser.open(auth_url)
                print("🌐 Browser opened automatically. Please complete authentication.")
            except:
                print("🌐 Please copy and paste the URL above into your browser.")
            
            # Wait for user to complete authentication
            print("\n📝 After completing authentication in Yahoo, you'll be redirected.")
            print("📝 Copy the 'code' parameter from the URL and paste it below.")
            
            authorization_code = input("\nEnter the authorization code from Yahoo: ").strip()
            
            if not authorization_code:
                logger.error("No authorization code provided")
                return False
            
            # Step 2: Exchange authorization code for tokens
            logger.info("Exchanging authorization code for tokens...")
            if self._exchange_code_for_tokens(authorization_code):
                logger.info("OAuth 2.0 authentication completed successfully")
                return True
            else:
                logger.error("Failed to exchange authorization code for tokens")
                return False
                
        except Exception as e:
            logger.error(f"OAuth 2.0 authentication failed: {e}")
            return False
    
    def _exchange_code_for_tokens(self, authorization_code: str) -> bool:
        """Exchange authorization code for access and refresh tokens"""
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id
            }
            
            # Include client secret if available (for server-side apps)
            if self.client_secret:
                data['client_secret'] = self.client_secret
            
            headers = {
                'Content-Type': 'application/xaml+xml, application/xml, text/xml, */*',
                'User-Agent': 'FantasyFootballApp/1.0'
            }
            
            response = requests.post(self.token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                self.token_type = token_data.get('token_type', 'Bearer')
                self.scope = token_data.get('scope')
                
                # Calculate expiration time
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                self.expires_at = int(time.time()) + expires_in
                
                # Save tokens
                self._save_tokens()
                
                logger.info("Successfully obtained OAuth 2.0 tokens")
                return True
            
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
        
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id
            }
            
            # Include client secret if available
            if self.client_secret:
                data['client_secret'] = self.client_secret
            
            headers = {
                'Content-Type': 'application/xaml+xml, application/xml, text/xml, */*',
                'User-Agent': 'FantasyFootballApp/1.0'
            }
            
            response = requests.post(self.token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token', self.refresh_token)  # Keep existing if not provided
                self.token_type = token_data.get('token_type', 'Bearer')
                
                # Calculate new expiration time
                expires_in = token_data.get('expires_in', 3600)
                self.expires_at = int(time.time()) + expires_in
                
                # Save updated tokens
                self._save_tokens()
                
                logger.info("Successfully refreshed OAuth 2.0 access token")
                return True
            
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return False
    
    def get_authorization_header(self) -> Optional[str]:
        """Get the Authorization header for API requests"""
        if not self.is_authenticated():
            return None
        
        return f"{self.token_type} {self.access_token}"
    
    def make_request(self, endpoint: str, method: str = 'GET', params: Dict[str, str] = None) -> Optional[Dict]:
        """Make an authenticated request to Yahoo Fantasy Sports API"""
        if not self.is_authenticated():
            logger.error("Not authenticated")
            return None
        
        try:
            # Build the full URL
            base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
            url = f"{base_url}/{endpoint}"
            
            # Add JSON format parameter
            if params is None:
                params = {}
            params['format'] = 'json'
            
            # Build headers
            headers = {
                'Authorization': self.get_authorization_header(),
                'User-Agent': 'FantasyFootballApp/1.0',
                'Accept': 'application/json'
            }
            
            # Make the request
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, data=params, headers=headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            # Log the API call
            logger.info(f"API call: {url} - {response.status_code} - {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'status': 'success',
                        'data': response.text,
                        'parsed': data
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'success',
                        'data': response.text,
                        'parsed': None
                    }
            
            elif response.status_code == 401:
                logger.warning("Access token expired, attempting refresh")
                if self.refresh_access_token():
                    # Retry the request once after refresh
                    return self.make_request(endpoint, method, params)
                else:
                    logger.error("Failed to refresh access token")
                    return None
            
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return None

def main():
    """Test the OAuth 2.0 client"""
    print("🚀 Yahoo OAuth 2.0 Client Test")
    print("=" * 50)
    
    client = YahooOAuth2Client()
    
    if client.is_authenticated():
        print("✅ Already authenticated with OAuth 2.0")
        print("🎯 Testing API call...")
        
        # Test a simple API call
        result = client.make_request("game/nfl")
        if result and result['status'] == 'success':
            print("✅ API call successful!")
            print(f"📊 Response: {result['parsed']}")
        else:
            print("❌ API call failed")
    else:
        print("🔐 Starting OAuth 2.0 authentication...")
        if client.authenticate():
            print("✅ OAuth 2.0 authentication successful!")
        else:
            print("❌ OAuth 2.0 authentication failed")

if __name__ == "__main__":
    main()
