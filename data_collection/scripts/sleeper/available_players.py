#!/usr/bin/env python3
"""
Sleeper NFL API - Available Players Data Extraction

This script loads the latest Yahoo available players list and enriches it with
comprehensive Sleeper NFL player data. It matches each available player to the
Sleeper database and extracts ALL available Sleeper player information.

Purpose: Clean, focused data extraction for available players using Sleeper API
Output: Organized markdown file + raw JSON of available players with Sleeper data
Focus: Extract ALL available Sleeper player data for free agents, no analysis
"""

import os
import sys
import json
import glob
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import player limits from config
from config.player_limits import DEFAULT_PLAYER_LIMITS, get_player_limits

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from sleeper_client import SimpleSleeperClient
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager
from team_mapping import normalize_team_abbreviation

# Configuration
DEVELOPMENT_MODE = False  # Set to False for production

def parse_arguments():
    """Parse command line arguments for configurable player limits"""
    parser = argparse.ArgumentParser(description='Sleeper Available Players Data Extraction')
    
    # Individual position limits
    parser.add_argument('--qb', type=int, help='Number of QB players to collect (default: 20)')
    parser.add_argument('--rb', type=int, help='Number of RB players to collect (default: 20)')
    parser.add_argument('--wr', type=int, help='Number of WR players to collect (default: 20)')
    parser.add_argument('--te', type=int, help='Number of TE players to collect (default: 20)')
    parser.add_argument('--k', type=int, help='Number of K players to collect (default: 20)')
    parser.add_argument('--defense', type=int, help='Number of DEF players to collect (default: 10)')
    parser.add_argument('--flex', type=int, help='Number of FLEX players to collect (default: 15)')
    
    # Bulk limit
    parser.add_argument('--all', type=int, help='Set all positions to this number (overrides individual limits)')
    
    # Development mode
    parser.add_argument('--dev', action='store_true', help='Enable development mode (reduced limits)')
    
    args = parser.parse_args()
    
    # Get default limits
    if args.dev:
        player_limits = {"QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DEF": 2, "FLEX": 2}
    else:
        player_limits = get_player_limits()
    
    # Apply bulk limit if specified
    if args.all:
        player_limits = {pos: args.all for pos in player_limits.keys()}
    
    # Apply individual limits if specified
    if args.qb is not None:
        player_limits['QB'] = args.qb
    if args.rb is not None:
        player_limits['RB'] = args.rb
    if args.wr is not None:
        player_limits['WR'] = args.wr
    if args.te is not None:
        player_limits['TE'] = args.te
    if args.k is not None:
        player_limits['K'] = args.k
    if args.defense is not None:
        player_limits['DEF'] = args.defense
    if args.flex is not None:
        player_limits['FLEX'] = args.flex
    
    return player_limits

