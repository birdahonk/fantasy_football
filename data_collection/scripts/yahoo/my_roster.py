#!/usr/bin/env python3
"""
Yahoo Fantasy Football - My Team Roster Data Extraction

This script extracts ALL data about the user's fantasy football team roster
from the Yahoo Fantasy API. It outputs both clean markdown and raw JSON data.

Purpose: Clean, focused data extraction for my team roster
Output: Organized markdown file + raw API response JSON
Focus: Extract ALL data, no analysis or filtering
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from yahoo_auth import SimpleYahooAuth
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager

class MyRosterExtractor:
    """
    Extracts complete roster data for the user's Yahoo Fantasy Football team.
    
    This class focuses on extracting ALL available data from the Yahoo API
    roster endpoint without filtering or analysis.
    """
    
    def __init__(self):
        """Initialize the roster extractor."""
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
            'api_calls_made': 0,
            'errors_encountered': 0,
            'players_extracted': 0,
            'data_completeness': {}
        }
        
        self.logger.info("My Roster Extractor initialized")
    
    def extract_roster_data(self) -> Dict[str, Any]:
        """
        Extract complete roster data from Yahoo Fantasy API.
        
        Returns:
            Dict containing all extracted roster data
        """
        try:
            self.logger.info("Starting roster data extraction")
            
            # Step 1: Discover user's leagues and teams
            self.logger.info("Discovering leagues and teams...")
            league_data = self.yahoo_auth.discover_leagues_and_teams()
            self.execution_stats['api_calls_made'] += 1
            
            if not league_data or league_data.get('status') != 'success':
                self.logger.error("Failed to discover leagues and teams")
                self.execution_stats['errors_encountered'] += 1
                return {}
            
            # Extract team and league information
            team_info = self._extract_team_info(league_data.get('parsed', {}))
            if not team_info:
                self.logger.error("Could not extract team information")
                self.execution_stats['errors_encountered'] += 1
                return {}
            
            self.logger.info(f"Found team: {team_info['team_name']} in league: {team_info['league_name']}")
            
            # Step 2: Get detailed roster data
            self.logger.info("Retrieving detailed roster...")
            roster_data = self.yahoo_auth.get_team_roster(team_info['team_key'])
            self.execution_stats['api_calls_made'] += 1
            
            if not roster_data or roster_data.get('status') != 'success':
                self.logger.error("Failed to retrieve roster data")
                self.execution_stats['errors_encountered'] += 1
                return {}
            
            # Get current week and season context
            season_context = self._extract_season_context(team_info, roster_data.get('parsed', {}))
            
            # Combine all data
            complete_data = {
                'team_info': team_info,
                'roster_raw': roster_data.get('parsed', {}),
                'roster_players': self._extract_players(roster_data.get('parsed', {})),
                'season_context': season_context,
                'extraction_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'api_calls_made': self.execution_stats['api_calls_made'],
                    'data_source': 'yahoo_fantasy_api'
                }
            }
            
            self.execution_stats['players_extracted'] = len(complete_data.get('roster_players', []))
            self.logger.info(f"Successfully extracted data for {self.execution_stats['players_extracted']} players")
            
            return complete_data
            
        except Exception as e:
            self.logger.error(f"Error during roster data extraction: {e}")
            self.execution_stats['errors_encountered'] += 1
            return {}
    
    def _extract_team_info(self, parsed_data: Dict) -> Dict[str, str]:
        """
        Extract team and league information from discovery response.
        
        Args:
            parsed_data: Parsed discovery response
            
        Returns:
            Dict with team_key, team_name, league_key, league_name
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
            
            # Validate we found the user's team
            if team_properties.get('is_owned_by_current_login') != 1:
                self.logger.error("Team is not owned by current user")
                return {}
            
            # Extract team key to determine league key
            team_key = team_properties.get('team_key', '')
            league_key = ''
            if team_key:
                # League key format: {game_id}.l.{league_id} (from team_key {game_id}.l.{league_id}.t.{team_id})
                parts = team_key.split('.t.')
                if len(parts) >= 1:
                    league_key = parts[0]
            
            result = {
                'team_key': team_key,
                'team_name': team_properties.get('name', ''),
                'team_id': team_properties.get('team_id', ''),
                'league_key': league_key,
                'league_name': f"Fantasy League ({league_info.get('season', '2025')})"
            }
            
            self.logger.info(f"Successfully extracted team info: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting team info: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def _extract_season_context(self, team_info: Dict, roster_data: Dict) -> Dict[str, Any]:
        """
        Extract season and week context from Yahoo data.
        
        Args:
            team_info: Team information dict
            roster_data: Raw roster data from Yahoo API
            
        Returns:
            Dict with season context information
        """
        try:
            current_date = datetime.now()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'data_source': 'Yahoo Fantasy API',
                'league_info': {
                    'league_key': team_info.get('league_key', ''),
                    'league_name': team_info.get('league_name', ''),
                    'team_key': team_info.get('team_key', '')
                },
                'current_week': None,
                'week_info': {},
                'verification_notes': []
            }
            
            # Extract season from league name or team key
            league_name = team_info.get('league_name', '')
            team_key = team_info.get('team_key', '')
            
            # Look for year in league name
            import re
            year_match = re.search(r'(\d{4})', league_name)
            if year_match:
                extracted_year = year_match.group(1)
                season_context['nfl_season'] = extracted_year
                season_context['verification_notes'].append(f"League name contains year: {extracted_year}")
            
            # Extract year from team key (format: 461.l.595012.t.3)
            if team_key and '.' in team_key:
                key_parts = team_key.split('.')
                if len(key_parts) >= 2 and key_parts[0].isdigit():
                    yahoo_code = int(key_parts[0])
                    # Yahoo uses 461 for 2025, 460 for 2024, etc.
                    yahoo_year = str(2025)  # For now, assume 2025 based on 461
                    season_context['nfl_season'] = yahoo_year
                    season_context['verification_notes'].append(f"Yahoo team key code {yahoo_code} indicates year: {yahoo_year}")
            
            # Extract current week from Yahoo API data
            try:
                # First, try to get week from team matchups data (most reliable)
                current_week = self._extract_current_week_from_yahoo_data(team_info.get('league_key', ''))
                
                if current_week:
                    season_context['current_week'] = current_week['week']
                    season_context['week_info'] = current_week
                    season_context['verification_notes'].append(f"Current week {current_week['week']} extracted from Yahoo team matchups API")
                else:
                    # Fallback: try to extract from roster data
                    fantasy_content = roster_data.get('fantasy_content', {})
                    team_data = fantasy_content.get('team', [])
                    
                    if isinstance(team_data, list) and len(team_data) > 0:
                        for item in team_data:
                            if isinstance(item, dict) and 'roster' in item:
                                roster_info = item['roster']
                                if isinstance(roster_info, list) and len(roster_info) > 0:
                                    for roster_item in roster_info:
                                        if isinstance(roster_item, dict) and 'coverage_type' in roster_item:
                                            coverage = roster_item.get('coverage_type', '')
                                            if 'week' in coverage.lower():
                                                week_num = roster_item.get('week', '1')
                                                season_context['current_week'] = int(week_num)
                                                season_context['week_info'] = {
                                                    'week': int(week_num),
                                                    'coverage_type': coverage,
                                                    'status': roster_item.get('status', 'unknown'),
                                                    'source': 'roster_data'
                                                }
                                                season_context['verification_notes'].append(f"Current week {week_num} extracted from roster data")
                                                break
                    
                    # Final fallback: estimate from date
                    if season_context['current_week'] is None:
                        current_date = datetime.now()
                        season_start = datetime(current_date.year, 9, 1)
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
                self.logger.warning(f"Could not extract week info: {e}")
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
                'data_source': 'Yahoo Fantasy API',
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
    
    def _extract_current_week_from_yahoo_data(self, league_key: str) -> Optional[Dict[str, Any]]:
        """
        Extract current week information from Yahoo team matchups data.
        
        Args:
            league_key: Yahoo league key (e.g., "461.l.595012")
            
        Returns:
            Dict with week information or None if not found
        """
        try:
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
    
    def _extract_players(self, roster_data: Dict) -> List[Dict[str, Any]]:
        """
        Extract all player data from roster response.
        
        Args:
            roster_data: Raw roster response data
            
        Returns:
            List of player dictionaries with ALL available data
        """
        players = []
        
        try:
            # Navigate Yahoo's roster structure
            team_data = roster_data.get('fantasy_content', {}).get('team', [])
            if not team_data or len(team_data) < 2:
                self.logger.warning("Unexpected roster data structure")
                return players
            
            # Find roster section (usually index 1)
            roster_section = None
            for section in team_data:
                if isinstance(section, dict) and 'roster' in section:
                    roster_section = section['roster']
                    break
            
            if not roster_section:
                self.logger.warning("No roster section found")
                return players
            
            # Extract players
            roster_players = roster_section.get('0', {}).get('players', {})
            if not roster_players:
                return players
            
            # Process each player
            player_index = 0
            while str(player_index) in roster_players:
                player_data = roster_players[str(player_index)].get('player', [])
                if not player_data:
                    player_index += 1
                    continue
                
                # Extract complete player information
                player_info = self._extract_complete_player_data(player_data)
                if player_info:
                    players.append(player_info)
                
                player_index += 1
            
            self.logger.info(f"Extracted {len(players)} players from roster")
            
        except Exception as e:
            self.logger.error(f"Error extracting players: {e}")
        
        return players
    
    def _extract_complete_player_data(self, player_data: List) -> Dict[str, Any]:
        """
        Extract ALL available data for a single player.
        
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
    
    def generate_clean_markdown(self, roster_data: Dict[str, Any]) -> str:
        """
        Generate clean, organized markdown from roster data.
        
        Args:
            roster_data: Complete roster data
            
        Returns:
            Formatted markdown string
        """
        # Create header
        team_name = roster_data.get('team_info', {}).get('team_name', 'My Team')
        league_name = roster_data.get('team_info', {}).get('league_name', 'Fantasy League')
        
        markdown = self.formatter.create_header(
            f"{team_name} - Current Roster",
            f"Yahoo Fantasy Football - {league_name}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Season and week context section
        season_context = roster_data.get('season_context', {})
        markdown += self._format_season_context(season_context)
        
        # Team information section
        team_info = roster_data.get('team_info', {})
        markdown += self.formatter.format_team_info(team_info, "Team Information")
        
        # Roster players section
        players = roster_data.get('roster_players', [])
        
        # Separate starters and bench
        starters = [p for p in players if p.get('selected_position', 'BN') != 'BN']
        bench = [p for p in players if p.get('selected_position', 'BN') == 'BN']
        
        # Format starting lineup
        if starters:
            markdown += self._format_player_table(starters, "Starting Lineup")
        
        # Format bench players
        if bench:
            markdown += self._format_player_table(bench, "Bench Players")
        
        # All players summary table
        if players:
            markdown += self._format_complete_player_table(players, "Complete Roster Details")
        
        # Add extraction summary
        stats = self.execution_stats.copy()
        stats['total_players'] = len(players)
        stats['starters'] = len(starters)
        stats['bench_players'] = len(bench)
        stats['end_time'] = datetime.now()
        stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        markdown += self.formatter.create_summary_footer(stats)
        
        return markdown
    
    def _format_season_context(self, season_context: Dict[str, Any]) -> str:
        """Format season and week context as markdown."""
        if not season_context:
            return ""
        
        markdown = "## Season & Week Context\n\n"
        markdown += f"- **NFL Season:** {season_context.get('nfl_season', 'Unknown')}\n"
        markdown += f"- **Current Week:** {season_context.get('current_week', 'Unknown')}\n"
        markdown += f"- **Season Phase:** {season_context.get('season_phase', 'Unknown')}\n"
        markdown += f"- **Data Source:** {season_context.get('data_source', 'Unknown')}\n"
        
        week_info = season_context.get('week_info', {})
        if week_info:
            markdown += f"- **Week Start:** {week_info.get('week_start', 'Unknown')}\n"
            markdown += f"- **Week End:** {week_info.get('week_end', 'Unknown')}\n"
            markdown += f"- **Week Status:** {week_info.get('status', 'Unknown')}\n"
            markdown += f"- **Week Source:** {week_info.get('source', 'Unknown')}\n"
        
        verification_notes = season_context.get('verification_notes', [])
        if verification_notes:
            markdown += "\n### Verification Notes\n"
            for note in verification_notes:
                markdown += f"- {note}\n"
        
        markdown += "\n---\n\n"
        return markdown
    
    def _format_player_table(self, players: List[Dict], title: str) -> str:
        """Format a group of players as a markdown table."""
        if not players:
            return f"## {title}\n\nNo players found.\n\n"
        
        headers = ["Name", "Position", "NFL Team", "Selected Pos", "Status", "Bye Week", "Player ID"]
        rows = []
        
        for player in players:
            name = player.get('full_name', 'Unknown')
            position = player.get('display_position', player.get('primary_position', ''))
            nfl_team = player.get('editorial_team_abbr', '')
            selected_pos = player.get('selected_position', '')
            status = player.get('status_full', player.get('status', ''))
            bye_week = player.get('bye_week', '')
            player_id = player.get('player_id', player.get('player_key', ''))
            
            rows.append([name, position, nfl_team, selected_pos, status, bye_week, player_id])
        
        table = self.formatter.format_table(headers, rows)
        return self.formatter.create_section(title, table)
    
    def _format_complete_player_table(self, players: List[Dict], title: str) -> str:
        """Format complete player details table."""
        if not players:
            return f"## {title}\n\nNo players found.\n\n"
        
        headers = ["Name", "Pos", "Team", "Status", "Injury", "Eligible Pos", "Uniform #", "Player Key"]
        rows = []
        
        for player in players:
            name = player.get('full_name', 'Unknown')
            position = player.get('display_position', '')
            nfl_team = player.get('editorial_team_abbr', '')
            status = player.get('status', '')
            injury = player.get('injury_note', '')
            eligible_pos = ', '.join(player.get('eligible_positions_list', []))
            uniform_num = player.get('uniform_number', '')
            player_key = player.get('player_key', '')
            
            rows.append([name, position, nfl_team, status, injury, eligible_pos, uniform_num, player_key])
        
        table = self.formatter.format_table(headers, rows)
        return self.formatter.create_section(title, table)
    
    def save_data(self, roster_data: Dict[str, Any], timestamp: str) -> Dict[str, str]:
        """
        Save both clean markdown and raw JSON data.
        
        Args:
            roster_data: Complete roster data
            timestamp: Timestamp for file naming
            
        Returns:
            Dict with file paths
        """
        try:
            # Generate clean markdown
            clean_markdown = self.generate_clean_markdown(roster_data)
            
            # Save clean data
            clean_file = self.file_manager.save_clean_data(
                "yahoo", "my_roster", clean_markdown, timestamp
            )
            
            # Save raw data
            raw_file = self.file_manager.save_raw_data(
                "yahoo", "my_roster", roster_data, timestamp
            )
            
            # Save execution log
            log_file = self.file_manager.save_execution_log(
                "yahoo", "my_roster", self.execution_stats, timestamp
            )
            
            self.logger.info("All data files saved successfully")
            
            return {
                'clean_file': clean_file,
                'raw_file': raw_file,
                'log_file': log_file
            }
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            self.execution_stats['errors_encountered'] += 1
            return {}
    
    def run(self) -> Dict[str, str]:
        """
        Run the complete roster extraction process.
        
        Returns:
            Dict with file paths of saved data
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("YAHOO FANTASY FOOTBALL - MY ROSTER EXTRACTION")
            self.logger.info("=" * 60)
            
            # Check authentication
            if not self.yahoo_auth.is_authenticated():
                self.logger.error("Yahoo authentication failed")
                return {}
            
            # Extract roster data
            roster_data = self.extract_roster_data()
            if not roster_data:
                self.logger.error("Failed to extract roster data")
                return {}
            
            # Generate timestamp
            timestamp = self.file_manager.generate_timestamp()
            
            # Save all data
            file_paths = self.save_data(roster_data, timestamp)
            
            # Final statistics
            self.execution_stats['end_time'] = datetime.now()
            self.execution_stats['duration'] = (
                self.execution_stats['end_time'] - self.execution_stats['start_time']
            ).total_seconds()
            
            self.logger.info("=" * 60)
            self.logger.info("EXTRACTION COMPLETE")
            self.logger.info(f"Players extracted: {self.execution_stats['players_extracted']}")
            self.logger.info(f"API calls made: {self.execution_stats['api_calls_made']}")
            self.logger.info(f"Duration: {self.execution_stats['duration']:.2f} seconds")
            self.logger.info(f"Errors: {self.execution_stats['errors_encountered']}")
            self.logger.info("=" * 60)
            
            if file_paths.get('clean_file'):
                print(f"\n✅ CLEAN DATA: {file_paths['clean_file']}")
            if file_paths.get('raw_file'):
                print(f"✅ RAW DATA: {file_paths['raw_file']}")
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Fatal error during extraction: {e}")
            return {}

def main():
    """Main entry point for the roster extraction script."""
    extractor = MyRosterExtractor()
    return extractor.run()

if __name__ == "__main__":
    result = main()
    if result:
        print("🏈 My Roster extraction completed successfully!")
    else:
        print("❌ My Roster extraction failed!")
        sys.exit(1)
