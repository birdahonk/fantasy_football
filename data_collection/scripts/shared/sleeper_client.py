#!/usr/bin/env python3
"""
Simplified Sleeper NFL API Client for Data Collection

A clean, focused client for Sleeper API endpoints used in data collection scripts.
This reuses the working client logic but provides a simpler interface.
"""

import os
import sys
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add the main scripts directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))

try:
    from external.sleeper_client import SleeperClient
except ImportError:
    print("WARNING: Cannot import existing Sleeper client. Creating standalone client.")
    SleeperClient = None

class SimpleSleeperClient:
    """
    Simplified Sleeper NFL API client for data collection scripts.
    
    Provides a clean interface for the most common Sleeper API operations
    needed by data extraction scripts.
    """
    
    def __init__(self):
        """Initialize the simplified Sleeper client."""
        self.logger = logging.getLogger(__name__)
        
        # Try to use the existing client if available
        if SleeperClient:
            try:
                self.sleeper_client = SleeperClient()
                self.logger.info("Using existing Sleeper client")
                self.use_existing = True
            except Exception as e:
                self.logger.warning(f"Failed to initialize existing client: {e}")
                self.use_existing = False
                self._init_standalone()
        else:
            self.logger.info("Creating standalone Sleeper client")
            self.use_existing = False
            self._init_standalone()
    
    def _init_standalone(self):
        """Initialize standalone client if existing one is not available."""
        self.base_url = "https://api.sleeper.app/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FantasyFootballDataCollection/1.0'
        })
        
        # Cache for player database (large download)
        self._players_cache = None
        self._cache_timestamp = None
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Sleeper API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            Dict containing the API response data
        """
        if self.use_existing:
            return self.sleeper_client._make_request(endpoint, params)
        
        # Standalone implementation
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making Sleeper API request: {endpoint}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Sleeper API request successful: {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Sleeper API request failed: {e}")
            raise
    
    def get_nfl_players(self, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Get all NFL players from Sleeper database.
        
        Args:
            force_refresh: Force refresh of cached data
            
        Returns:
            Dictionary of players keyed by player_id
        """
        if self.use_existing:
            return self.sleeper_client.get_nfl_players()
        
        # Check cache first (data is large and changes infrequently)
        if not force_refresh and self._players_cache:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if cache_age < 3600:  # Cache for 1 hour
                self.logger.info("Using cached NFL players data")
                return self._players_cache
        
        try:
            self.logger.info("Fetching NFL players database (this may take a moment...)")
            data = self._make_request("players/nfl")
            
            # Cache the data
            self._players_cache = data
            self._cache_timestamp = datetime.now()
            
            self.logger.info(f"Retrieved {len(data)} NFL players")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get NFL players: {e}")
            return {}
    
    def get_trending_players(self, trend_type: str = "add", lookback_hours: int = 24, 
                           limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get trending players (most added or dropped).
        
        Args:
            trend_type: "add" or "drop"
            lookback_hours: Hours to look back for trends
            limit: Maximum number of players to return
            
        Returns:
            List of trending player dictionaries
        """
        if self.use_existing:
            # Use the enhanced method if available
            if hasattr(self.sleeper_client, 'get_trending_players_with_details'):
                return self.sleeper_client.get_trending_players_with_details(
                    trend_type, lookback_hours, limit
                )
            else:
                return self.sleeper_client.get_trending_players(trend_type, lookback_hours, limit)
        
        # Standalone implementation
        endpoint = f"players/nfl/trending/{trend_type}"
        params = {
            'lookback_hours': lookback_hours,
            'limit': limit
        }
        
        try:
            trending_data = self._make_request(endpoint, params)
            self.logger.info(f"Retrieved {len(trending_data)} trending {trend_type} players")
            return trending_data
            
        except Exception as e:
            self.logger.error(f"Failed to get trending {trend_type} players: {e}")
            return []
    
    def get_trending_with_details(self, trend_type: str = "add", lookback_hours: int = 24, 
                                 limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get trending players with full player details.
        
        Args:
            trend_type: "add" or "drop"
            lookback_hours: Hours to look back
            limit: Maximum number of players
            
        Returns:
            List of trending players with enhanced details
        """
        # Get trending data
        trending = self.get_trending_players(trend_type, lookback_hours, limit)
        if not trending:
            return []
        
        # Get player database for details
        players_db = self.get_nfl_players()
        if not players_db:
            self.logger.warning("Could not get player database for details")
            return trending
        
        # Enhance trending data with player details
        enhanced = []
        for item in trending:
            player_id = item.get('player_id')
            if player_id and player_id in players_db:
                player_data = players_db[player_id].copy()
                player_data['trending_count'] = item.get('count', 0)
                player_data['trend_type'] = trend_type
                enhanced.append(player_data)
            else:
                # Keep original data even if we can't enhance it
                enhanced.append(item)
        
        self.logger.info(f"Enhanced {len(enhanced)} trending players with details")
        return enhanced
    
    def search_players_by_name(self, name: str, position: str = None) -> List[Dict[str, Any]]:
        """
        Search for players by name.
        
        Args:
            name: Player name to search for
            position: Optional position filter
            
        Returns:
            List of matching players
        """
        if self.use_existing:
            return self.sleeper_client.search_players_by_name(name, position)
        
        # Get player database
        players_db = self.get_nfl_players()
        if not players_db:
            return []
        
        name_lower = name.lower()
        matches = []
        
        for player_id, player in players_db.items():
            player_name = player.get('full_name', '').lower()
            first_name = player.get('first_name', '').lower()
            last_name = player.get('last_name', '').lower()
            
            # Check various name matches
            if (name_lower in player_name or 
                name_lower in f"{first_name} {last_name}" or
                name_lower == last_name):
                
                if not position or player.get('position') == position:
                    matches.append(player)
        
        self.logger.info(f"Found {len(matches)} players matching '{name}'")
        return matches
    
    def get_players_by_team(self, team_abbr: str) -> List[Dict[str, Any]]:
        """
        Get all players for a specific NFL team.
        
        Args:
            team_abbr: NFL team abbreviation (e.g., "BUF", "KC")
            
        Returns:
            List of players on the team
        """
        if self.use_existing:
            return self.sleeper_client.get_players_by_team(team_abbr)
        
        # Get player database
        players_db = self.get_nfl_players()
        if not players_db:
            return []
        
        team_players = []
        for player_id, player in players_db.items():
            if player.get('team') == team_abbr:
                team_players.append(player)
        
        self.logger.info(f"Found {len(team_players)} players for team {team_abbr}")
        return team_players
    
    def get_nfl_state(self) -> Dict[str, Any]:
        """
        Get current NFL season state information.
        
        Returns:
            Dict with current week, season, etc.
        """
        try:
            return self._make_request("state/nfl")
        except Exception as e:
            self.logger.error(f"Failed to get NFL state: {e}")
            return {}
    
    def match_yahoo_player(self, yahoo_name: str, yahoo_team: str = None) -> Optional[Dict[str, Any]]:
        """
        Match a Yahoo Fantasy player to Sleeper database.
        
        Args:
            yahoo_name: Player name from Yahoo
            yahoo_team: Player's NFL team from Yahoo
            
        Returns:
            Matching Sleeper player data or None
        """
        # Get player database
        players_db = self.get_nfl_players()
        if not players_db:
            return None
        
        yahoo_name_clean = yahoo_name.lower().strip()
        
        # Try various matching strategies
        for player_id, player in players_db.items():
            sleeper_name = player.get('full_name', '').lower().strip()
            sleeper_team = player.get('team')
            
            # Strategy 1: Exact name match with team validation
            if yahoo_name_clean == sleeper_name:
                if not yahoo_team or not sleeper_team or yahoo_team == sleeper_team:
                    return player
            
            # Strategy 2: Last name match with team validation
            if yahoo_team and sleeper_team and yahoo_team == sleeper_team:
                yahoo_last = yahoo_name_clean.split()[-1] if yahoo_name_clean else ""
                sleeper_last = sleeper_name.split()[-1] if sleeper_name else ""
                if yahoo_last and yahoo_last == sleeper_last:
                    return player
        
        return None

def main():
    """Test the simplified Sleeper client."""
    print("🏈 Testing Simplified Sleeper Client")
    print("=" * 50)
    
    client = SimpleSleeperClient()
    
    # Test NFL state
    print("\n🧪 Testing NFL state...")
    state = client.get_nfl_state()
    if state:
        print(f"✅ Current NFL week: {state.get('week', 'Unknown')}")
        print(f"   Season: {state.get('season', 'Unknown')}")
    
    # Test trending players
    print("\n🧪 Testing trending players...")
    trending = client.get_trending_with_details("add", limit=5)
    if trending:
        print(f"✅ Retrieved {len(trending)} trending players")
        for player in trending[:3]:  # Show first 3
            name = player.get('full_name', 'Unknown')
            position = player.get('position', 'Unknown')
            count = player.get('trending_count', 0)
            print(f"   {name} ({position}): +{count} adds")
    
    # Test player search
    print("\n🧪 Testing player search...")
    josh_allens = client.search_players_by_name("Josh Allen")
    if josh_allens:
        print(f"✅ Found {len(josh_allens)} Josh Allen(s)")
        for player in josh_allens:
            name = player.get('full_name', 'Unknown')
            position = player.get('position', 'Unknown')
            team = player.get('team', 'Unknown')
            print(f"   {name} - {position} - {team}")

if __name__ == "__main__":
    main()
