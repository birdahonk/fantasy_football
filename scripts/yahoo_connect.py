#!/usr/bin/env python3
"""
Yahoo Fantasy API connection and data fetching
Handles authentication, league discovery, and data retrieval
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

# Import local utilities
from utils import log_api_call, load_config, save_config, ensure_directories

# Configure logging
logger = logging.getLogger(__name__)

class YahooFantasyAPI:
    """Yahoo Fantasy Sports API client"""
    
    def __init__(self):
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Missing required Yahoo API environment variables: YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET")
        
        self.base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
        
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        
        # Load existing tokens if available
        self._load_tokens()
        
        # Ensure directories exist
        ensure_directories()
    
    def _load_tokens(self) -> None:
        """Load saved tokens from config"""
        config = load_config('yahoo_tokens')
        if config:
            self.access_token = config.get('access_token')
            self.refresh_token = config.get('refresh_token')
            self.token_expires_at = config.get('expires_at', 0)
            logger.info("Loaded existing Yahoo tokens from config")
    
    def _save_tokens(self) -> None:
        """Save tokens to config"""
        config = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at
        }
        save_config('yahoo_tokens', config)
        logger.info("Saved Yahoo tokens to config")
    
    def _is_token_valid(self) -> bool:
        """Check if current access token is still valid"""
        return self.access_token and time.time() < self.token_expires_at
    
    def authenticate(self) -> bool:
        """Complete OAuth 2.0 authentication flow"""
        if self._is_token_valid():
            logger.info("Using existing valid token")
            return True
        
        if self.refresh_token:
            logger.info("Attempting token refresh")
            if self._refresh_token():
                return True
        
        logger.info("Starting new authentication flow")
        return self._new_authentication()
    
    def _new_authentication(self) -> bool:
        """Start new OAuth 2.0 flow"""
        try:
            # Step 1: Get authorization code
            auth_params = {
                'client_id': self.client_id,
                'redirect_uri': 'http://localhost:8080', # Placeholder, will be replaced by local server
                'response_type': 'code',
                'scope': 'fspt-r'  # Fantasy Sports Read permission
            }
            
            auth_url = f"{self.auth_url}?{urlencode(auth_params)}"
            print(f"\n🔐 Yahoo Fantasy API Authentication Required")
            print(f"Please visit this URL in your browser:\n{auth_url}\n")
            
            # Try to open browser automatically
            try:
                webbrowser.open(auth_url)
                print("🌐 Browser opened automatically. Please complete authentication.")
            except:
                print("🌐 Please copy and paste the URL above into your browser.")
            
            # Wait for user to complete authentication
            auth_code = input("\nEnter the authorization code from Yahoo: ").strip()
            
            if not auth_code:
                logger.error("No authorization code provided")
                return False
            
            # Step 2: Exchange code for tokens
            return self._exchange_code_for_tokens(auth_code)
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange authorization code for access and refresh tokens"""
        try:
            token_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'http://localhost:8080', # Placeholder, will be replaced by local server
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.token_url, data=token_data)
            log_api_call(self.token_url, response.elapsed.total_seconds(), response.status_code)
            
            if response.status_code == 200:
                token_response = response.json()
                
                self.access_token = token_response['access_token']
                self.refresh_token = token_response.get('refresh_token')
                self.token_expires_at = time.time() + token_response.get('expires_in', 3600)
                
                self._save_tokens()
                logger.info("Successfully obtained new tokens")
                return True
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return False
    
    def _refresh_token(self) -> bool:
        """Refresh access token using refresh token"""
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.token_url, data=token_data)
            log_api_call(self.token_url, response.elapsed.total_seconds(), response.status_code)
            
            if response.status_code == 200:
                token_response = response.json()
                
                self.access_token = token_response['access_token']
                if 'refresh_token' in token_response:
                    self.refresh_token = token_response['refresh_token']
                self.token_expires_at = time.time() + token_response.get('expires_in', 3600)
                
                self._save_tokens()
                logger.info("Successfully refreshed token")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to Yahoo Fantasy API"""
        if not self.authenticate():
            logger.error("Authentication failed")
            return None
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, params=params)
            response_time = time.time() - start_time
            
            log_api_call(endpoint, response_time, response.status_code)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.warning("Token expired, attempting refresh")
                if self._refresh_token():
                    return self._make_request(endpoint, params)
                else:
                    logger.error("Token refresh failed")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def discover_league_info(self) -> Optional[Dict[str, Any]]:
        """Discover user's fantasy football league and team information"""
        try:
            # Get user's games
            games_response = self._make_request('users;use_login=1/games;game_keys=nfl')
            
            if not games_response:
                logger.error("Failed to get user games")
                return None
            
            # Find current NFL season
            games = games_response.get('fantasy_content', {}).get('users', [{}])[0].get('user', {}).get('games', [])
            
            if not games:
                logger.error("No NFL games found for user")
                return None
            
            # Get the most recent NFL season
            nfl_games = [g for g in games if g.get('game', {}).get('game_key') == '390']  # NFL game key
            
            if not nfl_games:
                logger.error("No NFL games found")
                return None
            
            current_game = nfl_games[0]
            game_key = current_game['game']['game_key']
            
            # Get user's teams for this game
            teams_response = self._make_request(f'users;use_login=1/games;game_keys={game_key}/teams')
            
            if not teams_response:
                logger.error("Failed to get user teams")
                return None
            
            teams = teams_response.get('fantasy_content', {}).get('users', [{}])[0].get('user', {}).get('games', [{}])[0].get('game', {}).get('teams', [])
            
            if not teams:
                logger.error("No teams found for user")
                return None
            
            # Get first team (assuming single team)
            team = teams[0]['team']
            team_key = team[0]['team_key']
            team_name = team[1]['name']
            
            # Get league info
            league_response = self._make_request(f'team/{team_key}/league')
            
            if not league_response:
                logger.error("Failed to get league info")
                return None
            
            league = league_response.get('fantasy_content', {}).get('team', [{}])[0].get('league', [{}])[0]
            league_key = league[0]['league_key']
            league_name = league[1]['name']
            
            league_info = {
                'game_key': game_key,
                'league_key': league_key,
                'league_name': league_name,
                'team_key': team_key,
                'team_name': team_name
            }
            
            # Save league info for future use
            save_config('league_info', league_info)
            logger.info(f"Discovered league: {league_name}, team: {team_name}")
            
            return league_info
            
        except Exception as e:
            logger.error(f"League discovery failed: {e}")
            return None
    
    def get_current_roster(self) -> Optional[Dict[str, Any]]:
        """Get current roster with player details"""
        try:
            league_info = load_config('league_info')
            if not league_info:
                logger.error("League info not found, run discover_league_info first")
                return None
            
            team_key = league_info['team_key']
            endpoint = f'team/{team_key}/roster'
            
            roster_response = self._make_request(endpoint)
            
            if not roster_response:
                logger.error("Failed to get roster")
                return None
            
            # Parse roster data
            roster_data = self._parse_roster_response(roster_response)
            
            # Save roster snapshot
            timestamp = int(time.time())
            roster_snapshot = {
                'timestamp': timestamp,
                'roster': roster_data
            }
            
            # Save to historical data
            from utils import create_historical_file
            create_historical_file(f'roster_snapshot_{timestamp}.json', roster_snapshot)
            
            logger.info(f"Retrieved roster with {len(roster_data)} players")
            return roster_data
            
        except Exception as e:
            logger.error(f"Get roster failed: {e}")
            return None
    
    def _parse_roster_response(self, response: Dict) -> List[Dict[str, Any]]:
        """Parse Yahoo Fantasy API roster response"""
        try:
            roster = response.get('fantasy_content', {}).get('team', [{}])[0].get('roster', [{}])[0].get('0', {}).get('players', [])
            
            players = []
            for player in roster:
                if isinstance(player, dict) and 'player' in player:
                    player_data = player['player'][0]
                    player_info = player['player'][1]
                    
                    # Extract player details
                    player_dict = {
                        'player_key': player_data.get('player_key'),
                        'name': player_info.get('name', {}).get('full'),
                        'position': player_info.get('display_position'),
                        'team': player_info.get('editorial_team_abbr'),
                        'status': player_info.get('status'),
                        'selected_position': player_info.get('selected_position', {}).get('position'),
                        'roster_slot': player_info.get('selected_position', {}).get('roster_slot')
                    }
                    
                    # Add additional stats if available
                    if 'player_stats' in player_info:
                        stats = player_info['player_stats'][0]['stats']
                        for stat in stats:
                            if isinstance(stat, dict) and 'stat' in stat:
                                stat_data = stat['stat']
                                player_dict[f"stat_{stat_data[0]['stat_id']}"] = stat_data[1]['value']
                    
                    players.append(player_dict)
            
            return players
            
        except Exception as e:
            logger.error(f"Roster parsing failed: {e}")
            return []
    
    def get_opponent_roster(self, week: int) -> Optional[Dict[str, Any]]:
        """Get opponent roster for specific week"""
        try:
            league_info = load_config('league_info')
            if not league_info:
                logger.error("League info not found")
                return None
            
            team_key = league_info['team_key']
            endpoint = f'team/{team_key}/matchups'
            
            matchups_response = self._make_request(endpoint)
            
            if not matchups_response:
                logger.error("Failed to get matchups")
                return None
            
            # Find current week matchup
            matchups = matchups_response.get('fantasy_content', {}).get('team', [{}])[0].get('matchups', [])
            
            current_matchup = None
            for matchup in matchups:
                if isinstance(matchup, dict) and 'matchup' in matchup:
                    matchup_data = matchup['matchup'][0]
                    matchup_info = matchup['matchup'][1]
                    
                    if matchup_info.get('week') == str(week):
                        current_matchup = matchup
                        break
            
            if not current_matchup:
                logger.error(f"No matchup found for week {week}")
                return None
            
            # Get opponent team key
            teams = current_matchup['matchup'][1].get('0', {}).get('teams', [])
            opponent_team = None
            
            for team in teams:
                if isinstance(team, dict) and 'team' in team:
                    team_data = team['team'][0]
                    if team_data.get('team_key') != team_key:
                        opponent_team = team_data
                        break
            
            if not opponent_team:
                logger.error("Opponent team not found")
                return None
            
            # Get opponent roster
            opponent_key = opponent_team['team_key']
            opponent_endpoint = f'team/{opponent_key}/roster'
            
            opponent_response = self._make_request(opponent_endpoint)
            
            if not opponent_response:
                logger.error("Failed to get opponent roster")
                return None
            
            opponent_roster = self._parse_roster_response(opponent_response)
            
            opponent_info = {
                'team_key': opponent_key,
                'team_name': opponent_team.get('name', 'Unknown'),
                'roster': opponent_roster
            }
            
            logger.info(f"Retrieved opponent roster for week {week}")
            return opponent_info
            
        except Exception as e:
            logger.error(f"Get opponent roster failed: {e}")
            return None
    
    def get_available_players(self, position: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get available free agents"""
        try:
            league_info = load_config('league_info')
            if not league_info:
                logger.error("League info not found")
                return None
            
            league_key = league_info['league_key']
            endpoint = f'league/{league_key}/players'
            
            params = {'status': 'FA'}  # Free agents only
            if position:
                params['position'] = position
            
            players_response = self._make_request(endpoint, params)
            
            if not players_response:
                logger.error("Failed to get available players")
                return None
            
            # Parse available players
            available_players = self._parse_available_players_response(players_response)
            
            logger.info(f"Retrieved {len(available_players)} available players")
            return available_players
            
        except Exception as e:
            logger.error(f"Get available players failed: {e}")
            return None
    
    def _parse_available_players_response(self, response: Dict) -> List[Dict[str, Any]]:
        """Parse Yahoo Fantasy API available players response"""
        try:
            players = response.get('fantasy_content', {}).get('league', [{}])[0].get('players', [])
            
            available_players = []
            for player in players:
                if isinstance(player, dict) and 'player' in player:
                    player_data = player['player'][0]
                    player_info = player['player'][1]
                    
                    player_dict = {
                        'player_key': player_data.get('player_key'),
                        'name': player_info.get('name', {}).get('full'),
                        'position': player_info.get('display_position'),
                        'team': player_info.get('editorial_team_abbr'),
                        'status': player_info.get('status'),
                        'percent_owned': player_info.get('percent_owned', {}).get('value', 0)
                    }
                    
                    available_players.append(player_dict)
            
            return available_players
            
        except Exception as e:
            logger.error(f"Available players parsing failed: {e}")
            return []
    
    def get_player_news(self, player_key: str) -> Optional[Dict[str, Any]]:
        """Get player news and status updates"""
        try:
            endpoint = f'player/{player_key}/news'
            
            news_response = self._make_request(endpoint)
            
            if not news_response:
                logger.error("Failed to get player news")
                return None
            
            # Parse news data
            news_data = self._parse_player_news_response(news_response)
            
            logger.info(f"Retrieved news for player {player_key}")
            return news_data
            
        except Exception as e:
            logger.error(f"Get player news failed: {e}")
            return None
    
    def _parse_player_news_response(self, response: Dict) -> Dict[str, Any]:
        """Parse Yahoo Fantasy API player news response"""
        try:
            news = response.get('fantasy_content', {}).get('player', [{}])[0].get('news', [])
            
            news_items = []
            for item in news:
                if isinstance(item, dict) and 'news' in item:
                    news_data = item['news'][0]
                    news_info = item['news'][1]
                    
                    news_item = {
                        'title': news_info.get('title'),
                        'summary': news_info.get('summary'),
                        'url': news_info.get('url'),
                        'timestamp': news_data.get('timestamp')
                    }
                    
                    news_items.append(news_item)
            
            return {'news': news_items}
            
        except Exception as e:
            logger.error(f"Player news parsing failed: {e}")
            return {'news': []}

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
                print(f"✅ League discovered: {league_info['league_name']}")
                print(f"   Team: {league_info['team_name']}")
                
                # Test roster retrieval
                roster = api.get_current_roster()
                if roster:
                    print(f"✅ Roster retrieved: {len(roster)} players")
                    
                    # Show first few players
                    print("\n📋 Sample roster:")
                    for i, player in enumerate(roster[:5]):
                        print(f"   {i+1}. {player['name']} ({player['position']}) - {player['team']}")
                    
                    if len(roster) > 5:
                        print(f"   ... and {len(roster) - 5} more players")
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
