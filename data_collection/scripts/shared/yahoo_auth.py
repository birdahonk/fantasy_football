#!/usr/bin/env python3
"""
Simplified Yahoo OAuth 2.0 Client for Data Collection Scripts

This is a streamlined version of the OAuth 2.0 client specifically designed
for the clean data extraction scripts. It reuses the working authentication
logic but simplifies the interface.
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Add the main scripts directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))

try:
    from oauth.oauth2_client import YahooOAuth2Client
except ImportError:
    print("ERROR: Cannot import existing OAuth client. Please ensure the main OAuth client is available.")
    sys.exit(1)

class SimpleYahooAuth:
    """
    Simplified Yahoo OAuth 2.0 client for data collection scripts.
    
    This wraps the existing working OAuth client with a cleaner interface
    focused on data extraction needs.
    """
    
    def __init__(self):
        """Initialize the simplified Yahoo auth client."""
        # Load environment variables
        load_dotenv()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize the working OAuth client
        try:
            self.oauth_client = YahooOAuth2Client()
            self.logger.info("Yahoo OAuth 2.0 client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OAuth client: {e}")
            self.oauth_client = None
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication."""
        if not self.oauth_client:
            return False
        
        try:
            return self.oauth_client.is_authenticated()
        except Exception as e:
            self.logger.error(f"Authentication check failed: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Ensure we have valid authentication."""
        if not self.oauth_client:
            self.logger.error("OAuth client not available")
            return False
        
        try:
            if self.is_authenticated():
                self.logger.info("Already authenticated")
                return True
            
            # Try to authenticate using the existing client
            self.logger.info("Attempting authentication...")
            return self.oauth_client.authenticate()
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Optional[Dict]:
        """
        Make an authenticated request to the Yahoo Fantasy API.
        
        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method (GET, POST)
            params: Optional query parameters
            
        Returns:
            Dict with 'status', 'data', and 'parsed' keys, or None on failure
        """
        if not self.oauth_client:
            self.logger.error("OAuth client not available")
            return None
        
        # Ensure we're authenticated
        if not self.authenticate():
            self.logger.error("Cannot authenticate with Yahoo API")
            return None
        
        try:
            self.logger.info(f"Making Yahoo API request: {endpoint}")
            result = self.oauth_client.make_request(endpoint, method, params)
            
            if result and result.get('status') == 'success':
                self.logger.info(f"API request successful: {endpoint}")
                return result
            else:
                self.logger.error(f"API request failed: {endpoint}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error making API request to {endpoint}: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get basic user information."""
        return self.make_request("users;use_login=1/profile")
    
    def discover_leagues_and_teams(self) -> Optional[Dict]:
        """Discover user's fantasy leagues and teams."""
        return self.make_request("users;use_login=1/games;game_keys=nfl/teams")
    
    def get_league_teams(self, league_key: str) -> Optional[Dict]:
        """Get all teams in a league."""
        return self.make_request(f"league/{league_key}/teams")
    
    def get_team_roster(self, team_key: str) -> Optional[Dict]:
        """Get a team's roster."""
        return self.make_request(f"team/{team_key}/roster")
    
    def get_league_players(self, league_key: str, position: str = None, status: str = "A", 
                          sort: str = "OR", start: int = 0, count: int = 25) -> Optional[Dict]:
        """Get available players in a league."""
        endpoint = f"league/{league_key}/players"
        
        params = {
            'status': status,
            'sort': sort,
            'start': start,
            'count': count
        }
        
        if position:
            params['position'] = position
        
        return self.make_request(endpoint, params=params)
    
    def get_league_scoreboard(self, league_key: str, week: int) -> Optional[Dict]:
        """Get weekly matchups/scoreboard for a league."""
        return self.make_request(f"league/{league_key}/scoreboard;week={week}")
    
    def get_league_transactions(self, league_key: str, start: int = 0, count: int = 50) -> Optional[Dict]:
        """Get league transactions."""
        return self.make_request(f"league/{league_key}/transactions", 
                               params={'start': start, 'count': count})

def main():
    """Test the simplified Yahoo auth client."""
    print("🔐 Testing Simplified Yahoo Auth Client")
    print("=" * 50)
    
    auth = SimpleYahooAuth()
    
    if auth.is_authenticated():
        print("✅ Authentication working")
        
        # Test basic user info
        print("\n🧪 Testing user info...")
        user_info = auth.get_user_info()
        if user_info:
            print("✅ User info retrieved successfully")
        else:
            print("❌ Failed to get user info")
        
        # Test league discovery
        print("\n🧪 Testing league discovery...")
        leagues = auth.discover_leagues_and_teams()
        if leagues:
            print("✅ League discovery successful")
        else:
            print("❌ Failed to discover leagues")
    
    else:
        print("❌ Authentication failed")
        print("Please ensure OAuth 2.0 is set up correctly in the main application")

if __name__ == "__main__":
    main()
