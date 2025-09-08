#!/usr/bin/env python3
"""
Tank01 NFL API - Opponent Roster Data Extraction

This script loads the latest Yahoo opponent roster data, maps players to the Tank01 NFL database,
and extracts ALL available Tank01 data including fantasy projections, news, and comprehensive stats.

Purpose: Clean, focused data extraction for opponent roster players using Tank01 API
Output: Comprehensive markdown file + raw JSON of all Tank01 data
Focus: Extract ALL available Tank01 data, no analysis
"""

import os
import sys
import json
import logging
import glob
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
        return None
    return team_abv.upper().strip()

class Tank01OpponentRosterExtractor:
    """Extract comprehensive Tank01 data for opponent roster players."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tank01_client = SimpleTank01Client()
        self.file_manager = DataFileManager()
        self.formatter = MarkdownFormatter()
        
        # Cache for weekly projections
        self._weekly_projections_cache = None
        
        self.stats = {
            'players_processed': 0,
            'players_matched': 0,
            'players_unmatched': 0,
            'api_calls': 0,
            'errors': 0
        }

    def _load_latest_yahoo_opponent_roster(self) -> tuple[List[Dict], Dict]:
        """Load the most recent Yahoo opponent roster data and find current week opponent."""
        try:
            # First, find the current week opponent from team matchups
            current_week_opponent = self._find_current_week_opponent()
            if not current_week_opponent:
                self.logger.error("Could not find current week opponent")
                return [], {}

            # Look for opponent roster files
            pattern = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'opponent_rosters', '*_raw_data.json'
            )
            files = glob.glob(pattern)
            
            if not files:
                self.logger.error("No Yahoo opponent roster files found")
                return [], {}

            # Get the most recent file
            latest_file = max(files, key=os.path.getctime)
            self.logger.info(f"Loading opponent roster from: {latest_file}")

            with open(latest_file, 'r') as f:
                data = json.load(f)

            # Extract opponent info and players from the rosters structure
            rosters = data.get('rosters', {})
            teams = data.get('teams', [])
            
            # Find the current week opponent's roster
            opponent_team_key = current_week_opponent.get('team_key')
            opponent_roster_data = rosters.get(opponent_team_key, {})
            opponent_team_info = next((team for team in teams if team.get("team_key") == opponent_team_key), {})
            
            if not opponent_roster_data:
                self.logger.error(f"No roster data found for opponent {current_week_opponent.get('name')}")
                return [], {}

            players = opponent_roster_data.get('players', [])
            opponent_data = {
                'opponent_name': current_week_opponent.get('name', 'Unknown Opponent'),
                'opponent_team_key': opponent_team_key,
                'players': players
            }
            
            self.logger.info(f"Loaded {len(players)} players for opponent: {opponent_data.get('opponent_name', 'Unknown')}")
            return players, opponent_data

        except Exception as e:
            self.logger.error(f"Error loading Yahoo opponent roster: {e}")
            return [], {}

    def _find_current_week_opponent(self) -> Optional[Dict[str, Any]]:
        """Find current week opponent from Yahoo team matchups data."""
        try:
            # Look for team matchups files
            matchups_pattern = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'team_matchups', '*_raw_data.json'
            )
            matchups_files = glob.glob(matchups_pattern)
            
            if not matchups_files:
                self.logger.error("No team matchups files found")
                return None

            # Get the most recent file
            latest_matchups = max(matchups_files, key=os.path.getctime)
            self.logger.info(f"Loading team matchups from: {latest_matchups}")

            with open(latest_matchups, 'r') as f:
                matchups_data = json.load(f)

            season_context = matchups_data.get("season_context", {})
            current_week = season_context.get("current_week", 1)
            league_info = matchups_data.get("league_info", {})
            my_team_key = league_info.get("team_key")
            
            if not my_team_key:
                self.logger.error("No team key found in matchups data")
                return None

            matchups = matchups_data.get("matchups", {})
            week_key = f"week_{current_week}"
            
            if week_key not in matchups:
                self.logger.error(f"No matchups found for week {current_week}")
                return None

            week_matchups = matchups[week_key].get("matchups", [])
            
            for matchup in week_matchups:
                teams = matchup.get("teams", [])
                if len(teams) == 2:
                    team1_key = teams[0].get("team_key")
                    team2_key = teams[1].get("team_key")
                    
                    if team1_key == my_team_key:
                        opponent_team = teams[1]
                        self.logger.info(f"Found current week opponent: {opponent_team.get('name')} (team_key: {opponent_team.get('team_key')})")
                        return opponent_team
                    elif team2_key == my_team_key:
                        opponent_team = teams[0]
                        self.logger.info(f"Found current week opponent: {opponent_team.get('name')} (team_key: {opponent_team.get('team_key')})")
                        return opponent_team

            self.logger.error(f"No matchup found for my team {my_team_key} in week {current_week}")
            return None

        except Exception as e:
            self.logger.error(f"Error finding current week opponent: {e}")
            return None

    def _extract_season_context(self, yahoo_data: Dict) -> Dict[str, Any]:
        """Extract season and week context from Yahoo data."""
        try:
            current_date = get_current_time_pacific()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'extraction_timestamp': current_date.isoformat()
            }
            
            # Try to get current week from Yahoo data
            week_info = self._extract_current_week_from_yahoo_data(yahoo_data)
            if week_info:
                season_context.update(week_info)
            else:
                # Fallback to estimated week
                season_context['current_week'] = self._estimate_current_week(current_date)
                
            return season_context
        except Exception as e:
            self.logger.error(f"Error extracting season context: {e}")
            return {}

    def _determine_season_phase(self, current_date: datetime) -> str:
        """Determine the current phase of the NFL season."""
        month = current_date.month
        
        if month in [1, 2]:
            return "Playoffs"
        elif month in [3, 4, 5, 6, 7]:
            return "Offseason"
        elif month in [8, 9]:
            return "Preseason"
        elif month in [10, 11, 12]:
            return "Regular Season"
        else:
            return "Unknown"

    def _extract_current_week_from_yahoo_data(self, yahoo_data: Dict) -> Optional[Dict[str, Any]]:
        """Extract current week information from Yahoo team matchups data."""
        try:
            if not yahoo_data or 'team_info' not in yahoo_data:
                return None
                
            league_key = yahoo_data['team_info'].get('league_key', '')
            if not league_key:
                return None
                
            # Look for team matchups file
            matchups_pattern = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'team_matchups', '*_raw_data.json'
            )
            matchups_files = glob.glob(matchups_pattern)
            
            if not matchups_files:
                return None
                
            latest_matchups = max(matchups_files, key=os.path.getctime)
            
            with open(latest_matchups, 'r') as f:
                matchups_data = json.load(f)
                
            season_context = matchups_data.get('season_context', {})
            current_week = season_context.get('current_week', 1)
            
            return {
                'current_week': current_week,
                'league_key': league_key
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting current week: {e}")
            return None

    def _estimate_current_week(self, current_date: datetime) -> int:
        """Estimate current week based on date."""
        # NFL regular season typically starts first week of September
        # This is a rough estimation
        if current_date.month < 9:
            return 1
        elif current_date.month == 9:
            return min(4, max(1, current_date.day // 7 + 1))
        elif current_date.month == 10:
            return min(8, 4 + (current_date.day // 7 + 1))
        elif current_date.month == 11:
            return min(12, 8 + (current_date.day // 7 + 1))
        elif current_date.month == 12:
            return min(17, 12 + (current_date.day // 7 + 1))
        else:
            return 17

    def _get_tank01_player_database(self) -> List[Dict[str, Any]]:
        """Get the Tank01 player database with caching."""
        if not hasattr(self, '_tank01_player_cache') or self._tank01_player_cache is None:
            try:
                self.logger.info("Loading Tank01 player database...")
                response = self.tank01_client.get_player_list()
                
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
        
        return self._tank01_player_cache

    def _match_player_to_tank01(self, yahoo_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Match a Yahoo player to Tank01 database using multiple strategies."""
        # Use cached player database
        tank01_players = self._get_tank01_player_database()
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
            player_info = self.tank01_client.get_player_info(yahoo_name, get_stats=True)
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

    def _extract_comprehensive_tank01_data(self, tank01_player: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive Tank01 data for a player."""
        try:
            player_id = tank01_player.get('playerID')
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
            
            # Get player-specific news
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
            
        except Exception as e:
            self.logger.error(f"Error extracting comprehensive data: {e}")
            return tank01_player

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
                team_news = self.tank01_client.get_news(fantasy_news=True, max_items=10, team_abv=team_abv)
                if team_news and 'body' in team_news:
                    news_articles = team_news['body'][:10]
                    self.logger.debug(f"Retrieved {len(news_articles)} team news articles for {team_abv} defense")
            else:
                # For regular players, get player-specific news
                player_news = self.tank01_client.get_news(fantasy_news=True, max_items=5, player_id=player_id)
                if player_news and 'body' in player_news:
                    news_articles = player_news['body'][:5]
                else:
                    # Fallback to team news if no player-specific news
                    team_news = self.tank01_client.get_news(fantasy_news=True, max_items=5, team_abv=team_abv)
                    if team_news and 'body' in team_news:
                        news_articles = team_news['body'][:5]
            
            self.logger.debug(f"Retrieved {len(news_articles)} news articles for {tank01_player.get('longName', 'Unknown')}")
            
        except Exception as e:
            self.logger.warning(f"Failed to get news for {tank01_player.get('longName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
        
        return news_articles

    def _get_player_game_stats(self, player_id: str) -> Dict[str, Any]:
        """Get player game statistics to infer injury status and performance."""
        try:
            game_stats = self.tank01_client.get_player_game_stats(player_id, season="2024")
            
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
                self._depth_charts_cache = self.tank01_client.get_depth_charts()
            
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
                self._teams_cache = self.tank01_client.get_nfl_teams(team_stats=True, top_performers=True)
            
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

    def extract_opponent_roster_data(self) -> Dict[str, Any]:
        """Extract comprehensive Tank01 data for opponent roster players."""
        self.logger.info("Starting Tank01 opponent roster data extraction")
        
        # Load Yahoo opponent roster players
        yahoo_players, yahoo_data = self._load_latest_yahoo_opponent_roster()
        if not yahoo_players:
            self.logger.error("No Yahoo opponent roster players loaded")
            return {"error": "No Yahoo opponent roster players loaded"}
        
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
            weekly_projections = self.tank01_client.get_weekly_projections(week=1, archive_season=2025)
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
        
        # Extract season context
        season_context = self._extract_season_context(yahoo_data)
        
        # Process each player
        matched_players = []
        unmatched_players = []
        
        for yahoo_player in yahoo_players:
            self.stats['players_processed'] += 1
            
            try:
                # Match to Tank01
                tank01_player = self._match_player_to_tank01(yahoo_player)
                
                if tank01_player:
                    self.stats['players_matched'] += 1
                    
                    # Extract comprehensive data
                    comprehensive_data = self._extract_comprehensive_tank01_data(tank01_player)
                    
                    matched_players.append({
                        'yahoo_data': yahoo_player,
                        'tank01_data': comprehensive_data,
                        'match_type': 'direct_id' if yahoo_player.get('player_id') else 'name_team'
                    })
                    
                    self.logger.info(f"Matched: {yahoo_player.get('name', {}).get('full', 'Unknown')}")
                else:
                    self.stats['players_unmatched'] += 1
                    unmatched_players.append(yahoo_player)
                    self.logger.warning(f"No Tank01 match: {yahoo_player.get('name', {}).get('full', 'Unknown')}")
                    
            except Exception as e:
                self.stats['errors'] += 1
                self.logger.error(f"Error processing player {yahoo_player.get('name', {}).get('full', 'Unknown')}: {e}")
        
        # Build final data structure
        result_data = {
            'extraction_metadata': {
                'script': 'tank01_opponent_roster.py',
                'extraction_timestamp': datetime.now().isoformat(),
                'opponent_name': yahoo_data.get('opponent_name', 'Unknown Opponent'),
                'opponent_team_key': yahoo_data.get('opponent_team_key', 'Unknown'),
                'execution_stats': self.stats
            },
            'season_context': season_context,
            'opponent_info': {
                'opponent_name': yahoo_data.get('opponent_name', 'Unknown Opponent'),
                'opponent_team_key': yahoo_data.get('opponent_team_key', 'Unknown'),
                'total_players': len(yahoo_players),
                'matched_players': len(matched_players),
                'unmatched_players': len(unmatched_players)
            },
            'matched_players': matched_players,
            'unmatched_players': unmatched_players
        }
        
        # Save data
        try:
            self._save_data(result_data)
            result_data['success'] = True
            result_data['output_files'] = self._get_output_files()
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            result_data['error'] = f"Error saving data: {e}"
        
        return result_data

    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save extracted data to files."""
        # Save raw JSON data
        raw_path = self.file_manager.save_raw_data('tank01', 'opponent_roster', data)
        self.logger.info(f"Raw data saved: {raw_path}")
        
        # Generate and save markdown report
        markdown_content = self._generate_markdown_report(data)
        markdown_path = self.file_manager.save_clean_data('tank01', 'opponent_roster', markdown_content)
        self.logger.info(f"Markdown report saved: {markdown_path}")

    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate markdown report from extracted data."""
        try:
            report = []
            
            # Header
            opponent_info = data.get('opponent_info', {})
            opponent_name = opponent_info.get('opponent_name', 'Unknown Opponent')
            total_players = opponent_info.get('total_players', 0)
            matched_players = opponent_info.get('matched_players', 0)
            unmatched_players = opponent_info.get('unmatched_players', 0)
            
            season_context = data.get('season_context', {})
            current_week = season_context.get('current_week', 'Unknown')
            nfl_season = season_context.get('nfl_season', 'Unknown')
            
            report.append(f"# Tank01 Opponent Roster Data - {opponent_name}")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**NFL Season:** {nfl_season}")
            report.append(f"**Current Week:** {current_week}")
            report.append(f"**Opponent:** {opponent_name}")
            report.append(f"**Total Players:** {total_players}")
            report.append(f"**Matched Players:** {matched_players}")
            report.append(f"**Unmatched Players:** {unmatched_players}")
            report.append(f"**Match Rate:** {(matched_players/total_players*100):.1f}%" if total_players > 0 else "N/A")
            report.append("")
            
            # Matched players
            matched = data.get('matched_players', [])
            if matched:
                report.append("## Matched Players")
                report.append("")
                
                for mp in matched:
                    yahoo_data = mp.get('yahoo_data', {})
                    tank01_data = mp.get('tank01_data', {})
                    match_type = mp.get('match_type', 'unknown')
                    
                    yahoo_name = yahoo_data.get('name', {}).get('full', 'Unknown')
                    yahoo_team = yahoo_data.get('team', 'N/A')
                    yahoo_pos = yahoo_data.get('display_position', 'N/A')
                    
                    report.append(f"### {yahoo_name} ({yahoo_team}, {yahoo_pos})")
                    report.append(f"**Match Type:** {match_type}")
                    report.append("")
                    
                    # Tank01 player details
                    report.append("#### Tank01 Player Info")
                    if tank01_data.get('longName'):
                        report.append(f"- **Name**: {tank01_data['longName']}")
                    if tank01_data.get('team'):
                        report.append(f"- **Team**: {tank01_data['team']}")
                    if tank01_data.get('pos'):
                        report.append(f"- **Position**: {tank01_data['pos']}")
                    if tank01_data.get('playerID'):
                        report.append(f"- **Tank01 ID**: {tank01_data['playerID']}")
                    if tank01_data.get('espnID'):
                        report.append(f"- **ESPN ID**: {tank01_data['espnID']}")
                    if tank01_data.get('sleeperBotID'):
                        report.append(f"- **Sleeper ID**: {tank01_data['sleeperBotID']}")
                    report.append("")
                    
                    # Recent news
                    recent_news = tank01_data.get('recent_news', [])
                    if recent_news:
                        report.append("#### Recent News")
                        for i, article in enumerate(recent_news[:3], 1):
                            if isinstance(article, dict):
                                title = article.get('title', 'No title')
                                link = article.get('link', '')
                                report.append(f"{i}. **{title}**")
                                if link:
                                    report.append(f"   - [Read More]({link})")
                        report.append("")
                    
                    # Game stats
                    game_stats = tank01_data.get('game_stats', {})
                    if game_stats:
                        report.append("#### Recent Performance")
                        injury_status = game_stats.get('injury_status', 'Unknown')
                        last_game = game_stats.get('last_game_played', 'N/A')
                        report.append(f"- **Injury Status**: {injury_status}")
                        report.append(f"- **Last Game**: {last_game}")
                        report.append("")
                    
                    # Depth chart
                    depth_chart = tank01_data.get('depth_chart', {})
                    if depth_chart and depth_chart.get('depth_position') != 'Unknown':
                        report.append("#### Depth Chart")
                        report.append(f"- **Position**: {depth_chart.get('depth_position', 'Unknown')}")
                        report.append(f"- **Rank**: {depth_chart.get('depth_rank', 'N/A')}")
                        report.append(f"- **Opportunity**: {depth_chart.get('opportunity', 'Unknown')}")
                        report.append("")
                    
                    # Fantasy projections
                    if 'fantasy_projections' in tank01_data:
                        projections = tank01_data['fantasy_projections']
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
                    
                    # Team context
                    team_context = tank01_data.get('team_context', {})
                    if team_context and team_context.get('team_performance') != 'Unknown':
                        report.append("#### Team Context")
                        report.append(f"- **Record**: {team_context.get('team_performance', 'Unknown')}")
                        report.append(f"- **Division**: {team_context.get('division', 'Unknown')}")
                        report.append(f"- **Fantasy Outlook**: {team_context.get('fantasy_outlook', 'Unknown')}")
                        report.append("")
                    
                    report.append("")
            
            # Unmatched players
            unmatched = data.get('unmatched_players', [])
            if unmatched:
                report.append("## Unmatched Yahoo Players (no Tank01 match)")
                report.append(f"**Showing:** {min(100, len(unmatched))} of {len(unmatched)}")
                report.append("")
                report.append("| Player | Team | Position |")
                report.append("|--------|------|----------|")
                for up in unmatched[:100]:
                    report.append(f"| {up.get('name', {}).get('full', 'Unknown')} | {up.get('team', 'N/A')} | {up.get('display_position', 'N/A')} |")
                if len(unmatched) > 100:
                    report.append("")
                    report.append(f"*... and {len(unmatched) - 100} more unmatched players*")
            
            return "\n".join(report)
        except Exception as e:
            self.logger.error(f"Error generating markdown report: {e}")
            return f"# Error generating report\n\nError: {e}"

    def _get_output_files(self) -> List[str]:
        """Get list of output files created."""
        # This would be implemented to return the actual file paths
        return ["opponent_roster_raw_data.json", "opponent_roster_clean.md"]


def main():
    """Main execution function."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        extractor = Tank01OpponentRosterExtractor()
        result = extractor.extract_opponent_roster_data()
        
        if result.get("success"):
            print(f"✅ Tank01 opponent roster extraction successful!")
            print(f"   Matched: {result['opponent_info']['matched_players']} players")
            print(f"   API calls: {result['extraction_metadata']['execution_stats']['api_calls']}")
            print(f"   Output files: {result['output_files']}")
        else:
            print(f"❌ Tank01 opponent roster extraction failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