class SleeperAvailablePlayersExtractor:
    """Loads Yahoo available players and enriches with comprehensive Sleeper data."""

    def __init__(self, player_limits: Dict[str, int] = None) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Set player limits (use defaults if not provided)
        self.player_limits = player_limits or get_player_limits()

        self.sleeper = SimpleSleeperClient()
        self.formatter = MarkdownFormatter()
        self.file_manager = DataFileManager()

        self.execution_stats: Dict[str, Any] = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'errors': 0,
            'yahoo_players_loaded': 0,
            'players_processed': 0,
            'players_matched': 0,
            'players_unmatched': 0
        }
    
    def _filter_players_by_position_limits(self, players: List[Dict]) -> List[Dict]:
        """Filter players by position-based limits"""
        position_counts = {pos: 0 for pos in self.player_limits.keys()}
        filtered_players = []
        
        for player in players:
            position = player.get('display_position', 'Unknown')
            
            # Handle multi-position players (FLEX) - same logic as ComprehensiveDataProcessor
            if position in ['W/R/T', 'W/R', 'Q/W/R/T', 'WR,TE', 'RB,TE', 'WR,RB', 'QB,WR']:
                position = 'FLEX'
            
            # Check if we need more players for this position
            if position in position_counts and position_counts[position] < self.player_limits[position]:
                filtered_players.append(player)
                position_counts[position] += 1
                
                # Log progress for first few players of each position
                if position_counts[position] <= 3:
                    self.logger.info(f"  Added {position} player {position_counts[position]}: {player.get('name', {}).get('full', 'Unknown')}")
        
        # Log final counts
        for position, count in position_counts.items():
            limit = self.player_limits[position]
            self.logger.info(f"  {position}: {count}/{limit} players")
        
        return filtered_players

    def extract_all_data(self) -> Dict[str, Any]:
        """Load latest Yahoo available players, match to Sleeper, return consolidated data."""
        try:
            self.logger.info("🚀 Starting Sleeper Available Players Extraction")

            yahoo_players = self._load_latest_yahoo_available_players()
            if not yahoo_players:
                self.logger.error("❌ Could not load Yahoo available players")
                return {}

            self.execution_stats['yahoo_players_loaded'] = len(yahoo_players)
            self.logger.info(f"📄 Loaded {len(yahoo_players)} Yahoo available players")
            
            # Apply position-based limits
            self.logger.info(f"🔍 Applying position-based limits: {self.player_limits}")
            yahoo_players = self._filter_players_by_position_limits(yahoo_players)
            self.logger.info(f"📊 Filtered to {len(yahoo_players)} players after position limits")

            matched_players: List[Dict[str, Any]] = []
            unmatched_players: List[Dict[str, Any]] = []

            # Load Sleeper players DB once and build yahoo_id -> sleeper map
            players_db = self.sleeper.get_nfl_players()
            yahoo_id_to_sleeper: Dict[str, Dict[str, Any]] = {}
            if players_db:
                for sp in players_db.values():
                    sleeper_yahoo_id = sp.get('yahoo_id')
                    if sleeper_yahoo_id is not None and str(sleeper_yahoo_id).strip():
                        yahoo_id_to_sleeper[str(sleeper_yahoo_id)] = sp

            # Process each Yahoo available player
            for yp in yahoo_players:
                self.execution_stats['players_processed'] += 1
                name = self._get_yahoo_player_name(yp)
                team = self._get_yahoo_player_team(yp)
                pos = self._get_yahoo_player_position(yp)
                yahoo_pid = str(yp.get('player_id', '')).strip()

                sleeper_player = None

                # 1) Try direct Yahoo ID mapping
                if yahoo_pid and yahoo_pid in yahoo_id_to_sleeper:
                    sleeper_player = yahoo_id_to_sleeper[yahoo_pid]

                # 2) DEF special-case
                if not sleeper_player and (pos == 'DEF' or self._normalize_name(name) == self._normalize_name(team or '')):
                    sleeper_player = self._match_defense_by_team(players_db, team)

                # 3) Fallback to name+team matching using local players DB
                if not sleeper_player and players_db:
                    name_l = self._normalize_name(name)
                    for sp in players_db.values():
                        sp_name = self._normalize_name(sp.get('full_name') or '')
                        sp_team_raw = sp.get('team')
                        sp_team = normalize_team_abbreviation(sp_team_raw, 'sleeper') if sp_team_raw else ''
                        if name_l == sp_name and (not team or not sp_team or sp_team == team):
                            sleeper_player = sp
                            break

                # 4) Last-name + team/position fallback
                if not sleeper_player and players_db and name:
                    last = self._normalize_name(name).split()[-1]
                    for sp in players_db.values():
                        sp_name = self._normalize_name(sp.get('full_name') or '')
                        sp_team_raw = sp.get('team')
                        sp_team = normalize_team_abbreviation(sp_team_raw, 'sleeper') if sp_team_raw else ''
                        if sp_name.endswith(' ' + last) or sp_name == last:
                            if (team and sp_team == team) or (pos and sp.get('position') == pos):
                                sleeper_player = sp
                                break

                # 5) Final fallback to client's search function
                if not sleeper_player:
                    try:
                        sleeper_player = self.sleeper.match_yahoo_player(name, team)
                    except Exception as e:
                        self.logger.warning(f"Match error for {name} ({team}): {e}")

                if sleeper_player:
                    # Merge core Yahoo identifiers for traceability
                    merged = {
                        'yahoo_player': yp,
                        'sleeper_player': sleeper_player,
                        'mapping': {
                            'yahoo_player_id': yahoo_pid,
                            'sleeper_player_id': sleeper_player.get('player_id'),
                            'matched_via': 'yahoo_id' if (yahoo_pid and sleeper_player and str(sleeper_player.get('yahoo_id', '')) == yahoo_pid) else 'name_team_fallback'
                        }
                    }
                    matched_players.append(merged)
                    self.execution_stats['players_matched'] += 1
                else:
                    unmatched_players.append({
                        'name': name,
                        'team': team,
                        'position': pos,
                        'yahoo_player': yp
                    })
                    self.execution_stats['players_unmatched'] += 1

            # Finalize timing
            self.execution_stats['execution_time'] = (
                datetime.now() - self.execution_stats['start_time']
            ).total_seconds()

            # Extract season context
            season_context = self._extract_season_context()
            
            result: Dict[str, Any] = {
                'extraction_metadata': {
                    'source': 'Sleeper API - Available Players',
                    'extraction_timestamp': datetime.now().isoformat(),
                    'yahoo_source': 'Latest available_players.py output',
                    'execution_stats': self.execution_stats
                },
                'season_context': season_context,
                'matched_players': matched_players,
                'unmatched_players': unmatched_players
            }

            self.logger.info(
                f"✅ Extraction complete: matched {self.execution_stats['players_matched']} / "
                f"{self.execution_stats['players_processed']} players; "
                f"{self.execution_stats['execution_time']:.2f}s"
            )
            return result

        except Exception as exc:
            self.logger.error(f"❌ Error in extract_all_data: {exc}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.execution_stats['errors'] += 1
            return {}
    
    def _extract_season_context(self) -> Dict[str, Any]:
        """Extract season and week context from Yahoo data."""
        try:
            current_date = datetime.now()
            season_context = {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': self._determine_season_phase(current_date),
                'data_source': 'Sleeper API',
                'verification_notes': []
            }
            
            # Try to load Yahoo data for more accurate season/week info
            try:
                yahoo_data = self._load_latest_yahoo_available_data()
                if yahoo_data and 'season_context' in yahoo_data:
                    yahoo_season_context = yahoo_data['season_context']
                    season_context.update(yahoo_season_context)
                    season_context['data_source'] = 'Sleeper API (with Yahoo context)'
                    season_context['verification_notes'].append("Season context extracted from Yahoo data")
                else:
                    season_context['verification_notes'].append("No Yahoo season context available, using date estimation")
            except Exception as e:
                self.logger.warning(f"Could not load Yahoo season context: {e}")
                season_context['verification_notes'].append(f"Could not load Yahoo data: {e}")
            
            return season_context
            
        except Exception as e:
            self.logger.error(f"Error extracting season context: {e}")
            return {
                'nfl_season': str(current_date.year),
                'current_date': current_date.strftime('%Y-%m-%d'),
                'season_phase': 'Unknown',
                'data_source': 'Sleeper API',
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
    
    def _load_latest_yahoo_available_data(self) -> Optional[Dict[str, Any]]:
        """Load the latest Yahoo available players raw data for season context."""
        try:
            base_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'available_players'
            )
            base_dir = os.path.abspath(base_dir)
            pattern = os.path.join(base_dir, '**', '*_available_players_raw_data.json')
            files = sorted(glob.glob(pattern, recursive=True))
            if not files:
                return None
            
            latest_file = files[-1]
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load Yahoo available players data: {e}")
            return None
    
    def _load_latest_yahoo_available_players(self) -> List[Dict[str, Any]]:
        """Load the latest Yahoo available players raw JSON and return extracted players list."""
        try:
            base_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'available_players'
            )
            base_dir = os.path.abspath(base_dir)
            pattern = os.path.join(base_dir, '**', '*_available_players_raw_data.json')
            files = sorted(glob.glob(pattern, recursive=True))
            if not files:
                self.logger.error(f"No Yahoo available players raw files found at {pattern}")
                return []
            latest = files[-1]
            self.logger.info(f"📄 Using latest Yahoo available players file: {os.path.basename(latest)}")

            with open(latest, 'r') as f:
                data = json.load(f)

            # Extract available players from the Yahoo output
            available_players = data.get('available_players', [])
            if available_players:
                self.logger.info(f"📄 Found {len(available_players)} available players in Yahoo data")
                return available_players
            else:
                self.logger.error("❌ No available_players found in Yahoo data")
                return []

        except Exception as exc:
            self.logger.error(f"Failed to load Yahoo available players: {exc}")
            return []

    def _get_yahoo_player_name(self, yp: Dict[str, Any]) -> str:
        name_obj = yp.get('name') or {}
        if isinstance(name_obj, dict):
            return name_obj.get('full') or name_obj.get('first') or 'Unknown'
        return str(yp.get('full_name') or 'Unknown')

    def _get_yahoo_player_team(self, yp: Dict[str, Any]) -> Optional[str]:
        team = yp.get('editorial_team_abbr') or yp.get('team') or None
        if isinstance(team, str):
            return normalize_team_abbreviation(team, 'yahoo')
        return team

    def _get_yahoo_player_position(self, yp: Dict[str, Any]) -> Optional[str]:
        pos = yp.get('display_position') or yp.get('primary_position') or None
        if isinstance(pos, str):
            return pos.split(',')[0].strip().upper()
        return pos

    def _normalize_name(self, name: str) -> str:
        if not isinstance(name, str):
            return ''
        n = name.lower().strip()
        for ch in ['.', ',', "'", '"']:
            n = n.replace(ch, '')
        for suffix in [' jr', ' sr', ' ii', ' iii', ' iv']:
            if n.endswith(suffix):
                n = n[: -len(suffix)].strip()
        return n

    def _match_defense_by_team(self, players_db: Dict[str, Any], team: Optional[str]) -> Optional[Dict[str, Any]]:
        if not team or not players_db:
            return None
        team_normalized = normalize_team_abbreviation(team, 'yahoo')
        for sp in players_db.values():
            if sp.get('position') == 'DEF':
                sp_team_raw = sp.get('team')
                sp_team = normalize_team_abbreviation(sp_team_raw, 'sleeper') if sp_team_raw else ''
                if sp_team == team_normalized:
                    return sp
        return None

    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save extracted data to files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_ok = self.file_manager.save_raw_data('sleeper', 'available_players', data, timestamp)
            md = self._generate_markdown_report(data)
            md_ok = self.file_manager.save_clean_data('sleeper', 'available_players', md, timestamp)
            log_ok = self.file_manager.save_execution_log('sleeper', 'available_players', self.execution_stats, timestamp)
            ok = raw_ok and md_ok and log_ok
            if ok:
                self.logger.info(f"✅ Data saved successfully with timestamp: {timestamp}")
            else:
                self.logger.error("❌ Failed to save some data files")
            return ok
        except Exception as exc:
            self.logger.error(f"❌ Error saving data: {exc}")
            return False

    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate clean markdown report from extracted data."""
        try:
            meta = data.get('extraction_metadata', {})
            stats = meta.get('execution_stats', {})
            matched = data.get('matched_players', [])
            unmatched = data.get('unmatched_players', [])

            report: List[str] = []
            report.append("# Sleeper NFL - Available Players Data")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**Yahoo Players Loaded:** {stats.get('yahoo_players_loaded', 0)}")
            report.append(f"**Matched Players:** {len(matched)}")
            report.append(f"**Unmatched Players:** {len(unmatched)}")
            report.append(f"**Match Rate:** {(len(matched) / max(1, stats.get('players_processed', 1)) * 100):.1f}%")
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

            # Matched players summary table (limit 100)
            if matched:
                report.append("## Available Players with Sleeper Data")
                report.append(f"**Showing:** {min(100, len(matched))} of {len(matched)}")
                report.append("")
                report.append("| Player | Pos | Team | Sleeper ID | Yahoo ID | Status | Injury | Depth | Fantasy Pos | News Updated |")
                report.append("|--------|-----|------|------------|----------|--------|--------|-------|-------------|-------------|")
                
                # Sort by position for better organization
                sorted_players = sorted(matched, key=lambda x: (
                    x.get('sleeper_player', {}).get('position', 'ZZZ'),
                    x.get('sleeper_player', {}).get('full_name', '')
                ))
                
                for item in sorted_players[:100]:
                    sp = item.get('sleeper_player', {})
                    mp = item.get('mapping', {})
                    name = sp.get('full_name', 'Unknown')
                    pos = sp.get('position', 'N/A')
                    team = sp.get('team', 'N/A')
                    pid = sp.get('player_id', 'N/A')
                    yid = mp.get('yahoo_player_id', 'N/A')
                    status = sp.get('status', 'N/A')
                    injury = sp.get('injury_status', 'N/A')
                    depth = sp.get('depth_chart_position', 'N/A')
                    fantasy_pos = ', '.join(sp.get('fantasy_positions', []) or ['N/A'])
                    news_updated = sp.get('news_updated', 'N/A')
                    
                    # Fix defense names - show team name instead of "Unknown"
                    if pos == 'DEF' and name == 'Unknown' and team != 'N/A':
                        name = self._get_team_full_name(team)
                    
                    if news_updated and news_updated != 'N/A':
                        try:
                            news_updated = datetime.fromtimestamp(int(news_updated) / 1000).strftime('%m/%d')
                        except:
                            pass
                    
                    report.append(f"| {name} | {pos} | {team} | {pid} | {yid} | {status} | {injury} | {depth} | {fantasy_pos} | {news_updated} |")
                
                if len(matched) > 100:
                    report.append("")
                    report.append(f"*... and {len(matched) - 100} more available players*")
                report.append("")

            # Position breakdown
            if matched:
                report.append("## Position Breakdown")
                report.append("")
                position_counts = {}
                for item in matched:
                    pos = item.get('sleeper_player', {}).get('position', 'Unknown')
                    position_counts[pos] = position_counts.get(pos, 0) + 1
                
                report.append("| Position | Count |")
                report.append("|----------|-------|")
                for pos, count in sorted(position_counts.items()):
                    report.append(f"| {pos} | {count} |")
                report.append("")

            # Top available players by position (detailed sections)
            if matched:
                report.append("## Top Available Players by Position - Detailed Information")
                report.append("")
                
                # Group by position and show top players
                by_position = {}
                for item in matched:
                    pos = item.get('sleeper_player', {}).get('position', 'Unknown')
                    if pos not in by_position:
                        by_position[pos] = []
                    by_position[pos].append(item)
                
                for pos in sorted(by_position.keys()):
                    players = by_position[pos][:10]  # Top 10 per position
                    if not players:
                        continue
                        
                    report.append(f"### {pos} - Top Available Players")
                    report.append("")
                    
                    for item in players:
                        sp = item.get('sleeper_player', {})
                        mp = item.get('mapping', {})
                        
                        player_name = sp.get('full_name', 'Unknown')
                        team = sp.get('team', 'N/A')
                        
                        # Fix defense names in detailed section too
                        if pos == 'DEF' and player_name == 'Unknown' and team != 'N/A':
                            player_name = self._get_team_full_name(team)
                        
                        report.append(f"#### {player_name} ({pos} - {team})")
                        report.append("")
                        report.append(f"- **Sleeper ID**: {sp.get('player_id','N/A')}")
                        report.append(f"- **Yahoo ID**: {mp.get('yahoo_player_id','N/A')}")
                        report.append(f"- **Status**: {sp.get('status','N/A')}")
                        
                        # Fantasy positions
                        fantasy_pos = sp.get('fantasy_positions', [])
                        if fantasy_pos:
                            report.append(f"- **Fantasy Positions**: {', '.join(fantasy_pos)}")
                        
                        # Injury info
                        injury_status = sp.get('injury_status', '')
                        injury_body_part = sp.get('injury_body_part', '')
                        injury_notes = sp.get('injury_notes', '')
                        if injury_status or injury_body_part or injury_notes:
                            injury_line = f"- **Injury**: {injury_status or 'N/A'}"
                            if injury_body_part:
                                injury_line += f" ({injury_body_part})"
                            if injury_notes:
                                injury_line += f" - {injury_notes}"
                            report.append(injury_line)
                        
                        # Depth chart
                        depth_pos = sp.get('depth_chart_position', '')
                        depth_order = sp.get('depth_chart_order', '')
                        if depth_pos or depth_order:
                            report.append(f"- **Depth Chart**: {depth_pos or 'N/A'} (order {depth_order or 'N/A'})")
                        
                        # Physical and experience
                        age = sp.get('age', 'N/A')
                        years_exp = sp.get('years_exp', 'N/A')
                        college = sp.get('college', 'N/A')
                        report.append(f"- **Bio**: Age {age}, {years_exp} years exp, {college}")
                        
                        # Cross-platform IDs for reference
                        yahoo_id = sp.get('yahoo_id', '')
                        espn_id = sp.get('espn_id', '')
                        if yahoo_id or espn_id:
                            ids = []
                            if yahoo_id:
                                ids.append(f"Yahoo: {yahoo_id}")
                            if espn_id:
                                ids.append(f"ESPN: {espn_id}")
                            report.append(f"- **Platform IDs**: {' | '.join(ids)}")
                        
                        report.append("")

            # Unmatched players (limit 100)
            if unmatched:
                report.append("## Unmatched Yahoo Players (no Sleeper match)")
                report.append(f"**Showing:** {min(100, len(unmatched))} of {len(unmatched)}")
                report.append("")
                report.append("| Player | Team | Position |")
                report.append("|--------|------|----------|")
                for up in unmatched[:100]:
                    report.append(f"| {up.get('name','Unknown')} | {up.get('team','N/A')} | {up.get('position','N/A')} |")
                if len(unmatched) > 100:
                    report.append("")
                    report.append(f"*... and {len(unmatched) - 100} more unmatched players*")

            return "\n".join(report)
        except Exception as exc:
            self.logger.error(f"❌ Error generating markdown report: {exc}")
            return f"# Error generating report\n\nError: {exc}"

    def _get_team_full_name(self, team_abbr: str) -> str:
        """Convert team abbreviation to full team name in all caps."""
        team_names = {
            'ARI': 'ARIZONA',
            'ATL': 'ATLANTA', 
            'BAL': 'BALTIMORE',
            'BUF': 'BUFFALO',
            'CAR': 'CAROLINA',
            'CHI': 'CHICAGO',
            'CIN': 'CINCINNATI',
            'CLE': 'CLEVELAND',
            'DAL': 'DALLAS',
            'DEN': 'DENVER',
            'DET': 'DETROIT',
            'GB': 'GREEN BAY',
            'HOU': 'HOUSTON',
            'IND': 'INDIANAPOLIS',
            'JAX': 'JACKSONVILLE',
            'KC': 'KANSAS CITY',
            'LV': 'LAS VEGAS',
            'LAC': 'LOS ANGELES CHARGERS',
            'LAR': 'LOS ANGELES RAMS',
            'MIA': 'MIAMI',
            'MIN': 'MINNESOTA',
            'NE': 'NEW ENGLAND',
            'NO': 'NEW ORLEANS',
            'NYG': 'NEW YORK GIANTS',
            'NYJ': 'NEW YORK JETS',
            'PHI': 'PHILADELPHIA',
            'PIT': 'PITTSBURGH',
            'SF': 'SAN FRANCISCO',
            'SEA': 'SEATTLE',
            'TB': 'TAMPA BAY',
            'TEN': 'TENNESSEE',
            'WAS': 'WASHINGTON'
        }
        return team_names.get(team_abbr.upper(), team_abbr.upper())


def main() -> None:
    # Parse command line arguments
    player_limits = parse_arguments()
    
    # Create extractor with configurable limits
    extractor = SleeperAvailablePlayersExtractor(player_limits)
    
    # Show configuration
    print(f"🎯 Player Limits: {player_limits}")
    
    data = extractor.extract_all_data()
    if data:
        ok = extractor.save_data(data)
        if ok:
            print("✅ Sleeper Available Players extraction completed successfully!")
            print(f"👥 Matched players: {len(data.get('matched_players', []))}")
            print(f"🙈 Unmatched players: {len(data.get('unmatched_players', []))}")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ No data extracted")


if __name__ == "__main__":
    main()
