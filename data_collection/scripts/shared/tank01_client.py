#!/usr/bin/env python3
"""
Simplified Tank01 NFL API Client for Data Collection

A clean, focused client for Tank01 API endpoints via RapidAPI used in data collection scripts.
This reuses the working client logic but provides a simpler interface.
"""

import os
import sys
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Add the main scripts directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))

try:
    from external.tank01_client import Tank01Client
except ImportError:
    print("WARNING: Cannot import existing Tank01 client. Creating standalone client.")
    Tank01Client = None

class SimpleTank01Client:
    """
    Simplified Tank01 NFL API client for data collection scripts.
    
    Provides a clean interface for the most common Tank01 API operations
    needed by data extraction scripts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the simplified Tank01 client."""
        load_dotenv()
        
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        
        if not self.api_key:
            self.logger.error("RapidAPI key required for Tank01 client")
            self.tank01_client = None
            return
        
        # Try to use the existing client if available
        if Tank01Client:
            try:
                self.tank01_client = Tank01Client(self.api_key)
                self.logger.info("Using existing Tank01 client")
                self.use_existing = True
            except Exception as e:
                self.logger.warning(f"Failed to initialize existing Tank01 client: {e}")
                self.use_existing = False
                self._init_standalone()
        else:
            self.logger.info("Creating standalone Tank01 client")
            self.use_existing = False
            self._init_standalone()
    
    def _init_standalone(self):
        """Initialize standalone client if existing one is not available."""
        self.base_url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
        self.session = requests.Session()
        self.session.headers.update({
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com',
            'User-Agent': 'FantasyFootballDataCollection/1.0'
        })
        
        # Track API usage
        self.api_calls_made = 0
        self.monthly_limit = 1000
    
    def is_available(self) -> bool:
        """Check if Tank01 client is available and configured."""
        return self.tank01_client is not None or (self.api_key is not None)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Tank01 API via RapidAPI.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            Dict containing the API response data
        """
        if not self.is_available():
            raise ValueError("Tank01 client not properly configured")
        
        if self.use_existing:
            return self.tank01_client._make_request(endpoint, params)
        
        # Check rate limits
        if self.api_calls_made >= self.monthly_limit:
            raise Exception(f"Monthly API limit of {self.monthly_limit} calls reached")
        
        # Standalone implementation
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making Tank01 API request: {endpoint}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            self.api_calls_made += 1
            data = response.json()
            
            self.logger.info(f"Tank01 API request successful: {endpoint}")
            self.logger.info(f"API calls made this session: {self.api_calls_made}/{self.monthly_limit}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Tank01 API request failed: {e}")
            raise
    
    def get_player_list(self) -> Dict[str, Any]:
        """
        Get comprehensive NFL player list from Tank01.
        
        Returns:
            Dict containing all NFL players with Tank01 data
        """
        if not self.is_available():
            self.logger.error("Tank01 client not available")
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_player_list()
            else:
                return self._make_request("getNFLPlayerList")
        except Exception as e:
            self.logger.error(f"Failed to get Tank01 player list: {e}")
            return {}
    
    def get_fantasy_projections(self, player_id: str) -> Dict[str, Any]:
        """
        Get fantasy projections for a specific player.
        
        Args:
            player_id: Tank01 player ID
            
        Returns:
            Dict containing player fantasy projections
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_fantasy_projections(player_id)
            else:
                return self._make_request("getNFLGamesForPlayer", {"playerID": player_id})
        except Exception as e:
            self.logger.error(f"Failed to get fantasy projections for {player_id}: {e}")
            return {}
    
    def get_weekly_projections(self, week: int, season: int = 2025) -> Dict[str, Any]:
        """
        Get weekly fantasy projections for all players.
        
        Args:
            week: NFL week number
            season: NFL season year
            
        Returns:
            Dict containing weekly projections for all players
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_weekly_projections(week, season)
            else:
                return self._make_request("getNFLProjections", 
                                        {"week": week, "archiveSeason": season})
        except Exception as e:
            self.logger.error(f"Failed to get weekly projections for week {week}: {e}")
            return {}
    
    def get_news(self, fantasy_news: bool = True, max_items: int = 20, 
                 player_id: Optional[str] = None, team_id: Optional[str] = None, 
                 team_abv: Optional[str] = None, top_news: bool = True, 
                 recent_news: bool = True) -> Dict[str, Any]:
        """
        Get NFL news, optionally filtered for fantasy relevance and specific players/teams.
        
        Args:
            fantasy_news: Filter for fantasy-relevant news
            max_items: Maximum number of news items
            player_id: Get news specific to a player
            team_id: Get news specific to a team (numeric)
            team_abv: Get news for team by abbreviation
            top_news: Include top news
            recent_news: Include recent news
            
        Returns:
            Dict containing news articles
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_news(fantasy_news, max_items, player_id, team_id, team_abv, top_news, recent_news)
            else:
                params = {
                    "maxItems": max_items,
                    "topNews": "true" if top_news else "false",
                    "recentNews": "true" if recent_news else "false"
                }
                
                if fantasy_news:
                    params["fantasyNews"] = "true"
                
                # Add optional parameters for targeted news
                if player_id:
                    params["playerID"] = player_id
                if team_id:
                    params["teamID"] = team_id
                if team_abv:
                    params["teamAbv"] = team_abv
                
                return self._make_request("getNFLNews", params)
        except Exception as e:
            self.logger.error(f"Failed to get NFL news: {e}")
            return {}
    
    def get_depth_charts(self, team_abbr: str = None) -> Dict[str, Any]:
        """
        Get NFL depth charts for a team or all teams.
        
        Args:
            team_abbr: NFL team abbreviation (optional)
            
        Returns:
            Dict containing depth chart information
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_depth_charts(team_abbr)
            else:
                params = {}
                if team_abbr:
                    params["teamAbv"] = team_abbr
                return self._make_request("getNFLDepthCharts", params)
        except Exception as e:
            self.logger.error(f"Failed to get depth charts: {e}")
            return {}
    
    def get_team_roster(self, team_abbr: str, get_stats: bool = True) -> Dict[str, Any]:
        """
        Get team roster with optional statistics.
        
        Args:
            team_abbr: NFL team abbreviation
            get_stats: Include player statistics
            
        Returns:
            Dict containing team roster data
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_team_roster(team_abbr, get_stats)
            else:
                params = {"teamAbv": team_abbr}
                if get_stats:
                    params["getStats"] = "true"
                return self._make_request("getNFLTeamRoster", params)
        except Exception as e:
            self.logger.error(f"Failed to get team roster for {team_abbr}: {e}")
            return {}
    
    def match_yahoo_player(self, yahoo_name: str, yahoo_team: str = None) -> Optional[Dict[str, Any]]:
        """
        Match a Yahoo Fantasy player to Tank01 database.
        
        Args:
            yahoo_name: Player name from Yahoo
            yahoo_team: Player's NFL team from Yahoo
            
        Returns:
            Matching Tank01 player data or None
        """
        # Get player database
        player_data = self.get_player_list()
        if not player_data or 'body' not in player_data:
            return None
        
        players = player_data['body']
        if not isinstance(players, list):
            return None
        
        yahoo_name_clean = yahoo_name.lower().strip()
        
        # Try various matching strategies
        for player in players:
            tank01_name = player.get('longName', '').lower().strip()
            tank01_team = player.get('team', '')
            yahoo_id = player.get('yahooID')
            
            # Strategy 1: Direct Yahoo ID match
            if yahoo_id:
                # This would require Yahoo player ID, which we may not have
                pass
            
            # Strategy 2: Exact name match with team validation
            if yahoo_name_clean == tank01_name:
                if not yahoo_team or not tank01_team or yahoo_team == tank01_team:
                    return player
            
            # Strategy 3: Last name match with team validation
            if yahoo_team and tank01_team and yahoo_team == tank01_team:
                yahoo_last = yahoo_name_clean.split()[-1] if yahoo_name_clean else ""
                tank01_last = tank01_name.split()[-1] if tank01_name else ""
                if yahoo_last and yahoo_last == tank01_last:
                    return player
        
        return None
    
    def get_api_usage(self) -> Dict[str, Any]:
        """
        Get current API usage information from RapidAPI headers (authoritative source).
        
        Returns:
            Dict with usage statistics
        """
        if self.use_existing and hasattr(self.tank01_client, 'get_usage_info'):
            # Use the external client's RapidAPI-based usage info
            usage = self.tank01_client.get_usage_info()
            usage.update({
                "available": self.is_available(),
                "using_existing_client": self.use_existing
            })
            return usage
        else:
            # Fallback for standalone client
            return {
                "calls_made_this_session": self.api_calls_made,
                "daily_limit": getattr(self, 'monthly_limit', 1000),
                "remaining_calls": getattr(self, 'monthly_limit', 1000) - self.api_calls_made,
                "percentage_used": (self.api_calls_made / getattr(self, 'monthly_limit', 1000)) * 100,
                "available": self.is_available(),
                "using_existing_client": self.use_existing,
                "data_source": "client_side_tracking"
            }
    
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
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_weekly_projections(week, archive_season, scoring_settings)
            else:
                # Build parameters for the API call
                params = {
                    "week": week,
                    "archiveSeason": archive_season,
                    "twoPointConversions": 2,
                    "passYards": 0.04,
                    "passTD": 4,
                    "passInterceptions": -2,
                    "pointsPerReception": 1,
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
                
                # Override with custom scoring if provided
                if scoring_settings:
                    params.update(scoring_settings)
                
                return self._make_request("getNFLProjections", params)
        except Exception as e:
            self.logger.error(f"Failed to get weekly projections: {e}")
            return {}
    
    def get_player_info(self, player_name: str, get_stats: bool = True) -> Dict[str, Any]:
        """
        Get player information by name.
        
        Args:
            player_name: Player name to search for
            get_stats: Include player statistics
            
        Returns:
            Dict containing player information
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_player_info(player_name, get_stats)
            else:
                params = {
                    "playerName": player_name,
                    "getStats": "true" if get_stats else "false"
                }
                return self._make_request("getNFLPlayerInfo", params)
        except Exception as e:
            self.logger.error(f"Failed to get player info for {player_name}: {e}")
            return {}
    
    def get_player_game_stats(self, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get NFL games and stats for a single player.
        
        Args:
            player_id: Tank01 player ID
            season: Optional season (default: current)
            
        Returns:
            Dict containing player game stats and fantasy points
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_player_game_stats(player_id, season)
            else:
                params = {
                    "playerID": player_id,
                    "fantasyPoints": "true",
                    "twoPointConversions": 2,
                    "passYards": 0.04,
                    "passTD": 4,
                    "passInterceptions": -2,
                    "pointsPerReception": 1,
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
                if season:
                    params["season"] = season
                return self._make_request("getNFLGamesForPlayer", params)
        except Exception as e:
            self.logger.error(f"Failed to get player game stats for {player_id}: {e}")
            return {}
    
    def get_team_roster(self, team: str, get_stats: bool = True) -> Dict[str, Any]:
        """
        Get NFL team roster with stats.
        
        Args:
            team: Team ID or abbreviation
            get_stats: Include player statistics
            
        Returns:
            Dict containing team roster and player stats
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_team_roster(team, get_stats)
            else:
                params = {
                    "teamID": team,
                    "getStats": "true" if get_stats else "false",
                    "fantasyPoints": "true"
                }
                return self._make_request("getNFLTeamRoster", params)
        except Exception as e:
            self.logger.error(f"Failed to get team roster for {team}: {e}")
            return {}
    
    def get_depth_charts(self) -> Dict[str, Any]:
        """
        Get NFL depth charts for all teams.
        
        Returns:
            Dict containing depth chart information
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_depth_charts()
            else:
                return self._make_request("getNFLDepthCharts", {})
        except Exception as e:
            self.logger.error(f"Failed to get depth charts: {e}")
            return {}
    
    def get_nfl_teams(self, sort_by: str = "standings", rosters: bool = False, schedules: bool = False, 
                      top_performers: bool = True, team_stats: bool = True, team_stats_season: int = 2024) -> Dict[str, Any]:
        """
        Get NFL teams information.
        
        Args:
            sort_by: Sort teams by (standings, etc.)
            rosters: Include team rosters
            schedules: Include team schedules
            top_performers: Include top performers
            team_stats: Include team statistics
            team_stats_season: Season for team stats
            
        Returns:
            Dict containing teams information
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_nfl_teams(sort_by, rosters, schedules, top_performers, team_stats, team_stats_season)
            else:
                params = {
                    "sortBy": sort_by,
                    "rosters": "true" if rosters else "false",
                    "schedules": "true" if schedules else "false",
                    "topPerformers": "true" if top_performers else "false",
                    "teamStats": "true" if team_stats else "false",
                    "teamStatsSeason": team_stats_season
                }
                return self._make_request("getNFLTeams", params)
        except Exception as e:
            self.logger.error(f"Failed to get teams: {e}")
            return {}
    
    def get_game_info(self, game_id: str) -> Dict[str, Any]:
        """
        Get general game information.
        
        Args:
            game_id: Game ID (e.g., "20260104_DET@CHI")
            
        Returns:
            Dict containing game information
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_game_info(game_id)
            else:
                params = {"gameID": game_id}
                return self._make_request("getNFLGameInfo", params)
        except Exception as e:
            self.logger.error(f"Failed to get game info for {game_id}: {e}")
            return {}
    
    def get_daily_scoreboard(self, game_date: str = "20250907", top_performers: bool = True) -> Dict[str, Any]:
        """
        Get daily scoreboard - live real time.
        
        Args:
            game_date: Game date (YYYYMMDD format)
            top_performers: Include top performers
            
        Returns:
            Dict containing scores and game data
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_daily_scoreboard(game_date, top_performers)
            else:
                params = {
                    "gameDate": game_date,
                    "topPerformers": "true" if top_performers else "false"
                }
                return self._make_request("getNFLScoresOnly", params)
        except Exception as e:
            self.logger.error(f"Failed to get scores for {game_date}: {e}")
            return {}
    
    def get_changelog(self, max_days: int = 30) -> Dict[str, Any]:
        """
        Get changelog information.
        
        Args:
            max_days: Maximum days to look back
            
        Returns:
            Dict containing changelog data
        """
        if not self.is_available():
            return {}
        
        try:
            if self.use_existing:
                return self.tank01_client.get_changelog(max_days)
            else:
                params = {"maxDays": max_days}
                return self._make_request("getNFLChangelog", params)
        except Exception as e:
            self.logger.error(f"Failed to get changelog: {e}")
            return {}

def main():
    """Test the simplified Tank01 client."""
    print("🏈 Testing Simplified Tank01 Client")
    print("=" * 50)
    
    client = SimpleTank01Client()
    
    if not client.is_available():
        print("❌ Tank01 client not available (RAPIDAPI_KEY required)")
        return
    
    # Test API usage info
    usage = client.get_api_usage()
    print(f"✅ Tank01 client initialized")
    print(f"   Available: {usage['available']}")
    print(f"   Monthly limit: {usage['monthly_limit']}")
    
    # Test news retrieval (low cost)
    print("\n🧪 Testing news retrieval...")
    news = client.get_news(fantasy_news=True, max_items=3)
    if news and 'body' in news:
        articles = news['body']
        if isinstance(articles, list) and articles:
            print(f"✅ Retrieved {len(articles)} news articles")
            for article in articles[:2]:  # Show first 2
                title = article.get('title', 'No title')[:50]
                player = article.get('playerName', 'General')
                print(f"   {player}: {title}...")
    
    # Test player search (if we have a small player list)
    print("\n🧪 Testing player matching...")
    # This would require a full player list, which is expensive
    # So we'll skip this in the test
    print("   Skipping player matching test (conserves API calls)")
    
    # Show final usage
    final_usage = client.get_api_usage()
    print(f"\n📊 Final API usage: {final_usage['calls_made_this_session']} calls")

if __name__ == "__main__":
    main()
