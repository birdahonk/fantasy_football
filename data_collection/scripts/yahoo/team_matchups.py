#!/usr/bin/env python3
"""
Yahoo Fantasy Football - Team Matchups Data Extraction

This script extracts ALL data about team matchups from the user's fantasy football league
from the Yahoo Fantasy API. It outputs both clean markdown and raw JSON data.

Purpose: Clean, focused data extraction for weekly team matchups
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

class TeamMatchupsExtractor:
    """
    Extracts complete matchup data for the user's Yahoo Fantasy Football league.
    
    This class focuses on extracting ALL available data from the Yahoo API
    scoreboard endpoint without filtering or analysis.
    """
    
    def __init__(self):
        """Initialize the team matchups extractor."""
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
            'weeks_processed': 0,
            'total_matchups': 0
        }
    
    def extract_team_matchups(self, weeks: List[int] = None) -> Dict[str, Any]:
        """
        Extract complete matchup data for specified weeks.
        
        Args:
            weeks: List of week numbers to extract (default: current week and previous week)
            
        Returns:
            Dict containing all extracted matchup data
        """
        self.logger.info("🏈 Starting team matchups extraction...")
        
        try:
            # Step 1: Get user's league information
            league_info = self._get_league_info()
            if not league_info:
                raise Exception("Failed to get league information")
            
            league_key = league_info['league_key']
            self.logger.info(f"📋 Found league: {league_info['league_name']} ({league_key})")
            
            # Step 2: Determine weeks to extract
            if weeks is None:
                # Default: current week and previous week
                current_week = self._get_current_week(league_key)
                if current_week:
                    weeks = [current_week - 1, current_week] if current_week > 1 else [current_week]
                else:
                    weeks = [1]  # Fallback to week 1
            
            self.logger.info(f"📅 Extracting matchups for weeks: {weeks}")
            
            # Step 3: Extract matchups for each week
            all_matchups = {}
            for week in weeks:
                self.logger.info(f"🔍 Extracting matchups for week {week}...")
                
                week_matchups = self._extract_week_matchups(league_key, week)
                if week_matchups:
                    all_matchups[f"week_{week}"] = week_matchups
                    self.execution_stats['weeks_processed'] += 1
                    self.execution_stats['total_matchups'] += len(week_matchups.get('matchups', []))
                else:
                    self.logger.warning(f"⚠️ Failed to extract matchups for week {week}")
                    self.execution_stats['errors'] += 1
            
            # Step 4: Compile complete data
            complete_data = {
                'league_info': league_info,
                'matchups': all_matchups,
                'extraction_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'weeks_requested': weeks,
                    'weeks_processed': self.execution_stats['weeks_processed'],
                    'total_matchups': self.execution_stats['total_matchups'],
                    'api_calls': self.execution_stats['api_calls'],
                    'errors': self.execution_stats['errors']
                }
            }
            
            self.logger.info(f"✅ Extraction complete: {self.execution_stats['weeks_processed']} weeks, {self.execution_stats['total_matchups']} total matchups")
            return complete_data
            
        except Exception as e:
            self.logger.error(f"❌ Error in team matchups extraction: {e}")
            self.execution_stats['errors'] += 1
            raise
    
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
        This is the exact same method as my_roster.py and opponent_rosters.py.
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
    
    def _get_current_week(self, league_key: str) -> Optional[int]:
        """Get the current week from league settings."""
        try:
            self.logger.info(f"🔍 Getting current week for league: {league_key}")
            
            # Use scoreboard endpoint to get current week (more efficient)
            response = self.yahoo_auth.make_request(f"league/{league_key}/scoreboard")
            self.execution_stats['api_calls'] += 1
            
            if not response or response.get('status') != 'success':
                self.logger.warning("Could not get current week, using week 1")
                return 1
            
            # Navigate to league info
            parsed_data = response.get('parsed', {})
            fantasy_content = parsed_data.get('fantasy_content', {})
            league = fantasy_content.get('league', [])
            
            # Find current_week in league info
            for league_section in league:
                if isinstance(league_section, dict) and 'current_week' in league_section:
                    current_week = league_section['current_week']
                    self.logger.info(f"✅ Current week: {current_week}")
                    return int(current_week)
            
            self.logger.warning("Could not find current week in league info, using week 1")
            return 1
            
        except Exception as e:
            self.logger.error(f"❌ Error getting current week: {e}")
            return 1
    
    def _extract_week_matchups(self, league_key: str, week: int) -> Optional[Dict[str, Any]]:
        """Extract matchup data for a specific week."""
        try:
            self.logger.info(f"🔍 Extracting matchups for week {week}...")
            
            response = self.yahoo_auth.make_request(f"league/{league_key}/scoreboard;week={week}")
            self.execution_stats['api_calls'] += 1
            
            if not response or response.get('status') != 'success':
                self.logger.error(f"❌ Failed to get scoreboard for week {week}")
                return None
            
            # Get the parsed Yahoo API response
            parsed_data = response.get('parsed', {})
            if 'fantasy_content' not in parsed_data:
                self.logger.error("❌ No fantasy_content in parsed response")
                return None
            

            
            # Extract matchup data using the same patterns as other scripts
            matchups = self._extract_matchups_from_response(parsed_data, week)
            
            week_data = {
                'week': week,
                'matchups': matchups,
                'week_summary': {
                    'total_matchups': len(matchups),
                    'completed_matchups': len([m for m in matchups if m.get('status') == 'postevent']),
                    'live_matchups': len([m for m in matchups if m.get('status') == 'midevent']),
                    'upcoming_matchups': len([m for m in matchups if m.get('status') == 'preevent'])
                }
            }
            
            self.logger.info(f"✅ Extracted {len(matchups)} matchups for week {week}")
            return week_data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting matchups for week {week}: {e}")
            return None
    
    def _extract_matchups_from_response(self, parsed_data: Dict[str, Any], week: int) -> List[Dict[str, Any]]:
        """Extract matchup data from the scoreboard response."""
        matchups = []
        
        try:
            # Navigate Yahoo's scoreboard structure
            fantasy_content = parsed_data.get('fantasy_content', {})
            league = fantasy_content.get('league', [])
            
            # Debug: Log the league structure
            self.logger.info(f"🔍 League structure: {type(league)}")
            if isinstance(league, list):
                self.logger.info(f"🔍 League list length: {len(league)}")
                for i, item in enumerate(league):
                    self.logger.info(f"🔍 League[{i}]: {type(item)} - {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
            
            # Find scoreboard section
            for league_section in league:
                if isinstance(league_section, dict) and 'scoreboard' in league_section:
                    scoreboard = league_section['scoreboard']
                    self.logger.info(f"🔍 Scoreboard type: {type(scoreboard)}")
                    if isinstance(scoreboard, dict):
                        self.logger.info(f"🔍 Scoreboard keys: {list(scoreboard.keys())}")
                    
                    # Extract matchups from scoreboard
                    matchups_data = scoreboard.get('0', {}).get('matchups', {})
                    self.logger.info(f"🔍 Matchups data type: {type(matchups_data)}")
                    if isinstance(matchups_data, dict):
                        self.logger.info(f"🔍 Matchups data keys: {list(matchups_data.keys())}")
                    
                    # Process each matchup
                    matchup_index = 0
                    while str(matchup_index) in matchups_data:
                        matchup_data = matchups_data[str(matchup_index)]
                        self.logger.info(f"🔍 Processing matchup {matchup_index}: {type(matchup_data)}")
                        
                        if isinstance(matchup_data, dict) and 'matchup' in matchup_data:
                            matchup = self._extract_single_matchup(matchup_data['matchup'], week)
                            if matchup:
                                matchups.append(matchup)
                                self.logger.info(f"✅ Added matchup {matchup_index}")
                        
                        matchup_index += 1
                    
                    break
            
            self.logger.info(f"✅ Extracted {len(matchups)} matchups from response")
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting matchups from response: {e}")
        
        return matchups
    
    def _extract_single_matchup(self, matchup_data: Dict[str, Any], week: int) -> Optional[Dict[str, Any]]:
        """Extract data for a single matchup."""
        try:
            # Extract basic matchup info
            matchup_info = {
                'week': week,
                'week_start': matchup_data.get('week_start', ''),
                'week_end': matchup_data.get('week_end', ''),
                'status': matchup_data.get('status', ''),
                'is_playoffs': matchup_data.get('is_playoffs', ''),
                'is_consolation': matchup_data.get('is_consolation', ''),
                'is_tied': matchup_data.get('is_tied', 0),
                'winner_team_key': matchup_data.get('winner_team_key', '')
            }
            
            # Extract team data - each matchup has numbered keys (0, 1) for the two teams
            teams = []
            team_index = 0
            while str(team_index) in matchup_data:
                team_section = matchup_data[str(team_index)]
                if isinstance(team_section, dict) and 'teams' in team_section:
                    teams_data = team_section['teams']
                    
                    # Extract both teams (0 and 1) from this matchup
                    team_data_index = 0
                    while str(team_data_index) in teams_data:
                        team_data = teams_data[str(team_data_index)]
                        if team_data:
                            team_info = self._extract_team_from_matchup(team_data)
                            if team_info:
                                teams.append(team_info)
                        team_data_index += 1
                team_index += 1
            
            matchup_info['teams'] = teams
            
            self.logger.info(f"✅ Extracted matchup with {len(teams)} teams")
            return matchup_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting single matchup: {e}")
            return None
    
    def _extract_team_from_matchup(self, team_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract team data from matchup team section."""
        try:
            # Extract team info from the list structure
            team_info = {}
            team_list = team_data.get('team', [])
            
            if isinstance(team_list, list):
                # Process list of team properties (same pattern as other scripts)
                for team_section in team_list:
                    if isinstance(team_section, list):
                        # It's a list of property objects
                        for team_item in team_section:
                            if isinstance(team_item, dict):
                                team_info.update(team_item)
                    elif isinstance(team_section, dict):
                        # It's a direct property object
                        team_info.update(team_section)
            
            # Extract team points and projected points
            team_points = team_info.get('team_points', {})
            projected_points = team_info.get('team_projected_points', {})
            
            result = {
                'team_key': team_info.get('team_key', ''),
                'team_id': team_info.get('team_id', ''),
                'name': team_info.get('name', ''),
                'managers': team_info.get('managers', []),
                'team_points': {
                    'coverage_type': team_points.get('coverage_type', ''),
                    'week': team_points.get('week', ''),
                    'total': team_points.get('total', '')
                },
                'team_projected_points': {
                    'coverage_type': projected_points.get('coverage_type', ''),
                    'week': projected_points.get('week', ''),
                    'total': projected_points.get('total', '')
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting team from matchup: {e}")
            return None
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save extracted data to files."""
        try:
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save raw JSON data
            raw_path = self.file_manager.save_raw_data("yahoo", "team_matchups", data, timestamp)
            
            # Generate and save markdown report
            markdown_content = self._generate_markdown_report(data)
            markdown_path = self.file_manager.save_clean_data("yahoo", "team_matchups", markdown_content, timestamp)
            
            # Save execution log
            execution_log = {
                'script': 'team_matchups.py',
                'timestamp': timestamp,
                'execution_stats': self.execution_stats,
                'files_created': [raw_path, markdown_path]
            }
            self.file_manager.save_execution_log("yahoo", "team_matchups", execution_log, timestamp)
            
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
            report.append(f"# Team Matchups - {league_info.get('league_name', 'Unknown League')}")
            report.append(f"**League Key:** {league_info.get('league_key', 'Unknown')}")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Summary
            metadata = data.get('extraction_metadata', {})
            report.append("## 📊 Extraction Summary")
            report.append(f"- **Weeks Requested:** {metadata.get('weeks_requested', [])}")
            report.append(f"- **Weeks Processed:** {metadata.get('weeks_processed', 0)}")
            report.append(f"- **Total Matchups:** {metadata.get('total_matchups', 0)}")
            report.append(f"- **API Calls:** {metadata.get('api_calls', 0)}")
            report.append(f"- **Errors:** {metadata.get('errors', 0)}")
            report.append("")
            
            # Weekly Matchups
            matchups_data = data.get('matchups', {})
            if matchups_data:
                report.append("## 🏈 Weekly Matchups")
                
                for week_key, week_data in matchups_data.items():
                    week_num = week_data.get('week', 'Unknown')
                    matchups = week_data.get('matchups', [])
                    summary = week_data.get('week_summary', {})
                    
                    report.append(f"### Week {week_num}")
                    report.append(f"**Total Matchups:** {summary.get('total_matchups', 0)}")
                    report.append(f"**Completed:** {summary.get('completed_matchups', 0)}")
                    report.append(f"**Live:** {summary.get('live_matchups', 0)}")
                    report.append(f"**Upcoming:** {summary.get('upcoming_matchups', 0)}")
                    report.append("")
                    
                    if matchups:
                        report.append("#### Matchup Details")
                        report.append("| Team 1 | Score | vs | Team 2 | Score | Status |")
                        report.append("|--------|-------|----|--------|-------|--------|")
                        
                        for matchup in matchups:
                            teams = matchup.get('teams', [])
                            if len(teams) >= 2:
                                team1 = teams[0]
                                team2 = teams[1]
                                
                                team1_name = team1.get('name', 'Unknown')
                                team1_score = team1.get('team_points', {}).get('total', '0')
                                team1_projected = team1.get('team_projected_points', {}).get('total', '0')
                                
                                team2_name = team2.get('name', 'Unknown')
                                team2_score = team2.get('team_points', {}).get('total', '0')
                                team2_projected = team2.get('team_projected_points', {}).get('total', '0')
                                
                                status = matchup.get('status', 'Unknown')
                                
                                # Use projected score if actual score is 0
                                score1 = team1_score if team1_score != '0' else f"{team1_projected} (proj)"
                                score2 = team2_score if team2_score != '0' else f"{team2_projected} (proj)"
                                
                                report.append(f"| {team1_name} | {score1} | vs | {team2_name} | {score2} | {status} |")
                        
                        report.append("")
                        
                        # Detailed matchup information
                        report.append("#### Detailed Matchup Information")
                        for i, matchup in enumerate(matchups, 1):
                            report.append(f"**Matchup {i}:**")
                            report.append(f"- **Week:** {matchup.get('week', 'Unknown')}")
                            report.append(f"- **Status:** {matchup.get('status', 'Unknown')}")
                            report.append(f"- **Week Start:** {matchup.get('week_start', 'Unknown')}")
                            report.append(f"- **Week End:** {matchup.get('week_end', 'Unknown')}")
                            report.append(f"- **Playoffs:** {matchup.get('is_playoffs', 'No')}")
                            report.append(f"- **Consolation:** {matchup.get('is_consolation', 'No')}")
                            report.append(f"- **Tied:** {matchup.get('is_tied', 'No')}")
                            if matchup.get('winner_team_key'):
                                report.append(f"- **Winner:** {matchup.get('winner_team_key', 'Unknown')}")
                            report.append("")
                            
                            # Team details
                            teams = matchup.get('teams', [])
                            for j, team in enumerate(teams, 1):
                                report.append(f"**Team {j}:** {team.get('name', 'Unknown')}")
                                report.append(f"- **Team Key:** {team.get('team_key', 'Unknown')}")
                                report.append(f"- **Manager:** {team.get('managers', [{}])[0].get('manager', {}).get('nickname', 'Unknown')}")
                                report.append(f"- **Points:** {team.get('team_points', {}).get('total', '0')}")
                                report.append(f"- **Projected:** {team.get('team_projected_points', {}).get('total', '0')}")
                                report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating markdown report: {e}")
            return f"# Error generating report\n\nError: {e}"

def main():
    """Main execution function."""
    try:
        extractor = TeamMatchupsExtractor()
        
        # Extract team matchup data (current week and previous week by default)
        data = extractor.extract_team_matchups()
        
        # Save the data
        extractor.save_data(data)
        
        # Print summary
        stats = extractor.execution_stats
        print(f"\n🎉 Team Matchups Extraction Complete!")
        print(f"📅 Weeks Processed: {stats['weeks_processed']}")
        print(f"🏈 Total Matchups: {stats['total_matchups']}")
        print(f"🔗 API Calls: {stats['api_calls']}")
        print(f"❌ Errors: {stats['errors']}")
        print(f"⏱️ Execution Time: {datetime.now() - stats['start_time']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
