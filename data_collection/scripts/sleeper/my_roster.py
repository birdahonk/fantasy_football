#!/usr/bin/env python3
"""
Sleeper NFL API - My Roster Data Extraction

This script maps your Yahoo roster players to the Sleeper NFL player database
and extracts ALL available Sleeper player data for those players. It outputs
both clean markdown and raw JSON for downstream analysis.

Purpose: Clean, focused data extraction for my roster using Sleeper API
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


class SleeperMyRosterExtractor:
    """Maps Yahoo roster players to Sleeper players and extracts Sleeper data."""

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
        """Load latest Yahoo roster, map to Sleeper players, return consolidated data."""
        try:
            self.logger.info("🚀 Starting Sleeper My Roster Extraction")

            yahoo_players = self._load_latest_yahoo_roster_players()
            if not yahoo_players:
                self.logger.error("❌ Could not load Yahoo roster players")
                return {}

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
                        sp_team = sp.get('team')
                        if name_l == sp_name and (not team or not sp_team or sp_team == team):
                            sleeper_player = sp
                            break

                # 4) Last-name + team/position fallback
                if not sleeper_player and players_db and name:
                    last = self._normalize_name(name).split()[-1]
                    for sp in players_db.values():
                        sp_name = self._normalize_name(sp.get('full_name') or '')
                        if sp_name.endswith(' ' + last) or sp_name == last:
                            if (team and sp.get('team') == team) or (pos and sp.get('position') == pos):
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
                        'yahoo_player': yp
                    })
                    self.execution_stats['players_unmatched'] += 1

            # finalize timing
            self.execution_stats['execution_time'] = (
                datetime.now() - self.execution_stats['start_time']
            ).total_seconds()

            # Extract season context from Yahoo data
            season_context = self._extract_season_context()
            
            result: Dict[str, Any] = {
                'extraction_metadata': {
                    'source': 'Sleeper API',
                    'extraction_timestamp': datetime.now().isoformat(),
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

        except Exception as exc:  # pragma: no cover
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
                yahoo_data = self._load_latest_yahoo_roster_data()
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
    
    def _load_latest_yahoo_roster_data(self) -> Optional[Dict[str, Any]]:
        """Load the latest Yahoo roster raw data for season context."""
        try:
            base_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'my_roster'
            )
            base_dir = os.path.abspath(base_dir)
            pattern = os.path.join(base_dir, '*_my_roster_raw_data.json')
            files = sorted(glob.glob(pattern))
            if not files:
                return None
            
            latest_file = files[-1]
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load Yahoo roster data: {e}")
            return None
    
    def _load_latest_yahoo_roster_players(self) -> List[Dict[str, Any]]:
        """Load the latest Yahoo my_roster raw JSON and return extracted players list."""
        try:
            base_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'outputs', 'yahoo', 'my_roster'
            )
            base_dir = os.path.abspath(base_dir)
            pattern = os.path.join(base_dir, '*_my_roster_raw_data.json')
            files = sorted(glob.glob(pattern))
            if not files:
                self.logger.error(f"No Yahoo my_roster raw files found at {pattern}")
                return []
            latest = files[-1]
            self.logger.info(f"📄 Using latest Yahoo roster file: {os.path.basename(latest)}")

            with open(latest, 'r') as f:
                data = json.load(f)

            # Our Yahoo script may store extracted players under 'players'
            players = data.get('players') or []
            if players:
                return players

            # Navigate raw fantasy_content saved under 'roster_raw'
            fc = (data.get('roster_raw') or {}).get('fantasy_content', {})
            team = fc.get('team', []) if isinstance(fc, dict) else []
            # This path mirrors Yahoo extraction in other scripts
            for section in team:
                if isinstance(section, dict) and 'roster' in section:
                    roster_players = section['roster'].get('0', {}).get('players', {})
                    collected: List[Dict[str, Any]] = []
                    idx = 0
                    while str(idx) in roster_players:
                        p_data = roster_players[str(idx)].get('player', [])
                        if isinstance(p_data, list) and p_data:
                            # flatten to dict similar to our extraction
                            p_flat: Dict[str, Any] = {}
                            for chunk in p_data:
                                if isinstance(chunk, dict):
                                    for k, v in chunk.items():
                                        p_flat[k] = v
                                elif isinstance(chunk, list):
                                    for prop in chunk:
                                        if isinstance(prop, dict):
                                            for k, v in prop.items():
                                                p_flat[k] = v
                            collected.append(p_flat)
                        idx += 1
                    if collected:
                        return collected
            return []
        except Exception as exc:
            self.logger.error(f"Failed to load Yahoo roster players: {exc}")
            return []

    def _get_yahoo_player_name(self, yp: Dict[str, Any]) -> str:
        name_obj = yp.get('name') or {}
        if isinstance(name_obj, dict):
            return name_obj.get('full') or name_obj.get('first') or 'Unknown'
        return str(yp.get('full_name') or 'Unknown')

    def _get_yahoo_player_team(self, yp: Dict[str, Any]) -> Optional[str]:
        team = yp.get('editorial_team_abbr') or yp.get('team') or None
        if isinstance(team, str):
            return team.upper()
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
        team = team.upper()
        for sp in players_db.values():
            if sp.get('position') == 'DEF' and sp.get('team') == team:
                return sp
        return None

    def save_data(self, data: Dict[str, Any]) -> bool:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_ok = self.file_manager.save_raw_data('sleeper', 'my_roster', data, timestamp)
            md = self._generate_markdown_report(data)
            md_ok = self.file_manager.save_clean_data('sleeper', 'my_roster', md, timestamp)
            log_ok = self.file_manager.save_execution_log('sleeper', 'my_roster', self.execution_stats, timestamp)
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
        try:
            meta = data.get('extraction_metadata', {})
            stats = meta.get('execution_stats', {})
            matched = data.get('matched_players', [])
            unmatched = data.get('unmatched_players', [])

            report: List[str] = []
            report.append("# Sleeper NFL - My Roster Data")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**Matched Players:** {len(matched)}")
            report.append(f"**Unmatched Players:** {len(unmatched)}")
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

            # Matched players table (limit 100)
            report.append("## Matched Players (Sleeper Data)")
            report.append(f"**Showing:** {min(100, len(matched))} of {len(matched)}")
            report.append("")
            if matched:
                report.append("| Player | Pos | Team | Sleeper ID | Yahoo ID | Status | Injury | Depth | Practice | News Updated |")
                report.append("|--------|-----|------|------------|----------|--------|--------|-------|----------|-------------|")
                for item in matched[:100]:
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
                    practice = sp.get('practice_participation', 'N/A')
                    news_updated = sp.get('news_updated', 'N/A')
                    if news_updated and news_updated != 'N/A':
                        try:
                            # Convert timestamp to readable format
                            news_updated = datetime.fromtimestamp(int(news_updated) / 1000).strftime('%m/%d')
                        except:
                            pass
                    report.append(f"| {name} | {pos} | {team} | {pid} | {yid} | {status} | {injury} | {depth} | {practice} | {news_updated} |")
                if len(matched) > 100:
                    report.append("")
                    report.append(f"*... and {len(matched) - 100} more matched players*")

            report.append("")

            # Detailed Sleeper fields per matched player
            if matched:
                report.append("## Detailed Sleeper Fields (per matched player)")
                report.append("")
                for item in matched[:100]:
                    sp = item.get('sleeper_player', {})
                    mp = item.get('mapping', {})
                    report.append(f"### {sp.get('full_name', 'Unknown')} ({sp.get('position','N/A')} - {sp.get('team','N/A')})")
                    report.append("")
                    
                    # Basic identifiers
                    report.append(f"- **Sleeper ID**: {sp.get('player_id','N/A')}")
                    report.append(f"- **Yahoo ID**: {mp.get('yahoo_player_id','N/A')}")
                    report.append(f"- **Status**: {sp.get('status','N/A')}")
                    report.append(f"- **Jersey #**: {sp.get('number','N/A')}")
                    
                    # Fantasy positions
                    fantasy_pos = sp.get('fantasy_positions', [])
                    if fantasy_pos:
                        report.append(f"- **Fantasy Positions**: {', '.join(fantasy_pos)}")
                    
                    # Injury and practice info
                    injury_status = sp.get('injury_status', 'N/A')
                    injury_body_part = sp.get('injury_body_part', '')
                    injury_notes = sp.get('injury_notes', '')
                    injury_start = sp.get('injury_start_date', '')
                    if injury_status != 'N/A' or injury_body_part or injury_notes:
                        injury_line = f"- **Injury**: {injury_status}"
                        if injury_body_part:
                            injury_line += f" ({injury_body_part})"
                        if injury_start:
                            injury_line += f" since {injury_start}"
                        if injury_notes:
                            injury_line += f" - {injury_notes}"
                        report.append(injury_line)
                    
                    practice_part = sp.get('practice_participation', '')
                    practice_desc = sp.get('practice_description', '')
                    if practice_part or practice_desc:
                        practice_line = f"- **Practice**: {practice_part}"
                        if practice_desc:
                            practice_line += f" - {practice_desc}"
                        report.append(practice_line)
                    
                    # Depth chart
                    depth_pos = sp.get('depth_chart_position', 'N/A')
                    depth_order = sp.get('depth_chart_order', 'N/A')
                    if depth_pos != 'N/A' or depth_order != 'N/A':
                        report.append(f"- **Depth Chart**: {depth_pos} (order {depth_order})")
                    
                    # Physical and bio
                    age = sp.get('age', 'N/A')
                    height = sp.get('height', 'N/A')
                    weight = sp.get('weight', 'N/A')
                    years_exp = sp.get('years_exp', 'N/A')
                    college = sp.get('college', 'N/A')
                    high_school = sp.get('high_school', '')
                    birth_city = sp.get('birth_city', '')
                    birth_state = sp.get('birth_state', '')
                    birth_country = sp.get('birth_country', '')
                    
                    report.append(f"- **Physical**: Age {age}, Height {height}, Weight {weight}")
                    report.append(f"- **Experience**: {years_exp} years | College: {college}")
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
    extractor = SleeperMyRosterExtractor()
    data = extractor.extract_all_data()
    if data:
        ok = extractor.save_data(data)
        if ok:
            print("✅ Sleeper My Roster extraction completed successfully!")
            print(f"👥 Matched players: {len(data.get('matched_players', []))}")
            print(f"🙈 Unmatched players: {len(data.get('unmatched_players', []))}")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ No data extracted")


if __name__ == "__main__":
    main()


