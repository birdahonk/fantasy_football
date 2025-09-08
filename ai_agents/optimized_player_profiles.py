#!/usr/bin/env python3
"""
Optimized player profile system with configurable limits
Creates comprehensive player profiles from Yahoo, Sleeper, and Tank01 data
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.player_limits import get_player_limits, get_total_available_players, validate_limits
import tiktoken

logger = logging.getLogger(__name__)

class OptimizedPlayerProfiles:
    def __init__(self, player_limits=None):
        """
        Initialize with configurable player limits
        
        Args:
            player_limits: Dict with position -> limit overrides
        """
        self.player_limits = get_player_limits(player_limits)
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Validate limits
        is_valid, error = validate_limits(self.player_limits)
        if not is_valid:
            raise ValueError(f"Invalid player limits: {error}")
        
        logger.info(f"Player limits: {self.player_limits}")
        logger.info(f"Total available players: {get_total_available_players(self.player_limits)}")
    
    def extract_yahoo_data(self, yahoo_player: Dict[str, Any]) -> Dict[str, Any]:
        """Extract essential Yahoo data only"""
        return {
            "player_key": yahoo_player.get("player_key"),
            "player_id": yahoo_player.get("player_id"),
            "name": {
                "full": yahoo_player.get("name", {}).get("full"),
                "first": yahoo_player.get("name", {}).get("first"),
                "last": yahoo_player.get("name", {}).get("last")
            },
            "display_position": yahoo_player.get("display_position"),
            "primary_position": yahoo_player.get("primary_position"),
            "eligible_positions": [pos.get("position") for pos in yahoo_player.get("eligible_positions", [])],
            "team": {
                "name": yahoo_player.get("editorial_team_full_name"),
                "abbr": yahoo_player.get("editorial_team_abbr"),
                "key": yahoo_player.get("editorial_team_key")
            },
            "bye_week": yahoo_player.get("bye_week"),
            "uniform_number": yahoo_player.get("uniform_number"),
            "injury_status": self._extract_injury_status(yahoo_player),
            "is_undroppable": yahoo_player.get("is_undroppable") == "1",
            "percent_owned": yahoo_player.get("percent_owned_value", "0")
        }
    
    def extract_sleeper_data(self, sleeper_player: Dict[str, Any]) -> Dict[str, Any]:
        """Extract essential Sleeper data only"""
        return {
            "player_id": sleeper_player.get("player_id"),
            "name": {
                "full": sleeper_player.get("full_name"),
                "first": sleeper_player.get("first_name"),
                "last": sleeper_player.get("last_name")
            },
            "position": sleeper_player.get("position"),
            "team": sleeper_player.get("team"),
            "depth_chart_position": sleeper_player.get("depth_chart_position"),
            "status": sleeper_player.get("status"),
            "injury_status": sleeper_player.get("injury_status"),
            "player_ids": {
                "sleeper_id": sleeper_player.get("player_id"),
                "yahoo_id": sleeper_player.get("yahoo_id"),
                "espn_id": sleeper_player.get("espn_id"),
                "sportradar_id": sleeper_player.get("sportradar_id"),
                "gsis_id": sleeper_player.get("gsis_id"),
                "pff_id": sleeper_player.get("pff_id"),
                "fantasypros_id": sleeper_player.get("fantasypros_id")
            }
        }
    
    def extract_tank01_data(self, tank01_player: Dict[str, Any]) -> Dict[str, Any]:
        """Extract essential Tank01 data only"""
        # Handle the new Tank01 structure where data is at root level
        tank01_data = tank01_player.get("tank01_data", {})
        
        return {
            "player_id": tank01_data.get("playerID"),
            "name": {
                "full": tank01_data.get("longName"),
                "first": tank01_data.get("longName", "").split()[0] if tank01_data.get("longName") else "",
                "last": tank01_data.get("longName", "").split()[-1] if tank01_data.get("longName") else ""
            },
            "display_position": tank01_data.get("pos"),
            "primary_position": tank01_data.get("pos"),
            "eligible_positions": [tank01_data.get("pos")] if tank01_data.get("pos") else [],
            "bye_week": None,  # Not available in this structure
            "team": tank01_data.get("team"),
            "injury_status": tank01_data.get("injury", "Healthy"),
            "depth_chart": tank01_player.get("depth_chart", {}),
            "projection": tank01_player.get("projection", {}),
            "news": tank01_player.get("news", []),
            "game_stats": tank01_player.get("game_stats", {}),
            "transaction_trends": tank01_player.get("transaction_trends", {}),
            "player_ids": {
                "espn_id": tank01_data.get("espnID"),
                "sleeper_id": tank01_data.get("sleeperBotID"),
                "fantasypros_id": tank01_data.get("fantasyProsPlayerID"),
                "yahoo_id": tank01_data.get("yahooPlayerID")
            }
        }
    
    def _extract_injury_status(self, yahoo_player: Dict[str, Any]) -> str:
        """Extract injury status from Yahoo player data"""
        status = yahoo_player.get("status", "")
        if status == "Q":
            return "Questionable"
        elif status == "D":
            return "Doubtful"
        elif status == "O":
            return "Out"
        elif status == "IR":
            return "Injured Reserve"
        else:
            return "Healthy"
    
    def create_player_profile(self, yahoo_data: Dict[str, Any], 
                            sleeper_data: Optional[Dict[str, Any]] = None,
                            tank01_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create optimized player profile from all available data sources"""
        
        profile = {
            "yahoo_data": self.extract_yahoo_data(yahoo_data),
            "sleeper_data": self.extract_sleeper_data(sleeper_data) if sleeper_data else None,
            "tank01_data": self.extract_tank01_data(tank01_data) if tank01_data else None
        }
        
        return profile
    
    def create_defense_profile(self, yahoo_data: Dict[str, Any],
                             sleeper_data: Optional[Dict[str, Any]] = None,
                             tank01_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create optimized defense profile from all available data sources"""
        
        # Defenses have slightly different structure
        profile = {
            "yahoo_data": self.extract_yahoo_data(yahoo_data),
            "sleeper_data": self.extract_sleeper_data(sleeper_data) if sleeper_data else None,
            "tank01_data": self.extract_tank01_data(tank01_data) if tank01_data else None
        }
        
        return profile
    
    def load_available_players(self, data_dir: str) -> Dict[str, List[Dict[str, Any]]]:
        """Load available players from all APIs with position limits"""
        
        available_players = {
            "yahoo": [],
            "sleeper": [],
            "tank01": []
        }
        
        # Load Yahoo available players
        try:
            yahoo_file = self._find_latest_file(f"{data_dir}/yahoo/available_players", "*_raw_data.json")
            if yahoo_file:
                with open(yahoo_file, 'r') as f:
                    yahoo_data = json.load(f)
                    available_players["yahoo"] = yahoo_data.get("available_players", [])
        except Exception as e:
            logger.warning(f"Could not load Yahoo available players: {e}")
        
        # Load Sleeper available players
        try:
            sleeper_file = self._find_latest_file(f"{data_dir}/sleeper/available_players", "*_raw_data.json")
            if sleeper_file:
                with open(sleeper_file, 'r') as f:
                    sleeper_data = json.load(f)
                    available_players["sleeper"] = sleeper_data.get("available_players", [])
        except Exception as e:
            logger.warning(f"Could not load Sleeper available players: {e}")
        
        # Load Tank01 available players (separate from Yahoo)
        try:
            tank01_file = self._find_latest_file(f"{data_dir}/tank01/available_players", "*_raw_data.json")
            if tank01_file:
                with open(tank01_file, 'r') as f:
                    tank01_data = json.load(f)
                    # Tank01 data is in processed_data.available_players
                    if "processed_data" in tank01_data and "available_players" in tank01_data["processed_data"]:
                        available_players["tank01"] = tank01_data["processed_data"]["available_players"]
                    else:
                        available_players["tank01"] = tank01_data.get("available_players", [])
        except Exception as e:
            logger.warning(f"Could not load Tank01 available players: {e}")
        
        return available_players
    
    def create_optimized_available_players(self, data_dir: str) -> Dict[str, Any]:
        """Create optimized available players with position limits"""
        
        # Load raw data
        raw_data = self.load_available_players(data_dir)
        
        # Group players by position
        players_by_position = {}
        
        # Process Yahoo players (primary source)
        for player in raw_data["yahoo"]:
            position = player.get("display_position", "Unknown")
            if position not in players_by_position:
                players_by_position[position] = []
            
            # Find matching Sleeper and Tank01 data
            sleeper_match = self._find_matching_player(player, raw_data["sleeper"])
            tank01_match = self._find_matching_tank01_player(player, raw_data["tank01"])
            
            # Create optimized profile
            profile = self.create_player_profile(player, sleeper_match, tank01_match)
            players_by_position[position].append(profile)
        
        # Apply position limits
        limited_players = {}
        for position, players in players_by_position.items():
            limit = self.player_limits.get(position, 20)
            limited_players[position] = players[:limit]
        
        # Calculate token usage
        total_tokens = self._calculate_token_usage(limited_players)
        
        return {
            "season_context": self._extract_season_context(raw_data),
            "player_limits": self.player_limits,
            "total_players": sum(len(players) for players in limited_players.values()),
            "total_tokens": total_tokens,
            "players_by_position": limited_players,
            "source_files": self._extract_source_files(raw_data)
        }
    
    def _find_matching_player(self, yahoo_player: Dict[str, Any], 
                            other_players: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching player in other API data"""
        yahoo_name = yahoo_player.get("name", {}).get("full", "").lower()
        yahoo_team = yahoo_player.get("editorial_team_abbr", "").upper()
        
        for player in other_players:
            other_name = player.get("full_name", "").lower()
            other_team = player.get("team", "").upper()
            
            # Simple name and team matching
            if yahoo_name == other_name and yahoo_team == other_team:
                return player
        
        return None
    
    def _find_matching_tank01_player(self, yahoo_player: Dict[str, Any], tank01_players: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching Tank01 player by matching Yahoo data within Tank01 structure"""
        yahoo_name = yahoo_player.get("name", {}).get("full", "").lower()
        yahoo_team = yahoo_player.get("editorial_team_abbr", "").upper()
        
        for tank01_player in tank01_players:
            if "yahoo_data" in tank01_player:
                yahoo_data = tank01_player["yahoo_data"]
                tank01_yahoo_name = yahoo_data.get("name", {}).get("full", "").lower()
                tank01_yahoo_team = yahoo_data.get("editorial_team_abbr", "").upper()
                
                # Match by name and team
                if yahoo_name == tank01_yahoo_name and yahoo_team == tank01_yahoo_team:
                    # Return the entire Tank01 player data (includes tank01_data, projection, news, etc.)
                    return tank01_player
        
        return None
    
    def _find_latest_file(self, directory: str, pattern: str) -> Optional[str]:
        """Find the latest file matching pattern in directory with YYYY/MM/DD structure"""
        import glob
        import os
        
        files = glob.glob(f"{directory}/**/{pattern}", recursive=True)
        if not files:
            return None
        
        return max(files, key=os.path.getctime)
    
    def _extract_season_context(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract season context from any available data source"""
        for api_data in raw_data.values():
            if isinstance(api_data, dict) and "season_context" in api_data:
                return api_data["season_context"]
        
        # Fallback to current date
        from datetime import datetime
        return {
            "nfl_season": "2025",
            "current_week": 1,
            "season_phase": "Early Regular Season"
        }
    
    def _extract_source_files(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract source file information"""
        source_files = []
        for api, data in raw_data.items():
            if isinstance(data, list) and data:
                # This is player data, not file info
                continue
            elif isinstance(data, dict) and "source_file" in data:
                source_files.append(f"{api}: {data['source_file']}")
        return source_files
    
    def _calculate_token_usage(self, players_by_position: Dict[str, List[Dict[str, Any]]]) -> int:
        """Calculate total token usage for all players"""
        total_tokens = 0
        
        for position, players in players_by_position.items():
            for player in players:
                player_json = json.dumps(player, indent=2)
                total_tokens += len(self.encoding.encode(player_json))
        
        return total_tokens
    
    def get_token_estimate(self) -> Dict[str, Any]:
        """Get token usage estimate for current configuration"""
        total_players = get_total_available_players(self.player_limits)
        
        # Estimate based on optimized profile size (~810 tokens per player)
        estimated_tokens_per_player = 810
        estimated_total_tokens = total_players * estimated_tokens_per_player
        
        return {
            "player_limits": self.player_limits,
            "total_players": total_players,
            "estimated_tokens_per_player": estimated_tokens_per_player,
            "estimated_total_tokens": estimated_total_tokens,
            "within_200k_limit": estimated_total_tokens <= 200000
        }
