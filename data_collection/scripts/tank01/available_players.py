#!/usr/bin/env python3
"""
Tank01 Available Players Data Collection Script

This script fetches comprehensive Tank01 API data for available players from Yahoo Fantasy Football.
It processes players from the Yahoo available players output and enriches them with Tank01 data.

Configuration:
- DEVELOPMENT_MODE: Set to True for testing with 5 players, False for production with 25 players
- AVAILABLE_PLAYERS_LIMIT: Number of available players to process (5 for dev, 25 for production)
- INJURY_REPORTS_LIMIT: Number of injury report players to process (0 for now, configurable)
- TOP_AVAILABLE_LIMIT: Number of top available players to process (0 for now, configurable)

Features:
- Configurable player limits for different sections
- Comprehensive Tank01 data extraction
- Team defense handling with appropriate data display
- RapidAPI usage tracking with Pacific Time Zone
- Batch API optimization for efficiency
- Player matching with multiple fallback strategies
"""

import json
import logging
import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pytz

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data_collection.scripts.shared.tank01_client import SimpleTank01Client
from data_collection.scripts.shared.file_utils import DataFileManager

# Configuration
DEVELOPMENT_MODE = False  # Set to False for production

# Import player limits from config
from config.player_limits import DEFAULT_PLAYER_LIMITS, get_player_limits

# Use position-based limits instead of total limit
PLAYER_LIMITS = get_player_limits() if not DEVELOPMENT_MODE else {
    "QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DEF": 2, "FLEX": 2
}

INJURY_REPORTS_LIMIT = 25  # Process 25 injury report players
TOP_AVAILABLE_LIMIT = 15   # Process 15 top available players

# Setup logging
log_dir = Path(__file__).parent.parent.parent / "debug" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "tank01_available_players.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_current_time_pacific():
    """Get current time in Pacific Time Zone"""
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific)

def format_timestamp_pacific(timestamp):
    """Format timestamp to Pacific Time Zone"""
    if not timestamp:
        return "N/A"
    
    try:
        # RapidAPI reset timestamp contains seconds remaining until reset, not Unix timestamp
        # Calculate when the reset will occur by adding to current time
        current_time = get_current_time_pacific()
        reset_time = current_time + timedelta(seconds=timestamp)
        return reset_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except (ValueError, TypeError) as e:
        return f"Invalid timestamp: {timestamp}"

def normalize_team_abbreviation(team_abv, source_api='yahoo'):
    """Normalize team abbreviation to standard format using comprehensive mapping"""
    if not team_abv:
        return team_abv
    
    # Import team mapping utility
    from ..shared.team_mapping import normalize_team_abbreviation as normalize_team
    
    return normalize_team(team_abv, source_api)

