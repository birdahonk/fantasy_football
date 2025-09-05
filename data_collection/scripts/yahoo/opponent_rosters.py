#!/usr/bin/env python3
"""
Yahoo Fantasy Football - Opponent Team Rosters Data Extraction

This script extracts ALL data about all opponent teams in the user's fantasy football league
from the Yahoo Fantasy API. It outputs both clean markdown and raw JSON data.

Purpose: Clean, focused data extraction for all league team rosters
Output: Organized markdown file + raw API response JSON
Focus: Extract ALL data, no analysis or filtering
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from yahoo_auth import SimpleYahooAuth
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager

class OpponentRostersExtractor:
    """
    Extracts complete roster data for all opponent teams in the user's Yahoo Fantasy Football league.
    
    This class focuses on extracting ALL available data from the Yahoo API
    league teams and individual team roster endpoints without filtering or analysis.
    """
    
    def __init__(self):
        """Initialize the opponent rosters extractor."""
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize utilities
        self.yahoo_auth = SimpleYahooAuth()
        self.formatter = MarkdownFormatter()
        self.file_manager = DataFileManager()
        
        # Execution tracking
        self.execution_stats = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'errors': 0,
            'teams_processed': 0,
            'total_players': 0
        }
    
    def extract_all_opponent_rosters(self) -> Dict[str, Any]:
        """
        Extract complete roster data for all opponent teams in the league.
        
        Returns:
            Dict containing all extracted data and metadata
        """
        self.logger.info("🏈 Starting opponent rosters extraction...")
        
        try:
            # Step 1: Get user's league information
            league_info = self._get_league_info()
            if not league_info:
                raise Exception("Failed to get league information")
            
            league_key = league_info['league_key']
            self.logger.info(f"📋 Found league: {league_info['league_name']} ({league_key})")
            
            # Step 2: Get all teams in the league
            all_teams = self._get_all_league_teams(league_key)
            if not all_teams:
                raise Exception("Failed to get league teams")
            
            self.logger.info(f"👥 Found {len(all_teams)} teams in league")
            
            # Step 3: Extract roster for each team
            all_rosters = {}
            for team in all_teams:
                team_key = team['team_key']
                team_name = team['name']
                
                self.logger.info(f"🔍 Extracting roster for: {team_name} ({team_key})")
                
                roster_data = self._extract_team_roster(team_key, team)
                if roster_data:
                    all_rosters[team_key] = roster_data
                    self.execution_stats['teams_processed'] += 1
                    self.execution_stats['total_players'] += len(roster_data.get('players', []))
                else:
                    self.logger.warning(f"⚠️ Failed to extract roster for {team_name}")
                    self.execution_stats['errors'] += 1
            
            # Extract season context
            season_context = self._extract_season_context(league_info)
            
            # Step 4: Compile complete data
            complete_data = {
                'league_info': league_info,
                'season_context': season_context,
                'teams': all_teams,
                'rosters': all_rosters,
                'extraction_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_teams': len(all_teams),
                    'teams_processed': self.execution_stats['teams_processed'],
                    'total_players': self.execution_stats['total_players'],
                    'api_calls': self.execution_stats['api_calls'],
                    'errors': self.execution_stats['errors']
                }
            }
            
            self.logger.info(f"✅ Extraction complete: {self.execution_stats['teams_processed']} teams, {self.execution_stats['total_players']} total players")
            return complete_data
            
        except Exception as e:
            self.logger.error(f"❌ Error in opponent rosters extraction: {e}")
            self.execution_stats['errors'] += 1
            raise
    
    def _extract_season_context(self, league_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract season and week context from Yahoo data."""
        try:
            current_date = datetime.now()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'data_source': 'Yahoo Fantasy API',
                'verification_notes': []
            }
            
            # Extract season info from league info
            league_name = league_info.get('league_name', '')
            league_key = league_info.get('league_key', '')
            
            # Extract year from league name
            year_match = re.search(r'(\d{4})', league_name)
            if year_match:
                extracted_year = year_match.group(1)
                season_context['nfl_season'] = extracted_year
                season_context['verification_notes'].append(f"League name contains year: {extracted_year}")
            
            # Extract year from Yahoo league key (e.g., "461.l.595012")
            if league_key:
                key_parts = league_key.split('.')
                if len(key_parts) > 0:
                    yahoo_year = str(2025)  # Hardcoded for now
                    season_context['nfl_season'] = yahoo_year
                    season_context['verification_notes'].append(f"Yahoo league key code {key_parts[0]} indicates year: {yahoo_year}")
            
            season_context['yahoo_league_info'] = {
                'league_key': league_key,
                'league_name': league_name
            }
            
            # Try to get current week from Yahoo team matchups
            season_context['current_week'] = None
            season_context['week_info'] = {}
            
            try:
                current_week = self._extract_current_week_from_yahoo_data(league_key)
                if current_week:
                    season_context['current_week'] = current_week['week']
                    season_context['week_info'] = current_week
                    season_context['verification_notes'].append(f"Current week {current_week['week']} extracted from Yahoo team matchups API")
                else:
                    # Fallback: estimate from date
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
                self.logger.warning(f"Could not determine week: {e}")
                season_context['current_week'] = 1
                season_context['week_info'] = {
                    'week': 1,
                    'coverage_type': 'fallback',
                    'status': 'fallback',
                    'source': 'error_fallback'
                }
                season_context['verification_notes'].append("Could not determine current week - using fallback week 1")
            
            return season_context
            
        except Exception as e:
            self.logger.error(f"Error extracting season context: {e}")
            return {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': 'Unknown',
                'data_source': 'Yahoo Fantasy API',
                'verification_notes': [f"Error extracting season context: {e}"]
            }
    
    def _determine_season_phase(self, current_date: datetime) -> str:
        """Determine the current phase of the NFL season based on date."""
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
    
    def _extract_current_week_from_yahoo_data(self, league_key: str) -> Optional[Dict[str, Any]]:
        """Extract current week information from Yahoo team matchups data."""
        try:
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
            matchup_files = list(matchups_dir.glob("*_team_matchups_raw_data.json"))
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
    
    def _get_league_info(self) -> Optional[Dict[str, Any]]:
        """Get the user's league information using the exact same logic as my_roster.py."""
        try:
            self.logger.info("🔍 Getting user's league information...")
            
            # Use the same endpoint as my_roster.py to get league info
            response = self.yahoo_auth.make_request("users;use_login=1/games;game_keys=nfl/teams")
            self.execution_stats['api_calls'] += 1
            
            if not response or response.get('status') != 'success':
                self.logger.error("❌ Failed to get league discovery response")
                return None
            
            # Use the exact same logic as my_roster.py
            parsed_data = response.get('parsed', {})
            team_info = self._extract_team_info(parsed_data)
            
            if not team_info:
                self.logger.error("❌ Could not extract team information")
                return None
            
            # Convert to league info format
            league_info = {
                'league_key': team_info['league_key'],
                'league_name': team_info['league_name'],
                'team_key': team_info['team_key']
            }
            
            self.logger.info(f"✅ Found league: {league_info['league_name']} ({league_info['league_key']})")
            return league_info
            
        except Exception as e:
            self.logger.error(f"❌ Error getting league info: {e}")
            return None
    
    def _extract_team_info(self, parsed_data: Dict) -> Dict[str, str]:
        """
        Extract team and league information from discovery response.
        This is the exact same method as my_roster.py.
        """
        try:
            # Navigate Yahoo's complex JSON structure
            users = parsed_data.get('fantasy_content', {}).get('users', {})
            if not users:
                self.logger.error("No users section found")
                return {}
            
            # Get user data (this is a list, not a dict)
            user_data = users.get('0', {}).get('user', [])
            if not isinstance(user_data, list) or not user_data:
                self.logger.error(f"Invalid user_data structure: {type(user_data)}")
                return {}
            
            # Find the games section within the user data list
            games_section = None
            for section in user_data:
                if isinstance(section, dict) and 'games' in section:
                    games_section = section['games']
                    break
            
            if not games_section:
                self.logger.error("No games section found")
                return {}
            
            # Find the NFL game data (this is also a list)
            nfl_game_data = games_section.get('0', {}).get('game', [])
            if not isinstance(nfl_game_data, list) or not nfl_game_data:
                self.logger.error(f"Invalid game data structure: {type(nfl_game_data)}")
                return {}
            
            # Extract league info and find teams section
            teams_section = None
            league_info = {}
            
            for game_section in nfl_game_data:
                if isinstance(game_section, dict):
                    # Check for teams section
                    if 'teams' in game_section:
                        teams_section = game_section['teams']
                    
                    # Collect league-level info
                    for key in ['game_key', 'name', 'season']:
                        if key in game_section:
                            league_info[key] = game_section[key]
            
            if not teams_section:
                self.logger.error("No teams section found")
                return {}
            
            # Extract team data (team is a list of property objects)
            team_data = teams_section.get('0', {}).get('team', [])
            if not isinstance(team_data, list) or not team_data:
                self.logger.error(f"Invalid team data structure: {type(team_data)}")
                return {}
            
            # Parse team properties from the list of lists structure
            team_properties = {}
            
            # Handle nested list structure - team_data could be a list of lists
            if team_data and isinstance(team_data[0], list):
                # It's a list of lists, use the first inner list
                property_list = team_data[0]
            else:
                # It's a list of property objects
                property_list = team_data
            
            # Extract properties from the list
            for prop in property_list:
                if isinstance(prop, dict):
                    for key, value in prop.items():
                        team_properties[key] = value
            
            # Extract league key from team key
            team_key = team_properties.get('team_key', '')
            if not team_key:
                self.logger.error("No team_key found")
                return {}
            
            # Team key format: 461.l.595012.t.3
            # League key is: 461.l.595012
            parts = team_key.split('.')
            if len(parts) < 3:
                self.logger.error(f"Invalid team_key format: {team_key}")
                return {}
            
            league_key = '.'.join(parts[:3])
            league_name = league_info.get('name', 'Unknown League')
            team_name = team_properties.get('name', 'Unknown Team')
            
            return {
                'team_key': team_key,
                'team_name': team_name,
                'league_key': league_key,
                'league_name': league_name
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting team info: {e}")
            return {}
    
    def _get_all_league_teams(self, league_key: str) -> List[Dict[str, Any]]:
        """Get all teams in the league."""
        try:
            self.logger.info(f"🔍 Getting all teams for league: {league_key}")
            
            response = self.yahoo_auth.make_request(f"league/{league_key}/teams")
            self.execution_stats['api_calls'] += 1
            
            if not response or 'parsed' not in response:
                self.logger.error("❌ Invalid response structure")
                return []
            
            # Get the parsed Yahoo API response
            parsed_data = response['parsed']
            if 'fantasy_content' not in parsed_data:
                self.logger.error("❌ No fantasy_content in parsed response")
                return []
            
            fantasy_content = parsed_data['fantasy_content']
            league = fantasy_content.get('league', [])
            
            # Debug: Log the league structure
            self.logger.info(f"🔍 League structure: {type(league)}")
            if isinstance(league, list):
                self.logger.info(f"🔍 League list length: {len(league)}")
                for i, item in enumerate(league):
                    self.logger.info(f"🔍 League[{i}]: {type(item)} - {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
            
            teams = []
            for league_section in league:
                if isinstance(league_section, dict) and 'teams' in league_section:
                    teams_data = league_section['teams']
                    self.logger.info(f"🔍 Teams data keys: {list(teams_data.keys()) if isinstance(teams_data, dict) else 'Not a dict'}")
                    
                    # Handle numbered keys (0, 1, 2, etc.)
                    for key, team_data in teams_data.items():
                        if key.isdigit():  # Skip non-numeric keys
                            self.logger.info(f"🔍 Processing team {key}: {type(team_data)}")
                            self.logger.info(f"🔍 Team {key} keys: {list(team_data.keys()) if isinstance(team_data, dict) else 'Not a dict'}")
                            
                            # The team data might be directly in team_data, not in a 'team' key
                            if isinstance(team_data, dict):
                                # Check if team_data has team properties directly
                                if 'name' in team_data or 'team_key' in team_data:
                                    teams.append(team_data)
                                    self.logger.info(f"✅ Added team directly: {team_data.get('name', 'Unknown')}")
                                else:
                                    # Try the nested structure
                                    team_info = team_data.get('team', [])
                                    self.logger.info(f"🔍 Team {key} team_info type: {type(team_info)}")
                                    if isinstance(team_info, list):
                                        self.logger.info(f"🔍 Team {key} team_info length: {len(team_info)}")
                                        if team_info:
                                            self.logger.info(f"🔍 Team {key} team_info[0] type: {type(team_info[0])}")
                                        
                                        # Handle list-of-lists structure (same as my_roster.py)
                                        team_dict = {}
                                        for team_section in team_info:
                                            if isinstance(team_section, list):
                                                # It's a list of property objects
                                                for team_item in team_section:
                                                    if isinstance(team_item, dict):
                                                        team_dict.update(team_item)
                                            elif isinstance(team_section, dict):
                                                # It's a direct property object
                                                team_dict.update(team_section)
                                        
                                        if team_dict:
                                            teams.append(team_dict)
                                            self.logger.info(f"✅ Added team from nested: {team_dict.get('name', 'Unknown')}")
                                    elif isinstance(team_info, dict):
                                        # Team info is already a dict, use it directly
                                        teams.append(team_info)
                                        self.logger.info(f"✅ Added team from dict: {team_info.get('name', 'Unknown')}")
                                    else:
                                        self.logger.warning(f"⚠️ Could not extract team {key} data - unexpected type: {type(team_info)}")
            
            self.logger.info(f"✅ Found {len(teams)} teams in league")
            return teams
            
        except Exception as e:
            self.logger.error(f"❌ Error getting league teams: {e}")
            return []
    
    def _extract_team_roster(self, team_key: str, team_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract roster data for a specific team."""
        try:
            self.logger.info(f"🔍 Extracting roster for team: {team_key}")
            
            response = self.yahoo_auth.make_request(f"team/{team_key}/roster")
            self.execution_stats['api_calls'] += 1
            
            if not response or 'parsed' not in response:
                self.logger.error("❌ Invalid response structure")
                return None
            
            # Get the parsed Yahoo API response
            parsed_data = response['parsed']
            if 'fantasy_content' not in parsed_data:
                self.logger.error("❌ No fantasy_content in parsed response")
                return None
            
            # Debug: Log the roster response structure
            self.logger.info(f"🔍 Roster response keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
            if 'fantasy_content' in parsed_data:
                fantasy_content = parsed_data['fantasy_content']
                self.logger.info(f"🔍 Fantasy content keys: {list(fantasy_content.keys()) if isinstance(fantasy_content, dict) else 'Not a dict'}")
                if 'team' in fantasy_content:
                    team_data = fantasy_content['team']
                    self.logger.info(f"🔍 Team data type: {type(team_data)}, length: {len(team_data) if isinstance(team_data, list) else 'Not a list'}")
                    if isinstance(team_data, list):
                        for i, item in enumerate(team_data):
                            self.logger.info(f"🔍 Team[{i}]: {type(item)} - {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
            
            # Use the exact same logic as my_roster.py
            parsed_roster_data = parsed_data
            roster_players = self._extract_roster_players(parsed_roster_data)
            
            # Combine team info with extracted data
            complete_team_data = {
                'team_info': team_info,
                'players': roster_players,
                'roster_summary': {
                    'total_players': len(roster_players),
                    'starters': len([p for p in roster_players if p.get('selected_position') != 'BN']),
                    'bench_players': len([p for p in roster_players if p.get('selected_position') == 'BN'])
                }
            }
            
            self.logger.info(f"✅ Extracted {len(roster_players)} players for {team_info.get('name', 'Unknown Team')}")
            return complete_team_data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting roster for {team_key}: {e}")
            return None
    
    def _extract_roster_players(self, roster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player data from roster section using exact same logic as my_roster.py."""
        players = []
        
        try:
            # Navigate Yahoo's roster structure (exact same as my_roster.py)
            team_data = roster_data.get('fantasy_content', {}).get('team', [])
            if not team_data or len(team_data) < 2:
                self.logger.warning("Unexpected roster data structure")
                return players
            
            # Find roster section (usually index 1)
            roster_section = None
            for i, section in enumerate(team_data):
                self.logger.info(f"🔍 Checking team_data[{i}]: {type(section)}")
                if isinstance(section, dict) and 'roster' in section:
                    roster_section = section['roster']
                    self.logger.info(f"✅ Found roster section at index {i}")
                    break
            
            if not roster_section:
                self.logger.warning("No roster section found")
                return players
            
            self.logger.info(f"🔍 Roster section type: {type(roster_section)}")
            if isinstance(roster_section, dict):
                self.logger.info(f"🔍 Roster section keys: {list(roster_section.keys())}")
            
            # Extract players
            roster_data_0 = roster_section.get('0', {})
            self.logger.info(f"🔍 Roster data '0' type: {type(roster_data_0)}")
            if isinstance(roster_data_0, dict):
                self.logger.info(f"🔍 Roster data '0' keys: {list(roster_data_0.keys())}")
            
            roster_players = roster_data_0.get('players', {})
            self.logger.info(f"🔍 Roster players type: {type(roster_players)}")
            if isinstance(roster_players, dict):
                self.logger.info(f"🔍 Roster players keys: {list(roster_players.keys())}")
            
            if not roster_players:
                self.logger.warning("No roster players found")
                return players
            
            # Process each player
            player_index = 0
            while str(player_index) in roster_players:
                self.logger.info(f"🔍 Processing player {player_index}")
                player_data = roster_players[str(player_index)].get('player', [])
                self.logger.info(f"🔍 Player {player_index} data type: {type(player_data)}")
                if isinstance(player_data, list):
                    self.logger.info(f"🔍 Player {player_index} data length: {len(player_data)}")
                
                if not player_data:
                    self.logger.info(f"⚠️ No player data for index {player_index}")
                    player_index += 1
                    continue
                
                # Extract complete player information
                player_info = self._extract_complete_player_data(player_data)
                if player_info:
                    players.append(player_info)
                    self.logger.info(f"✅ Added player {player_index}: {player_info.get('name', {}).get('full', 'Unknown')}")
                else:
                    self.logger.warning(f"⚠️ Failed to extract player {player_index}")
                
                player_index += 1
            
            self.logger.info(f"Extracted {len(players)} players from roster")
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting roster players: {e}")
        
        return players
    
    def _extract_complete_player_data(self, player_data: List) -> Dict[str, Any]:
        """
        Extract ALL available data for a single player.
        This is the exact same method as my_roster.py.
        
        Args:
            player_data: Player data array from Yahoo API (list of lists)
            
        Returns:
            Dict with all available player information
        """
        if not player_data:
            return {}
        
        # Yahoo stores player data as list of lists: [properties_list, position_list]
        player_info = {}
        selected_position_info = {}
        
        # Process each section in the player data
        for section in player_data:
            if isinstance(section, list):
                # This is a list of property objects or position objects
                for item in section:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == 'selected_position':
                                # Handle selected position specially - it's an array with position info
                                if isinstance(value, list) and value:
                                    # Find the position object in the array
                                    for pos_item in value:
                                        if isinstance(pos_item, dict) and 'position' in pos_item:
                                            selected_position_info = pos_item
                                            break
                            else:
                                player_info[key] = value
            elif isinstance(section, dict):
                # Direct dict (fallback for other formats)
                for key, value in section.items():
                    if key == 'selected_position':
                        if isinstance(value, list) and value:
                            # Find the position object in the array
                            for pos_item in value:
                                if isinstance(pos_item, dict) and 'position' in pos_item:
                                    selected_position_info = pos_item
                                    break
                    else:
                        player_info[key] = value
        
        # Process name object if present
        if 'name' in player_info and isinstance(player_info['name'], dict):
            name_obj = player_info['name']
            player_info.update({
                'full_name': name_obj.get('full', ''),
                'first_name': name_obj.get('first', ''),
                'last_name': name_obj.get('last', ''),
                'ascii_first': name_obj.get('ascii_first', ''),
                'ascii_last': name_obj.get('ascii_last', '')
            })
        
        # Add selected position info
        player_info.update({
            'selected_position': selected_position_info.get('position', 'BN'),  # Default to bench if not set
            'selected_coverage_type': selected_position_info.get('coverage_type', ''),
            'selected_date': selected_position_info.get('date', '')
        })
        
        # Process eligible positions if present
        if 'eligible_positions' in player_info and isinstance(player_info['eligible_positions'], list):
            positions = []
            for pos in player_info['eligible_positions']:
                if isinstance(pos, dict) and 'position' in pos:
                    positions.append(pos['position'])
                elif isinstance(pos, str):  # Handle direct string positions
                    positions.append(pos)
            player_info['eligible_positions_list'] = positions
        
        # Process bye weeks if present
        if 'bye_weeks' in player_info and isinstance(player_info['bye_weeks'], dict):
            player_info['bye_week'] = player_info['bye_weeks'].get('week', '')
        
        # Process headshot if present
        if 'headshot' in player_info and isinstance(player_info['headshot'], dict):
            player_info['headshot_url'] = player_info['headshot'].get('url', '')
        
        # Log successful parsing for debugging
        player_name = player_info.get('full_name', 'Unknown Player')
        self.logger.debug(f"Parsed player: {player_name}, Position: {player_info.get('selected_position', 'Unknown')}")
        
        return player_info
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save extracted data to files."""
        try:
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save raw JSON data
            raw_path = self.file_manager.save_raw_data("yahoo", "opponent_rosters", data, timestamp)
            
            # Generate and save markdown report
            markdown_content = self._generate_markdown_report(data)
            markdown_path = self.file_manager.save_clean_data("yahoo", "opponent_rosters", markdown_content, timestamp)
            
            # Save execution log
            execution_log = {
                'script': 'opponent_rosters.py',
                'timestamp': timestamp,
                'execution_stats': self.execution_stats,
                'files_created': [raw_path, markdown_path]
            }
            self.file_manager.save_execution_log("yahoo", "opponent_rosters", execution_log, timestamp)
            
            self.logger.info(f"✅ Data saved successfully")
            self.logger.info(f"📁 Raw data: {raw_path}")
            self.logger.info(f"📄 Markdown: {markdown_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving data: {e}")
            raise
    
    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate clean markdown report from extracted data."""
        try:
            report = []
            
            # Header
            league_info = data.get('league_info', {})
            report.append(f"# Opponent Team Rosters - {league_info.get('league_name', 'Unknown League')}")
            report.append(f"**League Key:** {league_info.get('league_key', 'Unknown')}")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Summary
            metadata = data.get('extraction_metadata', {})
            report.append("## 📊 Extraction Summary")
            report.append(f"- **Total Teams:** {metadata.get('total_teams', 0)}")
            report.append(f"- **Teams Processed:** {metadata.get('teams_processed', 0)}")
            report.append(f"- **Total Players:** {metadata.get('total_players', 0)}")
            report.append(f"- **API Calls:** {metadata.get('api_calls', 0)}")
            report.append(f"- **Errors:** {metadata.get('errors', 0)}")
            report.append("")
            
            # Add season and week context
            season_context = data.get('season_context', {})
            if season_context:
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
            
            # League Teams Overview
            teams = data.get('teams', [])
            if teams:
                report.append("## 👥 League Teams Overview")
                report.append("| Team Name | Manager | Team Key | Previous Rank |")
                report.append("|-----------|---------|----------|---------------|")
                
                for team in teams:
                    name = team.get('name', 'Unknown')
                    manager = team.get('managers', [{}])[0].get('manager', {}).get('nickname', 'Unknown')
                    team_key = team.get('team_key', 'Unknown')
                    rank = team.get('previous_rank', 'N/A')
                    report.append(f"| {name} | {manager} | {team_key} | {rank} |")
                report.append("")
            
            # Individual Team Rosters
            rosters = data.get('rosters', {})
            if rosters:
                report.append("## 🏈 Team Rosters")
                
                for team_key, roster_data in rosters.items():
                    team_info = roster_data.get('team_info', {})
                    team_name = team_info.get('name', 'Unknown Team')
                    players = roster_data.get('players', [])
                    summary = roster_data.get('roster_summary', {})
                    
                    report.append(f"### {team_name}")
                    report.append(f"**Team Key:** {team_key}")
                    report.append(f"**Manager:** {team_info.get('managers', [{}])[0].get('manager', {}).get('nickname', 'Unknown')}")
                    report.append(f"**Total Players:** {summary.get('total_players', 0)}")
                    report.append(f"**Starters:** {summary.get('starters', 0)}")
                    report.append(f"**Bench:** {summary.get('bench_players', 0)}")
                    report.append("")
                    
                    if players:
                        # Starting Lineup
                        starters = [p for p in players if p.get('selected_position') != 'BN']
                        if starters:
                            report.append("#### 🎯 Starting Lineup")
                            report.append("| Position | Player | Team | Bye Week |")
                            report.append("|----------|--------|------|----------|")
                            
                            for player in starters:
                                name = player.get('name', {}).get('full', 'Unknown')
                                position = player.get('selected_position', 'Unknown')
                                team = player.get('editorial_team_abbr', 'Unknown')
                                bye = player.get('bye_week', 'N/A')
                                report.append(f"| {position} | {name} | {team} | {bye} |")
                            report.append("")
                        
                        # Bench Players
                        bench = [p for p in players if p.get('selected_position') == 'BN']
                        if bench:
                            report.append("#### 🪑 Bench Players")
                            report.append("| Position | Player | Team | Bye Week |")
                            report.append("|----------|--------|------|----------|")
                            
                            for player in bench:
                                name = player.get('name', {}).get('full', 'Unknown')
                                position = player.get('display_position', 'Unknown')
                                team = player.get('editorial_team_abbr', 'Unknown')
                                bye = player.get('bye_week', 'N/A')
                                report.append(f"| {position} | {name} | {team} | {bye} |")
                            report.append("")
                        
                        # Complete Roster Details
                        report.append("#### 📋 Complete Roster Details")
                        report.append("| Player | Position | Selected Pos | Team | Bye Week | Player Key |")
                        report.append("|--------|----------|--------------|------|----------|------------|")
                        
                        for player in players:
                            name = player.get('name', {}).get('full', 'Unknown')
                            position = player.get('display_position', 'Unknown')
                            selected_pos = player.get('selected_position', 'Unknown')
                            team = player.get('editorial_team_abbr', 'Unknown')
                            bye = player.get('bye_week', 'N/A')
                            player_key = player.get('player_key', 'Unknown')
                            report.append(f"| {name} | {position} | {selected_pos} | {team} | {bye} | {player_key} |")
                        report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating markdown report: {e}")
            return f"# Error generating report\n\nError: {e}"

def main():
    """Main execution function."""
    try:
        extractor = OpponentRostersExtractor()
        
        # Extract all opponent roster data
        data = extractor.extract_all_opponent_rosters()
        
        # Save the data
        extractor.save_data(data)
        
        # Print summary
        stats = extractor.execution_stats
        print(f"\n🎉 Opponent Rosters Extraction Complete!")
        print(f"📊 Teams Processed: {stats['teams_processed']}")
        print(f"👥 Total Players: {stats['total_players']}")
        print(f"🔗 API Calls: {stats['api_calls']}")
        print(f"❌ Errors: {stats['errors']}")
        print(f"⏱️ Execution Time: {datetime.now() - stats['start_time']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
