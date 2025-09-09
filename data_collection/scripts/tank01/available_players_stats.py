#!/usr/bin/env python3
"""
Tank01 Available Players Game Stats Collection Script

This script fetches comprehensive Tank01 API game statistics for available players from Yahoo Fantasy Football.
It processes players from the Yahoo available players output and enriches them with Tank01 game stats data.

Configuration:
- DEVELOPMENT_MODE: Set to True for testing with 5 players, False for production with 25 players
- AVAILABLE_PLAYERS_LIMIT: Number of available players to process (5 for dev, 25 for production)
- INJURY_REPORTS_LIMIT: Number of injury report players to process (0 for now, configurable)
- TOP_AVAILABLE_LIMIT: Number of top available players to process (0 for now, configurable)

Features:
- Configurable player limits for different sections
- Comprehensive Tank01 game stats extraction using getNFLGamesForPlayer endpoint
- Team defense handling with appropriate data display
- RapidAPI usage tracking with Pacific Time Zone
- Batch API optimization for efficiency
- Player matching with multiple fallback strategies
- Season context detection and week-specific file naming
- Fantasy points calculation with PPR scoring
- Season totals, averages, and recent performance analysis
"""

import json
import logging
import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pytz

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Import player limits from config
from config.player_limits import DEFAULT_PLAYER_LIMITS, get_player_limits

from tank01_client import SimpleTank01Client
from file_utils import DataFileManager
from api_usage_manager import APIUsageManager

def parse_arguments():
    """Parse command line arguments for configurable player limits"""
    parser = argparse.ArgumentParser(description='Tank01 Available Players Game Stats Collection')
    parser.add_argument('--dev', action='store_true', help='Use development mode (5 players per position)')
    parser.add_argument('--all', type=int, help='Set all position limits to this value')
    parser.add_argument('--qb', type=int, help='Number of QBs to process')
    parser.add_argument('--rb', type=int, help='Number of RBs to process')
    parser.add_argument('--wr', type=int, help='Number of WRs to process')
    parser.add_argument('--te', type=int, help='Number of TEs to process')
    parser.add_argument('--k', type=int, help='Number of Ks to process')
    parser.add_argument('--def', type=int, dest='defense', help='Number of DEFs to process')
    parser.add_argument('--flex', type=int, help='Number of FLEX players to process')
    return parser.parse_args()

# Configuration
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true'

# Use position-based limits instead of total limit
PLAYER_LIMITS = get_player_limits() if not DEVELOPMENT_MODE else {
    "QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DEF": 2, "FLEX": 2
}

INJURY_REPORTS_LIMIT = 25  # Process 25 injury report players
TOP_AVAILABLE_LIMIT = 15   # Process 15 top available players

