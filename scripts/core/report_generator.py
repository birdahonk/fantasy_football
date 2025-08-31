#!/usr/bin/env python3
"""
Yahoo Fantasy Sports Report Generator

This script generates comprehensive reports from Yahoo Fantasy Sports API data,
including team rosters, matchups, available players, and player news.

Author: Fantasy Football AI Assistant
Date: January 2025
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the oauth directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
oauth_dir = os.path.join(script_dir, "..", "oauth")
sys.path.append(oauth_dir)

from data_retriever import YahooDataRetriever

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FantasyReportGenerator:
    """Generate comprehensive fantasy football reports"""
    
    def __init__(self):
        """Initialize the report generator"""
        self.data_retriever = YahooDataRetriever()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories in project root
        project_root = Path(__file__).parent.parent.parent
        self.base_dir = project_root / "analysis"
        self.reports_dir = self.base_dir / "reports"
        self.weekly_dir = self.base_dir / "weekly"
        self.teams_dir = self.base_dir / "teams"
        self.players_dir = self.base_dir / "players"
        
        for dir_path in [self.reports_dir, self.weekly_dir, self.teams_dir, self.players_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _format_table(self, headers: List[str], rows: List[List[str]]) -> List[str]:
        """Format a markdown table with proper column alignment"""
        if not rows:
            return []
        
        # Calculate max width for each column
        all_rows = [headers] + rows
        col_widths = []
        for col_idx in range(len(headers)):
            max_width = max(len(str(row[col_idx])) if col_idx < len(row) else 0 for row in all_rows)
            col_widths.append(max(max_width, 3))  # Minimum width of 3
        
        # Format header
        formatted_header = "| " + " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
        
        # Format separator
        separator = "|" + "|".join("-" * (col_widths[i] + 2) for i in range(len(headers))) + "|"
        
        # Format rows
        formatted_rows = []
        for row in rows:
            formatted_row = "| " + " | ".join(
                str(row[i]).ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[i]) 
                for i in range(len(headers))
            ) + " |"
            formatted_rows.append(formatted_row)
        
        return [formatted_header, separator] + formatted_rows
    
    def _get_player_projections(self, player_key: str) -> Dict[str, Any]:
        """Get player projections from Yahoo API"""
        try:
            # Try to get player stats/projections
            response = self.data_retriever.oauth_client.make_request(f"player/{player_key}/stats")
            if response and response.get('status') == 'success':
                return response.get('parsed', {})
        except Exception as e:
            logger.debug(f"Failed to get projections for {player_key}: {e}")
        return {}
    
    def _get_bye_weeks(self) -> Dict[str, int]:
        """Get bye week information for all NFL teams"""
        # This would ideally come from an external API or be hardcoded for the season
        # For now, return a placeholder mapping
        bye_weeks = {
            'Ari': 11, 'Atl': 12, 'Bal': 14, 'Buf': 12, 'Car': 11, 'Chi': 7, 'Cin': 12, 'Cle': 10,
            'Dal': 7, 'Den': 14, 'Det': 5, 'GB': 10, 'Hou': 14, 'Ind': 14, 'Jax': 12, 'KC': 6,
            'LV': 10, 'LAC': 5, 'LAR': 6, 'Mia': 6, 'Min': 6, 'NE': 14, 'NO': 12, 'NYG': 11,
            'NYJ': 12, 'Phi': 5, 'Pit': 9, 'SF': 9, 'Sea': 10, 'TB': 11, 'Ten': 5, 'Was': 14
        }
        return bye_weeks
    
    def generate_all_reports(self):
        """Generate all comprehensive reports"""
        logger.info("Starting comprehensive report generation...")
        
        try:
            # Test API connection
            if not self.data_retriever.test_basic_connection():
                logger.error("Failed to connect to Yahoo API")
                return False
            
            # Generate all reports
            self.generate_team_rosters_report()
            self.generate_matchups_report()
            self.generate_available_players_report()
            self.generate_my_team_news_report()
            
            logger.info("All reports generated successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            return False
    
    def generate_team_rosters_report(self):
        """Generate detailed roster report for all teams with enhanced data"""
        logger.info("Generating enhanced team rosters report...")
        
        try:
            # Get all teams and their rosters
            teams = self.data_retriever.get_all_league_teams()
            if not teams:
                logger.error("Failed to get league teams")
                return
            
            bye_weeks = self._get_bye_weeks()
            
            report_content = []
            report_content.append(f"# League Team Rosters Report - Enhanced")
            report_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append(f"**League:** Greg Mulligan Memorial League")
            report_content.append(f"**Week:** 1")
            report_content.append(f"**Total Teams:** {len(teams)}")
            report_content.append("")
            
            for team in teams:
                team_key = team.get('team_key')
                team_name = team.get('name', 'Unknown')
                manager = team.get('manager', 'Unknown')
                
                logger.info(f"Processing enhanced roster for {team_name}...")
                
                # Get team roster with detailed parsing
                roster_response = self.data_retriever.oauth_client.make_request(f"team/{team_key}/roster")
                if not roster_response or roster_response.get('status') != 'success':
                    logger.warning(f"Failed to get roster for {team_name}")
                    continue
                
                parsed_data = roster_response.get('parsed', {})
                players = self.data_retriever._parse_roster_response(parsed_data)
                
                # Get additional team info
                team_response = self.data_retriever.oauth_client.make_request(f"team/{team_key}")
                team_details = {}
                if team_response and team_response.get('status') == 'success':
                    team_parsed = team_response.get('parsed', {})
                    fantasy_content = team_parsed.get('fantasy_content', {})
                    team_data = fantasy_content.get('team', {})
                    if isinstance(team_data, list):
                        for item in team_data:
                            if isinstance(item, dict):
                                team_details.update(item)
                
                # Add team section
                report_content.append(f"## {team_name}")
                report_content.append(f"**Manager:** {manager}")
                report_content.append(f"**Team Key:** {team_key}")
                if team_details.get('draft_position'):
                    report_content.append(f"**Draft Position:** {team_details['draft_position']}")
                if team.get('previous_rank'):
                    report_content.append(f"**Previous Season Rank:** {team['previous_rank']}")
                report_content.append(f"**Total Players:** {len(players)}")
                report_content.append("")
                
                # Organize players by position with enhanced data
                starters = []
                bench = []
                
                for player in players:
                    selected_pos = player.get('selected_position', 'BN')
                    
                    # Get additional player data
                    player_key = player.get('player_key')
                    projections = self._get_player_projections(player_key) if player_key else {}
                    
                    # Enhanced player data
                    enhanced_player = {
                        'name': player.get('name', 'Unknown'),
                        'position': player.get('position', 'N/A'),
                        'selected_position': selected_pos,
                        'team': player.get('team', 'N/A'),
                        'status': player.get('status', '') or 'Healthy',
                        'status_full': player.get('status_full', ''),
                        'injury_note': player.get('injury_note', ''),
                        'bye_week': bye_weeks.get(player.get('team', ''), 'TBD'),
                        'projections': projections,
                        'player_key': player_key
                    }
                    
                    if selected_pos == 'BN':
                        bench.append(enhanced_player)
                    else:
                        starters.append(enhanced_player)
                
                # Add starters with enhanced table
                if starters:
                    report_content.append("### Starting Lineup")
                    
                    headers = ["Position", "Player Name", "NFL Team", "Status", "Bye Week", "Proj Pts"]
                    rows = []
                    
                    for player in starters:
                        status = player['status']
                        if player['status_full']:
                            status = f"{status} ({player['status_full']})"
                        if player['injury_note']:
                            status += f" - {player['injury_note']}"
                        
                        proj_pts = "TBD"  # Would extract from projections if available
                        
                        rows.append([
                            player['selected_position'],
                            player['name'],
                            player['team'],
                            status,
                            str(player['bye_week']),
                            proj_pts
                        ])
                    
                    table_lines = self._format_table(headers, rows)
                    report_content.extend(table_lines)
                    report_content.append("")
                
                # Add bench with enhanced table
                if bench:
                    report_content.append("### Bench Players")
                    
                    headers = ["Player Name", "Position", "NFL Team", "Status", "Bye Week"]
                    rows = []
                    
                    for player in bench:
                        status = player['status']
                        if player['status_full']:
                            status = f"{status} ({player['status_full']})"
                        if player['injury_note']:
                            status += f" - {player['injury_note']}"
                        
                        rows.append([
                            player['name'],
                            player['position'],
                            player['team'],
                            status,
                            str(player['bye_week'])
                        ])
                    
                    table_lines = self._format_table(headers, rows)
                    report_content.extend(table_lines)
                    report_content.append("")
                
                # Add team summary
                total_starters = len(starters)
                total_bench = len(bench)
                injured_players = len([p for p in (starters + bench) if p['status'] != 'Healthy'])
                
                report_content.append("### Team Summary")
                report_content.append(f"- **Starters:** {total_starters}")
                report_content.append(f"- **Bench:** {total_bench}")
                report_content.append(f"- **Injured/Questionable:** {injured_players}")
                report_content.append("")
                report_content.append("---")
                report_content.append("")
            
            # Save report
            filename = f"{self.timestamp}_team_rosters_enhanced.md"
            filepath = self.teams_dir / filename
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(report_content))
            
            logger.info(f"Enhanced team rosters report saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error generating enhanced team rosters report: {e}")
    
    def generate_matchups_report(self):
        """Generate week 1 matchups report with parsed data"""
        logger.info("Generating enhanced matchups report...")
        
        try:
            # Get league key
            league_key = self.data_retriever.get_league_key()
            if not league_key:
                logger.error("Failed to get league key")
                return
            
            # Get matchups for week 1
            matchups_response = self.data_retriever.oauth_client.make_request(f"league/{league_key}/scoreboard;week=1")
            
            report_content = []
            report_content.append(f"# Week 1 League Matchups - Enhanced")
            report_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append(f"**League:** Greg Mulligan Memorial League")
            report_content.append(f"**Week:** 1")
            report_content.append(f"**Week Dates:** September 4-8, 2025")
            report_content.append("")
            
            if matchups_response and matchups_response.get('status') == 'success':
                # Parse matchups data
                parsed_data = matchups_response.get('parsed', {})
                
                # Extract matchups from the complex nested structure
                matchups = self._parse_matchups_data(parsed_data)
                
                if matchups:
                    report_content.append("## Week 1 Matchups")
                    report_content.append("")
                    
                    headers = ["Matchup", "Team 1", "Manager 1", "Team 2", "Manager 2", "Status"]
                    rows = []
                    
                    for i, matchup in enumerate(matchups, 1):
                        team1 = matchup.get('team1', {})
                        team2 = matchup.get('team2', {})
                        
                        rows.append([
                            f"Matchup {i}",
                            team1.get('name', 'Unknown'),
                            team1.get('manager', 'Unknown'),
                            team2.get('name', 'Unknown'),
                            team2.get('manager', 'Unknown'),
                            matchup.get('status', 'Pre-Event')
                        ])
                    
                    table_lines = self._format_table(headers, rows)
                    report_content.extend(table_lines)
                    report_content.append("")
                    
                    # Add detailed matchup information
                    report_content.append("## Detailed Matchup Information")
                    report_content.append("")
                    
                    for i, matchup in enumerate(matchups, 1):
                        team1 = matchup.get('team1', {})
                        team2 = matchup.get('team2', {})
                        
                        report_content.append(f"### Matchup {i}")
                        report_content.append(f"**{team1.get('name', 'Team 1')}** vs **{team2.get('name', 'Team 2')}**")
                        report_content.append(f"- **Managers:** {team1.get('manager', 'Unknown')} vs {team2.get('manager', 'Unknown')}")
                        report_content.append(f"- **Team Keys:** {team1.get('team_key', 'N/A')} vs {team2.get('team_key', 'N/A')}")
                        report_content.append(f"- **Status:** {matchup.get('status', 'Pre-Event')}")
                        
                        if matchup.get('is_matchup_of_the_week'):
                            report_content.append(f"- **⭐ MATCHUP OF THE WEEK ⭐**")
                        
                        # Add projected scores if available
                        proj1 = team1.get('projected_points', 'TBD')
                        proj2 = team2.get('projected_points', 'TBD')
                        report_content.append(f"- **Projected Scores:** {proj1} - {proj2}")
                        
                        report_content.append("")
                    
                else:
                    report_content.append("## No Matchups Found")
                    report_content.append("Unable to parse matchup data from Yahoo API response.")
                    report_content.append("")
                
            else:
                report_content.append("## Error")
                report_content.append("Failed to retrieve matchup data from Yahoo API")
                report_content.append("")
            
            # Save report
            filename = f"{self.timestamp}_week1_matchups_enhanced.md"
            filepath = self.weekly_dir / filename
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(report_content))
            
            logger.info(f"Enhanced matchups report saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error generating enhanced matchups report: {e}")
    
    def _parse_matchups_data(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the complex matchups data structure from Yahoo API"""
        matchups = []
        
        try:
            fantasy_content = parsed_data.get('fantasy_content', {})
            league_data = fantasy_content.get('league', [])
            
            # Find the scoreboard data
            scoreboard_data = None
            for item in league_data:
                if isinstance(item, dict) and 'scoreboard' in item:
                    scoreboard_data = item['scoreboard']
                    break
            
            if not scoreboard_data:
                logger.warning("No scoreboard data found in matchups response")
                return matchups
            
            # Extract matchups from the nested structure
            matchups_data = scoreboard_data.get('0', {}).get('matchups', {})
            
            for matchup_key in matchups_data:
                if matchup_key.isdigit():  # Only process numeric keys
                    matchup_info = matchups_data[matchup_key].get('matchup', {})
                    
                    # Extract teams data
                    teams_data = matchup_info.get('0', {}).get('teams', {})
                    
                    team1_data = None
                    team2_data = None
                    
                    # Parse team data - Yahoo uses complex nested array structure
                    if '0' in teams_data:
                        team1_raw = teams_data['0'].get('team', [])
                        if isinstance(team1_raw, list) and len(team1_raw) > 0:
                            # Team data is in nested arrays - extract from the array elements
                            team1_data = {}
                            for item in team1_raw:
                                if isinstance(item, list) and len(item) > 0:
                                    for subitem in item:
                                        if isinstance(subitem, dict):
                                            team1_data.update(subitem)
                                elif isinstance(item, dict):
                                    team1_data.update(item)
                    
                    if '1' in teams_data:
                        team2_raw = teams_data['1'].get('team', [])
                        if isinstance(team2_raw, list) and len(team2_raw) > 0:
                            # Team data is in nested arrays - extract from the array elements
                            team2_data = {}
                            for item in team2_raw:
                                if isinstance(item, list) and len(item) > 0:
                                    for subitem in item:
                                        if isinstance(subitem, dict):
                                            team2_data.update(subitem)
                                elif isinstance(item, dict):
                                    team2_data.update(item)
                    
                    if team1_data and team2_data:
                        # Extract manager info
                        team1_manager = 'Unknown'
                        if team1_data.get('managers') and len(team1_data['managers']) > 0:
                            team1_manager = team1_data['managers'][0].get('manager', {}).get('nickname', 'Unknown')
                        
                        team2_manager = 'Unknown'
                        if team2_data.get('managers') and len(team2_data['managers']) > 0:
                            team2_manager = team2_data['managers'][0].get('manager', {}).get('nickname', 'Unknown')
                        
                        matchup = {
                            'team1': {
                                'name': team1_data.get('name', 'Unknown'),
                                'manager': team1_manager,
                                'team_key': team1_data.get('team_key', 'N/A'),
                                'projected_points': team1_data.get('team_projected_points', {}).get('total', 'TBD')
                            },
                            'team2': {
                                'name': team2_data.get('name', 'Unknown'),
                                'manager': team2_manager,
                                'team_key': team2_data.get('team_key', 'N/A'),
                                'projected_points': team2_data.get('team_projected_points', {}).get('total', 'TBD')
                            },
                            'status': matchup_info.get('status', 'Pre-Event'),
                            'is_matchup_of_the_week': matchup_info.get('is_matchup_of_the_week') == '1'
                        }
                        matchups.append(matchup)
            
        except Exception as e:
            logger.error(f"Error parsing matchups data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return matchups
    
    def generate_available_players_report(self):
        """Generate enhanced top available players by position"""
        logger.info("Generating enhanced available players report...")
        
        try:
            bye_weeks = self._get_bye_weeks()
            
            report_content = []
            report_content.append(f"# Top Available Players by Position - Enhanced")
            report_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append(f"**League:** Greg Mulligan Memorial League")
            report_content.append(f"**Note:** Players ranked by Yahoo's Overall Rank (OR)")
            report_content.append("")
            
            positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
            total_available = 0
            
            for position in positions:
                logger.info(f"Getting top 20 {position} players...")
                
                # Get top 20 available players for this position
                players = self.data_retriever.get_free_agents(position=position, count=20)
                
                report_content.append(f"## Top 20 Available {position}s")
                
                if players:
                    total_available += len(players)
                    
                    headers = ["Rank", "Player Name", "NFL Team", "Status", "Bye Week", "Ownership %", "Player Key"]
                    rows = []
                    
                    for i, player in enumerate(players, 1):
                        name = player.get('name', 'Unknown')
                        team = player.get('team', 'N/A')
                        status = player.get('status', '') or 'Healthy'
                        if player.get('status_full'):
                            status = f"{status} ({player['status_full']})"
                        if player.get('injury_note'):
                            status += f" - {player['injury_note']}"
                        
                        bye_week = bye_weeks.get(team, 'TBD')
                        ownership = player.get('ownership_pct', 'N/A')
                        player_key = player.get('player_key', 'N/A')
                        
                        rows.append([
                            str(i),
                            name,
                            team,
                            status,
                            str(bye_week),
                            str(ownership),
                            player_key
                        ])
                    
                    table_lines = self._format_table(headers, rows)
                    report_content.extend(table_lines)
                    
                    # Add position summary
                    injured_count = len([p for p in players if p.get('status') and p.get('status') != 'Healthy'])
                    report_content.append("")
                    report_content.append(f"**{position} Summary:** {len(players)} available, {injured_count} with injury concerns")
                    
                else:
                    report_content.append("No available players found for this position.")
                
                report_content.append("")
                report_content.append("---")
                report_content.append("")
            
            # Add overall summary
            report_content.append("## Overall Summary")
            report_content.append(f"- **Total Available Players:** {total_available}")
            report_content.append(f"- **Positions Covered:** {len(positions)}")
            report_content.append(f"- **Data Source:** Yahoo Fantasy Sports API")
            report_content.append(f"- **Ranking Method:** Yahoo Overall Rank (OR)")
            report_content.append("")
            
            # Save report
            filename = f"{self.timestamp}_available_players_enhanced.md"
            filepath = self.players_dir / filename
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(report_content))
            
            logger.info(f"Enhanced available players report saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error generating enhanced available players report: {e}")
    
    def generate_my_team_news_report(self):
        """Generate enhanced news report for my team's players"""
        logger.info("Generating enhanced my team news report...")
        
        try:
            # Get my team roster
            teams = self.data_retriever.get_all_league_teams()
            my_team = None
            
            for team in teams:
                if team.get('is_my_team'):
                    my_team = team
                    break
            
            if not my_team:
                logger.error("Could not find my team")
                return
            
            team_key = my_team.get('team_key')
            team_name = my_team.get('name', 'My Team')
            manager = my_team.get('manager', 'Unknown')
            
            # Get roster
            roster_response = self.data_retriever.oauth_client.make_request(f"team/{team_key}/roster")
            if not roster_response or roster_response.get('status') != 'success':
                logger.error("Failed to get my team roster")
                return
            
            parsed_data = roster_response.get('parsed', {})
            players = self.data_retriever._parse_roster_response(parsed_data)
            
            bye_weeks = self._get_bye_weeks()
            
            report_content = []
            report_content.append(f"# {team_name} - Enhanced Team Report")
            report_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append(f"**Team:** {team_name}")
            report_content.append(f"**Manager:** {manager}")
            report_content.append(f"**Team Key:** {team_key}")
            report_content.append(f"**Total Players:** {len(players)}")
            report_content.append("")
            
            # Organize players by position
            starters = []
            bench = []
            
            for player in players:
                selected_pos = player.get('selected_position', 'BN')
                
                # Enhanced player data
                enhanced_player = {
                    'name': player.get('name', 'Unknown'),
                    'position': player.get('position', 'N/A'),
                    'selected_position': selected_pos,
                    'team': player.get('team', 'N/A'),
                    'status': player.get('status', '') or 'Healthy',
                    'status_full': player.get('status_full', ''),
                    'injury_note': player.get('injury_note', ''),
                    'bye_week': bye_weeks.get(player.get('team', ''), 'TBD'),
                    'player_key': player.get('player_key', 'N/A')
                }
                
                if selected_pos == 'BN':
                    bench.append(enhanced_player)
                else:
                    starters.append(enhanced_player)
            
            # Team roster with enhanced formatting
            report_content.append("## Complete Team Roster")
            
            headers = ["Player Name", "Position", "NFL Team", "Status", "Selected Position", "Bye Week", "Player Key"]
            rows = []
            
            # Add starters first
            for player in starters:
                status = player['status']
                if player['status_full']:
                    status = f"{status} ({player['status_full']})"
                if player['injury_note']:
                    status += f" - {player['injury_note']}"
                
                rows.append([
                    player['name'],
                    player['position'],
                    player['team'],
                    status,
                    player['selected_position'],
                    str(player['bye_week']),
                    player['player_key']
                ])
            
            # Add bench players
            for player in bench:
                status = player['status']
                if player['status_full']:
                    status = f"{status} ({player['status_full']})"
                if player['injury_note']:
                    status += f" - {player['injury_note']}"
                
                rows.append([
                    player['name'],
                    player['position'],
                    player['team'],
                    status,
                    player['selected_position'],
                    str(player['bye_week']),
                    player['player_key']
                ])
            
            table_lines = self._format_table(headers, rows)
            report_content.extend(table_lines)
            report_content.append("")
            
            # Team analysis
            total_starters = len(starters)
            total_bench = len(bench)
            injured_players = len([p for p in (starters + bench) if p['status'] != 'Healthy'])
            
            # Bye week analysis
            bye_week_counts = {}
            for player in (starters + bench):
                bye_week = player['bye_week']
                if bye_week != 'TBD':
                    bye_week_counts[bye_week] = bye_week_counts.get(bye_week, 0) + 1
            
            report_content.append("## Team Analysis")
            report_content.append(f"- **Starting Lineup:** {total_starters} players")
            report_content.append(f"- **Bench Players:** {total_bench} players")
            report_content.append(f"- **Injured/Questionable:** {injured_players} players")
            report_content.append("")
            
            if bye_week_counts:
                report_content.append("### Bye Week Distribution")
                for week, count in sorted(bye_week_counts.items()):
                    report_content.append(f"- **Week {week}:** {count} players")
                report_content.append("")
            
            # Position breakdown
            position_counts = {}
            for player in (starters + bench):
                pos = player['position']
                position_counts[pos] = position_counts.get(pos, 0) + 1
            
            report_content.append("### Position Breakdown")
            for pos, count in sorted(position_counts.items()):
                report_content.append(f"- **{pos}:** {count} players")
            report_content.append("")
            
            # Injury report
            injured = [p for p in (starters + bench) if p['status'] != 'Healthy']
            if injured:
                report_content.append("### Injury Report")
                
                injury_headers = ["Player", "Position", "Team", "Status", "Details"]
                injury_rows = []
                
                for player in injured:
                    status = player['status']
                    details = ""
                    if player['status_full']:
                        details = player['status_full']
                    if player['injury_note']:
                        details += f" - {player['injury_note']}" if details else player['injury_note']
                    
                    injury_rows.append([
                        player['name'],
                        player['position'],
                        player['team'],
                        status,
                        details
                    ])
                
                injury_table = self._format_table(injury_headers, injury_rows)
                report_content.extend(injury_table)
                report_content.append("")
            
            # Player news section (placeholder since API endpoint failed)
            report_content.append("## Player News Headlines")
            report_content.append("*Note: Yahoo Player News API endpoint returned 400 error*")
            report_content.append("*Consider integrating external news sources (ESPN, NFL.com, etc.)*")
            report_content.append("")
            
            # Save report
            filename = f"{self.timestamp}_my_team_enhanced.md"
            filepath = self.reports_dir / filename
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(report_content))
            
            logger.info(f"Enhanced my team report saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error generating enhanced my team report: {e}")

def main():
    """Generate all fantasy football reports"""
    try:
        print("🏈 Generating Fantasy Football Reports...")
        
        generator = FantasyReportGenerator()
        success = generator.generate_all_reports()
        
        if success:
            print("✅ All reports generated successfully!")
            print(f"📁 Reports saved in:")
            print(f"   - Teams: analysis/teams/")
            print(f"   - Weekly: analysis/weekly/")
            print(f"   - Players: analysis/players/")
            print(f"   - Reports: analysis/reports/")
        else:
            print("❌ Failed to generate some reports")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
