#!/usr/bin/env python3
"""
Sleeper NFL API Client

This module provides a client for accessing the Sleeper NFL API to retrieve
trending players, player metadata, and other NFL-related data.

Sleeper API Documentation: https://docs.sleeper.com/
Base URL: https://api.sleeper.app/v1/

Key Features:
- Completely free (no API key required)
- Trending players (most added/dropped)
- Player metadata and basic stats
- No rate limits for reasonable usage

Author: Fantasy Football Optimizer
Date: January 2025
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

class SleeperClient:
    """Client for interacting with the Sleeper NFL API."""
    
    def __init__(self):
        """Initialize the Sleeper API client."""
        self.base_url = "https://api.sleeper.app/v1"
        self.session = requests.Session()
        self.session.headers.update({
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
                    logging.FileHandler(logs_dir / 'sleeper_api.log'),
                    logging.StreamHandler()
                ]
            )
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Sleeper API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            Dict containing the API response data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making request to: {url}")
            if params:
                self.logger.info(f"Parameters: {params}")
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Request successful. Response size: {len(str(data))} characters")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            self.logger.error(f"URL: {url}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Response text: {e.response.text}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise
    
    def get_nfl_players(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all NFL players data from Sleeper.
        
        Returns:
            Dict mapping player_id to player data
            
        Example response structure:
        {
            "player_id": {
                "player_id": "4046",
                "first_name": "Josh",
                "last_name": "Allen",
                "full_name": "Josh Allen",
                "position": "QB",
                "team": "BUF",
                "age": 27,
                "height": "76",
                "weight": "237",
                "years_exp": 6,
                "injury_status": null,
                "injury_body_part": null,
                "injury_start_date": null,
                "injury_notes": null
            }
        }
        """
        try:
            self.logger.info("Fetching all NFL players from Sleeper API")
            players_data = self._make_request("players/nfl")
            
            self.logger.info(f"Retrieved {len(players_data)} NFL players")
            return players_data
            
        except Exception as e:
            self.logger.error(f"Failed to get NFL players: {e}")
            return {}
    
    def get_trending_players(self, trend_type: str = "add", lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get trending NFL players (most added or dropped).
        
        Args:
            trend_type: "add" for most added, "drop" for most dropped
            lookback_hours: Hours to look back (default 24)
            limit: Number of players to return (default 25)
            
        Returns:
            List of trending player data
            
        Example response structure:
        [
            {
                "player_id": "4046",
                "count": 1234  # Number of times added/dropped
            }
        ]
        """
        try:
            self.logger.info(f"Fetching trending players: {trend_type} (last {lookback_hours}h, limit {limit})")
            
            # Sleeper API endpoint for trending players
            endpoint = f"players/nfl/trending/{trend_type}"
            params = {
                "lookback_hours": lookback_hours,
                "limit": limit
            }
            
            trending_data = self._make_request(endpoint, params)
            
            self.logger.info(f"Retrieved {len(trending_data)} trending {trend_type} players")
            return trending_data
            
        except Exception as e:
            self.logger.error(f"Failed to get trending players: {e}")
            return []
    
    def get_trending_players_with_details(self, trend_type: str = "add", lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get trending players with full player details.
        
        This method combines trending data with player metadata to provide
        complete information about trending players.
        
        Args:
            trend_type: "add" for most added, "drop" for most dropped
            lookback_hours: Hours to look back (default 24)
            limit: Number of players to return (default 25)
            
        Returns:
            List of trending players with full details
        """
        try:
            # Get trending players
            trending_players = self.get_trending_players(trend_type, lookback_hours, limit)
            
            if not trending_players:
                return []
            
            # Get all players data for lookup
            all_players = self.get_nfl_players()
            
            # Combine trending data with player details
            detailed_trending = []
            for trending_player in trending_players:
                player_id = trending_player.get("player_id")
                count = trending_player.get("count", 0)
                
                if player_id in all_players:
                    player_details = all_players[player_id].copy()
                    player_details["trending_count"] = count
                    player_details["trending_type"] = trend_type
                    detailed_trending.append(player_details)
                else:
                    self.logger.warning(f"Player {player_id} not found in players database")
            
            self.logger.info(f"Retrieved {len(detailed_trending)} trending players with details")
            return detailed_trending
            
        except Exception as e:
            self.logger.error(f"Failed to get trending players with details: {e}")
            return []
    
    def get_player_by_id(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific player data by player ID.
        
        Args:
            player_id: Sleeper player ID
            
        Returns:
            Player data dict or None if not found
        """
        try:
            all_players = self.get_nfl_players()
            return all_players.get(player_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get player {player_id}: {e}")
            return None
    
    def search_players_by_name(self, name: str, position: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for players by name.
        
        Args:
            name: Player name (first, last, or full name)
            position: Optional position filter (QB, RB, WR, TE, K, DEF)
            
        Returns:
            List of matching players
        """
        try:
            all_players = self.get_nfl_players()
            matches = []
            
            name_lower = name.lower()
            
            for player_data in all_players.values():
                # Check if name matches first, last, or full name
                first_name = player_data.get("first_name", "").lower()
                last_name = player_data.get("last_name", "").lower()
                full_name = player_data.get("full_name", "").lower()
                
                if (name_lower in first_name or 
                    name_lower in last_name or 
                    name_lower in full_name):
                    
                    # Apply position filter if specified
                    if position and player_data.get("position") != position:
                        continue
                        
                    matches.append(player_data)
            
            self.logger.info(f"Found {len(matches)} players matching '{name}'")
            return matches
            
        except Exception as e:
            self.logger.error(f"Failed to search players by name: {e}")
            return []
    
    def get_players_by_team(self, team: str) -> List[Dict[str, Any]]:
        """
        Get all players for a specific NFL team.
        
        Args:
            team: NFL team abbreviation (e.g., "BUF", "KC", "DAL")
            
        Returns:
            List of players on the team
        """
        try:
            all_players = self.get_nfl_players()
            team_players = []
            
            team_upper = team.upper()
            
            for player_data in all_players.values():
                if player_data.get("team") == team_upper:
                    team_players.append(player_data)
            
            self.logger.info(f"Found {len(team_players)} players for team {team}")
            return team_players
            
        except Exception as e:
            self.logger.error(f"Failed to get players for team {team}: {e}")
            return []
    
    def get_players_by_position(self, position: str) -> List[Dict[str, Any]]:
        """
        Get all players for a specific position.
        
        Args:
            position: Position abbreviation (QB, RB, WR, TE, K, DEF)
            
        Returns:
            List of players at the position
        """
        try:
            all_players = self.get_nfl_players()
            position_players = []
            
            position_upper = position.upper()
            
            for player_data in all_players.values():
                if player_data.get("position") == position_upper:
                    position_players.append(player_data)
            
            self.logger.info(f"Found {len(position_players)} players at position {position}")
            return position_players
            
        except Exception as e:
            self.logger.error(f"Failed to get players for position {position}: {e}")
            return []
    
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


def main():
    """Test the Sleeper API client."""
    client = SleeperClient()
    
    print("🏈 Testing Sleeper NFL API Client")
    print("=" * 50)
    
    # Test 1: Get trending added players
    print("\n📈 Most Added Players (Last 24 hours):")
    trending_added = client.get_trending_players_with_details("add", limit=10)
    for i, player in enumerate(trending_added, 1):
        name = player.get("full_name", "Unknown") or "Unknown"
        position = player.get("position", "N/A") or "N/A"
        team = player.get("team", "N/A") or "N/A"
        count = player.get("trending_count", 0)
        injury = player.get("injury_status", "") or ""
        injury_note = f" ({injury})" if injury else ""
        print(f"  {i:2d}. {name:<20} | {position:2} | {team:3} | Added {count:4d} times{injury_note}")
    
    # Test 2: Get trending dropped players
    print("\n📉 Most Dropped Players (Last 24 hours):")
    trending_dropped = client.get_trending_players_with_details("drop", limit=10)
    for i, player in enumerate(trending_dropped, 1):
        name = player.get("full_name", "Unknown") or "Unknown"
        position = player.get("position", "N/A") or "N/A"
        team = player.get("team", "N/A") or "N/A"
        count = player.get("trending_count", 0)
        injury = player.get("injury_status", "") or ""
        injury_note = f" ({injury})" if injury else ""
        print(f"  {i:2d}. {name:<20} | {position:2} | {team:3} | Dropped {count:4d} times{injury_note}")
    
    # Test 3: Search for a specific player
    print("\n🔍 Search Test - Josh Allen:")
    josh_allens = client.search_players_by_name("Josh Allen")
    for player in josh_allens:
        name = player.get("full_name", "Unknown") or "Unknown"
        position = player.get("position", "N/A") or "N/A"
        team = player.get("team", "N/A") or "N/A"
        age = player.get("age", "N/A") or "N/A"
        print(f"  {name} | {position} | {team} | Age {age}")
    
    # Test 4: Get players by team
    print("\n🏟️  Buffalo Bills Players (first 5):")
    bills_players = client.get_players_by_team("BUF")[:5]
    for player in bills_players:
        name = player.get("full_name", "Unknown") or "Unknown"
        position = player.get("position", "N/A") or "N/A"
        print(f"  {name:<25} | {position}")
    
    print("\n✅ Sleeper API Client test completed!")
    
    # Save debug data
    if trending_added:
        client.save_debug_data(trending_added[:3], "sleeper_trending_added.json")
    if trending_dropped:
        client.save_debug_data(trending_dropped[:3], "sleeper_trending_dropped.json")


if __name__ == "__main__":
    main()
