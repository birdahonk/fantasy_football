#!/usr/bin/env python3
"""
Tank01 NFL API - My Roster Data Extraction

This script loads the latest Yahoo my roster data, maps players to the Tank01 NFL database,
and extracts ALL available Tank01 data including fantasy projections, news, and comprehensive stats.

Purpose: Clean, focused data extraction for my roster players using Tank01 API
Output: Comprehensive markdown file + raw JSON of all Tank01 data
Focus: Extract ALL available Tank01 data, no analysis
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

def normalize_team_abbreviation(team_abv):
    """Normalize team abbreviation to uppercase for API consistency."""
    if not team_abv:
        return team_abv
    
    # Team abbreviation mapping for case normalization
    team_mapping = {
        'phi': 'PHI', 'pit': 'PIT', 'sf': 'SF', 'sea': 'SEA', 'tb': 'TB', 'ten': 'TEN', 'wsh': 'WSH',
        'ari': 'ARI', 'atl': 'ATL', 'bal': 'BAL', 'buf': 'BUF', 'car': 'CAR', 'chi': 'CHI', 'cin': 'CIN', 'cle': 'CLE',
        'dal': 'DAL', 'den': 'DEN', 'det': 'DET', 'gb': 'GB', 'hou': 'HOU', 'ind': 'IND', 'jax': 'JAX', 'kc': 'KC',
        'lv': 'LV', 'lac': 'LAC', 'lar': 'LAR', 'mia': 'MIA', 'min': 'MIN', 'ne': 'NE', 'no': 'NO', 'nyg': 'NYG', 'nyj': 'NYJ'
    }
    
    return team_mapping.get(team_abv.lower(), team_abv.upper())

class Tank01MyRosterExtractor:
    """
    Extract comprehensive Tank01 data for my Yahoo Fantasy roster players.
    
    This script:
    1. Loads latest Yahoo my roster data
    2. Maps Yahoo players to Tank01 database
    3. Extracts fantasy projections, news, and comprehensive stats
    4. Outputs organized markdown and raw JSON
    """
    
    def __init__(self):
        """Initialize the Tank01 my roster extractor."""
        self.logger = logging.getLogger(__name__)
        self.file_manager = DataFileManager()
        self.formatter = MarkdownFormatter()
        
        # Initialize Tank01 client
        self.tank01 = SimpleTank01Client()
        if not self.tank01.is_available():
            raise ValueError("Tank01 client not available. Check RAPIDAPI_KEY environment variable.")
        
        # Cache for Tank01 player database
        self._tank01_player_cache = None
        self._weekly_projections_cache = None
        
        # Track execution stats
        self.stats = {
            "start_time": datetime.now(),
            "api_calls": 0,
            "errors": 0,
            "yahoo_players_loaded": 0,
            "players_processed": 0,
            "players_matched": 0,
            "players_unmatched": 0
        }
        
        self.logger.info("Tank01 My Roster Extractor initialized")
    
    def _extract_season_context(self, yahoo_data: Dict) -> Dict[str, Any]:
        """
        Extract season and week context from Yahoo data.
        
        Args:
            yahoo_data: Yahoo roster data
            
        Returns:
            Dict with season context information
        """
        try:
            current_date = get_current_time_pacific()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'data_source': 'Tank01 API',
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
                'data_source': 'Tank01 API',
                'verification_notes': [f"Error extracting season context: {e}"]
            }
    
    def _determine_season_phase(self, current_date: datetime) -> str:
        """Determine the current phase of the NFL season based on date"""
        month = current_date.month
        day = current_date.day
        
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
            roster_files = list(yahoo_output_dir.glob("*_my_roster_raw_data.json"))
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
        
        return players, raw_data
    
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
            # Map team abbreviations to Tank01 team IDs
            team_id_map = {
                'PHI': '27', 'PIT': '26', 'SF': '28', 'SEA': '29', 'TB': '30', 'TEN': '31', 'WSH': '32',
                'ARI': '1', 'ATL': '2', 'BAL': '3', 'BUF': '4', 'CAR': '5', 'CHI': '6', 'CIN': '7', 'CLE': '8',
                'DAL': '9', 'DEN': '10', 'DET': '11', 'GB': '12', 'HOU': '13', 'IND': '14', 'JAX': '15', 'KC': '16',
                'LV': '17', 'LAC': '18', 'LAR': '19', 'MIA': '20', 'MIN': '21', 'NE': '22', 'NO': '23', 'NYG': '24', 'NYJ': '25'
            }
            
            team_id = team_id_map.get(yahoo_team.upper())
            if team_id:
                # Create a mock team defense player entry
                team_defense = {
                    'playerID': f'DEF_{team_id}',
                    'longName': f'{yahoo_team} Defense',
                    'team': yahoo_team,
                    'pos': 'DEF',
                    'teamID': team_id,
                    'isTeamDefense': True
                }
                self.logger.debug(f"Created team defense entry for {yahoo_team}")
                return team_defense
        
        self.logger.warning(f"No Tank01 match found for {yahoo_name} ({yahoo_team})")
        return None
    
    def _get_comprehensive_tank01_data(self, tank01_player: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive Tank01 data for a player including projections and news.
        
        Args:
            tank01_player: Tank01 player data
            
        Returns:
            Comprehensive Tank01 data including projections and news
        """
        player_id = tank01_player.get('playerID', '')
        if not player_id:
            return tank01_player
        
        comprehensive_data = tank01_player.copy()
        
        # Get fantasy projections from cached weekly projections (much more efficient)
        if self._weekly_projections_cache:
            player_projections = None
            
            # Check if this is a team defense
            if tank01_player.get('isTeamDefense'):
                team_id = tank01_player.get('teamID')
                if team_id and 'teamDefenseProjections' in self._weekly_projections_cache:
                    team_def_projs = self._weekly_projections_cache['teamDefenseProjections']
                    if team_id in team_def_projs:
                        player_projections = team_def_projs[team_id]
                        player_projections['playerID'] = player_id
                        player_projections['isTeamDefense'] = True
                        self.logger.debug(f"Found team defense projections for {player_id}")
            else:
                # Regular player projections
                if 'playerProjections' in self._weekly_projections_cache:
                    player_projs = self._weekly_projections_cache['playerProjections']
                    if player_id in player_projs:
                        player_projections = player_projs[player_id]
                        self.logger.debug(f"Found cached projections for {player_id}")
            
            if player_projections:
                comprehensive_data['fantasy_projections'] = player_projections
            else:
                self.logger.debug(f"No cached projections found for {player_id}")
        else:
            self.logger.warning("Weekly projections cache not available")
        
        # Get player-specific news (now with special defense handling)
        news = self._get_player_specific_news(tank01_player)
        comprehensive_data['recent_news'] = news
        
        # Get player game statistics for injury status and performance
        game_stats = self._get_player_game_stats(player_id)
        comprehensive_data['game_stats'] = game_stats
        
        # Get depth chart position
        depth_chart = self._get_depth_chart_position(tank01_player)
        comprehensive_data['depth_chart'] = depth_chart
        
        # Get team context
        team_context = self._get_team_context(tank01_player.get('team'))
        comprehensive_data['team_context'] = team_context
        
        return comprehensive_data
    
    def _get_player_specific_news(self, tank01_player: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get player-specific news, with special handling for team defense."""
        player_id = tank01_player.get('playerID')
        team_abv = normalize_team_abbreviation(tank01_player.get('team'))
        position = tank01_player.get('pos')
        
        news_articles = []
        
        try:
            # Special handling for team defense
            if position == 'DEF' or tank01_player.get('isTeamDefense'):
                # For team defense, get 10 most recent team news articles
                # Use normalized team abbreviation (e.g., 'PHI' not 'Phi')
                team_news = self.tank01.get_news(fantasy_news=True, max_items=10, team_abv=team_abv)
                if team_news and 'body' in team_news:
                    # Get all 10 team news articles (no filtering needed since we can't distinguish defense-specific news)
                    news_articles = team_news['body'][:10]
                    self.logger.debug(f"Retrieved {len(news_articles)} team news articles for {team_abv} defense")
                else:
                    self.logger.warning(f"No team news found for {team_abv} defense")
            else:
                # For regular players, get player-specific news
                player_news = self.tank01.get_news(fantasy_news=True, max_items=5, player_id=player_id)
                if player_news and 'body' in player_news:
                    news_articles = player_news['body'][:5]
                else:
                    # Fallback to team news if no player-specific news
                    team_news = self.tank01.get_news(fantasy_news=True, max_items=5, team_abv=team_abv)
                    if team_news and 'body' in team_news:
                        news_articles = team_news['body'][:5]
            
            # API call is tracked by the Tank01 client, not here
            self.logger.debug(f"Retrieved {len(news_articles)} news articles for {tank01_player.get('longName', 'Unknown')}")
            
        except Exception as e:
            self.logger.warning(f"Failed to get news for {tank01_player.get('longName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
        
        return news_articles
    
    def _get_player_game_stats(self, player_id: str) -> Dict[str, Any]:
        """Get player game statistics to infer injury status and performance."""
        try:
            game_stats = self.tank01.get_player_game_stats(player_id, season="2024")
            
            if game_stats and 'body' in game_stats:
                games = game_stats['body']
                if isinstance(games, dict):
                    # Convert to list and sort by game date (most recent first)
                    game_list = [(game_id, game_data) for game_id, game_data in games.items()]
                    game_list.sort(key=lambda x: x[0], reverse=True)  # Sort by game ID (date)
                    
                    recent_games = game_list[:3]  # Last 3 games
                    
                    # Determine injury status from snap counts
                    injury_status = "Healthy"
                    last_game_played = "N/A"
                    
                    if recent_games:
                        last_game_played = recent_games[0][0]  # Most recent game ID
                        
                        for game_id, game_data in recent_games:
                            snap_counts = game_data.get('snapCounts', {})
                            off_snap_pct = float(snap_counts.get('offSnapPct', '0'))
                            
                            if off_snap_pct < 0.1:  # Less than 10% snaps
                                injury_status = "Injured/Limited"
                                break
                            elif off_snap_pct < 0.5:  # Less than 50% snaps
                                injury_status = "Limited Role"
                    
                    return {
                        'injury_status': injury_status,
                        'last_game_played': last_game_played,
                        'recent_games': [game_data for _, game_data in recent_games],
                        'total_games': len(games)
                    }
            
            # API call is tracked by the Tank01 client, not here
            self.logger.debug(f"Retrieved game stats for player {player_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to get game stats for player {player_id}: {e}")
            self.stats["errors"] += 1
        
        return {
            'injury_status': 'No recent data',
            'last_game_played': 'N/A',
            'recent_games': [],
            'total_games': 0
        }
    
    def _get_depth_chart_position(self, tank01_player: Dict[str, Any]) -> Dict[str, Any]:
        """Get player's depth chart position for opportunity analysis."""
        player_id = tank01_player.get('playerID')
        team_abv = normalize_team_abbreviation(tank01_player.get('team'))
        position = tank01_player.get('pos')
        
        try:
            # Get depth charts (cached globally)
            if not hasattr(self, '_depth_charts_cache'):
                self._depth_charts_cache = self.tank01.get_depth_charts()
                # API call is tracked by the Tank01 client, not here
            
            if self._depth_charts_cache and 'body' in self._depth_charts_cache:
                for team_chart in self._depth_charts_cache['body']:
                    if team_chart.get('teamAbv') == team_abv:
                        depth_chart = team_chart.get('depthChart', {})
                        position_group = depth_chart.get(position, [])
                        
                        for i, player in enumerate(position_group):
                            if player.get('playerID') == player_id:
                                opportunity = 'High' if i < 2 else 'Limited'
                                return {
                                    'depth_position': player.get('depthPosition', 'Unknown'),
                                    'depth_rank': i + 1,
                                    'opportunity': opportunity,
                                    'total_at_position': len(position_group)
                                }
            
            self.logger.debug(f"Depth chart position not found for {tank01_player.get('longName', 'Unknown')}")
            
        except Exception as e:
            self.logger.warning(f"Failed to get depth chart for {tank01_player.get('longName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
        
        return {
            'depth_position': 'Unknown',
            'depth_rank': 'N/A',
            'opportunity': 'Unknown',
            'total_at_position': 'N/A'
        }
    
    def _get_team_context(self, team_abv: str) -> Dict[str, Any]:
        """Get team performance context for fantasy outlook."""
        try:
            # Normalize team abbreviation for consistent matching
            normalized_team_abv = normalize_team_abbreviation(team_abv)
            
            # Get teams data (cached globally)
            if not hasattr(self, '_teams_cache'):
                self._teams_cache = self.tank01.get_nfl_teams(team_stats=True, top_performers=True)
                # API call is tracked by the Tank01 client, not here
            
            if self._teams_cache and 'body' in self._teams_cache:
                for team in self._teams_cache['body']:
                    if team.get('teamAbv') == normalized_team_abv:
                        wins = int(team.get('wins', '0'))
                        losses = int(team.get('loss', '0'))
                        
                        # Determine fantasy outlook based on team performance
                        if wins > losses:
                            fantasy_outlook = 'Positive'
                        elif wins == losses:
                            fantasy_outlook = 'Neutral'
                        else:
                            fantasy_outlook = 'Challenging'
                        
                        return {
                            'team_performance': f"{wins}-{losses}",
                            'division': team.get('division', 'Unknown'),
                            'conference': team.get('conferenceAbv', 'Unknown'),
                            'fantasy_outlook': fantasy_outlook,
                            'top_performers': team.get('topPerformers', {}),
                            'current_streak': team.get('currentStreak', {})
                        }
            
            self.logger.debug(f"Team context not found for {team_abv}")
            
        except Exception as e:
            self.logger.warning(f"Failed to get team context for {team_abv}: {e}")
            self.stats["errors"] += 1
        
        return {
            'team_performance': 'Unknown',
            'division': 'Unknown',
            'conference': 'Unknown',
            'fantasy_outlook': 'Unknown',
            'top_performers': {},
            'current_streak': {}
        }
    
    def _generate_markdown_report(self, matched_players: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive markdown report of Tank01 data for my roster.
        
        Args:
            matched_players: List of matched players with Tank01 data
            
        Returns:
            Markdown report string
        """
        report = []
        report.append("# Tank01 NFL - My Roster Data")
        report.append("")
        
        # Header with execution stats
        end_time = datetime.now()
        execution_time = (end_time - self.stats["start_time"]).total_seconds()
        
        report.append(f"**Extraction Date:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Yahoo Players Loaded:** {self.stats['yahoo_players_loaded']}")
        report.append(f"**Matched Players:** {self.stats['players_matched']}")
        report.append(f"**Unmatched Players:** {self.stats['players_unmatched']}")
        report.append(f"**Match Rate:** {(self.stats['players_matched'] / max(1, self.stats['yahoo_players_loaded'])) * 100:.1f}%")
        report.append(f"**Execution Time:** {execution_time:.2f}s")
        # Get actual API usage from Tank01 client
        usage_info = self.tank01.get_api_usage()
        actual_calls = usage_info.get('calls_made_this_session', 0)
        
        report.append(f"**API Calls:** {actual_calls}")
        report.append(f"**Errors:** {self.stats['errors']}")
        report.append("")
        
        # Tank01 API Usage Info (from RapidAPI headers)
        report.append("## Tank01 API Usage")
        report.append(f"- **Current Time (Pacific):** {get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        report.append(f"- **Calls Made This Session:** {actual_calls}")
        report.append(f"- **Daily Limit:** {usage_info.get('daily_limit', 'Unknown')}")
        report.append(f"- **Remaining Calls Today:** {usage_info.get('remaining_calls', 'Unknown')}")
        report.append(f"- **Usage Percentage:** {usage_info.get('percentage_used', 0):.1f}%")
        report.append(f"- **Data Source:** {usage_info.get('data_source', 'Unknown')}")
        if usage_info.get('reset_timestamp'):
            report.append(f"- **Limit Resets:** {format_timestamp_pacific(usage_info['reset_timestamp'])}")
        report.append(f"- **Client Available:** {usage_info.get('available', False)}")
        report.append("")
        
        if not matched_players:
            report.append("## No Players Matched")
            report.append("No Yahoo roster players were successfully matched to Tank01 database.")
            return "\n".join(report)
        
        # Summary table
        report.append("## My Roster with Tank01 Data")
        report.append("")
        report.append("| Player | Pos | Team | Tank01 ID | Yahoo ID | Injury | Fantasy Outlook | Last Game |")
        report.append("|--------|-----|------|-----------|----------|--------|-----------------|-----------|")
        
        for player_data in matched_players:
            yahoo_player = player_data['yahoo_player']
            tank01_player = player_data['tank01_data']
            
            name = yahoo_player.get('name', {}).get('full', 'Unknown')
            pos = yahoo_player.get('display_position', 'N/A')
            team = yahoo_player.get('editorial_team_abbr', 'N/A')
            tank01_id = tank01_player.get('playerID', 'N/A')
            yahoo_id = yahoo_player.get('player_id', 'N/A')
            injury = tank01_player.get('injuryStatus', 'N/A')
            outlook = tank01_player.get('fantasyOutlook', 'N/A')
            last_game = tank01_player.get('lastGamePlayed', 'N/A')
            
            report.append(f"| {name} | {pos} | {team} | {tank01_id} | {yahoo_id} | {injury} | {outlook} | {last_game} |")
        
        report.append("")
        
        # Detailed player sections
        report.append("## Detailed Player Data")
        report.append("")
        
        for player_data in matched_players:
            yahoo_player = player_data['yahoo_player']
            tank01_player = player_data['tank01_data']
            
            name = yahoo_player.get('name', {}).get('full', 'Unknown')
            pos = yahoo_player.get('display_position', 'N/A')
            team = yahoo_player.get('editorial_team_abbr', 'N/A')
            
            report.append(f"### {name} ({pos} - {team})")
            report.append("")
            
            # Basic Tank01 info
            report.append("#### Tank01 Player Information")
            report.append(f"- **Tank01 ID**: {tank01_player.get('playerID', 'N/A')}")
            report.append(f"- **Yahoo ID**: {yahoo_player.get('player_id', 'N/A')}")
            report.append(f"- **Long Name**: {tank01_player.get('longName', 'N/A')}")
            report.append(f"- **Team**: {tank01_player.get('team', 'N/A')}")
            
            # Cross-platform IDs (different for team defense vs individual players)
            if tank01_player.get('isTeamDefense') or tank01_player.get('pos') == 'DEF':
                # Team defense specific information
                report.append("#### Team Defense Information")
                report.append(f"- **Team ID**: {tank01_player.get('teamID', 'N/A')}")
                report.append(f"- **Team Abbreviation**: {normalize_team_abbreviation(tank01_player.get('team', 'N/A'))}")
                report.append(f"- **Position**: {tank01_player.get('pos', 'N/A')}")
                report.append(f"- **Is Team Defense**: {tank01_player.get('isTeamDefense', 'N/A')}")
                report.append("")
            else:
                # Individual player information
                report.append("#### Cross-Platform IDs")
                report.append(f"- **ESPN ID**: {tank01_player.get('espnID', 'N/A')}")
                report.append(f"- **Sleeper ID**: {tank01_player.get('sleeperBotID', 'N/A')}")
                report.append(f"- **CBS ID**: {tank01_player.get('cbsPlayerID', 'N/A')}")
                report.append(f"- **RotoWire ID**: {tank01_player.get('rotoWirePlayerID', 'N/A')}")
                report.append(f"- **FRef ID**: {tank01_player.get('fRefID', 'N/A')}")
                report.append(f"- **Position**: {tank01_player.get('pos', 'N/A')}")
                report.append(f"- **Jersey Number**: {tank01_player.get('jerseyNum', 'N/A')}")
                report.append(f"- **Height**: {tank01_player.get('height', 'N/A')}")
                report.append(f"- **Weight**: {tank01_player.get('weight', 'N/A')}")
                report.append(f"- **Age**: {tank01_player.get('age', 'N/A')}")
                report.append(f"- **Experience**: {tank01_player.get('exp', 'N/A')}")
                report.append(f"- **School**: {tank01_player.get('school', 'N/A')}")
                report.append("")
            
            # Status and outlook (NO MORE N/A VALUES!)
            report.append("#### Status and Outlook")
            
            # Use game stats for injury status and last game
            game_stats = tank01_player.get('game_stats', {})
            injury_status = game_stats.get('injury_status', 'No recent data')
            last_game_played = game_stats.get('last_game_played', 'N/A')
            
            # Use team context for fantasy outlook
            team_context = tank01_player.get('team_context', {})
            fantasy_outlook = team_context.get('fantasy_outlook', 'Unknown')
            
            report.append(f"- **Injury Status**: {injury_status}")
            report.append(f"- **Fantasy Outlook**: {fantasy_outlook}")
            report.append(f"- **Last Game Played**: {last_game_played}")
            report.append("")
            
            # Depth chart position (not applicable for team defense)
            if not (tank01_player.get('isTeamDefense') or tank01_player.get('pos') == 'DEF'):
                depth_chart = tank01_player.get('depth_chart', {})
                if depth_chart.get('depth_position') != 'Unknown':
                    report.append("#### Depth Chart Position")
                    report.append(f"- **Position**: {depth_chart.get('depth_position', 'Unknown')}")
                    report.append(f"- **Rank**: {depth_chart.get('depth_rank', 'N/A')}")
                    report.append(f"- **Opportunity**: {depth_chart.get('opportunity', 'Unknown')}")
                    report.append("")
            
            # Recent performance (different for team defense vs individual players)
            if game_stats.get('recent_games'):
                if tank01_player.get('isTeamDefense') or tank01_player.get('pos') == 'DEF':
                    report.append("#### Recent Team Performance")
                    for i, game in enumerate(game_stats['recent_games'][:3], 1):
                        game_id = game.get('gameID', 'Unknown')
                        # For team defense, show different stats if available
                        report.append(f"- **Game {i}**: {game_id}")
                    report.append("")
                else:
                    report.append("#### Recent Performance")
                    for i, game in enumerate(game_stats['recent_games'][:3], 1):
                        game_id = game.get('gameID', 'Unknown')
                        snap_counts = game.get('snapCounts', {})
                        off_snap_pct = float(snap_counts.get('offSnapPct', '0'))
                        report.append(f"- **Game {i}**: {game_id} - {off_snap_pct*100:.1f}% offensive snaps")
                    report.append("")
            
            # Fantasy projections
            if 'fantasy_projections' in tank01_player:
                projections = tank01_player['fantasy_projections']
                report.append("#### Fantasy Projections")
                
                if isinstance(projections, dict):
                    # Show main fantasy points
                    if 'fantasyPoints' in projections:
                        report.append(f"- **Fantasy Points**: {projections['fantasyPoints']}")
                    
                    # Show fantasy points by format
                    if 'fantasyPointsDefault' in projections:
                        default_fp = projections['fantasyPointsDefault']
                        if isinstance(default_fp, dict):
                            report.append("- **Fantasy Points by Format:**")
                            for format_name, points in default_fp.items():
                                report.append(f"  - {format_name}: {points}")
                        else:
                            report.append(f"- **Default Fantasy Points**: {default_fp}")
                    
                    # Show detailed stats if available
                    if 'Passing' in projections:
                        passing = projections['Passing']
                        if isinstance(passing, dict):
                            report.append("- **Passing Projections:**")
                            for stat, value in passing.items():
                                report.append(f"  - {stat}: {value}")
                    
                    if 'Rushing' in projections:
                        rushing = projections['Rushing']
                        if isinstance(rushing, dict):
                            report.append("- **Rushing Projections:**")
                            for stat, value in rushing.items():
                                report.append(f"  - {stat}: {value}")
                    
                    if 'Receiving' in projections:
                        receiving = projections['Receiving']
                        if isinstance(receiving, dict):
                            report.append("- **Receiving Projections:**")
                            for stat, value in receiving.items():
                                report.append(f"  - {stat}: {value}")
                    
                    # Team defense specific stats
                    if projections.get('isTeamDefense'):
                        report.append("- **Team Defense Projections:**")
                        for stat, value in projections.items():
                            if stat not in ['playerID', 'isTeamDefense', 'fantasyPoints', 'fantasyPointsDefault']:
                                report.append(f"  - {stat}: {value}")
                else:
                    report.append(f"- **Projections Data**: {projections}")
            else:
                report.append("#### Fantasy Projections")
                report.append("- **Status**: No projections available")
            report.append("")
            
            # Recent news
            if 'recent_news' in tank01_player:
                news = tank01_player['recent_news']
                if news:
                    # Determine if this is a defense player to show more articles
                    is_defense = tank01_player.get('pos') == 'DEF' or tank01_player.get('isTeamDefense', False)
                    max_articles = 10 if is_defense else 5
                    news_type = "Team News" if is_defense else "Fantasy News"
                    
                    report.append(f"#### Recent {news_type}")
                    if is_defense:
                        report.append("*Note: For team defense, showing most recent team news (publication dates not available from API)*")
                    else:
                        report.append("*Note: Publication dates not available from Tank01 API*")
                    report.append("")
                    
                    if isinstance(news, list):
                        for i, article in enumerate(news[:max_articles], 1):
                            if isinstance(article, dict):
                                title = article.get('title', 'No title')
                                link = article.get('link', '')
                                image = article.get('image', '')
                                
                                report.append(f"{i}. **{title}**")
                                if link:
                                    report.append(f"   - [Read More]({link})")
                                if image:
                                    report.append(f"   - [Image]({image})")
                                report.append("")
                    else:
                        report.append(f"- **News Data**: {news}")
                else:
                    report.append("#### Recent Fantasy News")
                    report.append("- No recent news available")
            else:
                report.append("#### Recent Fantasy News")
                report.append("- No news data available")
            report.append("")
        
        # Add comprehensive API usage tracking at the end
        report.append("---")
        report.append("")
        report.append("## 📊 API Usage Tracking")
        report.append("")
        # Get final API usage for accurate reporting
        final_usage = self.tank01.get_api_usage()
        actual_calls = final_usage.get('calls_made_this_session', 0)
        
        # Calculate breakdown based on actual calls made
        base_calls = 4  # player list, projections, depth charts, teams
        player_specific_calls = actual_calls - base_calls
        calls_per_player = player_specific_calls / max(1, self.stats['players_matched'])
        
        report.append("### Tank01 API Session Summary")
        report.append(f"- **Total API Calls Made:** {actual_calls}")
        report.append(f"- **Base Calls:** {base_calls}")
        report.append(f"  - Player Database: 1 (getNFLPlayerList)")
        report.append(f"  - Weekly Projections: 1 (getNFLProjections - batch)")
        report.append(f"  - Depth Charts: 1 (getNFLDepthCharts)")
        report.append(f"  - Teams Data: 1 (getNFLTeams)")
        report.append(f"- **Player-Specific Calls:** {player_specific_calls}")
        report.append(f"  - News Calls: {self.stats['players_matched']} (getNFLNews - player-specific)")
        report.append(f"  - Game Stats Calls: {self.stats['players_matched']} (getNFLGamesForPlayer)")
        report.append(f"  - Player Info Calls: {max(0, player_specific_calls - (self.stats['players_matched'] * 2))} (getNFLPlayerInfo - for unmatched)")
        report.append("")
        
        # Current usage status (from RapidAPI headers)
        final_usage = self.tank01.get_api_usage()
        report.append("### Current API Status (RapidAPI Headers)")
        report.append(f"- **Report Generated:** {get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        report.append(f"- **Calls Made This Session:** {final_usage.get('calls_made_this_session', 'Unknown')}")
        report.append(f"- **Daily Limit:** {final_usage.get('daily_limit', 'Unknown')}")
        report.append(f"- **Remaining Calls Today:** {final_usage.get('remaining_calls', 'Unknown')}")
        report.append(f"- **Usage Percentage:** {final_usage.get('percentage_used', 0):.1f}%")
        report.append(f"- **Data Source:** {final_usage.get('data_source', 'Unknown')}")
        if final_usage.get('reset_timestamp'):
            report.append(f"- **Limit Resets:** {format_timestamp_pacific(final_usage['reset_timestamp'])}")
        report.append("")
        
        # API efficiency metrics
        if self.stats['players_matched'] > 0:
            calls_per_player = self.stats['api_calls'] / self.stats['players_matched']
            report.append("### API Efficiency Metrics")
            report.append(f"- **API Calls per Player:** {calls_per_player:.1f}")
            report.append(f"- **Players Processed:** {self.stats['players_matched']}")
            report.append(f"- **Match Rate:** {(self.stats['players_matched'] / max(1, self.stats['yahoo_players_loaded'])) * 100:.1f}%")
            report.append("")
        
        # Recommendations for future runs
        report.append("### Recommendations")
        if final_usage.get('calls_made_this_session', 0) > 50:
            report.append("- ⚠️ **High API Usage**: Consider caching player database between runs")
        if self.stats['players_unmatched'] > 0:
            report.append(f"- 🔍 **Player Matching**: {self.stats['players_unmatched']} players couldn't be matched to Tank01 database")
        if self.stats['errors'] > 0:
            report.append(f"- ❌ **Errors**: {self.stats['errors']} API errors occurred during extraction")
        
        report.append("- 💡 **Optimization**: Consider running this script once per day to minimize API usage")
        report.append("- 📈 **Monitoring**: Track daily usage to stay within 1000 call limit")
        report.append("")
        
        return "\n".join(report)
    
    def extract_my_roster_data(self) -> Dict[str, Any]:
        """
        Extract comprehensive Tank01 data for my Yahoo Fantasy roster.
        
        Returns:
            Dict containing extraction results and data
        """
        self.logger.info("Starting Tank01 my roster data extraction")
        
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
        
        # Get batch weekly projections for all players (much more efficient)
        self.logger.info("Loading weekly projections for all players...")
        try:
            # Get current week projections (you may want to make this configurable)
            weekly_projections = self.tank01.get_weekly_projections(week=1, archive_season=2025)
            if weekly_projections and 'body' in weekly_projections:
                self._weekly_projections_cache = weekly_projections['body']
                self.logger.info(f"Loaded weekly projections for {len(self._weekly_projections_cache)} players")
            else:
                self._weekly_projections_cache = {}
                self.logger.warning("No weekly projections data received")
            self.stats["api_calls"] += 1
        except Exception as e:
            self.logger.error(f"Failed to load weekly projections: {e}")
            self._weekly_projections_cache = {}
            self.stats["errors"] += 1
        
        # Process each player
        matched_players = []
        unmatched_players = []
        
        for yahoo_player in yahoo_players:
            self.stats["players_processed"] += 1
            
            # Match to Tank01
            tank01_player = self._match_yahoo_to_tank01(yahoo_player)
            
            if tank01_player:
                # Get comprehensive Tank01 data
                comprehensive_data = self._get_comprehensive_tank01_data(tank01_player)
                
                matched_players.append({
                    'yahoo_player': yahoo_player,
                    'tank01_data': comprehensive_data
                })
                self.stats["players_matched"] += 1
            else:
                unmatched_players.append(yahoo_player)
                self.stats["players_unmatched"] += 1
        
        # News is now retrieved individually for each player with player-specific filtering
        self.logger.info(f"Retrieved player-specific news for {len(matched_players)} players")
        
        # Generate outputs
        markdown_report = self._generate_markdown_report(matched_players)
        
        # Prepare raw data with comprehensive API usage tracking
        final_usage = self.tank01.get_api_usage()
        season_context = self._extract_season_context(yahoo_data)
        raw_data = {
            "extraction_metadata": {
                "source": "Tank01 API - My Roster",
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
                    "base_calls": 4,
                    "player_database_call": 1,
                    "weekly_projections_call": 1,
                    "depth_charts_call": 1,
                    "teams_call": 1,
                    "player_specific_calls": max(0, final_usage.get('calls_made_this_session', 0) - 4),
                    "news_calls": self.stats['players_matched'],
                    "game_stats_calls": self.stats['players_matched'],
                    "get_player_info_calls": max(0, final_usage.get('calls_made_this_session', 0) - 4 - (self.stats['players_matched'] * 2)),
                    "total_calls": final_usage.get('calls_made_this_session', 0)
                },
                "efficiency_metrics": {
                    "calls_per_player": (final_usage.get('calls_made_this_session', 0) - 4) / max(1, self.stats['players_matched']),
                    "match_rate_percentage": (self.stats['players_matched'] / max(1, self.stats['yahoo_players_loaded'])) * 100,
                    "remaining_calls_today": final_usage.get('remaining_calls', 0),
                    "usage_percentage": final_usage.get('percentage_used', 0),
                    "data_source": final_usage.get('data_source', 'Unknown'),
                    "reset_timestamp": final_usage.get('reset_timestamp'),
                    "reset_timestamp_pacific": format_timestamp_pacific(final_usage.get('reset_timestamp')),
                    "last_updated": final_usage.get('last_updated'),
                    "report_generated_pacific": get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')
                },
                "recommendations": {
                    "high_usage_warning": final_usage.get('calls_made_this_session', 0) > 50,
                    "unmatched_players": self.stats['players_unmatched'],
                    "api_errors": self.stats['errors'],
                    "optimization_suggestions": [
                        "Consider caching player database between runs",
                        "Run script once per day to minimize API usage",
                        "Monitor daily usage to stay within 1000 call limit"
                    ]
                }
            }
        }
        
        # Save outputs
        timestamp = self.file_manager.generate_timestamp()
        clean_file = self.file_manager.save_clean_data("tank01", "my_roster", markdown_report, timestamp)
        raw_file = self.file_manager.save_raw_data("tank01", "my_roster", raw_data, timestamp)
        
        output_files = {
            "clean": clean_file,
            "raw": raw_file
        }
        
        self.logger.info(f"Tank01 my roster extraction complete")
        self.logger.info(f"Matched: {self.stats['players_matched']}/{self.stats['yahoo_players_loaded']} players")
        self.logger.info(f"API calls: {self.stats['api_calls']}")
        self.logger.info(f"Output files: {output_files}")
        
        return {
            "success": True,
            "matched_players": len(matched_players),
            "unmatched_players": len(unmatched_players),
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
        extractor = Tank01MyRosterExtractor()
        result = extractor.extract_my_roster_data()
        
        if result.get("success"):
            print(f"✅ Tank01 my roster extraction successful!")
            print(f"   Matched: {result['matched_players']} players")
            print(f"   API calls: {result['api_calls']}")
            print(f"   Output files: {result['output_files']}")
        else:
            print(f"❌ Tank01 my roster extraction failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Tank01 my roster extraction failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
