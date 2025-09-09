#!/usr/bin/env python3
"""
Tank01 NFL API - My Roster Player Game Stats Collection

This script loads the latest Yahoo my roster data, maps players to the Tank01 NFL database,
and extracts comprehensive game statistics for each player from the current season.

Purpose: Collect historical game stats for my roster players using getNFLGamesForPlayer endpoint
Output: Comprehensive markdown file + raw JSON of all player game stats
Focus: Extract season-long game statistics for analysis and historical tracking
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the shared utilities to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "shared"))

from tank01_client import SimpleTank01Client
from file_utils import DataFileManager
from api_usage_manager import APIUsageManager
from data_formatter import MarkdownFormatter

def get_current_time_pacific():
    """Get current time in Pacific Time Zone."""
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific)

def format_timestamp_pacific(timestamp):
    """Convert RapidAPI reset timestamp to Pacific Time Zone."""
    if not timestamp:
        return "Unknown"
    
    try:
        # RapidAPI reset timestamp contains seconds remaining until reset, not Unix timestamp
        # Calculate when the reset will occur by adding to current time
        current_time = get_current_time_pacific()
        reset_time = current_time + timedelta(seconds=timestamp)
        return reset_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    except (ValueError, TypeError) as e:
        return f"Invalid timestamp: {timestamp}"

# Import shared team mapping
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
from data_collection.scripts.shared.team_mapping import normalize_team_abbreviation

class Tank01MyRosterStatsExtractor:
    """
    Extract comprehensive game statistics for my Yahoo Fantasy roster players.
    
    This script:
    1. Loads latest Yahoo my roster data
    2. Maps Yahoo players to Tank01 database
    3. Extracts season-long game statistics for each player
    4. Outputs organized markdown and raw JSON
    """
    
    def __init__(self):
        """Initialize the Tank01 my roster stats extractor."""
        self.logger = logging.getLogger(__name__)
        self.file_manager = DataFileManager()
        self.formatter = MarkdownFormatter()
        
        # Initialize Tank01 client
        self.tank01 = SimpleTank01Client()
        if not self.tank01.is_available():
            raise ValueError("Tank01 client not available. Check RAPIDAPI_KEY environment variable.")
        
        # Initialize centralized API usage manager
        self.usage_manager = APIUsageManager(self.tank01, "Tank01")
        
        # Cache for Tank01 player database
        self._tank01_player_cache = None
        
        # Track execution stats
        self.stats = {
            "start_time": datetime.now(),
            "api_calls": 0,
            "errors": 0,
            "yahoo_players_loaded": 0,
            "players_processed": 0,
            "players_matched": 0,
            "players_unmatched": 0,
            "total_games_collected": 0
        }
        
        self.logger.info("Tank01 My Roster Stats Extractor initialized")
    
    def _extract_season_context(self, yahoo_data: Dict) -> Dict[str, Any]:
        """
        Extract season and week context from Yahoo data.
        
        Args:
            yahoo_data: Yahoo roster data
            
        Returns:
            Dict with season context information
        """
        try:
            self.logger.info("Starting season context extraction")
            current_date = get_current_time_pacific()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'data_source': 'Tank01 API - Player Game Stats',
                'verification_notes': []
            }
            
            # Extract season from Yahoo data if available
            if yahoo_data and 'team_info' in yahoo_data:
                team_info = yahoo_data['team_info']
                league_name = team_info.get('league_name', '')
                team_key = team_info.get('team_key', '')
                
                # Look for year in league name
                import re
                year_match = re.search(r'(\d{4})', league_name)
                if year_match:
                    extracted_year = year_match.group(1)
                    season_context['nfl_season'] = extracted_year
                    season_context['verification_notes'].append(f"Yahoo league name contains year: {extracted_year}")
                
                # Extract year from team key (format: 461.l.595012.t.3)
                if team_key and '.' in team_key:
                    key_parts = team_key.split('.')
                    if len(key_parts) >= 2 and key_parts[0].isdigit():
                        yahoo_code = int(key_parts[0])
                        # Yahoo uses 461 for 2025, 460 for 2024, etc.
                        yahoo_year = str(2025)  # For now, assume 2025 based on 461
                        season_context['nfl_season'] = yahoo_year
                        season_context['verification_notes'].append(f"Yahoo team key code {yahoo_code} indicates year: {yahoo_year}")
                
                season_context['yahoo_league_info'] = {
                    'league_key': team_info.get('league_key', ''),
                    'league_name': team_info.get('league_name', ''),
                    'team_key': team_info.get('team_key', '')
                }
            
            # Extract current week from Tank01 API data and Yahoo data
            season_context['current_week'] = None
            season_context['week_info'] = {}
            
            # First, try to get week from Yahoo data (most reliable)
            current_week = self._extract_current_week_from_yahoo_data(yahoo_data)
            
            if current_week:
                season_context['current_week'] = current_week['week']
                season_context['week_info'] = current_week
                season_context['verification_notes'].append(f"Current week {current_week['week']} extracted from Yahoo team matchups API")
            else:
                # Fallback: try to determine from date
                try:
                    season_start = datetime(current_date.year, 9, 1, tzinfo=current_date.tzinfo)
                    if current_date >= season_start:
                        days_since_start = (current_date - season_start).days
                        estimated_week = min((days_since_start // 7) + 1, 18)
                        season_context['current_week'] = estimated_week
                        season_context['week_info'] = {
                            'week': estimated_week,
                            'coverage_type': 'estimated',
                            'status': 'estimated_from_date',
                            'source': 'date_estimation'
                        }
                        season_context['verification_notes'].append(f"Estimated week {estimated_week} from current date")
                    else:
                        season_context['current_week'] = 1
                        season_context['week_info'] = {
                            'week': 1,
                            'coverage_type': 'preseason',
                            'status': 'preseason',
                            'source': 'preseason_assumption'
                        }
                        season_context['verification_notes'].append("Preseason - using week 1")
                except Exception as e:
                    self.logger.warning(f"Could not determine week from date: {e}")
                    season_context['current_week'] = 1
                    season_context['week_info'] = {
                        'week': 1,
                        'coverage_type': 'fallback',
                        'status': 'fallback',
                        'source': 'error_fallback'
                    }
                    season_context['verification_notes'].append("Could not determine current week - using fallback week 1")
            
            # Add current date context
            if current_date.month >= 9:
                season_context['verification_notes'].append(f"Current date {current_date.strftime('%Y-%m-%d')} suggests NFL season is in progress")
            elif current_date.month <= 2:
                season_context['verification_notes'].append(f"Current date {current_date.strftime('%Y-%m-%d')} suggests NFL playoffs/super bowl period")
            else:
                season_context['verification_notes'].append(f"Current date {current_date.strftime('%Y-%m-%d')} suggests NFL offseason")
            
            return season_context
            
        except Exception as e:
            self.logger.error(f"Error extracting season context: {e}")
            return {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': 'Unknown',
                'data_source': 'Tank01 API - Player Game Stats',
                'verification_notes': [f"Error extracting season context: {e}"]
            }
    
    def _determine_season_phase(self, current_date: datetime) -> str:
        """Determine the current phase of the NFL season based on date"""
        try:
            month = current_date.month
            day = current_date.day
            self.logger.info(f"Determining season phase: month={month} (type: {type(month)}), day={day} (type: {type(day)})")
        except Exception as e:
            self.logger.error(f"Error in _determine_season_phase: {e}")
            return "Unknown"
        
        if month == 9 and day < 15:
            return "Early Regular Season"
        elif month == 9 or month == 10:
            return "Regular Season"
        elif month == 11 or month == 12:
            return "Late Regular Season"
        elif month == 1 and day < 15:
            return "Playoffs"
        elif month == 1 and day >= 15:
            return "Super Bowl"
        elif month == 2:
            return "Offseason"
        elif month >= 3 and month <= 8:
            return "Offseason"
        else:
            return "Unknown"
    
    def _extract_current_week_from_yahoo_data(self, yahoo_data: Dict) -> Optional[Dict[str, Any]]:
        """
        Extract current week information from Yahoo team matchups data.
        
        Args:
            yahoo_data: Yahoo roster data containing team info
            
        Returns:
            Dict with week information or None if not found
        """
        try:
            if not yahoo_data or 'team_info' not in yahoo_data:
                return None
                
            league_key = yahoo_data['team_info'].get('league_key', '')
            if not league_key:
                return None
                
            # Look for the most recent team matchups file
            from pathlib import Path
            current_path = Path(__file__).resolve()
            for parent in current_path.parents:
                if parent.name == "data_collection":
                    matchups_dir = parent / "outputs" / "yahoo" / "team_matchups"
                    break
            else:
                matchups_dir = Path("data_collection/outputs/yahoo/team_matchups")
            
            if not matchups_dir.exists():
                self.logger.warning("Team matchups directory not found")
                return None
            
            # Get the most recent matchups file
            matchup_files = list(matchups_dir.glob("**/*_team_matchups_raw_data.json"))
            if not matchup_files:
                self.logger.warning("No team matchups files found")
                return None
            
            latest_file = max(matchup_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading team matchups from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                matchups_data = json.load(f)
            
            # Extract week information from matchups
            matchups = matchups_data.get('matchups', {})
            if not matchups:
                return None
            
            # Find the current week (look for week_1, week_2, etc.)
            current_week_data = None
            for week_key, week_data in matchups.items():
                if week_key.startswith('week_'):
                    week_num = week_data.get('week', 1)
                    week_matchups = week_data.get('matchups', [])
                    
                    # Look for status in the matchups array
                    week_start = ''
                    week_end = ''
                    status = 'unknown'
                    
                    if week_matchups:
                        # Get status from first matchup
                        first_matchup = week_matchups[0]
                        week_start = first_matchup.get('week_start', '')
                        week_end = first_matchup.get('week_end', '')
                        status = first_matchup.get('status', 'unknown')
                    
                    # Check if this is the current week based on status
                    self.logger.info(f"Checking status: {status} (type: {type(status)})")
                    if status in ['midevent', 'postevent', 'preevent']:
                        current_week_data = {
                            'week': week_num,
                            'week_start': week_start,
                            'week_end': week_end,
                            'status': status,
                            'coverage_type': 'week',
                            'source': 'yahoo_team_matchups_api'
                        }
                        break
            
            # If no current week found, use the first available week
            if not current_week_data and matchups:
                first_week_key = sorted(matchups.keys())[0]
                first_week_data = matchups[first_week_key]
                week_num = first_week_data.get('week', 1)
                week_matchups = first_week_data.get('matchups', [])
                
                week_start = ''
                week_end = ''
                status = 'unknown'
                
                if week_matchups:
                    first_matchup = week_matchups[0]
                    week_start = first_matchup.get('week_start', '')
                    week_end = first_matchup.get('week_end', '')
                    status = first_matchup.get('status', 'unknown')
                
                current_week_data = {
                    'week': week_num,
                    'week_start': week_start,
                    'week_end': week_end,
                    'status': status,
                    'coverage_type': 'week',
                    'source': 'yahoo_team_matchups_api'
                }
            
            return current_week_data
            
        except Exception as e:
            self.logger.warning(f"Could not extract current week from Yahoo data: {e}")
            return None
    
    def _load_latest_yahoo_roster_players(self) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Load the latest Yahoo my roster players from the most recent output file.
        
        Returns:
            Tuple of (List of Yahoo roster players with their data, Raw Yahoo data)
        """
        try:
            # Find the most recent Yahoo my roster output
            # Get the project root by finding the data_collection directory
            current_path = Path(__file__).resolve()
            for parent in current_path.parents:
                if parent.name == "data_collection":
                    yahoo_output_dir = parent / "outputs" / "yahoo" / "my_roster"
                    break
            else:
                # Fallback: assume we're in the project root
                yahoo_output_dir = Path("data_collection/outputs/yahoo/my_roster")
            
            if not yahoo_output_dir.exists():
                raise FileNotFoundError(f"Yahoo my roster output directory not found: {yahoo_output_dir}")
            
            # Get the most recent file
            roster_files = list(yahoo_output_dir.glob("**/*_my_roster_raw_data.json"))
            if not roster_files:
                raise FileNotFoundError("No Yahoo my roster raw data files found")
            
            latest_file = max(roster_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading Yahoo roster from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                raw_data = json.load(f)
            
            # Extract players from the Yahoo raw data
            players = []
            
            # Handle the actual Yahoo data structure - simplified approach
            try:
                self.logger.debug(f"Raw data keys: {list(raw_data.keys())}")
                roster_raw = raw_data.get('roster_raw', {})
                self.logger.debug(f"Roster raw keys: {list(roster_raw.keys())}")
                fantasy_content = roster_raw.get('fantasy_content', {})
                self.logger.debug(f"Fantasy content keys: {list(fantasy_content.keys())}")
                team_data = fantasy_content.get('team', [])
                self.logger.debug(f"Team data type: {type(team_data)}, length: {len(team_data) if isinstance(team_data, list) else 'N/A'}")
                
                if isinstance(team_data, list) and len(team_data) > 0:
                    # Check both team data items
                    for team_idx, team_info in enumerate(team_data):
                        self.logger.debug(f"Team {team_idx} type: {type(team_info)}, length: {len(team_info) if isinstance(team_info, list) else 'N/A'}")
                        if isinstance(team_info, list):
                            # Find the roster section
                            for i, item in enumerate(team_info):
                                if isinstance(item, dict) and 'roster' in item:
                                    self.logger.debug(f"Found roster at team {team_idx}, item {i}")
                                    roster_data = item['roster']
                                    if isinstance(roster_data, dict):
                                        self.logger.debug(f"Roster data keys: {list(roster_data.keys())}")
                                        # Look for players in roster
                                        for key, value in roster_data.items():
                                            if key.isdigit() and isinstance(value, dict) and 'players' in value:
                                                self.logger.debug(f"Found players section at key {key}")
                                                players_data = value['players']
                                                if isinstance(players_data, dict):
                                                    self.logger.debug(f"Players data keys: {list(players_data.keys())}")
                                                    # Extract players
                                                    for player_key, player_value in players_data.items():
                                                        if player_key.isdigit() and isinstance(player_value, dict) and 'player' in player_value:
                                                            self.logger.debug(f"Found player at key {player_key}")
                                                            player_list = player_value['player']
                                                            if isinstance(player_list, list):
                                                                for player_item in player_list:
                                                                    if isinstance(player_item, list):
                                                                        # Flatten the player data
                                                                        player_data = {}
                                                                        for field in player_item:
                                                                            if isinstance(field, dict):
                                                                                player_data.update(field)
                                                                        if player_data:
                                                                            players.append(player_data)
                                                                            self.logger.debug(f"Added player: {player_data.get('name', {}).get('full', 'Unknown')}")
            except Exception as e:
                self.logger.error(f"Error parsing Yahoo roster data: {e}")
                # Try alternative parsing approach
                players = self._parse_yahoo_roster_alternative(raw_data)
            
            # If no players found, try the roster_players key
            if not players and 'roster_players' in raw_data:
                self.logger.debug("Trying roster_players key")
                roster_players = raw_data['roster_players']
                if isinstance(roster_players, list):
                    players = roster_players
                    self.logger.debug(f"Found {len(players)} players in roster_players")
            
            self.stats["yahoo_players_loaded"] = len(players)
            self.logger.info(f"Loaded {len(players)} Yahoo roster players")
            return players, raw_data
            
        except Exception as e:
            self.logger.error(f"Failed to load Yahoo roster players: {e}")
            self.stats["errors"] += 1
            return [], {}
    
    def _parse_yahoo_roster_alternative(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Alternative method to parse Yahoo roster data if the main method fails.
        
        Args:
            raw_data: Raw Yahoo data
            
        Returns:
            List of player data
        """
        players = []
        try:
            # Try to find players in any structure
            def find_players_recursive(data, depth=0):
                if depth > 10:  # Prevent infinite recursion
                    return
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == 'player' and isinstance(value, list):
                            for player_item in value:
                                if isinstance(player_item, list):
                                    player_data = {}
                                    for field in player_item:
                                        if isinstance(field, dict):
                                            player_data.update(field)
                                    if player_data and 'player_id' in player_data:
                                        players.append(player_data)
                        else:
                            find_players_recursive(value, depth + 1)
                elif isinstance(data, list):
                    for item in data:
                        find_players_recursive(item, depth + 1)
            
            find_players_recursive(raw_data)
            
        except Exception as e:
            self.logger.error(f"Alternative parsing also failed: {e}")
        
        return players
    
    def _get_tank01_player_database(self) -> List[Dict[str, Any]]:
        """
        Get the Tank01 player database with caching.
        
        Returns:
            List of all Tank01 players
        """
        if self._tank01_player_cache is not None:
            return self._tank01_player_cache
        
        try:
            self.logger.info("Loading Tank01 player database...")
            response = self.tank01.get_player_list()
            
            if not response or 'body' not in response:
                self.logger.error("Failed to get Tank01 player database")
                return []
            
            players = response['body']
            if not isinstance(players, list):
                self.logger.error("Tank01 player database format unexpected")
                return []
            
            self._tank01_player_cache = players
            self.stats["api_calls"] += 1
            self.logger.info(f"Loaded {len(players)} Tank01 players")
            return players
            
        except Exception as e:
            self.logger.error(f"Failed to load Tank01 player database: {e}")
            self.stats["errors"] += 1
            return []
    
    def _match_yahoo_to_tank01(self, yahoo_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Match a Yahoo player to Tank01 database using multiple strategies.
        
        Args:
            yahoo_player: Yahoo player data
            
        Returns:
            Matching Tank01 player data or None
        """
        # Use cached player database (should already be loaded)
        tank01_players = self._tank01_player_cache
        if not tank01_players:
            self.logger.error("Tank01 player database not loaded")
            return None
        
        # Extract Yahoo player info
        yahoo_name = yahoo_player.get('name', {}).get('full', '')
        yahoo_team = yahoo_player.get('editorial_team_abbr', '')
        yahoo_position = yahoo_player.get('display_position', '')
        
        if not yahoo_name:
            return None
        
        yahoo_name_clean = yahoo_name.lower().strip()
        
        # Strategy 1: Direct Yahoo ID match (if available in Tank01)
        yahoo_id = yahoo_player.get('player_id', '')
        for player in tank01_players:
            tank01_yahoo_id = player.get('yahooID', '')
            if yahoo_id and tank01_yahoo_id and yahoo_id == tank01_yahoo_id:
                self.logger.debug(f"Matched {yahoo_name} by Yahoo ID: {yahoo_id}")
                return player
        
        # Strategy 2: Exact name match with team validation
        for player in tank01_players:
            tank01_name = player.get('longName', '').lower().strip()
            tank01_team = player.get('team', '')
            tank01_pos = player.get('pos', '')
            
            if yahoo_name_clean == tank01_name:
                # Team validation (if both have team info) - case insensitive
                if yahoo_team and tank01_team and yahoo_team.upper() != tank01_team.upper():
                    continue
                # Position validation (if both have position info)
                if yahoo_position and tank01_pos and yahoo_position != tank01_pos:
                    continue
                
                self.logger.debug(f"Matched {yahoo_name} by exact name + team/position")
                return player
        
        # Strategy 3: Last name + team match
        if yahoo_team:
            yahoo_last = yahoo_name_clean.split()[-1] if yahoo_name_clean else ""
            for player in tank01_players:
                tank01_name = player.get('longName', '').lower().strip()
                tank01_team = player.get('team', '')
                tank01_pos = player.get('pos', '')
                tank01_last = tank01_name.split()[-1] if tank01_name else ""
                
                if (yahoo_last and tank01_last and yahoo_last == tank01_last and 
                    yahoo_team.upper() == tank01_team.upper()):
                    # Position validation
                    if yahoo_position and tank01_pos and yahoo_position != tank01_pos:
                        continue
                    
                    self.logger.debug(f"Matched {yahoo_name} by last name + team")
                    return player
        
        # Strategy 4: Try get_player_info API for unmatched players
        self.logger.info(f"Trying get_player_info API for unmatched player: {yahoo_name}")
        try:
            player_info = self.tank01.get_player_info(yahoo_name, get_stats=True)
            if player_info and 'body' in player_info:
                body = player_info['body']
                if isinstance(body, list) and body:
                    # Find best match from results
                    for result in body:
                        if isinstance(result, dict):
                            result_name = result.get('longName', '').lower().strip()
                            result_team = result.get('team', '')
                            
                            # Team abbreviation mapping for common differences (Yahoo -> Tank01)
                            team_mapping = {
                                'WAS': 'WSH', 'Was': 'WSH', 'was': 'WSH'
                            }
                            
                            yahoo_team_mapped = team_mapping.get(yahoo_team, yahoo_team)
                            result_team_mapped = team_mapping.get(result_team, result_team)
                            
                            if (result_name == yahoo_name_clean and 
                                (not yahoo_team or result_team_mapped.upper() == yahoo_team_mapped.upper())):
                                self.logger.debug(f"Matched {yahoo_name} via get_player_info API")
                                return result
                elif isinstance(body, dict):
                    self.logger.debug(f"Matched {yahoo_name} via get_player_info API (single result)")
                    return body
            self.stats["api_calls"] += 1
        except Exception as e:
            self.logger.warning(f"get_player_info API failed for {yahoo_name}: {e}")
        
        # Strategy 5: Handle team defense as special case
        if yahoo_position == 'DEF' or 'defense' in yahoo_name.lower():
            # Import team mapping utility using absolute import
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
            from team_mapping import normalize_team_abbreviation, get_team_id, get_team_name
            
            # Normalize team abbreviation from Yahoo to standard format
            standard_team = normalize_team_abbreviation(yahoo_team, 'yahoo')
            team_id = get_team_id(yahoo_team, 'yahoo')
            team_name = get_team_name(yahoo_team, 'yahoo')
            
            if team_id:
                # Create team defense player entry using real data
                team_defense = {
                    'playerID': f'DEF_{team_id}',
                    'longName': f'{team_name}',
                    'team': standard_team,
                    'pos': 'DEF',
                    'teamID': team_id,
                    'isTeamDefense': True,
                    'yahoo_team_abbr': yahoo_team,
                    'standard_team_abbr': standard_team
                }
                self.logger.debug(f"Created team defense entry for {yahoo_team} -> {standard_team} (ID: {team_id}) - {team_name}")
                return team_defense
        
        self.logger.warning(f"No Tank01 match found for {yahoo_name} ({yahoo_team})")
        return None
    
    def _get_player_game_stats(self, tank01_player: Dict[str, Any], season: str = "2025", team_defense_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get comprehensive game statistics for a player from the current season.
        
        Args:
            tank01_player: Tank01 player data
            season: Season year (default: 2025)
            
        Returns:
            Dict containing player game statistics
        """
        player_id = tank01_player.get('playerID', '')
        if not player_id:
            return {}
        
        try:
            self.logger.info(f"Fetching game stats for player {player_id} (season {season})")
            
            # Use the getNFLGamesForPlayer endpoint with season parameter
            game_stats = self.tank01.get_player_game_stats(player_id, season)
            
            if game_stats and 'body' in game_stats:
                games = game_stats['body']
                if isinstance(games, dict):
                    # Convert to list and sort by game date (most recent first)
                    game_list = [(game_id, game_data) for game_id, game_data in games.items()]
                    # Sort by date part of game ID (YYYYMMDD format)
                    game_list.sort(key=lambda x: x[0].split('_')[0] if '_' in x[0] else x[0], reverse=True)
                    
                    # Process each game to extract key statistics
                    processed_games = []
                    for game_id, game_data in game_list:
                        processed_game = {
                            'game_id': game_id,
                            'game_date': self._extract_game_date(game_id),
                            'week': self._extract_week_from_game_id(game_id),
                            'opponent': self._extract_opponent_from_game_id(game_id),
                            'team': game_data.get('teamAbv', ''),
                            'snap_counts': game_data.get('snapCounts', {}),
                            'passing': game_data.get('Passing', {}),
                            'rushing': game_data.get('Rushing', {}),
                            'receiving': game_data.get('Receiving', {}),
                            'defense': game_data.get('Defense', {}),
                            'fantasy_points': self._calculate_fantasy_points(game_data),
                            'raw_data': game_data
                        }
                        processed_games.append(processed_game)
                    
                    # Calculate season totals and averages
                    season_totals = self._calculate_season_totals(processed_games, team_defense_stats)
                    season_averages = self._calculate_season_averages(processed_games)
                    
                    return {
                        'games': processed_games,
                        'total_games': len(processed_games),
                        'season_totals': season_totals,
                        'season_averages': season_averages,
                        'recent_performance': processed_games[:3] if processed_games else [],  # Last 3 games
                        'raw_response': game_stats
                    }
                else:
                    self.logger.warning(f"Unexpected game stats format for player {player_id}")
                    return {'games': [], 'total_games': 0, 'error': 'Unexpected format'}
            else:
                self.logger.warning(f"No game stats data for player {player_id}")
                return {'games': [], 'total_games': 0, 'error': 'No data'}
            
            self.stats["api_calls"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to get game stats for player {player_id}: {e}")
            self.stats["errors"] += 1
            return {'games': [], 'total_games': 0, 'error': str(e)}
    
    def _extract_game_date(self, game_id: str) -> str:
        """Extract game date from game ID (format: 20241201_SF@BUF)"""
        try:
            if '_' in game_id:
                date_part = game_id.split('_')[0]
                if len(date_part) == 8:  # YYYYMMDD format
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    return f"{year}-{month}-{day}"
        except Exception:
            pass
        return game_id
    
    def _extract_week_from_game_id(self, game_id: str) -> int:
        """Extract week number from game ID (approximate)"""
        try:
            if '_' in game_id:
                date_part = game_id.split('_')[0]
                if len(date_part) == 8:  # YYYYMMDD format
                    year = int(date_part[:4])
                    month = int(date_part[4:6])
                    day = int(date_part[6:8])
                    
                    # Approximate week calculation (NFL season starts around September 8)
                    season_start = datetime(year, 9, 8)
                    game_date = datetime(year, month, day)
                    
                    if game_date >= season_start:
                        days_diff = (game_date - season_start).days
                        week = (days_diff // 7) + 1
                        return min(week, 18)  # Cap at week 18
        except Exception as e:
            self.logger.warning(f"Error extracting week from game_id {game_id}: {e}")
            pass
        return 1
    
    def _extract_opponent_from_game_id(self, game_id: str) -> str:
        """Extract opponent from game ID (format: 20241201_SF@BUF)"""
        try:
            if '@' in game_id:
                parts = game_id.split('@')
                if len(parts) == 2:
                    return parts[1]  # Return the team after @
        except Exception:
            pass
        return "Unknown"
    
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
            
            # Use the getNFLTeams endpoint with team stats
            team_stats = self.tank01.get_nfl_teams(team_stats=True, team_stats_season=2025)
            
            if team_stats and 'body' in team_stats:
                teams = team_stats['body']
                if isinstance(teams, list):
                    for team in teams:
                        if team.get('teamAbv', '').upper() == team_abbr.upper():
                            team_data = team.get('teamStats', {})
                            # Extract defense stats from the Defense section
                            defense_stats = team_data.get('Defense', {})
                            
                            # Convert all values to proper types
                            def safe_float(value, default=0):
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
            self.logger.error(f"Failed to get team defense stats for {team_abbr}: {e}")
            return {}

    def _calculate_fantasy_points(self, game_data: Dict[str, Any]) -> float:
        """Calculate fantasy points for a game using standard scoring"""
        try:
            points = 0.0
            
            # Passing stats
            passing = game_data.get('Passing', {})
            pass_yards = float(passing.get('passYds', 0))
            pass_tds = float(passing.get('passTD', 0))
            interceptions = float(passing.get('int', 0))
            
            points += pass_yards * 0.04  # 1 point per 25 yards
            points += pass_tds * 4       # 4 points per TD
            points += interceptions * -2  # -2 points per INT
            
            # Rushing stats
            rushing = game_data.get('Rushing', {})
            rush_yards = float(rushing.get('rushYds', 0))
            rush_tds = float(rushing.get('rushTD', 0))
            
            points += rush_yards * 0.1   # 1 point per 10 yards
            points += rush_tds * 6       # 6 points per TD
            
            # Receiving stats
            receiving = game_data.get('Receiving', {})
            rec_yards = float(receiving.get('recYds', 0))
            rec_tds = float(receiving.get('recTD', 0))
            receptions = float(receiving.get('receptions', 0))
            
            points += rec_yards * 0.1    # 1 point per 10 yards
            points += rec_tds * 6        # 6 points per TD
            points += receptions * 1     # 1 point per reception (PPR)
            
            # Defense stats
            defense = game_data.get('Defense', {})
            def_tds = float(defense.get('defTD', 0))
            interceptions = float(defense.get('interceptions', 0))
            fumbles_recovered = float(defense.get('fumblesRecovered', 0))
            safeties = float(defense.get('safeties', 0))
            sacks = float(defense.get('sacks', 0))
            points_allowed = float(defense.get('pointsAllowed', 0))
            
            points += def_tds * 6        # 6 points per defensive TD
            points += interceptions * 2  # 2 points per interception
            points += fumbles_recovered * 2  # 2 points per fumble recovery
            points += safeties * 2       # 2 points per safety
            points += sacks * 1          # 1 point per sack
            
            # Points allowed scoring (standard fantasy defense scoring)
            if points_allowed == 0:
                points += 10  # Shutout
            elif points_allowed <= 6:
                points += 7   # 1-6 points allowed
            elif points_allowed <= 13:
                points += 4   # 7-13 points allowed
            elif points_allowed <= 20:
                points += 1   # 14-20 points allowed
            elif points_allowed <= 27:
                points += 0   # 21-27 points allowed
            else:
                points -= 1   # 28+ points allowed
            
            return round(points, 2)
        except Exception:
            return 0.0
    
    def _calculate_season_totals(self, games: List[Dict[str, Any]], team_defense_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate season totals for all games"""
        totals = {
            'passing': {'passYds': 0, 'passTD': 0, 'int': 0, 'passAttempts': 0, 'passCompletions': 0},
            'rushing': {'rushYds': 0, 'rushTD': 0, 'carries': 0},
            'receiving': {'recYds': 0, 'recTD': 0, 'receptions': 0, 'targets': 0},
            'defense': {
                'fumblesLost': 0, 'defensiveInterceptions': 0, 'forcedFumbles': 0, 'fumbles': 0, 'fumblesRecovered': 0,
                'defTD': 0, 'totalTackles': 0, 'soloTackles': 0, 'tacklesForLoss': 0, 'qbHits': 0, 
                'interceptions': 0, 'sacks': 0, 'passDeflections': 0, 'safeties': 0, 'pointsAllowed': 0,
                'yardsAllowed': 0, 'passYardsAllowed': 0, 'rushYardsAllowed': 0, 'turnovers': 0
            },
            'fantasy_points': 0,
            'games_played': len(games)
        }
        
        # If no games but we have team defense stats, use those instead
        if not games and team_defense_stats:
            totals['games_played'] = 1  # Team defense stats represent 1 game
            # Map team defense stats to our defense totals
            totals['defense']['fumblesRecovered'] = team_defense_stats.get('fumblesRecovered', 0)
            totals['defense']['interceptions'] = team_defense_stats.get('interceptions', 0)
            totals['defense']['sacks'] = team_defense_stats.get('sacks', 0)
            totals['defense']['safeties'] = team_defense_stats.get('safeties', 0)
            totals['defense']['defTD'] = team_defense_stats.get('defTD', 0)
            totals['defense']['totalTackles'] = team_defense_stats.get('totalTackles', 0)
            totals['defense']['soloTackles'] = team_defense_stats.get('soloTackles', 0)
            totals['defense']['tacklesForLoss'] = team_defense_stats.get('tacklesForLoss', 0)
            totals['defense']['qbHits'] = team_defense_stats.get('qbHits', 0)
            totals['defense']['passDeflections'] = team_defense_stats.get('passDeflections', 0)
            totals['defense']['pointsAllowed'] = team_defense_stats.get('pointsAllowed', 0)
            totals['defense']['yardsAllowed'] = team_defense_stats.get('yardsAllowed', 0)
            totals['defense']['passYardsAllowed'] = team_defense_stats.get('passYardsAllowed', 0)
            totals['defense']['rushYardsAllowed'] = team_defense_stats.get('rushYardsAllowed', 0)
            totals['defense']['turnovers'] = team_defense_stats.get('turnovers', 0)
            
            # Calculate fantasy points for team defense
            totals['fantasy_points'] = self._calculate_fantasy_points(totals['defense'])
            return totals
        
        for game in games:
            # Passing totals
            passing = game.get('passing', {})
            for stat in totals['passing']:
                try:
                    totals['passing'][stat] += float(passing.get(stat, 0))
                except (ValueError, TypeError):
                    totals['passing'][stat] += 0.0
            
            # Rushing totals
            rushing = game.get('rushing', {})
            for stat in totals['rushing']:
                try:
                    totals['rushing'][stat] += float(rushing.get(stat, 0))
                except (ValueError, TypeError):
                    totals['rushing'][stat] += 0.0
            
            # Receiving totals
            receiving = game.get('receiving', {})
            for stat in totals['receiving']:
                try:
                    totals['receiving'][stat] += float(receiving.get(stat, 0))
                except (ValueError, TypeError):
                    totals['receiving'][stat] += 0.0
            
            # Defense totals
            defense = game.get('defense', {})
            for stat in totals['defense']:
                try:
                    totals['defense'][stat] += float(defense.get(stat, 0))
                except (ValueError, TypeError):
                    totals['defense'][stat] += 0.0
            
            # Fantasy points
            try:
                totals['fantasy_points'] += float(game.get('fantasy_points', 0))
            except (ValueError, TypeError):
                totals['fantasy_points'] += 0.0
        
        return totals
    
    def _calculate_season_averages(self, games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate season averages per game"""
        if not games:
            return {}
        
        totals = self._calculate_season_totals(games)
        games_played = len(games)
        
        averages = {
            'passing': {},
            'rushing': {},
            'receiving': {},
            'defense': {},
            'fantasy_points': 0
        }
        
        # Calculate averages for each category
        for category in ['passing', 'rushing', 'receiving', 'defense']:
            for stat in totals[category]:
                try:
                    averages[category][stat] = round(totals[category][stat] / games_played, 2)
                except (TypeError, ZeroDivisionError) as e:
                    self.logger.warning(f"Error calculating average for {category}.{stat}: {e}")
                    averages[category][stat] = 0.0
        
        try:
            averages['fantasy_points'] = round(totals['fantasy_points'] / games_played, 2)
        except (TypeError, ZeroDivisionError) as e:
            self.logger.warning(f"Error calculating fantasy points average: {e}")
            averages['fantasy_points'] = 0.0
        
        return averages
    
    def _generate_markdown_report(self, matched_players: List[Dict[str, Any]], season_context: Dict[str, Any]) -> str:
        """
        Generate a comprehensive markdown report of player game stats.
        
        Args:
            matched_players: List of matched players with game stats
            season_context: Season and week context information
            
        Returns:
            Markdown report string
        """
        report = []
        report.append("# Tank01 NFL - My Roster Player Game Stats")
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
            report.append("No Yahoo roster players were successfully matched to Tank01 database.")
            return "\n".join(report)
        
        # Summary table
        report.append("## My Roster Player Game Stats Summary")
        report.append("")
        report.append("| Player | Pos | Team | Games | Avg FP | Total FP | Recent Form | Key Stats |")
        report.append("|--------|-----|------|-------|--------|----------|-------------|-----------|")
        
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
            
            # Generate key stats summary
            key_stats = []
            if pos == 'QB':
                passing = season_totals.get('passing', {})
                if passing.get('passYds', 0) > 0:
                    key_stats.append(f"{passing.get('passYds', 0):.0f} pass yds")
                if passing.get('passTD', 0) > 0:
                    key_stats.append(f"{passing.get('passTD', 0):.0f} pass TDs")
            elif pos == 'RB':
                rushing = season_totals.get('rushing', {})
                if rushing.get('rushYds', 0) > 0:
                    key_stats.append(f"{rushing.get('rushYds', 0):.0f} rush yds")
                if rushing.get('rushTD', 0) > 0:
                    key_stats.append(f"{rushing.get('rushTD', 0):.0f} rush TDs")
            elif pos == 'WR' or pos == 'TE':
                receiving = season_totals.get('receiving', {})
                if receiving.get('recYds', 0) > 0:
                    key_stats.append(f"{receiving.get('recYds', 0):.0f} rec yds")
                if receiving.get('recTD', 0) > 0:
                    key_stats.append(f"{receiving.get('recTD', 0):.0f} rec TDs")
                if receiving.get('receptions', 0) > 0:
                    key_stats.append(f"{receiving.get('receptions', 0):.0f} rec")
            elif pos == 'K':
                key_stats.append(f"{total_fp:.1f} FP")
            elif pos == 'DEF':
                team_defense_stats = game_stats.get('team_defense_stats', {})
                if team_defense_stats:
                    if team_defense_stats.get('sacks', 0) > 0:
                        key_stats.append(f"{team_defense_stats.get('sacks', 0):.0f} sacks")
                    if team_defense_stats.get('interceptions', 0) > 0:
                        key_stats.append(f"{team_defense_stats.get('interceptions', 0):.0f} INTs")
                    if team_defense_stats.get('fumblesRecovered', 0) > 0:
                        key_stats.append(f"{team_defense_stats.get('fumblesRecovered', 0):.0f} FR")
                    if team_defense_stats.get('pointsAllowed', 0) >= 0:
                        key_stats.append(f"{team_defense_stats.get('pointsAllowed', 0):.0f} PA")
                    if team_defense_stats.get('pointsFor', 0) > 0:
                        key_stats.append(f"{team_defense_stats.get('pointsFor', 0):.0f} PF")
                    if team_defense_stats.get('totalTackles', 0) > 0:
                        key_stats.append(f"{team_defense_stats.get('totalTackles', 0):.0f} tackles")
            
            key_stats_str = ', '.join(key_stats[:3]) if key_stats else 'No stats'
            
            report.append(f"| {name} | {pos} | {team} | {games_played} | {avg_fp:.1f} | {total_fp:.1f} | {recent_form} | {key_stats_str} |")
        
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing passing stat {stat}: {value} (type: {type(value)}): {e}")
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing rushing stat {stat}: {value} (type: {type(value)}): {e}")
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing receiving stat {stat}: {value} (type: {type(value)}): {e}")
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing defense stat {stat}: {value} (type: {type(value)}): {e}")
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing passing avg {stat}: {value} (type: {type(value)}): {e}")
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing rushing avg {stat}: {value} (type: {type(value)}): {e}")
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
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Error processing receiving avg {stat}: {value} (type: {type(value)}): {e}")
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
    
    def extract_my_roster_stats(self) -> Dict[str, Any]:
        """
        Extract comprehensive game statistics for my Yahoo Fantasy roster.
        
        Returns:
            Dict containing extraction results and data
        """
        self.logger.info("Starting Tank01 my roster stats extraction")
        
        # Load Yahoo roster players
        yahoo_players, yahoo_data = self._load_latest_yahoo_roster_players()
        if not yahoo_players:
            self.logger.error("No Yahoo roster players loaded")
            return {"error": "No Yahoo roster players loaded"}
        
        # Load Tank01 player database once at the start
        self.logger.info("Loading Tank01 player database...")
        self._tank01_player_cache = self._get_tank01_player_database()
        if not self._tank01_player_cache:
            self.logger.error("Failed to load Tank01 player database")
            return {"error": "Failed to load Tank01 player database"}
        
        # Process each player
        matched_players = []
        unmatched_players = []
        
        for yahoo_player in yahoo_players:
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
                try:
                    game_stats = self._get_player_game_stats(tank01_player, season="2025", team_defense_stats=team_defense_stats)
                    
                    # Add team defense stats to game stats for display
                    if team_defense_stats:
                        game_stats['team_defense_stats'] = team_defense_stats
                    
                    # Update total games collected
                    self.stats["total_games_collected"] += game_stats.get('total_games', 0)
                except Exception as e:
                    self.logger.error(f"Error getting game stats for player {tank01_player.get('playerID', 'Unknown')}: {e}")
                    game_stats = {'games': [], 'total_games': 0, 'error': str(e)}
                
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
                "source": "Tank01 API - My Roster Player Game Stats",
                "extraction_timestamp": datetime.now().isoformat(),
                "yahoo_source": "Latest my_roster.py output",
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
        
        clean_file = self.file_manager.save_clean_data("tank01", "my_roster_stats", markdown_report, week_prefix)
        raw_file = self.file_manager.save_raw_data("tank01", "my_roster_stats", raw_data, week_prefix)
        
        output_files = {
            "clean": clean_file,
            "raw": raw_file
        }
        
        self.logger.info(f"Tank01 my roster stats extraction complete")
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
        extractor = Tank01MyRosterStatsExtractor()
        result = extractor.extract_my_roster_stats()
        
        if result.get("success"):
            print(f"✅ Tank01 my roster stats extraction successful!")
            print(f"   Matched: {result['matched_players']} players")
            print(f"   Total games collected: {result['total_games_collected']}")
            print(f"   API calls: {result['api_calls']}")
            print(f"   Output files: {result['output_files']}")
        else:
            print(f"❌ Tank01 my roster stats extraction failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Tank01 my roster stats extraction failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
