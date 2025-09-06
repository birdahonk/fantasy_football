#!/usr/bin/env python3
"""
Sleeper NFL API - Opponent Roster Data Extraction

This script maps the current week opponent's Yahoo roster players to the Sleeper NFL player database
and extracts ALL available Sleeper player data for those players. It outputs
both clean markdown and raw JSON for downstream analysis.

Purpose: Clean, focused data extraction for opponent roster using Sleeper API
Output: Organized markdown file + raw JSON of matched Sleeper players
Focus: Extract ALL available Sleeper player data, no analysis
"""

import os
import sys
import json
import glob
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from sleeper_client import SimpleSleeperClient
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager


class SleeperOpponentRosterExtractor:
    """Maps opponent's Yahoo roster players to Sleeper players and extracts Sleeper data."""

    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.sleeper = SimpleSleeperClient()
        self.formatter = MarkdownFormatter()
        self.file_manager = DataFileManager()

        self.execution_stats: Dict[str, Any] = {
            'start_time': datetime.now(),
            'api_calls': 0,  # internal to client, not exposed; kept for parity
            'errors': 0,
            'players_processed': 0,
            'players_matched': 0,
            'players_unmatched': 0
        }

    def extract_all_data(self) -> Dict[str, Any]:
        """Load latest Yahoo opponent roster, map to Sleeper players, return consolidated data."""
        try:
            self.logger.info("🚀 Starting Sleeper Opponent Roster Extraction")

            # Load opponent roster data
            opponent_data = self._load_latest_yahoo_opponent_roster()
            if not opponent_data:
                self.logger.error("❌ Could not load Yahoo opponent roster")
                return {}

            yahoo_players = opponent_data.get('players', [])
            opponent_name = opponent_data.get('opponent_name', 'Unknown Opponent')
            opponent_team_key = opponent_data.get('opponent_team_key', 'Unknown')

            self.logger.info(f"📊 Processing opponent: {opponent_name} (Team Key: {opponent_team_key})")
            self.logger.info(f"👥 Found {len(yahoo_players)} players in opponent roster")

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

            for yp in yahoo_players:
                self.execution_stats['players_processed'] += 1
                name = self._get_yahoo_player_name(yp)
                team = self._get_yahoo_player_team(yp)
                pos = self._get_yahoo_player_position(yp)
                yahoo_pid = str(yp.get('player_id', '')).strip()

                sleeper_player = None

                # Try direct yahoo_id match first
                if yahoo_pid in yahoo_id_to_sleeper:
                    sleeper_player = yahoo_id_to_sleeper[yahoo_pid]
                    self.logger.info(f"✅ Direct match: {name} ({team}) -> {sleeper_player.get('full_name', 'Unknown')}")
                else:
                    # Try name + team matching as fallback
                    sleeper_player = self._find_sleeper_player_by_name_and_team(
                        players_db, name, team, pos
                    )
                    if sleeper_player:
                        self.logger.info(f"✅ Name+team match: {name} ({team}) -> {sleeper_player.get('full_name', 'Unknown')}")
                    else:
                        self.logger.warning(f"❌ No match found: {name} ({team})")

                if sleeper_player:
                    matched_players.append({
                        'yahoo_data': yp,
                        'sleeper_player': sleeper_player,
                        'match_type': 'direct' if yahoo_pid in yahoo_id_to_sleeper else 'name_team'
                    })
                    self.execution_stats['players_matched'] += 1
                else:
                    unmatched_players.append(yp)
                    self.execution_stats['players_unmatched'] += 1

            # Build final data structure
            data = {
                'extraction_metadata': {
                    'script': 'sleeper_opponent_roster.py',
                    'extraction_timestamp': datetime.now().isoformat(),
                    'opponent_name': opponent_name,
                    'opponent_team_key': opponent_team_key,
                    'execution_stats': self.execution_stats
                },
                'opponent_info': {
                    'opponent_name': opponent_name,
                    'opponent_team_key': opponent_team_key,
                    'total_players': len(yahoo_players),
                    'matched_players': len(matched_players),
                    'unmatched_players': len(unmatched_players)
                },
                'matched_players': matched_players,
                'unmatched_players': unmatched_players
            }

            self.logger.info(f"✅ Extraction completed: {len(matched_players)} matched, {len(unmatched_players)} unmatched")
            return data

        except Exception as exc:
            self.logger.error(f"❌ Error in extract_all_data: {exc}")
            self.execution_stats['errors'] += 1
            return {}

    def _load_latest_yahoo_opponent_roster(self) -> Optional[Dict[str, Any]]:
        """Load the most recent Yahoo opponent roster data and find current week opponent."""
        try:
            # First, find the current week opponent from team matchups
            current_week_opponent = self._find_current_week_opponent()
            if not current_week_opponent:
                self.logger.error("❌ Could not find current week opponent")
                return None

            # Look for opponent roster files
            pattern = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'opponent_rosters', '*_raw_data.json'
            )
            files = glob.glob(pattern)
            
            if not files:
                self.logger.error("❌ No Yahoo opponent roster files found")
                return None

            # Get the most recent file
            latest_file = max(files, key=os.path.getctime)
            self.logger.info(f"📁 Loading opponent roster from: {latest_file}")

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
                self.logger.error(f"❌ No roster data found for opponent {current_week_opponent.get('name')}")
                return None

            return {
                'opponent_name': current_week_opponent.get('name', 'Unknown Opponent'),
                'opponent_team_key': opponent_team_key,
                'players': opponent_roster_data.get('players', [])
            }

        except Exception as exc:
            self.logger.error(f"❌ Error loading Yahoo opponent roster: {exc}")
            return None

    def _find_current_week_opponent(self) -> Optional[Dict[str, Any]]:
        """Find current week opponent from Yahoo team matchups data."""
        try:
            # Look for team matchups files
            matchups_pattern = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'team_matchups', '*_raw_data.json'
            )
            matchups_files = glob.glob(matchups_pattern)
            
            if not matchups_files:
                self.logger.error("❌ No team matchups files found")
                return None

            # Get the most recent file
            latest_matchups = max(matchups_files, key=os.path.getctime)
            self.logger.info(f"📁 Loading team matchups from: {latest_matchups}")

            with open(latest_matchups, 'r') as f:
                matchups_data = json.load(f)

            season_context = matchups_data.get("season_context", {})
            current_week = season_context.get("current_week", 1)
            league_info = matchups_data.get("league_info", {})
            my_team_key = league_info.get("team_key")
            
            if not my_team_key:
                self.logger.error("❌ No team key found in matchups data")
                return None

            matchups = matchups_data.get("matchups", {})
            week_key = f"week_{current_week}"
            
            if week_key not in matchups:
                self.logger.error(f"❌ No matchups found for week {current_week}")
                return None

            week_matchups = matchups[week_key].get("matchups", [])
            
            for matchup in week_matchups:
                teams = matchup.get("teams", [])
                if len(teams) == 2:
                    team1_key = teams[0].get("team_key")
                    team2_key = teams[1].get("team_key")
                    
                    if team1_key == my_team_key:
                        opponent_team = teams[1]
                        self.logger.info(f"✅ Found current week opponent: {opponent_team.get('name')} (team_key: {opponent_team.get('team_key')})")
                        return opponent_team
                    elif team2_key == my_team_key:
                        opponent_team = teams[0]
                        self.logger.info(f"✅ Found current week opponent: {opponent_team.get('name')} (team_key: {opponent_team.get('team_key')})")
                        return opponent_team

            self.logger.error(f"❌ No matchup found for my team {my_team_key} in week {current_week}")
            return None

        except Exception as exc:
            self.logger.error(f"❌ Error finding current week opponent: {exc}")
            return None

    def _get_yahoo_player_name(self, yahoo_player: Dict[str, Any]) -> str:
        """Extract player name from Yahoo player data."""
        name_data = yahoo_player.get('name', {})
        if isinstance(name_data, dict):
            return name_data.get('full', 'Unknown')
        return str(name_data) if name_data else 'Unknown'

    def _get_yahoo_player_team(self, yahoo_player: Dict[str, Any]) -> str:
        """Extract team from Yahoo player data."""
        return yahoo_player.get('team', 'N/A')

    def _get_yahoo_player_position(self, yahoo_player: Dict[str, Any]) -> str:
        """Extract position from Yahoo player data."""
        return yahoo_player.get('display_position', 'N/A')

    def _find_sleeper_player_by_name_and_team(self, players_db: Dict[str, Any], 
                                            name: str, team: str, position: str) -> Optional[Dict[str, Any]]:
        """Find Sleeper player by name and team matching."""
        if not players_db:
            return None

        # Normalize inputs - handle None values
        name_lower = (name or '').lower().strip()
        team_upper = (team or '').upper().strip()
        position_upper = (position or '').upper().strip()

        for sp in players_db.values():
            sleeper_name = (sp.get('full_name') or '').lower().strip()
            sleeper_team = (sp.get('team') or '').upper().strip()
            sleeper_pos = (sp.get('position') or '').upper().strip()

            # Check name similarity (exact match or contains)
            name_match = (name_lower == sleeper_name or 
                         name_lower in sleeper_name or 
                         sleeper_name in name_lower)

            # Check team match (only if team is provided)
            team_match = True  # Default to True if no team specified
            if team_upper:
                team_match = (team_upper == sleeper_team or 
                             team_upper in sleeper_team or 
                             sleeper_team in team_upper)

            # Check position match (only if position is provided)
            pos_match = True  # Default to True if no position specified
            if position_upper:
                pos_match = (position_upper == sleeper_pos or 
                            position_upper in sleeper_pos or 
                            sleeper_pos in position_upper)

            if name_match and team_match and pos_match:
                return sp

        return None

    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save extracted data to files."""
        try:
            # Save raw JSON data
            raw_path = self.file_manager.save_raw_data('sleeper', 'opponent_roster', data)
            self.logger.info(f"💾 Raw data saved: {raw_path}")

            # Generate and save markdown report
            markdown_content = self._generate_markdown_report(data)
            markdown_path = self.file_manager.save_clean_data('sleeper', 'opponent_roster', markdown_content)
            self.logger.info(f"📄 Markdown report saved: {markdown_path}")

            return True

        except Exception as exc:
            self.logger.error(f"❌ Error saving data: {exc}")
            return False

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

            report.append(f"# Sleeper Opponent Roster Data - {opponent_name}")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
                    sleeper_data = mp.get('sleeper_player', {})
                    match_type = mp.get('match_type', 'unknown')
                    
                    yahoo_name = self._get_yahoo_player_name(yahoo_data)
                    yahoo_team = self._get_yahoo_player_team(yahoo_data)
                    yahoo_pos = self._get_yahoo_player_position(yahoo_data)
                    
                    sleeper_name = sleeper_data.get('full_name', 'Unknown')
                    sleeper_team = sleeper_data.get('team', 'N/A')
                    sleeper_pos = sleeper_data.get('position', 'N/A')
                    
                    report.append(f"### {yahoo_name} ({yahoo_team}, {yahoo_pos})")
                    report.append(f"**Match Type:** {match_type}")
                    report.append(f"**Sleeper Name:** {sleeper_name}")
                    report.append(f"**Sleeper Team:** {sleeper_team}")
                    report.append(f"**Sleeper Position:** {sleeper_pos}")
                    report.append("")
                    
                    # Sleeper player details
                    sp = sleeper_data
                    report.append("#### Sleeper Player Details")
                    
                    # Basic info
                    if sp.get('height'):
                        report.append(f"- **Height**: {sp['height']}")
                    if sp.get('weight'):
                        report.append(f"- **Weight**: {sp['weight']} lbs")
                    if sp.get('age'):
                        report.append(f"- **Age**: {sp['age']}")
                    
                    # College and birthplace
                    college = sp.get('college', '')
                    if college:
                        report.append(f"- **College**: {college}")
                    
                    birth_city = sp.get('birth_city', '')
                    birth_state = sp.get('birth_state', '')
                    birth_country = sp.get('birth_country', '')
                    high_school = sp.get('high_school', '')
                    
                    if high_school:
                        report.append(f"- **High School**: {high_school}")
                    
                    birth_parts = [p for p in [birth_city, birth_state, birth_country] if p]
                    if birth_parts:
                        report.append(f"- **Birthplace**: {', '.join(birth_parts)}")
                    
                    # Cross-platform IDs
                    ids = []
                    for id_type, id_key in [
                        ('ESPN', 'espn_id'), ('RotoWire', 'rotowire_id'), ('Rotoworld', 'rotoworld_id'),
                        ('Sportradar', 'sportradar_id'), ('GSIS', 'gsis_id'), ('Stats', 'stats_id'),
                        ('FantasyData', 'fantasy_data_id')
                    ]:
                        id_val = sp.get(id_key, '')
                        if id_val:
                            ids.append(f"{id_type}: {id_val}")
                    if ids:
                        report.append(f"- **Cross-Platform IDs**: {' | '.join(ids)}")
                    
                    # News/search metadata
                    news_updated = sp.get('news_updated', '')
                    search_rank = sp.get('search_rank', '')
                    hashtag = sp.get('hashtag', '')
                    
                    meta_parts = []
                    if news_updated:
                        try:
                            news_date = datetime.fromtimestamp(int(news_updated) / 1000).strftime('%Y-%m-%d %H:%M')
                            meta_parts.append(f"News: {news_date}")
                        except:
                            meta_parts.append(f"News: {news_updated}")
                    if search_rank:
                        meta_parts.append(f"Search Rank: {search_rank}")
                    if hashtag:
                        meta_parts.append(f"#{hashtag}")
                    
                    if meta_parts:
                        report.append(f"- **Metadata**: {' | '.join(meta_parts)}")
                    
                    report.append("")

            # Unmatched players (limit 100)
            unmatched = data.get('unmatched_players', [])
            if unmatched:
                report.append("## Unmatched Yahoo Players (no Sleeper match)")
                report.append(f"**Showing:** {min(100, len(unmatched))} of {len(unmatched)}")
                report.append("")
                report.append("| Player | Team |")
                report.append("|--------|------|")
                for up in unmatched[:100]:
                    report.append(f"| {up.get('name','Unknown')} | {up.get('team','N/A')} |")
                if len(unmatched) > 100:
                    report.append("")
                    report.append(f"*... and {len(unmatched) - 100} more unmatched players*")

            return "\n".join(report)
        except Exception as exc:
            self.logger.error(f"❌ Error generating markdown report: {exc}")
            return f"# Error generating report\n\nError: {exc}"


def main() -> None:
    extractor = SleeperOpponentRosterExtractor()
    data = extractor.extract_all_data()
    if data:
        ok = extractor.save_data(data)
        if ok:
            print("✅ Sleeper Opponent Roster extraction completed successfully!")
            print(f"👥 Matched players: {len(data.get('matched_players', []))}")
            print(f"🙈 Unmatched players: {len(data.get('unmatched_players', []))}")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ No data extracted")


if __name__ == "__main__":
    main()