class Tank01AvailablePlayersCollector:
    def __init__(self):
        self.tank01 = SimpleTank01Client()
        self.file_manager = DataFileManager()
        self.stats = {
            "start_time": datetime.now(),
            "api_calls": 0,
            "players_processed": 0,
            "players_matched": 0,
            "players_unmatched": 0,
            "errors": 0
        }
        
        # Cache for batch data
        self.cached_players = {}
        self.cached_projections = {}
        self.cached_depth_charts = {}
        self.cached_teams = {}
        
    def load_yahoo_available_players(self) -> Dict[str, Any]:
        """Load the latest Yahoo available players data"""
        try:
            # Find the latest available players file
            # Get the data_collection root directory
            script_dir = Path(__file__).parent
            data_collection_root = script_dir.parent.parent
            outputs_dir = data_collection_root / "outputs" / "yahoo" / "available_players"
            
            if not outputs_dir.exists():
                raise FileNotFoundError(f"Yahoo available players output directory not found: {outputs_dir}")
            
            # Get the most recent file
            files = list(outputs_dir.glob("*_available_players_raw_data.json"))
            if not files:
                raise FileNotFoundError("No Yahoo available players raw data files found")
            
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            logger.info(f"Loading Yahoo available players from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {len(data['available_players'])} available players from Yahoo")
            return data
            
        except Exception as e:
            logger.error(f"Error loading Yahoo available players: {e}")
            self.stats["errors"] += 1
            raise
    
    def extract_players_by_section(self, yahoo_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Extract players from different sections based on position-based configuration limits"""
        available_players = yahoo_data.get('available_players', [])
        
        # Filter players by position with limits
        available_limited = self._filter_players_by_position_limits(available_players)
        
        # For now, injury reports and top available are empty (limits set to 0)
        injury_reports = []  # Would extract from yahoo_data if limit > 0
        top_available = []   # Would extract from yahoo_data if limit > 0
        
        total_expected = sum(PLAYER_LIMITS.values())
        logger.info(f"Extracting players with position-based limits:")
        logger.info(f"  Available Players: {len(available_limited)} (expected: {total_expected})")
        logger.info(f"  Position limits: {PLAYER_LIMITS}")
        logger.info(f"  Injury Reports: {len(injury_reports)} (limit: {INJURY_REPORTS_LIMIT})")
        logger.info(f"  Top Available: {len(top_available)} (limit: {TOP_AVAILABLE_LIMIT})")
        
        return {
            'available_players': available_limited,
            'injury_reports': injury_reports,
            'top_available': top_available
        }
    
    def _filter_players_by_position_limits(self, players: List[Dict]) -> List[Dict]:
        """Filter players by position-based limits"""
        position_counts = {pos: 0 for pos in PLAYER_LIMITS.keys()}
        filtered_players = []
        
        for player in players:
            position = player.get('display_position', 'Unknown')
            
            # Handle multi-position players (FLEX)
            if position in ['W/R/T', 'W/R', 'Q/W/R/T']:
                position = 'FLEX'
            
            # Check if we need more players for this position
            if position in position_counts and position_counts[position] < PLAYER_LIMITS[position]:
                filtered_players.append(player)
                position_counts[position] += 1
                
                # Log progress for first few players of each position
                if position_counts[position] <= 3:
                    logger.info(f"  Added {position} player {position_counts[position]}: {player.get('name', {}).get('full', 'Unknown')}")
        
        # Log final counts
        for position, count in position_counts.items():
            limit = PLAYER_LIMITS[position]
            logger.info(f"  {position}: {count}/{limit} players")
        
        return filtered_players
    
    def match_player_to_tank01(self, yahoo_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Match a Yahoo player to Tank01 player data"""
        try:
            yahoo_id = yahoo_player.get('player_id')
            full_name = yahoo_player.get('name', {}).get('full', '')
            team_abv = yahoo_player.get('editorial_team_abbr', '')
            position = yahoo_player.get('display_position', '')
            
            # Strategy 1: Direct Yahoo ID match
            if yahoo_id in self.cached_players:
                player = self.cached_players[yahoo_id]
                logger.debug(f"Direct Yahoo ID match for {full_name}: {player.get('playerID')}")
                return player
            
            # Strategy 2: Exact name + team match
            for player in self.cached_players.values():
                if (player.get('fullName', '').lower() == full_name.lower() and 
                    player.get('team', '').upper() == team_abv.upper()):
                    logger.debug(f"Exact name + team match for {full_name}: {player.get('playerID')}")
                    return player
            
            # Strategy 3: Last name + team match
            last_name = yahoo_player.get('name', {}).get('last', '')
            for player in self.cached_players.values():
                if (player.get('lastName', '').lower() == last_name.lower() and 
                    player.get('team', '').upper() == team_abv.upper()):
                    logger.debug(f"Last name + team match for {full_name}: {player.get('playerID')}")
                    return player
            
            # Strategy 4: Use get_player_info API for unmatched players
            logger.info(f"Attempting get_player_info API call for unmatched player: {full_name}")
            player_info_response = self.tank01.get_player_info(full_name, team_abv)
            if player_info_response and player_info_response.get('body'):
                player_info = player_info_response.get('body')
                if isinstance(player_info, list) and len(player_info) > 0:
                    player = player_info[0]
                    logger.info(f"get_player_info match for {full_name}: {player.get('playerID')}")
                    return player
                elif isinstance(player_info, dict):
                    logger.info(f"get_player_info match for {full_name}: {player_info.get('playerID')}")
                    return player_info
            
            logger.warning(f"No Tank01 match found for {full_name} ({team_abv})")
            return None
            
        except Exception as e:
            logger.error(f"Error matching player {full_name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def get_player_specific_news(self, player: Dict[str, Any], yahoo_player: Dict[str, Any]) -> List[Dict]:
        """Get player-specific news"""
        try:
            player_id = player.get('playerID')
            team_abv = normalize_team_abbreviation(player.get('team', ''))
            position = player.get('pos', '')
            
            if position == 'DEF':
                # For team defense, get team news (no defense-specific filter available)
                news_response = self.tank01.get_news(team_abv=team_abv, recent_news=10)
                news = news_response.get('body', []) if news_response else []
                logger.debug(f"Team defense news for {team_abv}: {len(news)} articles")
            else:
                # For individual players, get player-specific news
                news_response = self.tank01.get_news(player_id=player_id, recent_news=5)
                news = news_response.get('body', []) if news_response else []
                if not news:
                    # Fallback to team news if no player-specific news
                    news_response = self.tank01.get_news(team_abv=team_abv, recent_news=5)
                    news = news_response.get('body', []) if news_response else []
                logger.debug(f"Player news for {player_id}: {len(news)} articles")
            
            return news
            
        except Exception as e:
            logger.error(f"Error getting news for player {player.get('fullName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
            return []
    
    def get_player_game_stats(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Get player game statistics to infer injury status and performance (matching my_roster logic)"""
        try:
            player_id = player.get('playerID')
            if not player_id:
                return {
                    'injury_status': 'No recent data',
                    'last_game_played': 'N/A',
                    'recent_games': [],
                    'total_games': 0
                }
            
            game_stats_response = self.tank01.get_player_game_stats(player_id, season="2024")
            game_stats = game_stats_response.get('body', {})
            
            if isinstance(game_stats, dict):
                # Convert to list and sort by game date (most recent first)
                game_list = [(game_id, game_data) for game_id, game_data in game_stats.items()]
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
                    'total_games': len(game_stats)
                }
            
            logger.debug(f"Retrieved game stats for player {player_id}")
            
        except Exception as e:
            logger.error(f"Error getting game stats for player {player.get('fullName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
        
        return {
            'injury_status': 'No recent data',
            'last_game_played': 'N/A',
            'recent_games': [],
            'total_games': 0
        }
    
    def get_depth_chart_position(self, player: Dict[str, Any]) -> Optional[Dict]:
        """Get player's depth chart position (matching my_roster logic)"""
        try:
            player_id = player.get('playerID')
            team_abv = normalize_team_abbreviation(player.get('team', ''))
            position = player.get('pos')
            
            if not team_abv or not position or position == 'DEF':
                return None
            
            # Get depth chart for this team
            team_chart = self.cached_depth_charts.get(team_abv)
            if not team_chart:
                return None
            
            depth_chart = team_chart.get('depthChart', {})
            position_group = depth_chart.get(position, [])
            
            # Find this player in the depth chart
            for i, depth_player in enumerate(position_group):
                if depth_player.get('playerID') == player_id:
                    opportunity = 'High' if i < 2 else 'Limited'
                    return {
                        'depth_position': depth_player.get('depthPosition', 'Unknown'),
                        'depth_rank': i + 1,
                        'opportunity': opportunity,
                        'total_at_position': len(position_group)
                    }
            
            logger.debug(f"Depth chart position not found for {player.get('longName', 'Unknown')}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting depth chart for player {player.get('longName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
            return None
    
    def get_team_context(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Get team performance context for fantasy outlook (matching my_roster logic)"""
        try:
            team_abv = normalize_team_abbreviation(player.get('team', ''))
            if not team_abv:
                return {
                    'team_performance': 'Unknown',
                    'division': 'Unknown',
                    'conference': 'Unknown',
                    'fantasy_outlook': 'Unknown',
                    'top_performers': {},
                    'current_streak': {}
                }
            
            team_data = self.cached_teams.get(team_abv)
            if team_data:
                wins = int(team_data.get('wins', '0'))
                losses = int(team_data.get('loss', '0'))
                
                # Determine fantasy outlook based on team performance
                if wins > losses:
                    fantasy_outlook = 'Positive'
                elif wins == losses:
                    fantasy_outlook = 'Neutral'
                else:
                    fantasy_outlook = 'Challenging'
                
                return {
                    'team_performance': f"{wins}-{losses}",
                    'division': team_data.get('division', 'Unknown'),
                    'conference': team_data.get('conferenceAbv', 'Unknown'),
                    'fantasy_outlook': fantasy_outlook,
                    'top_performers': team_data.get('topPerformers', {}),
                    'current_streak': team_data.get('currentStreak', {})
                }
            
            logger.debug(f"Team context not found for {team_abv}")
            
        except Exception as e:
            logger.error(f"Error getting team context for player {player.get('fullName', 'Unknown')}: {e}")
            self.stats["errors"] += 1
        
        return {
            'team_performance': 'Unknown',
            'division': 'Unknown',
            'conference': 'Unknown',
            'fantasy_outlook': 'Unknown',
            'top_performers': {},
            'current_streak': {}
        }
    
    def cache_batch_data(self):
        """Cache large datasets to optimize API calls"""
        try:
            logger.info("Caching Tank01 batch data...")
            
            # Cache all players
            logger.info("Caching player database...")
            player_list_response = self.tank01.get_player_list()
            all_players = player_list_response.get('body', [])
            for player in all_players:
                yahoo_id = player.get('yahooID')
                if yahoo_id:
                    self.cached_players[yahoo_id] = player
            logger.info(f"Cached {len(self.cached_players)} players with Yahoo IDs")
            
            # Cache weekly projections (using current week 1, season 2025)
            logger.info("Caching weekly projections...")
            projections_response = self.tank01.get_weekly_projections(week=1, archive_season=2025)
            projections = projections_response.get('body', {})
            if isinstance(projections, dict):
                # Store the entire projections response for later processing
                self.cached_projections = projections
                logger.info(f"Cached weekly projections data structure with keys: {list(projections.keys())}")
            else:
                logger.warning(f"Projections response is not a dict: {type(projections)}")
                self.cached_projections = {}
            
            # Cache depth charts
            logger.info("Caching depth charts...")
            depth_charts_response = self.tank01.get_depth_charts()
            depth_charts = depth_charts_response.get('body', [])
            if isinstance(depth_charts, list):
                for chart in depth_charts:
                    team_abv = chart.get('teamAbv')
                    if team_abv:
                        self.cached_depth_charts[team_abv] = chart
                logger.info(f"Cached {len(self.cached_depth_charts)} depth charts")
            else:
                logger.warning(f"Depth charts response is not a list: {type(depth_charts)}")
                logger.info(f"Cached {len(self.cached_depth_charts)} depth charts")
            
            # Cache teams data
            logger.info("Caching teams data...")
            teams_response = self.tank01.get_nfl_teams()
            teams = teams_response.get('body', [])
            for team in teams:
                team_abv = team.get('teamAbv')
                if team_abv:
                    self.cached_teams[team_abv] = team
            logger.info(f"Cached {len(self.cached_teams)} teams")
            
        except Exception as e:
            logger.error(f"Error caching batch data: {e}")
            self.stats["errors"] += 1
    
    def process_players(self, players_by_section: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Process all players and enrich with Tank01 data"""
        processed_data = {
            'available_players': [],
            'injury_reports': [],
            'top_available': []
        }
        
        for section_name, players in players_by_section.items():
            logger.info(f"Processing {len(players)} players in {section_name} section...")
            
            for yahoo_player in players:
                try:
                    self.stats["players_processed"] += 1
                    
                    # Match to Tank01
                    tank01_player = self.match_player_to_tank01(yahoo_player)
                    if not tank01_player:
                        self.stats["players_unmatched"] += 1
                        continue
                    
                    self.stats["players_matched"] += 1
                    
                    # Get additional Tank01 data
                    news = self.get_player_specific_news(tank01_player, yahoo_player)
                    game_stats = self.get_player_game_stats(tank01_player)
                    depth_chart = self.get_depth_chart_position(tank01_player)
                    team_context = self.get_team_context(tank01_player)
                    
                    # Get projection data (matching my_roster logic)
                    player_id = tank01_player.get('playerID')
                    projection = {}
                    
                    if self.cached_projections:
                        # Check if this is a team defense
                        if tank01_player.get('isTeamDefense'):
                            team_id = tank01_player.get('teamID')
                            if team_id and 'teamDefenseProjections' in self.cached_projections:
                                team_def_projs = self.cached_projections['teamDefenseProjections']
                                if team_id in team_def_projs:
                                    projection = team_def_projs[team_id]
                                    projection['playerID'] = player_id
                                    projection['isTeamDefense'] = True
                        else:
                            # Regular player projections
                            if 'playerProjections' in self.cached_projections:
                                player_projs = self.cached_projections['playerProjections']
                                if player_id in player_projs:
                                    projection = player_projs[player_id]
                    
                    # Combine all data
                    enriched_player = {
                        'yahoo_data': yahoo_player,
                        'tank01_data': tank01_player,
                        'projection': projection,
                        'news': news,
                        'game_stats': game_stats,
                        'depth_chart': depth_chart,
                        'team_context': team_context
                    }
                    
                    processed_data[section_name].append(enriched_player)
                    
                except Exception as e:
                    logger.error(f"Error processing player {yahoo_player.get('name', {}).get('full', 'Unknown')}: {e}")
                    self.stats["errors"] += 1
                    continue
        
        return processed_data
    
    def generate_markdown_report(self, processed_data: Dict[str, List[Dict]], yahoo_metadata: Dict[str, Any]) -> str:
        """Generate comprehensive markdown report"""
        current_time = get_current_time_pacific()
        
        # Get API usage info
        usage_info = self.tank01.get_api_usage()
        total_calls = usage_info.get('total_calls', 0)
        
        # If total_calls is 0, get it from the client directly
        if total_calls == 0:
            total_calls = self.tank01.tank01_client.api_calls_made
        
        # Extract season context
        season_context = self._extract_season_context(yahoo_metadata)
        
        report = f"""# Tank01 Available Players Data

**Extraction Date:** {current_time.strftime("%Y-%m-%d %H:%M:%S %Z")}
**Development Mode:** {DEVELOPMENT_MODE}
**Source:** Yahoo Fantasy Football Available Players
**League:** {yahoo_metadata.get('league_info', {}).get('league_name', 'Unknown')}
**League Key:** {yahoo_metadata.get('league_info', {}).get('league_key', 'Unknown')}

## Season & Week Context
- **NFL Season:** {season_context.get('nfl_season', 'Unknown')}
- **Current Week:** {season_context.get('current_week', 'Unknown')}
- **Season Phase:** {season_context.get('season_phase', 'Unknown')}
- **Data Source:** {season_context.get('data_source', 'Unknown')}

### Week Information
- **Week Start:** {season_context.get('week_info', {}).get('week_start', 'Unknown')}
- **Week End:** {season_context.get('week_info', {}).get('week_end', 'Unknown')}
- **Week Status:** {season_context.get('week_info', {}).get('status', 'Unknown')}
- **Week Source:** {season_context.get('week_info', {}).get('source', 'Unknown')}

### Verification Notes
{chr(10).join(f"- {note}" for note in season_context.get('verification_notes', []))}

## Configuration
- **Player Limits:** {PLAYER_LIMITS}
- **Injury Reports Limit:** {INJURY_REPORTS_LIMIT}
- **Top Available Limit:** {TOP_AVAILABLE_LIMIT}

## Processing Statistics
- **Players Processed:** {self.stats['players_processed']}
- **Players Matched:** {self.stats['players_matched']}
- **Players Unmatched:** {self.stats['players_unmatched']}
- **Match Rate:** {(self.stats['players_matched'] / max(self.stats['players_processed'], 1) * 100):.1f}%
- **Errors:** {self.stats['errors']}
- **Execution Time:** {(datetime.now() - self.stats['start_time']).total_seconds():.2f}s

## API Usage (RapidAPI Headers)
- **Current Time (Pacific):** {current_time.strftime("%Y-%m-%d %H:%M:%S %Z")}
- **Total API Calls:** {total_calls}
- **Daily Limit:** {usage_info.get('daily_limit', 'Unknown')}
- **Remaining Calls:** {usage_info.get('remaining_calls', 'Unknown')}
- **Limit Resets:** {format_timestamp_pacific(usage_info.get('reset_timestamp'))}

"""
        
        # Process each section
        for section_name, players in processed_data.items():
            if not players:
                continue
                
            section_title = section_name.replace('_', ' ').title()
            report += f"\n## {section_title}\n"
            report += f"**Total Players:** {len(players)}\n\n"
            
            # Group by position
            positions = {}
            for player in players:
                position = player['tank01_data'].get('pos', 'UNKNOWN')
                if position not in positions:
                    positions[position] = []
                positions[position].append(player)
            
            for position, pos_players in sorted(positions.items()):
                report += f"\n### {position} ({len(pos_players)} players)\n\n"
                
                for player in pos_players:
                    yahoo_data = player['yahoo_data']
                    tank01_data = player['tank01_data']
                    projection = player['projection']
                    news = player['news']
                    game_stats = player['game_stats']
                    depth_chart = player['depth_chart']
                    team_context = player['team_context']
                    
                    # Player header
                    full_name = yahoo_data.get('name', {}).get('full', 'Unknown')
                    team_abv = yahoo_data.get('editorial_team_abbr', 'Unknown')
                    yahoo_id = yahoo_data.get('player_id', 'Unknown')
                    
                    report += f"#### {full_name} ({tank01_data.get('pos', 'N/A')} - {team_abv})\n\n"
                    
                    # Tank01 Player Information
                    report += f"#### Tank01 Player Information\n"
                    report += f"- **Tank01 ID**: {tank01_data.get('playerID', 'N/A')}\n"
                    report += f"- **Yahoo ID**: {yahoo_id}\n"
                    report += f"- **Long Name**: {tank01_data.get('longName', 'N/A')}\n"
                    report += f"- **Team**: {tank01_data.get('team', 'N/A')}\n"
                    
                    # Conditional display based on player type
                    if tank01_data.get('pos') == 'DEF':
                        # Team Defense Information
                        report += f"#### Team Defense Information\n"
                        report += f"- **Team ID**: {tank01_data.get('teamID', 'N/A')}\n"
                        report += f"- **Team Abbreviation**: {tank01_data.get('team', 'N/A')}\n"
                        report += f"- **Position**: {tank01_data.get('pos', 'N/A')}\n"
                        report += f"- **Is Team Defense**: {tank01_data.get('isTeamDefense', 'N/A')}\n"
                    else:
                        # Cross-Platform IDs
                        report += f"#### Cross-Platform IDs\n"
                        report += f"- **ESPN ID**: {tank01_data.get('espnID', 'N/A')}\n"
                        report += f"- **Sleeper ID**: {tank01_data.get('sleeperBotID', 'N/A')}\n"
                        report += f"- **CBS ID**: {tank01_data.get('cbsPlayerID', 'N/A')}\n"
                        report += f"- **RotoWire ID**: {tank01_data.get('rotoWirePlayerID', 'N/A')}\n"
                        report += f"- **FRef ID**: {tank01_data.get('fRefID', 'Not Available')}\n"
                        report += f"- **Position**: {tank01_data.get('pos', 'N/A')}\n"
                        report += f"- **Jersey Number**: {tank01_data.get('jerseyNum', 'N/A')}\n"
                        report += f"- **Height**: {tank01_data.get('height', 'N/A')}\n"
                        report += f"- **Weight**: {tank01_data.get('weight', 'N/A')}\n"
                        report += f"- **Age**: {tank01_data.get('age', 'N/A')}\n"
                        report += f"- **Experience**: {tank01_data.get('exp', 'N/A')}\n"
                        report += f"- **School**: {tank01_data.get('school', 'N/A')}\n"
                    
                    # Status and Outlook (matching my_roster logic)
                    report += f"\n#### Status and Outlook\n"
                    
                    # Use game stats for injury status and last game
                    injury_status = 'No recent data'
                    last_game_played = 'No recent data'
                    if game_stats and isinstance(game_stats, dict):
                        injury_status = game_stats.get('injury_status', 'No recent data')
                        last_game_played = game_stats.get('last_game_played', 'No recent data')
                    
                    # Use team context for fantasy outlook
                    fantasy_outlook = 'Unknown'
                    if team_context and isinstance(team_context, dict):
                        fantasy_outlook = team_context.get('fantasy_outlook', 'Unknown')
                    
                    report += f"- **Injury Status**: {injury_status}\n"
                    report += f"- **Fantasy Outlook**: {fantasy_outlook}\n"
                    report += f"- **Last Game Played**: {last_game_played}\n"
                    
                    # Fantasy Projections
                    if projection and projection != {}:
                        report += f"\n#### Fantasy Projections\n"
                        report += f"- **Fantasy Points**: {projection.get('fantasyPoints', 'N/A')}\n"
                        
                        # Show fantasy points by format (matching my_roster logic)
                        if 'fantasyPointsDefault' in projection:
                            default_fp = projection['fantasyPointsDefault']
                            if isinstance(default_fp, dict):
                                report += f"- **Fantasy Points by Format:**\n"
                                for format_name, points in default_fp.items():
                                    report += f"  - {format_name}: {points}\n"
                            else:
                                report += f"- **Default Fantasy Points**: {default_fp}\n"
                        
                        # Passing Projections
                        if any(projection.get(key) for key in ['passAttempts', 'passTD', 'passYds', 'int', 'passCompletions']):
                            report += f"- **Passing Projections:**\n"
                            report += f"  - passAttempts: {projection.get('passAttempts', 'N/A')}\n"
                            report += f"  - passTD: {projection.get('passTD', 'N/A')}\n"
                            report += f"  - passYds: {projection.get('passYds', 'N/A')}\n"
                            report += f"  - int: {projection.get('int', 'N/A')}\n"
                            report += f"  - passCompletions: {projection.get('passCompletions', 'N/A')}\n"
                        
                        # Rushing Projections
                        if any(projection.get(key) for key in ['rushYds', 'carries', 'rushTD']):
                            report += f"- **Rushing Projections:**\n"
                            report += f"  - rushYds: {projection.get('rushYds', 'N/A')}\n"
                            report += f"  - carries: {projection.get('carries', 'N/A')}\n"
                            report += f"  - rushTD: {projection.get('rushTD', 'N/A')}\n"
                        
                        # Receiving Projections
                        if any(projection.get(key) for key in ['receptions', 'recTD', 'targets', 'recYds']):
                            report += f"- **Receiving Projections:**\n"
                            report += f"  - receptions: {projection.get('receptions', 'N/A')}\n"
                            report += f"  - recTD: {projection.get('recTD', 'N/A')}\n"
                            report += f"  - targets: {projection.get('targets', 'N/A')}\n"
                            report += f"  - recYds: {projection.get('recYds', 'N/A')}\n"
                        
                        # Kicking Projections
                        if any(projection.get(key) for key in ['fgMade', 'fgMissed', 'xpMade', 'xpMissed']):
                            report += f"- **Kicking Projections:**\n"
                            report += f"  - fgMade: {projection.get('fgMade', 'N/A')}\n"
                            report += f"  - fgMissed: {projection.get('fgMissed', 'N/A')}\n"
                            report += f"  - xpMade: {projection.get('xpMade', 'N/A')}\n"
                            report += f"  - xpMissed: {projection.get('xpMissed', 'N/A')}\n"
                        
                        # Defense Projections
                        if any(projection.get(key) for key in ['interceptions', 'sacks', 'blockKick']):
                            report += f"- **Defense Projections:**\n"
                            report += f"  - interceptions: {projection.get('interceptions', 'N/A')}\n"
                            report += f"  - sacks: {projection.get('sacks', 'N/A')}\n"
                            report += f"  - blockKick: {projection.get('blockKick', 'N/A')}\n"
                    
                    # Depth Chart Position (skip for team defense)
                    if tank01_data.get('pos') != 'DEF' and depth_chart and depth_chart != {}:
                        report += f"\n#### Depth Chart Position\n"
                        report += f"- **Position**: {depth_chart.get('depth_position', 'Unknown')}\n"
                        report += f"- **Rank**: {depth_chart.get('depth_rank', 'N/A')}\n"
                        report += f"- **Opportunity**: {depth_chart.get('opportunity', 'Unknown')}\n"
                    
                    # Recent News
                    if news:
                        if tank01_data.get('pos') == 'DEF':
                            report += f"\n#### Recent Team News\n"
                            report += f"*Note: For team defense, showing most recent team news (publication dates not available from API)*\n\n"
                        else:
                            report += f"\n#### Recent News\n"
                            report += f"*Note: Publication dates not available from Tank01 API*\n\n"
                        
                        max_news = 10 if tank01_data.get('pos') == 'DEF' else 5
                        for i, article in enumerate(news[:max_news], 1):
                            title = article.get('title', 'N/A')
                            url = article.get('url', '')
                            image = article.get('image', '')
                            
                            report += f"{i}. **{title}**\n"
                            if url:
                                report += f"   - [Read More]({url})\n"
                            if image:
                                report += f"   - [Image]({image})\n"
                            report += "\n"
                    
                    # Recent Performance (matching my_roster logic)
                    if game_stats and game_stats.get('recent_games'):
                        report += f"\n#### Recent Performance\n"
                        for i, game in enumerate(game_stats['recent_games'][:3], 1):
                            game_id = game.get('gameID', 'Unknown')
                            snap_counts = game.get('snapCounts', {})
                            off_snap_pct = float(snap_counts.get('offSnapPct', '0'))
                            report += f"- **Game {i}**: {game_id} - {off_snap_pct*100:.1f}% offensive snaps\n"
                    else:
                        report += f"\n#### Recent Performance\n"
                        report += f"- **Status**: No recent game data available\n"
                    
                    # Team Context (matching my_roster logic)
                    if team_context and team_context != {}:
                        report += f"\n#### Team Context\n"
                        report += f"- **Team Performance**: {team_context.get('team_performance', 'Unknown')}\n"
                        report += f"- **Division**: {team_context.get('division', 'Unknown')}\n"
                        report += f"- **Conference**: {team_context.get('conference', 'Unknown')}\n"
                    
                    report += "\n---\n\n"
        
        # Add comprehensive API usage tracking section
        report += f"\n## 📊 API Usage Tracking\n\n"
        
        # Get detailed API usage info
        usage_info = self.tank01.get_api_usage()
        total_calls = usage_info.get('total_calls', 0)
        
        # If total_calls is 0, get it from the client directly
        if total_calls == 0:
            total_calls = self.tank01.tank01_client.api_calls_made
        
        report += f"### Tank01 API Session Summary\n"
        report += f"- **Total API Calls Made**: {total_calls}\n"
        report += f"- **Base Calls**: 4\n"
        report += f"  - Player Database: 1 (getNFLPlayerList)\n"
        report += f"  - Weekly Projections: 1 (getNFLProjections - batch)\n"
        report += f"  - Depth Charts: 1 (getNFLDepthCharts)\n"
        report += f"  - Teams Data: 1 (getNFLTeams)\n"
        
        # Calculate player-specific calls
        players_processed = self.stats['players_processed']
        news_calls = players_processed
        game_stats_calls = players_processed
        player_info_calls = self.stats['players_unmatched']
        
        report += f"- **Player-Specific Calls**: {news_calls + game_stats_calls + player_info_calls}\n"
        report += f"  - News Calls: {news_calls} (getNFLNews - player-specific)\n"
        report += f"  - Game Stats Calls: {game_stats_calls} (getNFLGamesForPlayer)\n"
        report += f"  - Player Info Calls: {player_info_calls} (getNFLPlayerInfo - for unmatched)\n"
        
        report += f"\n### Current API Status (RapidAPI Headers)\n"
        report += f"- **Report Generated**: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        report += f"- **Calls Made This Session**: {total_calls}\n"
        report += f"- **Daily Limit**: {usage_info.get('daily_limit', 'N/A')}\n"
        report += f"- **Remaining Calls Today**: {usage_info.get('remaining_calls', 'N/A')}\n"
        report += f"- **Usage Percentage**: {usage_info.get('percentage_used', 0):.1f}%\n"
        report += f"- **Data Source**: {usage_info.get('data_source', 'Unknown')}\n"
        if usage_info.get('reset_timestamp'):
            report += f"- **Limit Resets**: {format_timestamp_pacific(usage_info.get('reset_timestamp'))}\n"
        report += f"- **Client Available**: {usage_info.get('available', False)}\n"
        
        report += f"\n### API Efficiency Metrics\n"
        report += f"- **API Calls per Player**: {total_calls / max(players_processed, 1):.1f}\n"
        report += f"- **Players Processed**: {players_processed}\n"
        report += f"- **Match Rate**: {(self.stats['players_matched'] / max(self.stats['players_processed'], 1) * 100):.1f}%\n"
        
        report += f"\n### Recommendations\n"
        if total_calls > 100:
            report += f"- ⚠️ **High API Usage**: Consider caching player database between runs\n"
        report += f"- 💡 **Optimization**: Consider running this script once per day to minimize API usage\n"
        report += f"- 📈 **Monitoring**: Track daily usage to stay within 1000 call limit\n"
        
        return report
    
    def _extract_season_context(self, yahoo_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract season and week context from Yahoo data."""
        try:
            current_date = datetime.now()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'data_source': 'Tank01 API',
                'verification_notes': []
            }
            
            # Try to extract season info from Yahoo metadata
            league_info = yahoo_metadata.get('league_info', {})
            if league_info:
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
                current_week = self._extract_current_week_from_yahoo_data()
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
                logger.warning(f"Could not determine week: {e}")
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
            logger.error(f"Error extracting season context: {e}")
            return {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': 'Unknown',
                'data_source': 'Tank01 API',
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
    
    def _extract_current_week_from_yahoo_data(self) -> Optional[Dict[str, Any]]:
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
                logger.warning("Team matchups directory not found")
                return None

            # Get the most recent matchups file
            matchup_files = list(matchups_dir.glob("*_team_matchups_raw_data.json"))
            if not matchup_files:
                logger.warning("No team matchups files found")
                return None

            latest_file = max(matchup_files, key=lambda f: f.stat().st_mtime)
            logger.info(f"Loading team matchups from: {latest_file}")

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
            logger.warning(f"Could not extract current week from Yahoo data: {e}")
            return None
    
    def save_outputs(self, processed_data: Dict[str, List[Dict]], yahoo_metadata: Dict[str, Any]):
        """Save markdown and raw JSON outputs"""
        try:
            # Generate timestamp
            timestamp = self.file_manager.generate_timestamp()
            
            # Generate markdown report
            markdown_content = self.generate_markdown_report(processed_data, yahoo_metadata)
            
            # Save markdown file
            markdown_path = self.file_manager.save_clean_data("tank01", "available_players", markdown_content, timestamp)
            logger.info(f"Saved markdown report: {markdown_path}")
            
            # Extract season context for raw data
            season_context = self._extract_season_context(yahoo_metadata)
            
            # Prepare raw data
            raw_data = {
                "extraction_metadata": {
                    "script": "tank01_available_players.py",
                    "development_mode": DEVELOPMENT_MODE,
                    "configuration": {
                        "player_limits": PLAYER_LIMITS,
                        "injury_reports_limit": INJURY_REPORTS_LIMIT,
                        "top_available_limit": TOP_AVAILABLE_LIMIT
                    },
                    "yahoo_source": yahoo_metadata,
                    "extraction_timestamp": datetime.now().isoformat(),
                    "processing_stats": self.stats,
                    "api_usage": self.tank01.get_api_usage()
                },
                "season_context": season_context,
                "processed_data": processed_data,
                "efficiency_metrics": {
                    "players_processed": self.stats["players_processed"],
                    "players_matched": self.stats["players_matched"],
                    "match_rate": (self.stats["players_matched"] / max(self.stats["players_processed"], 1) * 100),
                    "api_calls_made": self.tank01.get_api_usage().get('total_calls', 0),
                    "execution_time_seconds": (datetime.now() - self.stats["start_time"]).total_seconds(),
                    "report_generated_pacific": get_current_time_pacific().isoformat(),
                    "reset_timestamp_pacific": format_timestamp_pacific(
                        self.tank01.get_api_usage().get('reset_timestamp')
                    )
                }
            }
        
            # Save raw JSON file
            json_path = self.file_manager.save_raw_data("tank01", "available_players", raw_data, timestamp)
            logger.info(f"Saved raw data: {json_path}")
            
        except Exception as e:
            logger.error(f"Error saving outputs: {e}")
            self.stats["errors"] += 1
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting Tank01 Available Players Data Collection")
            logger.info(f"Development Mode: {DEVELOPMENT_MODE}")
            logger.info(f"Player Limits: {PLAYER_LIMITS}")
            logger.info(f"Total Expected Players: {sum(PLAYER_LIMITS.values())}")
            
            # Load Yahoo available players data
            yahoo_data = self.load_yahoo_available_players()
            
            # Extract players by section with limits
            players_by_section = self.extract_players_by_section(yahoo_data)
            
            # Cache batch data for efficiency
            self.cache_batch_data()
            
            # Process all players
            processed_data = self.process_players(players_by_section)
            
            # Save outputs
            self.save_outputs(processed_data, yahoo_data.get('extraction_metadata', {}))
            
            # Final statistics
            execution_time = (datetime.now() - self.stats["start_time"]).total_seconds()
            logger.info(f"Tank01 Available Players collection completed in {execution_time:.2f}s")
            logger.info(f"Processed {self.stats['players_processed']} players")
            logger.info(f"Matched {self.stats['players_matched']} players ({(self.stats['players_matched'] / max(self.stats['players_processed'], 1) * 100):.1f}%)")
            logger.info(f"API calls made: {self.tank01.get_api_usage().get('total_calls', 0)}")
            
        except Exception as e:
            logger.error(f"Fatal error in Tank01 Available Players collection: {e}")
            self.stats["errors"] += 1
            raise

def main():
    """Main entry point with command line argument support"""
    # Declare globals first
    global PLAYER_LIMITS, INJURY_REPORTS_LIMIT, TOP_AVAILABLE_LIMIT
    
    parser = argparse.ArgumentParser(description="Tank01 Available Players Data Collection")
    parser.add_argument(
        "--players", 
        type=int, 
        default=sum(PLAYER_LIMITS.values()),
        help=f"Total number of available players to process (default: {sum(PLAYER_LIMITS.values())})"
    )
    parser.add_argument(
        "--injury-reports",
        type=int,
        default=INJURY_REPORTS_LIMIT,
        help=f"Number of injury report players to process (default: {INJURY_REPORTS_LIMIT})"
    )
    parser.add_argument(
        "--top-available",
        type=int,
        default=TOP_AVAILABLE_LIMIT,
        help=f"Number of top available players to process (default: {TOP_AVAILABLE_LIMIT})"
    )
    
    args = parser.parse_args()
    
    # Update global configuration based on arguments
    # Note: Position-based limits are used instead of total limit
    # args.players is kept for compatibility but not used in filtering
    INJURY_REPORTS_LIMIT = args.injury_reports
    TOP_AVAILABLE_LIMIT = args.top_available
    
    print(f"🏈 Tank01 Available Players Collection")
    print(f"📊 Processing players with position limits: {PLAYER_LIMITS}")
    print(f"📊 Total expected players: {sum(PLAYER_LIMITS.values())}")
    if INJURY_REPORTS_LIMIT > 0:
        print(f"🏥 Processing {INJURY_REPORTS_LIMIT} injury report players")
    if TOP_AVAILABLE_LIMIT > 0:
        print(f"⭐ Processing {TOP_AVAILABLE_LIMIT} top available players")
    print("=" * 50)
    
    collector = Tank01AvailablePlayersCollector()
    collector.run()

if __name__ == "__main__":
    main()
