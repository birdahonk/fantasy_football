#!/usr/bin/env python3
"""
Tank01 NFL API Client via RapidAPI

This module provides a client for accessing the Tank01 NFL API through RapidAPI
to retrieve fantasy projections, player information, news, and other NFL data.

Tank01 API via RapidAPI: https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl
Rate Limits: 1000 calls/month on free tier

Key Features:
- Fantasy point projections
- Player information and stats
- Top news and headlines
- Team rosters and depth charts
- Live game data

Author: Fantasy Football Optimizer
Date: January 2025
"""

import requests
import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Tank01Client:
    """Client for interacting with the Tank01 NFL API via RapidAPI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Tank01 API client.
        
        Args:
            api_key: RapidAPI key (if not provided, will look in environment)
        """
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        if not self.api_key:
            raise ValueError("RapidAPI key is required. Set RAPIDAPI_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
        self.session = requests.Session()
        
        # Set default headers for RapidAPI
        self.session.headers.update({
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com',
            'User-Agent': 'FantasyFootballOptimizer/1.0'
        })
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(logs_dir / 'tank01_api.log'),
                    logging.StreamHandler()
                ]
            )
        
        # Track API usage for rate limiting
        self.api_calls_made = 0
        self.monthly_limit = 1000  # Free tier limit
        
        # RapidAPI usage data from headers (authoritative source)
        self.rapidapi_usage = {
            'limit': 1000,
            'remaining': 1000,
            'reset_timestamp': None,
            'last_updated': None
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Tank01 API via RapidAPI.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            Dict containing the API response data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        # Check rate limits
        if self.api_calls_made >= self.monthly_limit:
            raise Exception(f"Monthly API limit of {self.monthly_limit} calls reached")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making Tank01 API request to: {url}")
            if params:
                self.logger.info(f"Parameters: {params}")
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Extract RapidAPI usage data from response headers (authoritative source)
            self._extract_rapidapi_usage(response.headers)
            
            # Increment usage counter (for backward compatibility)
            self.api_calls_made += 1
            
            data = response.json()
            self.logger.info(f"Tank01 API request successful. Response size: {len(str(data))} characters")
            self.logger.info(f"API calls made this session: {self.api_calls_made}/{self.monthly_limit}")
            self.logger.info(f"RapidAPI remaining calls: {self.rapidapi_usage['remaining']}/{self.rapidapi_usage['limit']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Tank01 API request failed: {e}")
            self.logger.error(f"URL: {url}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise
    
    def _extract_rapidapi_usage(self, headers: Dict[str, str]) -> None:
        """
        Extract RapidAPI usage data from response headers.
        
        Args:
            headers: HTTP response headers from RapidAPI
        """
        import time
        
        # Extract usage data from RapidAPI headers
        if 'X-RateLimit-Requests-Limit' in headers:
            self.rapidapi_usage['limit'] = int(headers['X-RateLimit-Requests-Limit'])
        
        if 'X-RateLimit-Requests-Remaining' in headers:
            self.rapidapi_usage['remaining'] = int(headers['X-RateLimit-Requests-Remaining'])
        
        if 'X-RateLimit-Requests-Reset' in headers:
            self.rapidapi_usage['reset_timestamp'] = int(headers['X-RateLimit-Requests-Reset'])
        
        self.rapidapi_usage['last_updated'] = time.time()
        
        # Update monthly_limit to match RapidAPI limit (in case it changed)
        self.monthly_limit = self.rapidapi_usage['limit']
    
    def get_player_list(self) -> Dict[str, Any]:
        """
        Get the complete NFL player list from Tank01.
        
        This endpoint provides all NFL players with their Tank01 playerID,
        which is needed for other API calls.
        
        Returns:
            Dict containing player list data
            
        Example response structure (needs to be determined from actual API call):
        {
            "players": [
                {
                    "playerID": "12345",
                    "playerName": "Josh Allen",
                    "team": "BUF",
                    "position": "QB"
                }
            ]
        }
        """
        try:
            self.logger.info("Fetching NFL player list from Tank01 API")
            
            # Based on the RapidAPI pattern, this endpoint likely doesn't need parameters
            # We'll need to adjust based on the actual API response
            data = self._make_request("getNFLPlayerList")
            
            # Log the structure for debugging
            if data:
                self.logger.info(f"Player list retrieved. Keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                if isinstance(data, dict) and 'players' in data:
                    self.logger.info(f"Number of players: {len(data['players'])}")
                elif isinstance(data, list):
                    self.logger.info(f"Player list is array with {len(data)} items")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get player list: {e}")
            return {}
    
    def get_fantasy_projections(self, player_id: str, scoring_settings: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Get fantasy point projections for a specific player.
        
        Args:
            player_id: Tank01 player ID
            scoring_settings: Optional custom scoring settings (uses standard PPR if not provided)
            
        Returns:
            Dict containing fantasy projection data
        """
        try:
            self.logger.info(f"Fetching fantasy projections for player {player_id}")
            
            # Default PPR scoring settings
            default_scoring = {
                "fantasyPoints": "true",
                "twoPointConversions": 2,
                "passYards": 0.04,
                "passTD": 4,
                "passInterceptions": -2,
                "pointsPerReception": 1,  # PPR
                "carries": 0.2,
                "rushYards": 0.1,
                "rushTD": 6,
                "fumbles": -2,
                "receivingYards": 0.1,
                "receivingTD": 6,
                "targets": 0,
                "defTD": 6,
                "xpMade": 1,
                "xpMissed": -1,
                "fgMade": 3,
                "fgMissed": -3,
                "idpTotalTackles": 1,
                "idpSoloTackles": 1,
                "idpTFL": 1,
                "idpQbHits": 1,
                "idpInt": 1,
                "idpSacks": 1,
                "idpPassDeflections": 1,
                "idpFumblesRecovered": 1
            }
            
            # Use custom scoring if provided, otherwise use defaults
            scoring = scoring_settings or default_scoring
            
            # Build parameters
            params = {
                "playerID": player_id,
                **scoring
            }
            
            data = self._make_request("getNFLGamesForPlayer", params)
            
            self.logger.info(f"Fantasy projections retrieved for player {player_id}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get fantasy projections for player {player_id}: {e}")
            return {}
    
    def get_team_roster(self, team: str, get_stats: bool = False) -> Dict[str, Any]:
        """
        Get NFL team roster information.
        
        Args:
            team: NFL team abbreviation (e.g., "BUF", "KC")
            get_stats: Whether to include player stats
            
        Returns:
            Dict containing team roster data
        """
        try:
            self.logger.info(f"Fetching team roster for {team}")
            
            params = {
                "team": team.upper()
            }
            if get_stats:
                params["getStats"] = "true"
            
            data = self._make_request("getNFLTeamRoster", params)
            
            self.logger.info(f"Team roster retrieved for {team}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get team roster for {team}: {e}")
            return {}
    
    def get_depth_charts(self, team: Optional[str] = None) -> Dict[str, Any]:
        """
        Get NFL depth charts.
        
        Args:
            team: Optional specific team (if not provided, gets all teams)
            
        Returns:
            Dict containing depth chart data
        """
        try:
            self.logger.info(f"Fetching depth charts" + (f" for {team}" if team else " for all teams"))
            
            params = {}
            if team:
                params["team"] = team.upper()
            
            data = self._make_request("getNFLDepthCharts", params)
            
            self.logger.info("Depth charts retrieved successfully")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get depth charts: {e}")
            return {}
    
    def get_news(self, fantasy_news: bool = True, max_items: int = 20, 
                 player_id: Optional[str] = None, team_id: Optional[str] = None, 
                 team_abv: Optional[str] = None, top_news: bool = True, 
                 recent_news: bool = True) -> Dict[str, Any]:
        """
        Get NFL news and headlines.
        
        Args:
            fantasy_news: Whether to focus on fantasy-relevant news
            max_items: Maximum number of news items to return
            player_id: Get news specific to a player
            team_id: Get news specific to a team (numeric)
            team_abv: Get news for team by abbreviation
            top_news: Include top news
            recent_news: Include recent news
            
        Returns:
            Dict containing news data
        """
        try:
            self.logger.info(f"Fetching NFL news (fantasy_news={fantasy_news}, max_items={max_items}, player_id={player_id}, team_id={team_id}, team_abv={team_abv})")
            
            params = {
                "fantasyNews": str(fantasy_news).lower(),
                "maxItems": max_items,
                "topNews": str(top_news).lower(),
                "recentNews": str(recent_news).lower()
            }
            
            # Add optional parameters for targeted news
            if player_id:
                params["playerID"] = player_id
            if team_id:
                params["teamID"] = team_id
            if team_abv:
                params["teamAbv"] = team_abv
            
            data = self._make_request("getNFLNews", params)
            
            self.logger.info("News retrieved successfully")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get NFL news: {e}")
            return {}
    
    def get_daily_scoreboard(self, game_date: str = "20250907", top_performers: bool = True) -> Dict[str, Any]:
        """
        Get daily NFL scoreboard with live game data.
        
        Args:
            game_date: Date in YYYYMMDD format (e.g., "20250907")
            top_performers: Whether to include top performers
            
        Returns:
            Dict containing scoreboard data
        """
        try:
            self.logger.info(f"Fetching daily scoreboard for {game_date}")
            
            params = {
                "gameDate": game_date,
                "topPerformers": str(top_performers).lower()
            }
            
            data = self._make_request("getNFLScoresOnly", params)
            
            self.logger.info(f"Scoreboard retrieved for {game_date}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get scoreboard: {e}")
            return {}
    
    def get_weekly_projections(self, week: int, archive_season: int = 2025, scoring_settings: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Get weekly fantasy projections for all players.
        
        Args:
            week: Week number (1-18)
            archive_season: Season year (default: 2025)
            scoring_settings: Optional custom scoring settings
            
        Returns:
            Dict containing weekly projections for all players
        """
        try:
            self.logger.info(f"Fetching weekly projections for week {week}, season {archive_season}")
            
            # Default scoring settings from your documentation
            default_scoring = {
                "twoPointConversions": 2,
                "passYards": 0.04,
                "passAttempts": -0.5,
                "passTD": 4,
                "passCompletions": 1,
                "passInterceptions": -2,
                "pointsPerReception": 1,
                "carries": 0.2,
                "rushYards": 0.1,
                "rushTD": 6,
                "fumbles": -2,
                "receivingYards": 0.1,
                "receivingTD": 6,
                "targets": 0.1,
                "fgMade": 3,
                "fgMissed": -1,
                "xpMade": 1,
                "xpMissed": -1
            }
            
            scoring = scoring_settings or default_scoring
            
            params = {
                "week": week,
                "archiveSeason": archive_season,
                **scoring
            }
            
            data = self._make_request("getNFLProjections", params)
            
            self.logger.info(f"Weekly projections retrieved for week {week}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly projections: {e}")
            return {}
    
    def get_player_info(self, player_name: str, get_stats: bool = True) -> Dict[str, Any]:
        """
        Get detailed player information by name.
        
        Args:
            player_name: Player name (e.g., "keenan_a")
            get_stats: Whether to include player statistics
            
        Returns:
            Dict containing player information and stats
        """
        try:
            self.logger.info(f"Fetching player info for {player_name}")
            
            params = {
                "playerName": player_name,
                "getStats": str(get_stats).lower()
            }
            
            data = self._make_request("getNFLPlayerInfo", params)
            
            self.logger.info(f"Player info retrieved for {player_name}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get player info for {player_name}: {e}")
            return {}
    
    def get_player_game_stats(self, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get NFL games and stats for a single player.
        
        Args:
            player_id: Tank01 player ID
            season: Optional season year (current season if not specified)
            
        Returns:
            Dict containing player game stats
        """
        try:
            self.logger.info(f"Fetching game stats for player {player_id}")
            
            params = {
                "playerID": player_id
            }
            if season:
                params["season"] = season
            
            data = self._make_request("getNFLGamesForPlayer", params)
            
            self.logger.info(f"Game stats retrieved for player {player_id}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get game stats for player {player_id}: {e}")
            return {}
    
    def get_changelog(self, max_days: int = 30) -> Dict[str, Any]:
        """
        Get API changelog to understand recent updates.
        
        Args:
            max_days: Maximum number of days to look back
            
        Returns:
            Dict containing changelog data
        """
        try:
            self.logger.info(f"Fetching Tank01 API changelog for last {max_days} days")
            
            params = {
                "maxDays": max_days
            }
            
            data = self._make_request("getNFLChangelog", params)
            
            self.logger.info("Changelog retrieved successfully")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get changelog: {e}")
            return {}
    
    def get_nfl_teams(self, sort_by: str = "standings", rosters: bool = False, schedules: bool = False, 
                      top_performers: bool = True, team_stats: bool = True, team_stats_season: int = 2024) -> Dict[str, Any]:
        """
        Get NFL teams information.
        
        Args:
            sort_by: How to sort teams (default: "standings")
            rosters: Whether to include team rosters
            schedules: Whether to include team schedules
            top_performers: Whether to include top performers
            team_stats: Whether to include team statistics
            team_stats_season: Season year for team stats
            
        Returns:
            Dict containing NFL teams data
        """
        try:
            self.logger.info("Fetching NFL teams data")
            
            params = {
                "sortBy": sort_by,
                "rosters": str(rosters).lower(),
                "schedules": str(schedules).lower(),
                "topPerformers": str(top_performers).lower(),
                "teamStats": str(team_stats).lower(),
                "teamStatsSeason": team_stats_season
            }
            
            data = self._make_request("getNFLTeams", params)
            
            self.logger.info("NFL teams data retrieved successfully")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get NFL teams: {e}")
            return {}
    
    def get_game_info(self, game_id: str) -> Dict[str, Any]:
        """
        Get general game information.
        
        Args:
            game_id: Game ID (e.g., "20260104_DET%40CHI")
            
        Returns:
            Dict containing game information
        """
        try:
            self.logger.info(f"Fetching game info for {game_id}")
            
            params = {
                "gameID": game_id
            }
            
            data = self._make_request("getNFLGameInfo", params)
            
            self.logger.info(f"Game info retrieved for {game_id}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get game info for {game_id}: {e}")
            return {}
    
    def save_debug_data(self, data: Any, filename: str) -> None:
        """
        Save data to a debug file for inspection.
        
        Args:
            data: Data to save
            filename: Name of the debug file
        """
        try:
            debug_path = Path(f"debug_{filename}")
            with open(debug_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.info(f"Debug data saved to {debug_path}")
        except Exception as e:
            self.logger.error(f"Failed to save debug data: {e}")
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get current API usage information from RapidAPI headers (authoritative source).
        
        Returns:
            Dict with usage statistics
        """
        import time
        
        # Use RapidAPI data as primary source, fallback to client-side tracking
        if self.rapidapi_usage['last_updated']:
            # Calculate calls made from RapidAPI data
            calls_made = self.rapidapi_usage['limit'] - self.rapidapi_usage['remaining']
            
            return {
                "calls_made_this_session": calls_made,
                "daily_limit": self.rapidapi_usage['limit'],
                "remaining_calls": self.rapidapi_usage['remaining'],
                "percentage_used": (calls_made / self.rapidapi_usage['limit']) * 100,
                "reset_timestamp": self.rapidapi_usage['reset_timestamp'],
                "last_updated": self.rapidapi_usage['last_updated'],
                "data_source": "rapidapi_headers"
            }
        else:
            # Fallback to client-side tracking if no RapidAPI data available
            return {
                "calls_made_this_session": self.api_calls_made,
                "daily_limit": self.monthly_limit,
                "remaining_calls": self.monthly_limit - self.api_calls_made,
                "percentage_used": (self.api_calls_made / self.monthly_limit) * 100,
                "reset_timestamp": None,
                "last_updated": None,
                "data_source": "client_side_tracking"
            }


def main():
    """Test the Tank01 API client."""
    print("🏈 Testing Tank01 NFL API Client via RapidAPI")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ Error: RAPIDAPI_KEY environment variable not set")
        print("Please set your RapidAPI key in .env file:")
        print("RAPIDAPI_KEY=your_rapidapi_key_here")
        return
    
    try:
        # Initialize client
        client = Tank01Client()
        
        print(f"✅ Tank01 client initialized")
        print(f"📊 Usage limit: {client.monthly_limit} calls/month")
        
        # Test 1: Get player list (this will help us understand the data structure)
        print("\n🔍 Testing Player List Endpoint...")
        player_list = client.get_player_list()
        
        if player_list:
            print(f"✅ Player list retrieved successfully")
            print(f"📄 Response keys: {list(player_list.keys()) if isinstance(player_list, dict) else 'List response'}")
            
            # Save debug data to understand structure
            client.save_debug_data(player_list, "tank01_player_list.json")
            print(f"💾 Debug data saved to debug_tank01_player_list.json")
        else:
            print("❌ No player list data received")
        
        # Test 2: Get changelog (should be lightweight)
        print("\n📋 Testing Changelog Endpoint...")
        changelog = client.get_changelog()
        
        if changelog:
            print(f"✅ Changelog retrieved successfully")
            client.save_debug_data(changelog, "tank01_changelog.json")
        else:
            print("❌ No changelog data received")
        
        # Show usage info
        usage = client.get_usage_info()
        print(f"\n📊 API Usage:")
        print(f"  • Calls made: {usage['calls_made_this_session']}")
        print(f"  • Monthly limit: {usage['monthly_limit']}")
        print(f"  • Remaining: {usage['remaining_calls']}")
        print(f"  • Usage: {usage['percentage_used']:.1f}%")
        
    except Exception as e:
        print(f"❌ Error testing Tank01 API: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Tank01 API Client test completed!")


if __name__ == "__main__":
    main()
