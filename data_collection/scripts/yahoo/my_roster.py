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
            
            # Combine all data
            complete_data = {
                'team_info': team_info,
                'roster_raw': roster_data.get('parsed', {}),
                'roster_players': self._extract_players(roster_data.get('parsed', {})),
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
                return {}
            
            user_data = users.get('0', {}).get('user', [])
            if not user_data:
                return {}
            
            # Find the games section
            games_section = None
            for section in user_data:
                if 'games' in section:
                    games_section = section['games']
                    break
            
            if not games_section:
                return {}
            
            # Find the NFL game
            nfl_game = games_section.get('0', {}).get('game', [])
            if not nfl_game:
                return {}
            
            # Extract league and team info
            teams_section = None
            league_info = {}
            
            for section in nfl_game:
                if 'teams' in section:
                    teams_section = section['teams']
                elif isinstance(section, dict):
                    # Look for league-level info
                    for key in ['league_key', 'name', 'league_id']:
                        if key in section:
                            league_info[key] = section[key]
            
            if not teams_section:
                return {}
            
            # Find user's team (is_owned_by_current_login = 1)
            user_team = teams_section.get('0', {}).get('team', {})
            if user_team.get('is_owned_by_current_login') != 1:
                return {}
            
            return {
                'team_key': user_team.get('team_key', ''),
                'team_name': user_team.get('name', ''),
                'team_id': user_team.get('team_id', ''),
                'league_key': user_team.get('team_key', '').split('.t.')[0] if user_team.get('team_key') else '',
                'league_name': league_info.get('name', 'Unknown League')
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting team info: {e}")
            return {}
    
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
    
    def _extract_complete_player_data(self, player_data: List[Dict]) -> Dict[str, Any]:
        """
        Extract ALL available data for a single player.
        
        Args:
            player_data: Player data array from Yahoo API
            
        Returns:
            Dict with all available player information
        """
        if not player_data:
            return {}
        
        # Yahoo stores player data in array format
        player_info = {}
        selected_position_info = {}
        
        for section in player_data:
            if isinstance(section, dict):
                # Main player data
                for key, value in section.items():
                    if key == 'selected_position':
                        # Handle selected position specially
                        if isinstance(value, list) and value:
                            pos_data = value[0] if isinstance(value[0], dict) else {}
                            selected_position_info = pos_data
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
            'selected_position': selected_position_info.get('position', 'Unknown'),
            'selected_coverage_type': selected_position_info.get('coverage_type', ''),
            'selected_date': selected_position_info.get('date', '')
        })
        
        # Process eligible positions if present
        if 'eligible_positions' in player_info and isinstance(player_info['eligible_positions'], list):
            positions = []
            for pos in player_info['eligible_positions']:
                if isinstance(pos, dict) and 'position' in pos:
                    positions.append(pos['position'])
            player_info['eligible_positions_list'] = positions
        
        # Process bye weeks if present
        if 'bye_weeks' in player_info and isinstance(player_info['bye_weeks'], dict):
            player_info['bye_week'] = player_info['bye_weeks'].get('week', '')
        
        # Process headshot if present
        if 'headshot' in player_info and isinstance(player_info['headshot'], dict):
            player_info['headshot_url'] = player_info['headshot'].get('url', '')
        
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
