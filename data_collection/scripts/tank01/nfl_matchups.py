#!/usr/bin/env python3
"""
Tank01 NFL API - Current Week Team Matchups Data Extraction

This script extracts current week NFL team matchups, game times, and schedules
from the Tank01 API. It provides critical timing information for fantasy football
recommendations, including game start times in both Eastern and Pacific time zones.

Purpose: Extract NFL game schedules and timing for fantasy football analysis
Output: Organized markdown file + raw JSON data with game schedules
Focus: Game times, matchups, and scheduling information for all NFL games
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import pytz

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from tank01_client import SimpleTank01Client
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager
from api_usage_manager import APIUsageManager


class NFLMatchupsExtractor:
    """Extract current week NFL team matchups and game schedules from Tank01 API."""

    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.tank01 = SimpleTank01Client()
        self.formatter = MarkdownFormatter()
        self.file_manager = DataFileManager()
        self.usage_manager = APIUsageManager(self.tank01, "Tank01")

        self.execution_stats: Dict[str, Any] = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'errors': 0,
            'games_found': 0,
            'current_week': None,
            'season': None
        }

    def extract_nfl_matchups(self) -> Dict[str, Any]:
        """Extract current week NFL matchups and game schedules."""
        try:
            self.logger.info("Starting NFL matchups extraction...")
            
            # Get current NFL season state
            season_state = self._get_current_season_state()
            if not season_state:
                raise Exception("Could not determine current NFL season state")
            
            current_week = season_state.get('current_week', 1)
            season = season_state.get('season', '2025')
            
            self.execution_stats['current_week'] = current_week
            self.execution_stats['season'] = season
            
            # Get current week games
            games_data = self._get_current_week_games(current_week, season)
            if not games_data:
                raise Exception("No games found for current week")
            
            # Process and format the data
            processed_data = self._process_games_data(games_data, current_week, season)
            
            self.execution_stats['games_found'] = len(processed_data.get('games', []))
            self.execution_stats['api_calls'] = self.tank01.get_api_usage()['calls_made_this_session']
            
            self.logger.info(f"Successfully extracted {self.execution_stats['games_found']} games for Week {current_week}")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error extracting NFL matchups: {e}")
            self.execution_stats['errors'] += 1
            raise

    def _get_current_season_state(self) -> Optional[Dict[str, Any]]:
        """Get current NFL season state from Tank01 API."""
        try:
            # Use the daily scoreboard to get current week info
            # We'll get today's date and use it to determine the current week
            today = datetime.now().strftime("%Y%m%d")
            
            # Get today's games to determine current week
            response = self.tank01.get_daily_scoreboard(game_date=today, top_performers=True)
            
            if response and 'body' in response:
                # Extract week info from the first game if available
                games = response['body']
                if games:
                    # Get the first game to extract week info
                    first_game_id = list(games.keys())[0]
                    first_game = games[first_game_id]
                    
                    # Try to get week from game info
                    game_info = self._get_game_info(first_game_id)
                    if game_info and 'gameWeek' in game_info:
                        week_str = game_info['gameWeek']
                        # Extract week number from "Week X" format
                        week_match = week_str.replace('Week ', '') if 'Week ' in week_str else week_str
                        current_week = int(week_match) if week_match.isdigit() else 1
                    else:
                        current_week = 1
                    
                    self.logger.info(f"Detected current week: {current_week}")
                    return {
                        'current_week': current_week,
                        'season': '2025',
                        'season_type': 'Regular Season'
                    }
            
            # If no games today, try to find games from the past few days to determine week
            self.logger.info("No games found for today, searching past days for week info...")
            for days_back in range(1, 8):  # Check past 7 days
                check_date = datetime.now() - timedelta(days=days_back)
                date_str = check_date.strftime("%Y%m%d")
                
                response = self.tank01.get_daily_scoreboard(game_date=date_str, top_performers=True)
                
                if response and 'body' in response:
                    games = response['body']
                    if games:
                        # Get the first game to extract week info
                        first_game_id = list(games.keys())[0]
                        game_info = self._get_game_info(first_game_id)
                        if game_info and 'gameWeek' in game_info:
                            week_str = game_info['gameWeek']
                            week_match = week_str.replace('Week ', '') if 'Week ' in week_str else week_str
                            current_week = int(week_match) if week_match.isdigit() else 1
                            
                            self.logger.info(f"Found week info from {date_str}: Week {current_week}")
                            return {
                                'current_week': current_week,
                                'season': '2025',
                                'season_type': 'Regular Season'
                            }
            
            # Fallback: assume current week 1
            self.logger.warning("Could not determine current week, defaulting to Week 1")
            return {
                'current_week': 1,
                'season': '2025',
                'season_type': 'Regular Season'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current season state: {e}")
            return None

    def _get_current_week_games(self, week: int, season: str) -> Optional[Dict[str, Any]]:
        """Get all games for the current week."""
        try:
            # Get games for the current week by checking multiple days
            # NFL games typically span Thursday-Monday, so we need to look both backwards and forwards
            games_data = {}
            
            # Check the past 5 days and next 4 days for games (Thursday to Monday)
            # This ensures we catch Thursday games even if they're further back
            for days_offset in range(-5, 5):  # -5 to +4 days
                check_date = datetime.now() + timedelta(days=days_offset)
                date_str = check_date.strftime("%Y%m%d")
                
                response = self.tank01.get_daily_scoreboard(game_date=date_str, top_performers=True)
                
                if response and 'body' in response:
                    day_games = response['body']
                    if day_games:
                        # Verify these are the right week games
                        for game_id, game_data in day_games.items():
                            game_info = self._get_game_info(game_id)
                            if game_info and game_info.get('gameWeek') == f'Week {week}':
                                games_data[game_id] = {
                                    'game_data': game_data,
                                    'game_info': game_info,
                                    'date': date_str
                                }
                                self.logger.info(f"Found Week {week} game: {game_id} on {date_str}")
            
            # If we didn't find any games, try a broader search
            if not games_data:
                self.logger.warning(f"No games found for Week {week} in the standard range. Trying broader search...")
                # Try looking back up to 7 days and forward 6 days
                for days_offset in range(-7, 7):  # -7 to +6 days
                    check_date = datetime.now() + timedelta(days=days_offset)
                    date_str = check_date.strftime("%Y%m%d")
                    
                    response = self.tank01.get_daily_scoreboard(game_date=date_str, top_performers=True)
                    
                    if response and 'body' in response:
                        day_games = response['body']
                        if day_games:
                            for game_id, game_data in day_games.items():
                                game_info = self._get_game_info(game_id)
                                if game_info and game_info.get('gameWeek') == f'Week {week}':
                                    games_data[game_id] = {
                                        'game_data': game_data,
                                        'game_info': game_info,
                                        'date': date_str
                                    }
                                    self.logger.info(f"Found Week {week} game in broader search: {game_id} on {date_str}")
            
            # Special check for Thursday games - they might be further back
            thursday_games = self._find_thursday_games(week, season)
            if thursday_games:
                games_data.update(thursday_games)
                self.logger.info(f"Added {len(thursday_games)} Thursday games to the results")
            
            self.logger.info(f"Found {len(games_data)} total games for Week {week}")
            return games_data if games_data else None
            
        except Exception as e:
            self.logger.error(f"Error getting current week games: {e}")
            return None

    def _find_thursday_games(self, week: int, season: str) -> Dict[str, Any]:
        """Specifically look for Thursday games for the given week."""
        try:
            thursday_games = {}
            
            # Look back up to 10 days to find Thursday games
            for days_back in range(1, 11):  # Check past 10 days
                check_date = datetime.now() - timedelta(days=days_back)
                date_str = check_date.strftime("%Y%m%d")
                
                # Check if this date is a Thursday
                if check_date.weekday() == 3:  # Thursday is weekday 3
                    self.logger.info(f"Checking Thursday {date_str} for Week {week} games...")
                    
                    response = self.tank01.get_daily_scoreboard(game_date=date_str, top_performers=True)
                    
                    if response and 'body' in response:
                        day_games = response['body']
                        if day_games:
                            for game_id, game_data in day_games.items():
                                game_info = self._get_game_info(game_id)
                                if game_info and game_info.get('gameWeek') == f'Week {week}':
                                    thursday_games[game_id] = {
                                        'game_data': game_data,
                                        'game_info': game_info,
                                        'date': date_str
                                    }
                                    self.logger.info(f"Found Thursday Week {week} game: {game_id} on {date_str}")
            
            return thursday_games
            
        except Exception as e:
            self.logger.error(f"Error finding Thursday games: {e}")
            return {}

    def _get_game_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed game information for a specific game."""
        try:
            response = self.tank01.get_game_info(game_id=game_id)
            return response.get('body') if response else None
        except Exception as e:
            self.logger.error(f"Error getting game info for {game_id}: {e}")
            return None

    def _process_games_data(self, games_data: Dict[str, Any], week: int, season: str) -> Dict[str, Any]:
        """Process and format the games data."""
        processed_games = []
        
        for game_id, game_info in games_data.items():
            try:
                game_data = game_info['game_data']
                detailed_info = game_info['game_info']
                date = game_info['date']
                
                # Extract game details
                game_details = {
                    'game_id': game_id,
                    'date': date,
                    'week': week,
                    'season': season,
                    'home_team': detailed_info.get('home', 'Unknown'),
                    'away_team': detailed_info.get('away', 'Unknown'),
                    'venue': detailed_info.get('venue', 'Unknown'),
                    'game_time_et': detailed_info.get('gameTime', 'Unknown'),
                    'game_time_pt': self._convert_to_pacific(detailed_info.get('gameTime', 'Unknown')),
                    'game_time_epoch': detailed_info.get('gameTime_epoch', 'Unknown'),
                    'game_time_utc': detailed_info.get('gameTime_utc_iso8601', 'Unknown'),
                    'game_status': detailed_info.get('gameStatus', 'Unknown'),
                    'game_status_code': detailed_info.get('gameStatusCode', 'Unknown'),
                    'season_type': detailed_info.get('seasonType', 'Regular Season'),
                    'neutral_site': detailed_info.get('neutralSite', 'False'),
                    'espn_id': detailed_info.get('espnID', 'Unknown'),
                    'espn_link': detailed_info.get('espnLink', 'Unknown'),
                    'cbs_link': detailed_info.get('cbsLink', 'Unknown'),
                    'team_id_home': detailed_info.get('teamIDHome', 'Unknown'),
                    'team_id_away': detailed_info.get('teamIDAway', 'Unknown')
                }
                
                # Add any additional game data
                if 'topPerformers' in game_data:
                    game_details['top_performers'] = game_data['topPerformers']
                
                processed_games.append(game_details)
                
            except Exception as e:
                self.logger.error(f"Error processing game {game_id}: {e}")
                continue
        
        # Sort games by game time
        processed_games.sort(key=lambda x: x.get('game_time_epoch', '0'))
        
        return {
            'season_context': {
                'current_week': week,
                'season': season,
                'season_type': 'Regular Season',
                'extraction_date': datetime.now().isoformat()
            },
            'games': processed_games,
            'total_games': len(processed_games),
            'api_usage': self.tank01.get_api_usage()
        }

    def _convert_to_pacific(self, game_time_et: str) -> str:
        """Convert Eastern Time to Pacific Time."""
        try:
            if game_time_et == 'Unknown' or not game_time_et:
                return 'Unknown'
            
            # Parse the time (assuming format like "8:20p" or "1:00p")
            time_str = game_time_et.replace('p', ' PM').replace('a', ' AM')
            if ':' not in time_str:
                return game_time_et
            
            # Add current date for timezone conversion
            today = datetime.now().date()
            time_parts = time_str.split(' ')
            if len(time_parts) == 2:
                time_part, ampm = time_parts
                hour, minute = time_part.split(':')
                hour = int(hour)
                if ampm == 'PM' and hour != 12:
                    hour += 12
                elif ampm == 'AM' and hour == 12:
                    hour = 0
                
                # Create datetime object in Eastern time
                et_tz = pytz.timezone('US/Eastern')
                pt_tz = pytz.timezone('US/Pacific')
                
                dt_et = et_tz.localize(datetime.combine(today, datetime.min.time().replace(hour=hour, minute=int(minute))))
                dt_pt = dt_et.astimezone(pt_tz)
                
                # Format back to readable time
                return dt_pt.strftime("%I:%M%p").lower().replace('am', 'a').replace('pm', 'p')
            
            return game_time_et
            
        except Exception as e:
            self.logger.error(f"Error converting time {game_time_et}: {e}")
            return game_time_et

    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report of NFL matchups."""
        try:
            report = []
            
            # Header
            report.append("# NFL Current Week Team Matchups")
            report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**Week:** {data['season_context']['current_week']}")
            report.append(f"**Season:** {data['season_context']['season']}")
            report.append("")
            
            # API Usage (using centralized manager)
            report.append(self.usage_manager.get_usage_summary_for_markdown())
            report.append("")
            
            # Games Summary
            games = data.get('games', [])
            report.append(f"## Games Summary ({len(games)} games)")
            report.append("")
            
            if not games:
                report.append("No games found for the current week.")
                return "\n".join(report)
            
            # Group games by day
            games_by_day = {}
            for game in games:
                date = game['date']
                if date not in games_by_day:
                    games_by_day[date] = []
                games_by_day[date].append(game)
            
            # Display games by day
            for date in sorted(games_by_day.keys()):
                day_games = games_by_day[date]
                day_name = datetime.strptime(date, '%Y%m%d').strftime('%A, %B %d, %Y')
                
                report.append(f"### {day_name}")
                report.append("")
                
                for game in day_games:
                    report.append(f"**{game['away_team']} @ {game['home_team']}**")
                    report.append(f"- **Time:** {game['game_time_et']} ET / {game['game_time_pt']} PT")
                    report.append(f"- **Venue:** {game['venue']}")
                    report.append(f"- **Status:** {game['game_status']}")
                    report.append(f"- **Game ID:** {game['game_id']}")
                    report.append("")
            
            # Fantasy Football Context
            report.append("## Fantasy Football Context")
            report.append("")
            report.append("### Game Timing for Roster Decisions")
            report.append("")
            report.append("**Important:** You cannot change your fantasy roster after a player's game has started.")
            report.append("")
            report.append("**Game Times by Day:**")
            report.append("")
            
            for date in sorted(games_by_day.keys()):
                day_games = games_by_day[date]
                day_name = datetime.strptime(date, '%Y%m%d').strftime('%A')
                
                report.append(f"**{day_name}:**")
                for game in day_games:
                    report.append(f"- {game['away_team']} @ {game['home_team']}: {game['game_time_et']} ET / {game['game_time_pt']} PT")
                report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating markdown report: {e}")
            return f"# Error generating report: {e}"

    def run(self) -> bool:
        """Run the complete NFL matchups extraction process."""
        try:
            self.logger.info("Starting NFL matchups extraction...")
            
            # Extract data
            data = self.extract_nfl_matchups()
            
            # Generate timestamp
            timestamp = self.file_manager.generate_timestamp()
            
            # Generate markdown report
            markdown_report = self.generate_markdown_report(data)
            
            # Save outputs
            clean_file = self.file_manager.save_clean_data(
                "tank01", "nfl_matchups", markdown_report, timestamp
            )
            
            raw_file = self.file_manager.save_raw_data(
                "tank01", "nfl_matchups", data, timestamp
            )
            
            # Save execution log
            self.execution_stats['end_time'] = datetime.now()
            self.execution_stats['duration'] = (
                self.execution_stats['end_time'] - self.execution_stats['start_time']
            ).total_seconds()
            
            log_file = self.file_manager.save_execution_log(
                "tank01", "nfl_matchups", self.execution_stats, timestamp
            )
            
            self.logger.info(f"NFL matchups extraction completed successfully!")
            self.logger.info(f"Clean data saved to: {clean_file}")
            self.logger.info(f"Raw data saved to: {raw_file}")
            self.logger.info(f"Execution log saved to: {log_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"NFL matchups extraction failed: {e}")
            self.execution_stats['errors'] += 1
            return False


def main():
    """Main execution function."""
    extractor = NFLMatchupsExtractor()
    success = extractor.run()
    
    if success:
        print("✅ NFL matchups extraction completed successfully!")
        sys.exit(0)
    else:
        print("❌ NFL matchups extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