class Tank01AvailablePlayersStatsExtractor:
    """Extract Tank01 game statistics for available Yahoo Fantasy players."""
    
    def __init__(self, player_limits: Optional[Dict[str, int]] = None):
        """Initialize the extractor with configurable player limits."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Tank01 client
        self.tank01 = SimpleTank01Client()
        
        # Initialize file manager
        self.file_manager = DataFileManager()
        
        # Set player limits (use defaults if not provided)
        self.player_limits = player_limits or get_player_limits()
        
        # Initialize centralized API usage manager
        self.usage_manager = APIUsageManager(self.tank01, "Tank01")
        
        self.stats = {
            "start_time": datetime.now(),
            "yahoo_players_loaded": 0,
            "players_processed": 0,
            "players_matched": 0,
            "players_unmatched": 0,
            "total_games_collected": 0,
            "api_calls": 0,
            "errors": 0
        }
        
        # Cache for Tank01 player database
        self._tank01_player_cache = None
    
    def _extract_season_context(self, yahoo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract season and week context from Yahoo data.
        
        Args:
            yahoo_data: Raw Yahoo data containing season/week info
            
        Returns:
            Dict containing season context information
        """
        season_context = {
            "nfl_season": "2025",
            "current_week": 1,
            "season_phase": "Regular Season",
            "data_source": "Yahoo Fantasy API",
            "week_info": {},
            "verification_notes": []
        }
        
        try:
            # Try to extract week info from Yahoo data
            if 'league' in yahoo_data:
                league = yahoo_data['league']
                if 'current_week' in league:
                    season_context['current_week'] = league['current_week']
                    season_context['verification_notes'].append(f"Week extracted from Yahoo league data: {league['current_week']}")
                
                if 'season' in league:
                    season_context['nfl_season'] = str(league['season'])
                    season_context['verification_notes'].append(f"Season extracted from Yahoo league data: {league['season']}")
            
            # Add week info details
            current_week = season_context['current_week']
            season_context['week_info'] = {
                'week_start': f"Week {current_week} Start",
                'week_end': f"Week {current_week} End", 
                'status': 'In Progress',
                'source': 'Yahoo Fantasy API'
            }
            
            # Add verification notes
            season_context['verification_notes'].extend([
                f"Season context extracted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Using NFL season: {season_context['nfl_season']}",
                f"Current week: {season_context['current_week']}"
            ])
            
        except Exception as e:
            self.logger.warning(f"Could not extract season context from Yahoo data: {e}")
            season_context['verification_notes'].append(f"Season context extraction failed: {str(e)}")
        
        return season_context
    
    def _load_latest_yahoo_available_players(self) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Load the latest Yahoo available players data.
        
        Returns:
            Tuple of (available_players_list, full_yahoo_data)
        """
        try:
            # Find the most recent available_players output file
            outputs_dir = Path("data_collection/outputs/yahoo/available_players")
            if not outputs_dir.exists():
                self.logger.error(f"Yahoo available players output directory not found: {outputs_dir}")
                return [], {}
            
            # Get all JSON files and sort by modification time
            json_files = list(outputs_dir.glob("**/*.json"))
            if not json_files:
                self.logger.error("No Yahoo available players JSON files found")
                return [], {}
            
            # Sort by modification time (newest first)
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading latest Yahoo available players data from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                yahoo_data = json.load(f)
            
            # Extract available players
            available_players = yahoo_data.get('available_players', [])
            if not available_players:
                self.logger.error("No available players found in Yahoo data")
                return [], yahoo_data
            
            self.logger.info(f"Loaded {len(available_players)} available players from Yahoo")
            self.stats["yahoo_players_loaded"] = len(available_players)
            
            return available_players, yahoo_data
            
        except Exception as e:
            self.logger.error(f"Failed to load Yahoo available players data: {e}")
            self.stats["errors"] += 1
            return [], {}
    
    def _filter_players_by_position_limits(self, players: List[Dict]) -> List[Dict]:
        """Filter players by position-based limits"""
        position_counts = {pos: 0 for pos in self.player_limits.keys()}
        filtered_players = []
        
        for player in players:
            position = player.get('display_position', 'Unknown')
            
            # Handle multi-position players (FLEX) - same logic as ComprehensiveDataProcessor
            if position in ['W/R/T', 'W/R', 'Q/W/R/T', 'WR,TE', 'RB,TE', 'WR,RB', 'QB,WR']:
                position = 'FLEX'
            
            # Check if we need more players for this position
            if position in position_counts and position_counts[position] < self.player_limits[position]:
                filtered_players.append(player)
                position_counts[position] += 1
                
                # Log progress for first few players of each position
                if position_counts[position] <= 3:
                    self.logger.info(f"  Added {position} player {position_counts[position]}: {player.get('name', {}).get('full', 'Unknown')}")
        
        # Log final counts
        for position, count in position_counts.items():
            limit = self.player_limits[position]
            self.logger.info(f"  {position}: {count}/{limit} players")
        
        return filtered_players
    
    def _get_tank01_player_database(self) -> Dict[str, Any]:
        """
        Get Tank01 player database for matching.
        
        Returns:
            Dict containing Tank01 player database
        """
        try:
            self.logger.info("Fetching Tank01 player database...")
            player_db = self.tank01.get_player_database()
            
            if not player_db:
                self.logger.error("Failed to get Tank01 player database")
                return {}
            
            self.stats["api_calls"] += 1
            self.logger.info(f"Loaded Tank01 player database with {len(player_db)} players")
            return player_db
            
        except Exception as e:
            self.logger.error(f"Failed to get Tank01 player database: {e}")
            self.stats["errors"] += 1
            return {}
    
    def _match_yahoo_to_tank01(self, yahoo_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Match a Yahoo player to Tank01 player data.
        
        Args:
            yahoo_player: Yahoo player data
            
        Returns:
            Tank01 player data if matched, None otherwise
        """
        if not self._tank01_player_cache:
            return None
        
        try:
            # Strategy 1: Try to match by Yahoo player ID
            yahoo_id = yahoo_player.get('player_id')
            if yahoo_id:
                for tank01_player in self._tank01_player_cache.values():
                    if tank01_player.get('yahoo_id') == str(yahoo_id):
                        return tank01_player
            
            # Strategy 2: Try to match by exact name and team
            yahoo_name = yahoo_player.get('name', {}).get('full', '').strip()
            yahoo_team = yahoo_player.get('editorial_team_abbr', '').strip()
            
            if yahoo_name and yahoo_team:
                for tank01_player in self._tank01_player_cache.values():
                    tank01_name = tank01_player.get('longName', '').strip()
                    tank01_team = tank01_player.get('team', '').strip()
                    
                    if yahoo_name.lower() == tank01_name.lower() and yahoo_team.upper() == tank01_team.upper():
                        return tank01_player
            
            # Strategy 3: Try to match by last name and team
            yahoo_last_name = yahoo_name.split()[-1] if yahoo_name else ''
            if yahoo_last_name and yahoo_team:
                for tank01_player in self._tank01_player_cache.values():
                    tank01_name = tank01_player.get('longName', '').strip()
                    tank01_team = tank01_player.get('team', '').strip()
                    tank01_last_name = tank01_name.split()[-1] if tank01_name else ''
                    
                    if (yahoo_last_name.lower() == tank01_last_name.lower() and 
                        yahoo_team.upper() == tank01_team.upper()):
                        return tank01_player
            
            # Strategy 4: Try to get player info directly from Tank01 API
            if yahoo_name:
                try:
                    player_info = self.tank01.get_player_info(yahoo_name)
                    if player_info:
                        self.stats["api_calls"] += 1
                        return player_info
                except Exception as e:
                    self.logger.debug(f"get_player_info failed for {yahoo_name}: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error matching Yahoo player {yahoo_player.get('name', {}).get('full', 'Unknown')}: {e}")
            self.stats["errors"] += 1
            return None
    
    def _get_team_defense_stats(self, team_abbr: str) -> Dict[str, Any]:
        """
        Get team-level defense stats using the getNFLTeams endpoint.
        
        Args:
            team_abbr: Team abbreviation (e.g., 'PHI', 'DAL')
            
        Returns:
            Dict containing team defense statistics
        """
        try:
            self.logger.info(f"Fetching team defense stats for {team_abbr}")
            
            # Get team data from Tank01 API
            team_data = self.tank01.get_nfl_teams(team_stats=True, team_stats_season=2025)
            
            if not team_data or 'body' not in team_data:
                self.logger.warning(f"No team data found for {team_abbr}")
                return {}
            
            teams = team_data.get('body', [])
            if not isinstance(teams, list):
                self.logger.warning(f"Invalid team data format for {team_abbr}")
                return {}
            
            # Find the specific team
            for team in teams:
                if team.get('teamAbv', '').upper() == team_abbr.upper():
                    team_data = team.get('teamStats', {})
                    defense_stats = team_data.get('Defense', {})
                    
                    def safe_float(value, default=0.0):
                        """Safely convert value to float"""
                        try:
                            return float(value) if value is not None else default
                        except (ValueError, TypeError):
                            return default
                    
                    interceptions = safe_float(defense_stats.get('defensiveInterceptions', 0))
                    fumbles_recovered = safe_float(defense_stats.get('fumblesRecovered', 0))
                    
                    return {
                        'pointsAllowed': safe_float(team.get('pa', 0)),
                        'pointsFor': safe_float(team.get('pf', 0)),
                        'yardsAllowed': safe_float(defense_stats.get('passingYardsAllowed', 0)) + safe_float(defense_stats.get('rushingYardsAllowed', 0)),
                        'passYardsAllowed': safe_float(defense_stats.get('passingYardsAllowed', 0)),
                        'rushYardsAllowed': safe_float(defense_stats.get('rushingYardsAllowed', 0)),
                        'passTDAllowed': safe_float(defense_stats.get('passingTDAllowed', 0)),
                        'rushTDAllowed': safe_float(defense_stats.get('rushingTDAllowed', 0)),
                        'interceptions': interceptions,
                        'fumblesRecovered': fumbles_recovered,
                        'sacks': safe_float(defense_stats.get('sacks', 0)),
                        'safeties': safe_float(defense_stats.get('safeties', 0)),
                        'defTD': safe_float(defense_stats.get('defTD', 0)),
                        'turnovers': interceptions + fumbles_recovered,
                        'totalTackles': safe_float(defense_stats.get('totalTackles', 0)),
                        'soloTackles': safe_float(defense_stats.get('soloTackles', 0)),
                        'tacklesForLoss': safe_float(defense_stats.get('tfl', 0)),
                        'qbHits': safe_float(defense_stats.get('qbHits', 0)),
                        'passDeflections': safe_float(defense_stats.get('passDeflections', 0)),
                        'twoPointConversionReturn': safe_float(defense_stats.get('twoPointConversionReturn', 0)),
                        'wins': safe_float(team.get('wins', 0)),
                        'losses': safe_float(team.get('loss', 0)),
                        'ties': safe_float(team.get('tie', 0)),
                        'raw_team_data': team
                    }
            
            self.logger.warning(f"No team defense stats found for {team_abbr}")
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting team defense stats for {team_abbr}: {e}")
            return {}
    
    def _get_player_game_stats(self, tank01_player: Dict[str, Any], season: str = "2025", team_defense_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get comprehensive game statistics for a player.
        
        Args:
            tank01_player: Tank01 player data
            season: NFL season year
            
        Returns:
            Dict containing comprehensive game statistics
        """
        try:
            player_id = tank01_player.get('playerID')
            if not player_id:
                self.logger.warning(f"No player ID found for {tank01_player.get('longName', 'Unknown')}")
                return {}
            
            # Get player game stats from Tank01
            game_data = self.tank01.get_player_game_stats(player_id, season)
            if not game_data:
                self.logger.warning(f"No game data found for {tank01_player.get('longName', 'Unknown')}")
                return {}
            
            self.stats["api_calls"] += 1
            
            # Process the game data
            games = game_data.get('body', [])
            if not games:
                self.logger.warning(f"No games found in data for {tank01_player.get('longName', 'Unknown')}")
                return {}
            
            # Process each game
            processed_games = []
            for game in games:
                processed_game = self._process_game_data(game, tank01_player)
                if processed_game:
                    processed_games.append(processed_game)
            
            # Calculate season totals and averages
            season_totals = self._calculate_season_totals(processed_games, team_defense_stats)
            season_averages = self._calculate_season_averages(processed_games, season_totals)
            
            # Get recent performance (last 3 games)
            recent_performance = processed_games[-3:] if len(processed_games) >= 3 else processed_games
            
            return {
                'total_games': len(processed_games),
                'games': processed_games,
                'season_totals': season_totals,
                'season_averages': season_averages,
                'recent_performance': recent_performance
            }
            
        except Exception as e:
            self.logger.error(f"Error getting game stats for {tank01_player.get('longName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
            return {}
    
    def _process_game_data(self, game: Dict[str, Any], tank01_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process individual game data and calculate fantasy points.
        
        Args:
            game: Raw game data from Tank01 API
            tank01_player: Tank01 player data for context
            
        Returns:
            Processed game data with fantasy points
        """
        try:
            # Extract basic game info
            game_id = game.get('gameID', '')
            game_date = self._extract_game_date(game_id)
            week = self._extract_week_from_game_id(game_id)
            opponent = self._extract_opponent_from_game_id(game_id, tank01_player)
            
            # Extract stats by category
            passing = game.get('passing', {})
            rushing = game.get('rushing', {})
            receiving = game.get('receiving', {})
            defense = game.get('defense', {})
            
            # Calculate fantasy points
            fantasy_points = self._calculate_fantasy_points(passing, rushing, receiving, defense)
            
            return {
                'game_id': game_id,
                'game_date': game_date,
                'week': week,
                'opponent': opponent,
                'fantasy_points': fantasy_points,
                'passing': passing,
                'rushing': rushing,
                'receiving': receiving,
                'defense': defense
            }
            
        except Exception as e:
            self.logger.error(f"Error processing game data: {e}")
            return None
    
    def _extract_game_date(self, game_id: str) -> str:
        """Extract game date from game ID."""
        try:
            # Game ID format: YYYYMMDD_HHMMSS_team1_team2
            if '_' in game_id:
                date_part = game_id.split('_')[0]
                if len(date_part) == 8:  # YYYYMMDD
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    return f"{year}-{month}-{day}"
        except Exception:
            pass
        return "Unknown"
    
    def _extract_week_from_game_id(self, game_id: str) -> str:
        """Extract week number from game ID."""
        try:
            # This is a simplified approach - in reality, you'd need to map dates to weeks
            # For now, return a placeholder
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def _extract_opponent_from_game_id(self, game_id: str, tank01_player: Dict[str, Any]) -> str:
        """Extract opponent team from game ID."""
        try:
            # Game ID format: YYYYMMDD_HHMMSS_team1_team2
            if '_' in game_id:
                parts = game_id.split('_')
                if len(parts) >= 4:
                    team1 = parts[2]
                    team2 = parts[3]
                    player_team = tank01_player.get('team', '').upper()
                    
                    # Return the team that's not the player's team
                    if team1.upper() == player_team:
                        return team2.upper()
                    elif team2.upper() == player_team:
                        return team1.upper()
                    else:
                        # If neither matches, return both
                        return f"{team1.upper()}/{team2.upper()}"
        except Exception:
            pass
        return "Unknown"
    
    def _calculate_fantasy_points(self, passing: Dict, rushing: Dict, receiving: Dict, defense: Dict) -> float:
        """
        Calculate fantasy points using PPR scoring.
        
        Args:
            passing: Passing statistics
            rushing: Rushing statistics  
            receiving: Receiving statistics
            defense: Defense statistics
            
        Returns:
            Total fantasy points
        """
        points = 0.0
        
        def safe_float(value, default=0.0):
            """Safely convert value to float"""
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        # Passing points
        points += safe_float(passing.get('passYds', 0)) * 0.04  # 1 point per 25 yards
        points += safe_float(passing.get('passTD', 0)) * 4      # 4 points per passing TD
        points += safe_float(passing.get('passInt', 0)) * -2    # -2 points per interception
        
        # Rushing points
        points += safe_float(rushing.get('rushYds', 0)) * 0.1   # 1 point per 10 yards
        points += safe_float(rushing.get('rushTD', 0)) * 6      # 6 points per rushing TD
        
        # Receiving points (PPR)
        points += safe_float(receiving.get('recYds', 0)) * 0.1  # 1 point per 10 yards
        points += safe_float(receiving.get('recTD', 0)) * 6     # 6 points per receiving TD
        points += safe_float(receiving.get('receptions', 0)) * 1 # 1 point per reception (PPR)
        
        # Defense points (simplified)
        points += safe_float(defense.get('defTD', 0)) * 6       # 6 points per defensive TD
        points += safe_float(defense.get('defInt', 0)) * 2      # 2 points per interception
        points += safe_float(defense.get('defFR', 0)) * 2       # 2 points per fumble recovery
        points += safe_float(defense.get('defSack', 0)) * 1     # 1 point per sack
        
        return round(points, 2)
    
    def _calculate_season_totals(self, games: List[Dict[str, Any]], team_defense_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate season totals from game data.
        
        Args:
            games: List of processed game data
            team_defense_stats: Team defense stats for defense players
            
        Returns:
            Dict containing season totals
        """
        totals = {
            'games_played': len(games),
            'fantasy_points': 0.0,
            'passing': {},
            'rushing': {},
            'receiving': {},
            'defense': {}
        }
        
        # If no games but we have team defense stats, use those instead
        if not games and team_defense_stats:
            totals['games_played'] = 1  # Team defense stats represent 1 game
            # Map team defense stats to our defense totals
            totals['defense'] = {
                'fumblesRecovered': team_defense_stats.get('fumblesRecovered', 0),
                'interceptions': team_defense_stats.get('interceptions', 0),
                'sacks': team_defense_stats.get('sacks', 0),
                'safeties': team_defense_stats.get('safeties', 0),
                'defTD': team_defense_stats.get('defTD', 0),
                'totalTackles': team_defense_stats.get('totalTackles', 0),
                'soloTackles': team_defense_stats.get('soloTackles', 0),
                'tacklesForLoss': team_defense_stats.get('tacklesForLoss', 0),
                'qbHits': team_defense_stats.get('qbHits', 0),
                'passDeflections': team_defense_stats.get('passDeflections', 0),
                'pointsAllowed': team_defense_stats.get('pointsAllowed', 0),
                'yardsAllowed': team_defense_stats.get('yardsAllowed', 0),
                'passYardsAllowed': team_defense_stats.get('passYardsAllowed', 0),
                'rushYardsAllowed': team_defense_stats.get('rushYardsAllowed', 0),
                'turnovers': team_defense_stats.get('turnovers', 0)
            }
            
            # Calculate fantasy points for team defense
            totals['fantasy_points'] = self._calculate_fantasy_points(totals['defense'])
            return totals
        
        # Initialize stat categories
        stat_categories = ['passing', 'rushing', 'receiving', 'defense']
        for category in stat_categories:
            totals[category] = {}
        
        # Sum up all games
        for game in games:
            totals['fantasy_points'] += game.get('fantasy_points', 0)
            
            for category in stat_categories:
                game_stats = game.get(category, {})
                for stat, value in game_stats.items():
                    if isinstance(value, (int, float)):
                        totals[category][stat] = totals[category].get(stat, 0) + value
        
        return totals
    
    def _calculate_season_averages(self, games: List[Dict[str, Any]], totals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate season averages from totals.
        
        Args:
            games: List of processed game data
            totals: Season totals
            
        Returns:
            Dict containing season averages
        """
        games_played = totals.get('games_played', 1)
        if games_played == 0:
            games_played = 1
        
        averages = {
            'fantasy_points': 0.0,
            'passing': {},
            'rushing': {},
            'receiving': {},
            'defense': {}
        }
        
        # Calculate averages for each category
        for category in ['passing', 'rushing', 'receiving', 'defense']:
            for stat in totals[category]:
                averages[category][stat] = round(totals[category][stat] / games_played, 2)
        
        averages['fantasy_points'] = round(totals['fantasy_points'] / games_played, 2)
        
        return averages
    
    def _generate_markdown_report(self, matched_players: List[Dict[str, Any]], season_context: Dict[str, Any]) -> str:
        """
        Generate a comprehensive markdown report of available players game stats.
        
        Args:
            matched_players: List of matched players with game stats
            season_context: Season and week context information
            
        Returns:
            Markdown report string
        """
        report = []
        report.append("# Tank01 NFL - Available Players Game Stats")
        report.append("")
        
        # Header with execution stats
        end_time = datetime.now()
        execution_time = (end_time - self.stats["start_time"]).total_seconds()
        
        report.append(f"**Extraction Date:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Yahoo Players Loaded:** {self.stats['yahoo_players_loaded']}")
        report.append(f"**Matched Players:** {self.stats['players_matched']}")
        report.append(f"**Unmatched Players:** {self.stats['players_unmatched']}")
        report.append(f"**Total Games Collected:** {self.stats['total_games_collected']}")
        report.append(f"**Match Rate:** {(self.stats['players_matched'] / max(1, self.stats['yahoo_players_loaded'])) * 100:.1f}%")
        report.append(f"**Execution Time:** {execution_time:.2f}s")
        
        # Get actual API usage from Tank01 client
        usage_info = self.tank01.get_api_usage()
        actual_calls = usage_info.get('calls_made_this_session', 0)
        
        report.append(f"**API Calls:** {actual_calls}")
        report.append(f"**Errors:** {self.stats['errors']}")
        report.append("")
        
        # Tank01 API Usage Info (from centralized manager)
        report.append("## Tank01 API Usage")
        usage_info = self.usage_manager.get_usage_info()
        report.append(f"- **Current Time (Pacific):** {usage_info.get('current_time_formatted', 'Unknown')}")
        report.append(f"- **Calls Made This Session:** {actual_calls}")
        report.append(f"- **Daily Limit:** {usage_info.get('daily_limit', 'Unknown')}")
        report.append(f"- **Remaining Calls Today:** {usage_info.get('remaining_calls', 'Unknown')}")
        report.append(f"- **Usage Percentage:** {usage_info.get('percentage_used', 0):.1f}%")
        report.append(f"- **Data Source:** {usage_info.get('data_source', 'Unknown')}")
        if usage_info.get('reset_time_pacific'):
            report.append(f"- **Limit Resets:** {usage_info.get('reset_time_pacific')}")
        report.append(f"- **Client Available:** {usage_info.get('available', False)}")
        report.append("")
        
        # Add season and week context
        report.append("## Season & Week Context")
        report.append(f"- **NFL Season:** {season_context.get('nfl_season', 'Unknown')}")
        report.append(f"- **Current Week:** {season_context.get('current_week', 'Unknown')}")
        report.append(f"- **Season Phase:** {season_context.get('season_phase', 'Unknown')}")
        report.append(f"- **Data Source:** {season_context.get('data_source', 'Unknown')}")
        
        week_info = season_context.get('week_info', {})
        if week_info:
            report.append(f"- **Week Start:** {week_info.get('week_start', 'Unknown')}")
            report.append(f"- **Week End:** {week_info.get('week_end', 'Unknown')}")
            report.append(f"- **Week Status:** {week_info.get('status', 'Unknown')}")
            report.append(f"- **Week Source:** {week_info.get('source', 'Unknown')}")
        
        verification_notes = season_context.get('verification_notes', [])
        if verification_notes:
            report.append("")
            report.append("### Verification Notes")
            for note in verification_notes:
                report.append(f"- {note}")
        
        report.append("")
        
        if not matched_players:
            report.append("## No Players Matched")
            report.append("No Yahoo available players were successfully matched to Tank01 database.")
            return "\n".join(report)
        
        # Summary table
        report.append("## Available Players Game Stats Summary")
        report.append("")
        report.append("| Player | Pos | Team | Games | Avg FP | Total FP | Recent Form |")
        report.append("|--------|-----|------|-------|--------|----------|-------------|")
        
        for player_data in matched_players:
            yahoo_player = player_data['yahoo_player']
            tank01_player = player_data['tank01_data']
            game_stats = player_data['game_stats']
            
            name = yahoo_player.get('name', {}).get('full', 'Unknown')
            pos = yahoo_player.get('display_position', 'N/A')
            team = yahoo_player.get('editorial_team_abbr', 'N/A')
            
            games_played = game_stats.get('total_games', 0)
            season_totals = game_stats.get('season_totals', {})
            season_averages = game_stats.get('season_averages', {})
            
            avg_fp = season_averages.get('fantasy_points', 0)
            total_fp = season_totals.get('fantasy_points', 0)
            
            # Calculate recent form (last 3 games)
            recent_performance = game_stats.get('recent_performance', [])
            recent_fp = sum(game.get('fantasy_points', 0) for game in recent_performance)
            recent_avg = recent_fp / len(recent_performance) if recent_performance else 0
            
            recent_form = f"{recent_avg:.1f} FP" if recent_performance else "No games"
            
            report.append(f"| {name} | {pos} | {team} | {games_played} | {avg_fp:.1f} | {total_fp:.1f} | {recent_form} |")
        
        report.append("")
        
        # Detailed player sections
        report.append("## Detailed Player Game Statistics")
        report.append("")
        
        for player_data in matched_players:
            yahoo_player = player_data['yahoo_player']
            tank01_player = player_data['tank01_data']
            game_stats = player_data['game_stats']
            
            name = yahoo_player.get('name', {}).get('full', 'Unknown')
            pos = yahoo_player.get('display_position', 'N/A')
            team = yahoo_player.get('editorial_team_abbr', 'N/A')
            
            report.append(f"### {name} ({pos} - {team})")
            report.append("")
            
            # Basic info
            report.append("#### Player Information")
            report.append(f"- **Tank01 ID**: {tank01_player.get('playerID', 'N/A')}")
            report.append(f"- **Yahoo ID**: {yahoo_player.get('player_id', 'N/A')}")
            report.append(f"- **Long Name**: {tank01_player.get('longName', 'N/A')}")
            report.append(f"- **Team**: {tank01_player.get('team', 'N/A')}")
            report.append("")
            
            # Season totals
            season_totals = game_stats.get('season_totals', {})
            if season_totals:
                report.append("#### Season Totals")
                report.append(f"- **Games Played**: {season_totals.get('games_played', 0)}")
                report.append(f"- **Total Fantasy Points**: {season_totals.get('fantasy_points', 0):.1f}")
                
                # Passing stats
                passing = season_totals.get('passing', {})
                if any(passing.values()):
                    report.append("- **Passing Totals:**")
                    for stat, value in passing.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                # Rushing stats
                rushing = season_totals.get('rushing', {})
                if any(rushing.values()):
                    report.append("- **Rushing Totals:**")
                    for stat, value in rushing.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                # Receiving stats
                receiving = season_totals.get('receiving', {})
                if any(receiving.values()):
                    report.append("- **Receiving Totals:**")
                    for stat, value in receiving.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                # Defense stats
                defense = season_totals.get('defense', {})
                if any(defense.values()):
                    report.append("- **Defense Totals:**")
                    for stat, value in defense.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                report.append("")
            
            # Season averages
            season_averages = game_stats.get('season_averages', {})
            if season_averages:
                report.append("#### Season Averages (Per Game)")
                report.append(f"- **Average Fantasy Points**: {season_averages.get('fantasy_points', 0):.1f}")
                
                # Passing averages
                passing_avg = season_averages.get('passing', {})
                if any(passing_avg.values()):
                    report.append("- **Passing Averages:**")
                    for stat, value in passing_avg.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value:.1f}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                # Rushing averages
                rushing_avg = season_averages.get('rushing', {})
                if any(rushing_avg.values()):
                    report.append("- **Rushing Averages:**")
                    for stat, value in rushing_avg.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value:.1f}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                # Receiving averages
                receiving_avg = season_averages.get('receiving', {})
                if any(receiving_avg.values()):
                    report.append("- **Receiving Averages:**")
                    for stat, value in receiving_avg.items():
                        try:
                            if float(value) > 0:
                                report.append(f"  - {stat}: {value:.1f}")
                        except (ValueError, TypeError):
                            if str(value) != '0' and str(value) != '0.0':
                                report.append(f"  - {stat}: {value}")
                
                report.append("")
            
            # Team defense stats (for defense players)
            team_defense_stats = game_stats.get('team_defense_stats', {})
            if team_defense_stats:
                report.append("#### Team Defense Statistics")
                report.append(f"- **Record**: {team_defense_stats.get('wins', 0)}-{team_defense_stats.get('losses', 0)}-{team_defense_stats.get('ties', 0)}")
                report.append(f"- **Points For**: {team_defense_stats.get('pointsFor', 0)}")
                report.append(f"- **Points Allowed**: {team_defense_stats.get('pointsAllowed', 0)}")
                report.append(f"- **Total Yards Allowed**: {team_defense_stats.get('yardsAllowed', 0)}")
                report.append(f"- **Pass Yards Allowed**: {team_defense_stats.get('passYardsAllowed', 0)}")
                report.append(f"- **Rush Yards Allowed**: {team_defense_stats.get('rushYardsAllowed', 0)}")
                report.append(f"- **Pass TDs Allowed**: {team_defense_stats.get('passTDAllowed', 0)}")
                report.append(f"- **Rush TDs Allowed**: {team_defense_stats.get('rushTDAllowed', 0)}")
                report.append(f"- **Interceptions**: {team_defense_stats.get('interceptions', 0)}")
                report.append(f"- **Fumbles Recovered**: {team_defense_stats.get('fumblesRecovered', 0)}")
                report.append(f"- **Sacks**: {team_defense_stats.get('sacks', 0)}")
                report.append(f"- **Safeties**: {team_defense_stats.get('safeties', 0)}")
                report.append(f"- **Defensive TDs**: {team_defense_stats.get('defTD', 0)}")
                report.append(f"- **Turnovers**: {team_defense_stats.get('turnovers', 0)}")
                report.append(f"- **Total Tackles**: {team_defense_stats.get('totalTackles', 0)}")
                report.append(f"- **Solo Tackles**: {team_defense_stats.get('soloTackles', 0)}")
                report.append(f"- **Tackles for Loss**: {team_defense_stats.get('tacklesForLoss', 0)}")
                report.append(f"- **QB Hits**: {team_defense_stats.get('qbHits', 0)}")
                report.append(f"- **Pass Deflections**: {team_defense_stats.get('passDeflections', 0)}")
                report.append(f"- **2PT Conversion Returns**: {team_defense_stats.get('twoPointConversionReturn', 0)}")
                report.append("")
            
            # Recent games
            recent_performance = game_stats.get('recent_performance', [])
            if recent_performance:
                report.append("#### Recent Games (Last 3)")
                for i, game in enumerate(recent_performance, 1):
                    game_date = game.get('game_date', 'Unknown')
                    week = game.get('week', 'Unknown')
                    opponent = game.get('opponent', 'Unknown')
                    fantasy_points = game.get('fantasy_points', 0)
                    
                    report.append(f"- **Game {i}** (Week {week} vs {opponent}): {fantasy_points:.1f} FP")
                    
                    # Show key stats for this game
                    passing = game.get('passing', {})
                    rushing = game.get('rushing', {})
                    receiving = game.get('receiving', {})
                    
                    game_stats_summary = []
                    try:
                        if float(passing.get('passYds', 0)) > 0:
                            game_stats_summary.append(f"{passing.get('passYds', 0)} pass yds")
                    except (ValueError, TypeError):
                        pass
                    try:
                        if float(rushing.get('rushYds', 0)) > 0:
                            game_stats_summary.append(f"{rushing.get('rushYds', 0)} rush yds")
                    except (ValueError, TypeError):
                        pass
                    try:
                        if float(receiving.get('recYds', 0)) > 0:
                            game_stats_summary.append(f"{receiving.get('recYds', 0)} rec yds")
                    except (ValueError, TypeError):
                        pass
                    
                    if game_stats_summary:
                        report.append(f"  - Key Stats: {', '.join(game_stats_summary)}")
                
                report.append("")
            
            # All games (if not too many)
            all_games = game_stats.get('games', [])
            if all_games and len(all_games) <= 10:  # Only show if 10 or fewer games
                report.append("#### All Games This Season")
                report.append("| Week | Date | Opponent | Fantasy Points | Key Stats |")
                report.append("|------|------|----------|----------------|-----------|")
                
                for game in all_games:
                    week = game.get('week', 'Unknown')
                    game_date = game.get('game_date', 'Unknown')
                    opponent = game.get('opponent', 'Unknown')
                    fantasy_points = game.get('fantasy_points', 0)
                    
                    # Build key stats summary
                    passing = game.get('passing', {})
                    rushing = game.get('rushing', {})
                    receiving = game.get('receiving', {})
                    
                    key_stats = []
                    try:
                        if float(passing.get('passYds', 0)) > 0:
                            key_stats.append(f"{passing.get('passYds', 0)} pass yds")
                    except (ValueError, TypeError):
                        pass
                    try:
                        if float(rushing.get('rushYds', 0)) > 0:
                            key_stats.append(f"{rushing.get('rushYds', 0)} rush yds")
                    except (ValueError, TypeError):
                        pass
                    try:
                        if float(receiving.get('recYds', 0)) > 0:
                            key_stats.append(f"{receiving.get('recYds', 0)} rec yds")
                    except (ValueError, TypeError):
                        pass
                    
                    key_stats_str = ', '.join(key_stats) if key_stats else 'No stats'
                    
                    report.append(f"| {week} | {game_date} | {opponent} | {fantasy_points:.1f} | {key_stats_str} |")
                
                report.append("")
        
        return "\n".join(report)
    
    def extract_available_players_stats(self) -> Dict[str, Any]:
        """
        Extract comprehensive game statistics for available Yahoo Fantasy players.
        
        Returns:
            Dict containing extraction results and data
        """
        self.logger.info("Starting Tank01 available players stats extraction")
        
        # Load Yahoo available players
        yahoo_players, yahoo_data = self._load_latest_yahoo_available_players()
        if not yahoo_players:
            self.logger.error("No Yahoo available players loaded")
            return {"error": "No Yahoo available players loaded"}
        
        # Filter players by position limits
        filtered_players = self._filter_players_by_position_limits(yahoo_players)
        self.logger.info(f"Filtered to {len(filtered_players)} players based on position limits")
        
        # Load Tank01 player database once at the start
        self.logger.info("Loading Tank01 player database...")
        self._tank01_player_cache = self._get_tank01_player_database()
        if not self._tank01_player_cache:
            self.logger.error("Failed to load Tank01 player database")
            return {"error": "Failed to load Tank01 player database"}
        
        # Process each player
        matched_players = []
        unmatched_players = []
        
        for yahoo_player in filtered_players:
            self.stats["players_processed"] += 1
            
            # Match to Tank01
            tank01_player = self._match_yahoo_to_tank01(yahoo_player)
            
            if tank01_player:
                # For defense players, get team-level stats first
                team_defense_stats = None
                if tank01_player.get('isTeamDefense', False):
                    team_abbr = tank01_player.get('team', '')
                    if team_abbr:
                        team_defense_stats = self._get_team_defense_stats(team_abbr)
                
                # Get comprehensive game stats
                game_stats = self._get_player_game_stats(tank01_player, season="2025", team_defense_stats=team_defense_stats)
                
                # Add team defense stats to game stats for display
                if team_defense_stats:
                    game_stats['team_defense_stats'] = team_defense_stats
                
                # Update total games collected
                self.stats["total_games_collected"] += game_stats.get('total_games', 0)
                
                matched_players.append({
                    'yahoo_player': yahoo_player,
                    'tank01_data': tank01_player,
                    'game_stats': game_stats
                })
                self.stats["players_matched"] += 1
            else:
                unmatched_players.append(yahoo_player)
                self.stats["players_unmatched"] += 1
        
        # Prepare raw data with comprehensive API usage tracking
        final_usage = self.tank01.get_api_usage()
        season_context = self._extract_season_context(yahoo_data)
        
        # Generate outputs
        markdown_report = self._generate_markdown_report(matched_players, season_context)
        raw_data = {
            "extraction_metadata": {
                "source": "Tank01 API - Available Players Game Stats",
                "extraction_timestamp": datetime.now().isoformat(),
                "yahoo_source": "Latest available_players.py output",
                "execution_stats": self.stats
            },
            "season_context": season_context,
            "matched_players": matched_players,
            "unmatched_players": unmatched_players,
            "tank01_api_usage": {
                "session_usage": final_usage,
                "api_calls_breakdown": {
                    "player_database_call": 1,
                    "player_specific_calls": max(0, final_usage.get('calls_made_this_session', 0) - 1),
                    "game_stats_calls": self.stats['players_matched'],
                    "get_player_info_calls": max(0, final_usage.get('calls_made_this_session', 0) - 1 - self.stats['players_matched']),
                    "total_calls": final_usage.get('calls_made_this_session', 0)
                },
                "efficiency_metrics": {
                    "calls_per_player": final_usage.get('calls_made_this_session', 0) / max(1, self.stats['players_matched']),
                    "match_rate_percentage": (self.stats['players_matched'] / max(1, self.stats['yahoo_players_loaded'])) * 100,
                    "total_games_collected": self.stats['total_games_collected'],
                    "remaining_calls_today": final_usage.get('remaining_calls', 0),
                    "usage_percentage": final_usage.get('percentage_used', 0),
                    "data_source": final_usage.get('data_source', 'Unknown'),
                    "reset_timestamp": final_usage.get('reset_timestamp'),
                    "reset_timestamp_pacific": format_timestamp_pacific(final_usage.get('reset_timestamp')),
                    "last_updated": final_usage.get('last_updated'),
                    "report_generated_pacific": get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')
                }
            }
        }
        
        # Save outputs with week-specific naming
        current_week = season_context.get('current_week', 1)
        timestamp = self.file_manager.generate_timestamp()
        week_prefix = f"{timestamp}_wk{current_week:02d}_"
        
        clean_file = self.file_manager.save_clean_data("tank01", "available_players_stats", markdown_report, week_prefix)
        raw_file = self.file_manager.save_raw_data("tank01", "available_players_stats", raw_data, week_prefix)
        
        output_files = {
            "clean": clean_file,
            "raw": raw_file
        }
        
        self.logger.info(f"Tank01 available players stats extraction complete")
        self.logger.info(f"Matched: {self.stats['players_matched']}/{self.stats['yahoo_players_loaded']} players")
        self.logger.info(f"Total games collected: {self.stats['total_games_collected']}")
        self.logger.info(f"API calls: {self.stats['api_calls']}")
        self.logger.info(f"Output files: {output_files}")
        
        return {
            "success": True,
            "matched_players": len(matched_players),
            "unmatched_players": len(unmatched_players),
            "total_games_collected": self.stats['total_games_collected'],
            "api_calls": self.stats["api_calls"],
            "output_files": output_files
        }

def main():
    """Main execution function."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        extractor = Tank01AvailablePlayersStatsExtractor()
        result = extractor.extract_available_players_stats()
        
        if result.get("success"):
            print(f"✅ Tank01 available players stats extraction successful!")
            print(f"   Matched: {result['matched_players']} players")
            print(f"   Total games collected: {result['total_games_collected']}")
            print(f"   API calls: {result['api_calls']}")
            print(f"   Output files: {result['output_files']}")
        else:
            print(f"❌ Tank01 available players stats extraction failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Tank01 available players stats extraction failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
