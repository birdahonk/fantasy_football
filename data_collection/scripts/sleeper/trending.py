#!/usr/bin/env python3
"""
Sleeper NFL API - Trending Players Data Extraction

This script extracts trending add/drop player data from the Sleeper API for the
last 24 hours, enriches it with full player details, and outputs both clean
markdown and raw JSON for downstream analysis.

Purpose: Clean, focused data extraction for trending players using Sleeper API
Output: Organized markdown file + raw JSON of trending players with full details
Focus: Extract ALL available trending and player data, no analysis
"""

import os
import sys
import json
import logging
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from sleeper_client import SimpleSleeperClient
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager


class SleeperTrendingExtractor:
    """Extracts trending add/drop players from Sleeper API with full player details."""

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
            'api_calls': 0,
            'errors': 0,
            'trending_adds_count': 0,
            'trending_drops_count': 0,
            'enriched_players': 0
        }

    def extract_all_data(self) -> Dict[str, Any]:
        """Extract trending add/drop data and enrich with full player details."""
        try:
            self.logger.info("🚀 Starting Sleeper Trending Players Extraction")

            # Get trending data
            trending_adds = self._get_trending_adds()
            trending_drops = self._get_trending_drops()
            
            if not trending_adds and not trending_drops:
                self.logger.warning("⚠️ No trending data retrieved")
                return {}

            # Load full player database for enrichment
            players_db = self.sleeper.get_nfl_players()
            if not players_db:
                self.logger.error("❌ Could not load Sleeper players database")
                return {}

            # Enrich trending data with full player details
            enriched_adds = self._enrich_trending_data(trending_adds, players_db, 'add')
            enriched_drops = self._enrich_trending_data(trending_drops, players_db, 'drop')

            # Get current NFL state for context
            nfl_state = self._get_nfl_state()

            # Finalize timing
            self.execution_stats['execution_time'] = (
                datetime.now() - self.execution_stats['start_time']
            ).total_seconds()

            # Extract season context
            season_context = self._extract_season_context()

            result: Dict[str, Any] = {
                'extraction_metadata': {
                    'source': 'Sleeper API - Trending Players',
                    'extraction_timestamp': datetime.now().isoformat(),
                    'lookback_period': '24 hours',
                    'nfl_state': nfl_state,
                    'execution_stats': self.execution_stats
                },
                'season_context': season_context,
                'trending_adds': enriched_adds,
                'trending_drops': enriched_drops,
                'raw_trending_adds': trending_adds,
                'raw_trending_drops': trending_drops
            }

            self.logger.info(
                f"✅ Extraction complete: {len(enriched_adds)} adds, {len(enriched_drops)} drops; "
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
        """Load the latest Yahoo my_roster raw data for season context."""
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
            self.logger.warning(f"Could not load Yahoo my_roster data: {e}")
            return None
    
    def _get_trending_adds(self) -> List[Dict[str, Any]]:
        """Get trending add players from Sleeper API."""
        try:
            self.logger.info("📈 Fetching trending adds...")
            trending = self.sleeper.get_trending_players('add', 24)
            self.execution_stats['api_calls'] += 1
            self.execution_stats['trending_adds_count'] = len(trending) if trending else 0
            self.logger.info(f"📈 Found {self.execution_stats['trending_adds_count']} trending adds")
            return trending or []
        except Exception as exc:
            self.logger.error(f"❌ Error getting trending adds: {exc}")
            self.execution_stats['errors'] += 1
            return []

    def _get_trending_drops(self) -> List[Dict[str, Any]]:
        """Get trending drop players from Sleeper API."""
        try:
            self.logger.info("📉 Fetching trending drops...")
            trending = self.sleeper.get_trending_players('drop', 24)
            self.execution_stats['api_calls'] += 1
            self.execution_stats['trending_drops_count'] = len(trending) if trending else 0
            self.logger.info(f"📉 Found {self.execution_stats['trending_drops_count']} trending drops")
            return trending or []
        except Exception as exc:
            self.logger.error(f"❌ Error getting trending drops: {exc}")
            self.execution_stats['errors'] += 1
            return []

    def _get_nfl_state(self) -> Dict[str, Any]:
        """Get current NFL season/week state for context."""
        try:
            self.logger.info("🏈 Fetching NFL state...")
            state = self.sleeper.get_nfl_state()
            self.execution_stats['api_calls'] += 1
            return state or {}
        except Exception as exc:
            self.logger.error(f"❌ Error getting NFL state: {exc}")
            self.execution_stats['errors'] += 1
            return {}

    def _enrich_trending_data(self, trending_data: List[Dict[str, Any]], 
                            players_db: Dict[str, Any], trend_type: str) -> List[Dict[str, Any]]:
        """Enrich trending player data with full player details from the database."""
        enriched: List[Dict[str, Any]] = []
        
        for trend_item in trending_data:
            player_id = trend_item.get('player_id')
            count = trend_item.get('count', 0)
            
            if not player_id:
                continue
                
            # Look up full player details
            player_details = players_db.get(player_id, {})
            
            if player_details:
                enriched_item = {
                    'trend_type': trend_type,
                    'trend_count': count,
                    'player_id': player_id,
                    'player_details': player_details,
                    'trend_data': trend_item  # Keep original trending data
                }
                enriched.append(enriched_item)
                self.execution_stats['enriched_players'] += 1
            else:
                self.logger.warning(f"⚠️ No player details found for ID: {player_id}")
        
        return enriched

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

    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save extracted data to files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_ok = self.file_manager.save_raw_data('sleeper', 'trending', data, timestamp)
            md = self._generate_markdown_report(data)
            md_ok = self.file_manager.save_clean_data('sleeper', 'trending', md, timestamp)
            log_ok = self.file_manager.save_execution_log('sleeper', 'trending', self.execution_stats, timestamp)
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
            nfl_state = meta.get('nfl_state', {})
            trending_adds = data.get('trending_adds', [])
            trending_drops = data.get('trending_drops', [])

            report: List[str] = []
            report.append("# Sleeper NFL - Trending Players Data")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**Lookback Period:** {meta.get('lookback_period', '24 hours')}")
            report.append(f"**Trending Adds:** {len(trending_adds)}")
            report.append(f"**Trending Drops:** {len(trending_drops)}")
            report.append(f"**Execution Time:** {stats.get('execution_time', 0):.2f}s")
            report.append(f"**API Calls:** {stats.get('api_calls', 0)}")
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

            # NFL Context
            if nfl_state:
                report.append("## NFL Season Context")
                report.append("")
                season = nfl_state.get('season', 'N/A')
                season_type = nfl_state.get('season_type', 'N/A')
                week = nfl_state.get('week', 'N/A')
                display_week = nfl_state.get('display_week', 'N/A')
                report.append(f"**Season:** {season} | **Type:** {season_type} | **Week:** {week} | **Display Week:** {display_week}")
                report.append("")

            # Trending Adds
            if trending_adds:
                report.append("## Trending Adds (Last 24 Hours)")
                report.append(f"**Showing:** {min(100, len(trending_adds))} of {len(trending_adds)}")
                report.append("")
                report.append("| Player | Pos | Team | Add Count | Status | Injury | Depth | Fantasy Pos | News Updated |")
                report.append("|--------|-----|------|-----------|--------|--------|-------|-------------|-------------|")
                
                # Sort by trend count descending
                sorted_adds = sorted(trending_adds, key=lambda x: x.get('trend_count', 0), reverse=True)
                
                for item in sorted_adds[:100]:
                    player = item.get('player_details', {})
                    count = item.get('trend_count', 0)
                    name = player.get('full_name', 'Unknown')
                    pos = player.get('position', 'N/A')
                    team = player.get('team', 'N/A')
                    status = player.get('status', 'N/A')
                    injury = player.get('injury_status', 'N/A')
                    depth = player.get('depth_chart_position', 'N/A')
                    fantasy_pos = ', '.join(player.get('fantasy_positions', []) or ['N/A'])
                    news_updated = player.get('news_updated', 'N/A')
                    
                    # Fix defense names - show team name instead of "Unknown"
                    if pos == 'DEF' and name == 'Unknown' and team != 'N/A':
                        name = self._get_team_full_name(team)
                    
                    if news_updated and news_updated != 'N/A':
                        try:
                            news_updated = datetime.fromtimestamp(int(news_updated) / 1000).strftime('%m/%d')
                        except:
                            pass
                    
                    report.append(f"| {name} | {pos} | {team} | {count} | {status} | {injury} | {depth} | {fantasy_pos} | {news_updated} |")
                
                if len(trending_adds) > 100:
                    report.append("")
                    report.append(f"*... and {len(trending_adds) - 100} more trending adds*")
                report.append("")

            # Trending Drops
            if trending_drops:
                report.append("## Trending Drops (Last 24 Hours)")
                report.append(f"**Showing:** {min(100, len(trending_drops))} of {len(trending_drops)}")
                report.append("")
                report.append("| Player | Pos | Team | Drop Count | Status | Injury | Depth | Fantasy Pos | News Updated |")
                report.append("|--------|-----|------|------------|--------|--------|-------|-------------|-------------|")
                
                # Sort by trend count descending
                sorted_drops = sorted(trending_drops, key=lambda x: x.get('trend_count', 0), reverse=True)
                
                for item in sorted_drops[:100]:
                    player = item.get('player_details', {})
                    count = item.get('trend_count', 0)
                    name = player.get('full_name', 'Unknown')
                    pos = player.get('position', 'N/A')
                    team = player.get('team', 'N/A')
                    status = player.get('status', 'N/A')
                    injury = player.get('injury_status', 'N/A')
                    depth = player.get('depth_chart_position', 'N/A')
                    fantasy_pos = ', '.join(player.get('fantasy_positions', []) or ['N/A'])
                    news_updated = player.get('news_updated', 'N/A')
                    
                    # Fix defense names - show team name instead of "Unknown"
                    if pos == 'DEF' and name == 'Unknown' and team != 'N/A':
                        name = self._get_team_full_name(team)
                    
                    if news_updated and news_updated != 'N/A':
                        try:
                            news_updated = datetime.fromtimestamp(int(news_updated) / 1000).strftime('%m/%d')
                        except:
                            pass
                    
                    report.append(f"| {name} | {pos} | {team} | {count} | {status} | {injury} | {depth} | {fantasy_pos} | {news_updated} |")
                
                if len(trending_drops) > 100:
                    report.append("")
                    report.append(f"*... and {len(trending_drops) - 100} more trending drops*")
                report.append("")

            # Detailed player information for top trending players
            if trending_adds or trending_drops:
                report.append("## Top Trending Players - Detailed Information")
                report.append("")
                
                # Combine and sort all trending players by count
                all_trending = []
                all_trending.extend(trending_adds)
                all_trending.extend(trending_drops)
                all_trending.sort(key=lambda x: x.get('trend_count', 0), reverse=True)
                
                for item in all_trending[:20]:  # Top 20 most trending
                    player = item.get('player_details', {})
                    trend_type = item.get('trend_type', 'unknown')
                    count = item.get('trend_count', 0)
                    
                    player_name = player.get('full_name', 'Unknown')
                    pos = player.get('position', 'N/A')
                    team = player.get('team', 'N/A')
                    
                    # Fix defense names in detailed section too
                    if pos == 'DEF' and player_name == 'Unknown' and team != 'N/A':
                        player_name = self._get_team_full_name(team)
                    
                    report.append(f"### {player_name} ({pos} - {team})")
                    report.append("")
                    report.append(f"- **Trending**: {count} {trend_type}s in last 24h")
                    report.append(f"- **Sleeper ID**: {player.get('player_id','N/A')}")
                    report.append(f"- **Status**: {player.get('status','N/A')}")
                    
                    # Fantasy positions
                    fantasy_pos = player.get('fantasy_positions', [])
                    if fantasy_pos:
                        report.append(f"- **Fantasy Positions**: {', '.join(fantasy_pos)}")
                    
                    # Injury info
                    injury_status = player.get('injury_status', '')
                    injury_body_part = player.get('injury_body_part', '')
                    injury_notes = player.get('injury_notes', '')
                    if injury_status or injury_body_part or injury_notes:
                        injury_line = f"- **Injury**: {injury_status or 'N/A'}"
                        if injury_body_part:
                            injury_line += f" ({injury_body_part})"
                        if injury_notes:
                            injury_line += f" - {injury_notes}"
                        report.append(injury_line)
                    
                    # Depth chart
                    depth_pos = player.get('depth_chart_position', '')
                    depth_order = player.get('depth_chart_order', '')
                    if depth_pos or depth_order:
                        report.append(f"- **Depth Chart**: {depth_pos or 'N/A'} (order {depth_order or 'N/A'})")
                    
                    # Physical and experience
                    age = player.get('age', 'N/A')
                    years_exp = player.get('years_exp', 'N/A')
                    college = player.get('college', 'N/A')
                    report.append(f"- **Bio**: Age {age}, {years_exp} years exp, {college}")
                    
                    # Cross-platform IDs for reference
                    yahoo_id = player.get('yahoo_id', '')
                    espn_id = player.get('espn_id', '')
                    if yahoo_id or espn_id:
                        ids = []
                        if yahoo_id:
                            ids.append(f"Yahoo: {yahoo_id}")
                        if espn_id:
                            ids.append(f"ESPN: {espn_id}")
                        report.append(f"- **Platform IDs**: {' | '.join(ids)}")
                    
                    report.append("")

            return "\n".join(report)
        except Exception as exc:
            self.logger.error(f"❌ Error generating markdown report: {exc}")
            return f"# Error generating report\n\nError: {exc}"


def main() -> None:
    extractor = SleeperTrendingExtractor()
    data = extractor.extract_all_data()
    if data:
        ok = extractor.save_data(data)
        if ok:
            print("✅ Sleeper Trending extraction completed successfully!")
            print(f"📈 Trending adds: {len(data.get('trending_adds', []))}")
            print(f"📉 Trending drops: {len(data.get('trending_drops', []))}")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ No data extracted")


if __name__ == "__main__":
    main()
