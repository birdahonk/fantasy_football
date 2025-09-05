#!/usr/bin/env python3
"""
Yahoo Fantasy Football - Available Players Data Extraction

This script extracts ALL available players data from the Yahoo Fantasy API.
It includes pagination to get the complete player list and extracts multiple sections:
- Available Players (complete list with pagination)
- Injury Reports (players with injury notes)
- Who's Hot (trending players)
- Top Available Players (sorted by Yahoo Overall Rank)

Purpose: Clean, focused data extraction for available players
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

class AvailablePlayersExtractor:
    """
    Extracts complete available players data from Yahoo Fantasy Football API.
    
    This class focuses on extracting ALL available data from the Yahoo API
    players endpoint with pagination and multiple sections.
    """
    
    def __init__(self):
        """Initialize the available players extractor."""
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
            'players_extracted': 0,
            'pages_processed': 0
        }
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        Extract all available players data from Yahoo Fantasy API.
        
        Returns:
            Dict containing all extracted data
        """
        self.logger.info("🚀 Starting Available Players Data Extraction")
        
        try:
            # Get league info first
            league_info = self._get_league_info()
            if not league_info:
                self.logger.error("❌ Failed to get league info")
                return {}
            
            league_key = league_info.get('league_key', '')
            if not league_key:
                self.logger.error("❌ No league key found")
                return {}
            
            self.logger.info(f"✅ Found league: {league_info.get('league_name', 'Unknown')} ({league_key})")
            
            # Extract all available players with pagination
            all_players = self._extract_all_available_players(league_key)
            
            # Organize players into sections
            organized_data = self._organize_players_into_sections(all_players)
            
            # Extract season context
            season_context = self._extract_season_context(league_info)
            
            # Add metadata
            result = {
                'extraction_metadata': {
                    'league_info': league_info,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'total_players': len(all_players),
                    'execution_stats': self.execution_stats
                },
                'season_context': season_context,
                'available_players': organized_data['available_players'],
                'injury_reports': organized_data['injury_reports'],
                'whos_hot': organized_data['whos_hot'],
                'top_available': organized_data['top_available'],
                'all_players': all_players  # Complete list for reference
            }
            
            # Calculate execution time
            execution_time = (datetime.now() - self.execution_stats['start_time']).total_seconds()
            self.execution_stats['execution_time'] = execution_time
            
            self.logger.info(f"✅ Extraction complete: {len(all_players)} players, {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error in extract_all_data: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.execution_stats['errors'] += 1
            return {}
    
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
    
    def _get_league_info(self) -> Dict[str, Any]:
        """
        Get league information from user's team.
        
        Returns:
            Dict with league information
        """
        try:
            self.logger.info("🔍 Getting league information")
            
            # Get user's team info first
            response = self.yahoo_auth.make_request("users;use_login=1/games;game_keys=nfl/teams")
            self.execution_stats['api_calls'] += 1
            
            if not response or 'parsed' not in response:
                self.logger.error("❌ Invalid response structure")
                return {}
            
            # Get the parsed Yahoo API response
            parsed_data = response['parsed']
            if 'fantasy_content' not in parsed_data:
                self.logger.error("❌ No fantasy_content in parsed response")
                return {}
            
            fantasy_content = parsed_data['fantasy_content']
            users = fantasy_content.get('users', {})
            

            
            if not users:
                self.logger.error("❌ No users data found")
                return {}
            
            # Get user data (this is a list, not a dict)
            user_data = users.get('0', {}).get('user', [])
            if not isinstance(user_data, list) or not user_data:
                self.logger.error(f"❌ Invalid user_data structure: {type(user_data)}")
                return {}
            
            # Find the games section within the user data list
            games_section = None
            for section in user_data:
                if isinstance(section, dict) and 'games' in section:
                    games_section = section['games']
                    break
            
            if not games_section:
                self.logger.error("❌ No games section found")
                return {}
            
            # Find the NFL game data (this is also a list)
            nfl_game_data = games_section.get('0', {}).get('game', [])
            if not isinstance(nfl_game_data, list) or not nfl_game_data:
                self.logger.error(f"❌ Invalid game data structure: {type(nfl_game_data)}")
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
                self.logger.error("❌ No teams section found")
                return {}
            
            # Extract team data (team is a list of property objects)
            team_data = teams_section.get('0', {}).get('team', [])
            if not isinstance(team_data, list) or not team_data:
                self.logger.error(f"❌ Invalid team data structure: {type(team_data)}")
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
                self.logger.error("❌ Team is not owned by current user")
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
            
            self.logger.info(f"✅ Successfully extracted team info: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error getting league info: {e}")
            return {}
    
    def _extract_all_available_players(self, league_key: str) -> List[Dict[str, Any]]:
        """
        Extract all available players with pagination.
        
        Args:
            league_key: League key for API calls
            
        Returns:
            List of all available players
        """
        all_players = []
        start = 0
        count = 25  # Yahoo's default page size
        total_players = None
        
        self.logger.info(f"🔍 Starting pagination for league: {league_key}")
        
        while True:
            try:
                self.logger.info(f"📄 Fetching players {start}-{start + count - 1}")
                
                # Make API request with pagination
                endpoint = f"league/{league_key}/players;position=;status=A;sort=OR;start={start};count={count}"
                response = self.yahoo_auth.make_request(endpoint)
                self.execution_stats['api_calls'] += 1
                self.execution_stats['pages_processed'] += 1
                
                if not response or 'parsed' not in response:
                    self.logger.error(f"❌ Invalid response for page {start}")
                    break
                
                # Get the parsed Yahoo API response
                parsed_data = response['parsed']
                if 'fantasy_content' not in parsed_data:
                    self.logger.error(f"❌ No fantasy_content for page {start}")
                    break
                
                fantasy_content = parsed_data['fantasy_content']
                league = fantasy_content.get('league', [])
                
                if not league or len(league) < 2:
                    self.logger.error(f"❌ Unexpected league structure for page {start}")
                    break
                
                # Find players section
                players_section = None
                for section in league:
                    if isinstance(section, dict) and 'players' in section:
                        players_section = section['players']
                        break
                
                if not players_section:
                    self.logger.error(f"❌ No players section for page {start}")
                    break
                
                # Get pagination info
                if total_players is None:
                    total_players = int(players_section.get('total', 0))
                    self.logger.info(f"📊 Total players available: {total_players}")
                    
                    # If total is 0, we might need to continue pagination until we get no more players
                    if total_players == 0:
                        self.logger.info("📊 Total count is 0, will continue pagination until no more players")
                
                # Extract players from this page
                page_players = self._extract_players_from_page(players_section)
                all_players.extend(page_players)
                
                self.logger.info(f"✅ Page {start//count + 1}: {len(page_players)} players extracted")
                
                # Check if we've got all players
                if total_players > 0 and len(all_players) >= total_players:
                    break
                elif len(page_players) < count:
                    # No more players available
                    break
                
                start += count
                
            except Exception as e:
                self.logger.error(f"❌ Error processing page {start}: {e}")
                self.execution_stats['errors'] += 1
                break
        
        self.execution_stats['players_extracted'] = len(all_players)
        self.logger.info(f"✅ Pagination complete: {len(all_players)} total players extracted")
        
        return all_players
    
    def _extract_players_from_page(self, players_section: Dict) -> List[Dict[str, Any]]:
        """
        Extract players from a single page response.
        
        Args:
            players_section: Players section from API response
            
        Returns:
            List of player dictionaries
        """
        players = []
        
        try:
            # Process numbered player keys (0, 1, 2, etc.)
            player_index = 0
            while str(player_index) in players_section:
                player_data = players_section[str(player_index)].get('player', [])
                if not player_data:
                    player_index += 1
                    continue
                
                # Extract complete player information
                player_info = self._extract_complete_player_data(player_data)
                if player_info:
                    players.append(player_info)
                
                player_index += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting players from page: {e}")
        
        return players
    
    def _extract_complete_player_data(self, player_data: List) -> Dict[str, Any]:
        """
        Extract ALL available data for a single player.
        
        Args:
            player_data: Player data array from Yahoo API (list of lists)
            
        Returns:
            Dict with all available player information
        """
        try:
            player_info = {}
            
            # Handle the list-of-lists structure
            if not isinstance(player_data, list) or not player_data:
                return {}
            
            # The player_data is a list of lists, we need to flatten it
            # Each inner list contains property objects
            for prop_list in player_data:
                if isinstance(prop_list, list):
                    for prop in prop_list:
                        if isinstance(prop, dict):
                            for key, value in prop.items():
                                player_info[key] = value
            
            # Extract bye week from bye_weeks object
            if 'bye_weeks' in player_info and isinstance(player_info['bye_weeks'], dict):
                bye_weeks = player_info['bye_weeks']
                if 'week' in bye_weeks:
                    player_info['bye_week'] = bye_weeks['week']
                else:
                    player_info['bye_week'] = 'N/A'
            else:
                player_info['bye_week'] = 'N/A'
            
            # Extract headshot URL
            if 'headshot' in player_info and isinstance(player_info['headshot'], dict):
                headshot = player_info['headshot']
                player_info['headshot_url'] = headshot.get('url', '')
            else:
                player_info['headshot_url'] = ''
            
            # Extract percent owned value
            if 'percent_owned' in player_info and isinstance(player_info['percent_owned'], dict):
                percent_owned = player_info['percent_owned']
                player_info['percent_owned_value'] = percent_owned.get('value', '0')
            else:
                player_info['percent_owned_value'] = '0'
            
            return player_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting player data: {e}")
            return {}
    
    def _organize_players_into_sections(self, all_players: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize players into different sections for analysis.
        
        Args:
            all_players: Complete list of all players
            
        Returns:
            Dict with organized player sections
        """
        try:
            organized = {
                'available_players': all_players,  # All players
                'injury_reports': [],
                'whos_hot': [],
                'top_available': []
            }
            
            # Filter injury reports (players with injury notes)
            for player in all_players:
                if player.get('injury_note') and player.get('injury_note').strip():
                    organized['injury_reports'].append(player)
            
            # Filter who's hot (high percent owned or trending)
            for player in all_players:
                percent_owned = float(player.get('percent_owned_value', '0'))
                if percent_owned > 50:  # Arbitrary threshold for "hot" players
                    organized['whos_hot'].append(player)
            
            # Top available players (sort by percent owned descending)
            top_available = sorted(all_players, 
                                 key=lambda x: float(x.get('percent_owned_value', '0')), 
                                 reverse=True)
            organized['top_available'] = top_available[:50]  # Top 50
            
            self.logger.info(f"📊 Organized sections: {len(organized['available_players'])} total, "
                           f"{len(organized['injury_reports'])} injured, "
                           f"{len(organized['whos_hot'])} hot, "
                           f"{len(organized['top_available'])} top available")
            
            return organized
            
        except Exception as e:
            self.logger.error(f"❌ Error organizing players: {e}")
            return {
                'available_players': all_players,
                'injury_reports': [],
                'whos_hot': [],
                'top_available': []
            }
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        Save extracted data to files.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save raw data
            raw_success = self.file_manager.save_raw_data(
                'yahoo', 'available_players', data, timestamp
            )
            
            # Generate and save markdown report
            markdown_content = self._generate_markdown_report(data)
            markdown_success = self.file_manager.save_clean_data(
                'yahoo', 'available_players', markdown_content, timestamp
            )
            
            # Save execution log
            log_success = self.file_manager.save_execution_log(
                'yahoo', 'available_players', self.execution_stats, timestamp
            )
            
            success = raw_success and markdown_success and log_success
            
            if success:
                self.logger.info(f"✅ Data saved successfully with timestamp: {timestamp}")
            else:
                self.logger.error("❌ Failed to save some data files")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error saving data: {e}")
            return False
    
    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """
        Generate markdown report from extracted data.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Formatted markdown string
        """
        try:
            metadata = data.get('extraction_metadata', {})
            league_info = metadata.get('league_info', {})
            stats = metadata.get('execution_stats', {})
            
            report = []
            report.append("# Yahoo Fantasy Football - Available Players Data")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**League:** {league_info.get('league_name', 'Unknown')}")
            report.append(f"**League Key:** {league_info.get('league_key', 'Unknown')}")
            report.append(f"**Total Players:** {metadata.get('total_players', 0)}")
            report.append(f"**API Calls:** {stats.get('api_calls', 0)}")
            report.append(f"**Execution Time:** {stats.get('execution_time', 0):.2f}s")
            report.append(f"**Errors:** {stats.get('errors', 0)}")
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
            
            # Available Players Section
            available_players = data.get('available_players', [])
            report.append("## Available Players")
            report.append(f"**Total Available Players:** {len(available_players)}")
            report.append("")
            
            if available_players:
                report.append("| Player | Position | Team | Status | % Owned | Injury |")
                report.append("|--------|----------|------|--------|---------|--------|")
                
                for player in available_players[:100]:  # Show first 100
                    name = player.get('name', {}).get('full', 'Unknown')
                    position = player.get('display_position', 'N/A')
                    team = player.get('editorial_team_abbr', 'N/A')
                    status = player.get('status', 'N/A')
                    percent_owned = player.get('percent_owned_value', '0')
                    injury = player.get('injury_note', 'N/A')
                    
                    report.append(f"| {name} | {position} | {team} | {status} | {percent_owned}% | {injury} |")
                
                if len(available_players) > 100:
                    report.append(f"")
                    report.append(f"*... and {len(available_players) - 100} more players*")
            
            report.append("")
            
            # Injury Reports Section
            injury_reports = data.get('injury_reports', [])
            report.append("## Injury Reports")
            report.append(f"**Players with Injuries:** {len(injury_reports)}")
            report.append("")
            
            if injury_reports:
                report.append("| Player | Position | Team | Injury Note | Status |")
                report.append("|--------|----------|------|-------------|--------|")
                
                for player in injury_reports[:100]:  # Show first 100
                    name = player.get('name', {}).get('full', 'Unknown')
                    position = player.get('display_position', 'N/A')
                    team = player.get('editorial_team_abbr', 'N/A')
                    injury = player.get('injury_note', 'N/A')
                    status = player.get('status', 'N/A')
                    
                    report.append(f"| {name} | {position} | {team} | {injury} | {status} |")
                
                if len(injury_reports) > 100:
                    report.append("")
                    report.append(f"*... and {len(injury_reports) - 100} more injured players*")
            
            report.append("")
            
            # Removed Who's Hot section per requirements
            # (Previously listed trending players by percent owned)
            # Maintain spacing
            report.append("")
            
            # Top Available Section
            top_available = data.get('top_available', [])
            report.append("## Top Available Players")
            report.append(f"**Top Players by % Owned:** {len(top_available)}")
            report.append("")
            
            if top_available:
                report.append("| Rank | Player | Position | Team | % Owned | Status |")
                report.append("|------|--------|----------|------|---------|--------|")
                
                for i, player in enumerate(top_available[:100], 1):  # Show first 100
                    name = player.get('name', {}).get('full', 'Unknown')
                    position = player.get('display_position', 'N/A')
                    team = player.get('editorial_team_abbr', 'N/A')
                    percent_owned = player.get('percent_owned_value', '0')
                    status = player.get('status', 'N/A')
                    
                    report.append(f"| {i} | {name} | {position} | {team} | {percent_owned}% | {status} |")
                
                if len(top_available) > 100:
                    report.append("")
                    report.append(f"*... and {len(top_available) - 100} more top players*")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating markdown report: {e}")
            return f"# Error generating report\n\nError: {e}"

def main():
    """Main execution function."""
    extractor = AvailablePlayersExtractor()
    
    try:
        # Extract all data
        data = extractor.extract_all_data()
        
        if data:
            # Save data
            success = extractor.save_data(data)
            
            if success:
                print("✅ Available Players extraction completed successfully!")
                print(f"📊 Total players: {data.get('extraction_metadata', {}).get('total_players', 0)}")
                print(f"⏱️  Execution time: {extractor.execution_stats.get('execution_time', 0):.2f}s")
                print(f"🔗 API calls: {extractor.execution_stats.get('api_calls', 0)}")
                print(f"❌ Errors: {extractor.execution_stats.get('errors', 0)}")
            else:
                print("❌ Failed to save data")
        else:
            print("❌ No data extracted")
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
