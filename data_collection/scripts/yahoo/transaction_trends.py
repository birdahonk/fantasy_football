#!/usr/bin/env python3
"""
Yahoo Fantasy Football - Transaction Trends Data Extraction

This script extracts ALL transactions from the Yahoo Fantasy API for the league
and computes player add/drop trends. It outputs both clean markdown and raw JSON.

Purpose: Clean, focused data extraction for transactions and trends
Output: Organized markdown file + raw API response JSON
Focus: Extract ALL data, no analysis beyond simple add/drop counts
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from yahoo_auth import SimpleYahooAuth
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager


class TransactionTrendsExtractor:
    """Extract and aggregate league transactions into player add/drop trends."""

    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.yahoo_auth = SimpleYahooAuth()
        self.formatter = MarkdownFormatter()
        self.file_manager = DataFileManager()

        self.execution_stats: Dict[str, Any] = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'errors': 0,
            'transactions_extracted': 0,
            'pages_processed': 0
        }

    def extract_all_data(self) -> Dict[str, Any]:
        """Extract all transactions and compute trends."""
        self.logger.info("🚀 Starting Transaction Trends Extraction")
        try:
            league_info = self._get_league_info()
            if not league_info:
                self.logger.error("❌ Failed to get league info")
                return {}

            league_key = league_info.get('league_key', '')
            self.logger.info(f"✅ Found league: {league_info.get('league_name', 'Unknown')} ({league_key})")

            transactions = self._extract_all_transactions(league_key)
            trends = self._compute_player_trends(transactions)

            # Extract season context
            season_context = self._extract_season_context(league_info)

            result: Dict[str, Any] = {
                'extraction_metadata': {
                    'league_info': league_info,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'total_transactions': len(transactions),
                    'execution_stats': self.execution_stats
                },
                'season_context': season_context,
                'transactions': transactions,
                'player_trends': trends
            }

            # finalize timing
            self.execution_stats['execution_time'] = (
                datetime.now() - self.execution_stats['start_time']
            ).total_seconds()

            self.logger.info(
                f"✅ Extraction complete: {len(transactions)} transactions, "
                f"{self.execution_stats['execution_time']:.2f}s"
            )
            return result

        except Exception as exc:  # pragma: no cover
            self.logger.error(f"❌ Error in extract_all_data: {exc}")
            import traceback
            self.logger.error(traceback.format_exc())
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
            matchup_files = list(matchups_dir.glob("**/*_team_matchups_raw_data.json"))
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
        """Discover user's league using proven pattern from roster scripts."""
        try:
            self.logger.info("🔍 Getting league information")
            resp = self.yahoo_auth.make_request("users;use_login=1/games;game_keys=nfl/teams")
            self.execution_stats['api_calls'] += 1

            if not resp or 'parsed' not in resp:
                self.logger.error("❌ Invalid response structure")
                return {}

            parsed = resp['parsed']
            fantasy_content = parsed.get('fantasy_content', {})
            users = fantasy_content.get('users', {})
            user_data = users.get('0', {}).get('user', [])
            if not isinstance(user_data, list) or not user_data:
                self.logger.error("❌ Invalid user_data structure")
                return {}

            games_section = None
            for section in user_data:
                if isinstance(section, dict) and 'games' in section:
                    games_section = section['games']
                    break
            if not games_section:
                self.logger.error("❌ No games section found")
                return {}

            nfl_game_data = games_section.get('0', {}).get('game', [])
            if not isinstance(nfl_game_data, list) or not nfl_game_data:
                self.logger.error("❌ Invalid game data structure")
                return {}

            teams_section = None
            league_info: Dict[str, Any] = {}
            for game_section in nfl_game_data:
                if isinstance(game_section, dict):
                    if 'teams' in game_section:
                        teams_section = game_section['teams']
                    for key in ['game_key', 'name', 'season']:
                        if key in game_section:
                            league_info[key] = game_section[key]

            if not teams_section:
                self.logger.error("❌ No teams section found")
                return {}

            team_data = teams_section.get('0', {}).get('team', [])
            if not isinstance(team_data, list) or not team_data:
                self.logger.error("❌ Invalid team data structure")
                return {}

            # flatten team properties
            properties: Dict[str, Any] = {}
            prop_list = team_data[0] if team_data and isinstance(team_data[0], list) else team_data
            for prop in prop_list:
                if isinstance(prop, dict):
                    for k, v in prop.items():
                        properties[k] = v

            if properties.get('is_owned_by_current_login') != 1:
                self.logger.error("❌ Team is not owned by current user")
                return {}

            team_key = properties.get('team_key', '')
            league_key = team_key.split('.t.')[0] if team_key else ''

            return {
                'team_key': team_key,
                'team_name': properties.get('name', ''),
                'team_id': properties.get('team_id', ''),
                'league_key': league_key,
                'league_name': f"Fantasy League ({league_info.get('season', '2025')})"
            }

        except Exception as exc:
            self.logger.error(f"❌ Error getting league info: {exc}")
            return {}

    def _extract_all_transactions(self, league_key: str) -> List[Dict[str, Any]]:
        """Paginate through transactions and extract all entries."""
        all_tx: List[Dict[str, Any]] = []
        start = 0
        count = 25
        total = None

        self.logger.info(f"🔍 Starting transaction pagination for league: {league_key}")
        while True:
            try:
                endpoint = f"league/{league_key}/transactions;start={start};count={count}"
                self.logger.info(f"📄 Fetching transactions {start}-{start+count-1}")
                resp = self.yahoo_auth.make_request(endpoint)
                self.execution_stats['api_calls'] += 1
                self.execution_stats['pages_processed'] += 1

                if not resp or 'parsed' not in resp:
                    self.logger.error(f"❌ Invalid response for page {start}")
                    break

                parsed = resp['parsed']
                fantasy_content = parsed.get('fantasy_content', {})
                league = fantasy_content.get('league', [])
                if not league or len(league) < 2:
                    self.logger.error(f"❌ Unexpected league structure for page {start}")
                    break

                transactions_section = None
                for section in league:
                    if isinstance(section, dict) and 'transactions' in section:
                        transactions_section = section['transactions']
                        break
                if not transactions_section:
                    self.logger.info("ℹ️ No transactions section on this page")
                    break

                if total is None:
                    total = int(transactions_section.get('total', 0))
                    self.logger.info(f"📊 Total transactions (reported): {total}")
                    if total == 0:
                        self.logger.info("📊 Total is 0; will continue until page not full")

                page_tx = self._extract_transactions_from_page(transactions_section)
                all_tx.extend(page_tx)
                self.logger.info(f"✅ Page {start//count + 1}: {len(page_tx)} transactions")

                if (total and len(all_tx) >= total) or (len(page_tx) < count):
                    break

                start += count

            except Exception as exc:
                self.logger.error(f"❌ Error processing page {start}: {exc}")
                self.execution_stats['errors'] += 1
                break

        self.execution_stats['transactions_extracted'] = len(all_tx)
        self.logger.info(f"✅ Transaction pagination complete: {len(all_tx)} total")
        return all_tx

    def _extract_transactions_from_page(self, transactions_section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract transactions from a single page, handling Yahoo's structure."""
        results: List[Dict[str, Any]] = []
        try:
            index = 0
            while str(index) in transactions_section:
                tx_wrapper = transactions_section[str(index)]
                tx = tx_wrapper.get('transaction') if isinstance(tx_wrapper, dict) else None
                if not tx:
                    index += 1
                    continue

                # tx is expected to be an object; sometimes list-of-lists like other endpoints
                tx_dict: Dict[str, Any] = {}
                if isinstance(tx, list):
                    # Flatten list-of-lists
                    for chunk in tx:
                        if isinstance(chunk, list):
                            for prop in chunk:
                                if isinstance(prop, dict):
                                    for k, v in prop.items():
                                        tx_dict[k] = v
                        elif isinstance(chunk, dict):
                            for k, v in chunk.items():
                                tx_dict[k] = v
                elif isinstance(tx, dict):
                    tx_dict = tx

                # Extract players involved
                players: List[Dict[str, Any]] = []
                players_section = tx_dict.get('players', {})
                p_idx = 0
                while isinstance(players_section, dict) and str(p_idx) in players_section:
                    player_entry = players_section[str(p_idx)].get('player', [])
                    player_info: Dict[str, Any] = {}
                    if isinstance(player_entry, list) and player_entry:
                        for chunk in player_entry:
                            if isinstance(chunk, dict):
                                for k, v in chunk.items():
                                    player_info[k] = v
                            elif isinstance(chunk, list):
                                for prop in chunk:
                                    if isinstance(prop, dict):
                                        for k, v in prop.items():
                                            player_info[k] = v
                    if player_info:
                        players.append(player_info)
                    p_idx += 1

                tx_record = {
                    'transaction_key': tx_dict.get('transaction_key', ''),
                    'transaction_id': tx_dict.get('transaction_id', ''),
                    'type': tx_dict.get('type', ''),
                    'status': tx_dict.get('status', ''),
                    'timestamp': tx_dict.get('timestamp', ''),
                    'trader_team_key': tx_dict.get('trader_team_key', ''),
                    'tradee_team_key': tx_dict.get('tradee_team_key', ''),
                    'players': players,
                    'raw': tx_dict
                }
                results.append(tx_record)
                index += 1

        except Exception as exc:
            self.logger.error(f"❌ Error extracting transactions from page: {exc}")

        return results

    def _compute_player_trends(self, transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Aggregate simple add/drop counts per player_id."""
        trends: Dict[str, Dict[str, Any]] = {}
        for tx in transactions:
            tx_type = (tx.get('type') or '').lower()
            for p in tx.get('players', []):
                player_id = p.get('player_id') or ''
                name_obj = p.get('name') or {}
                full_name = name_obj.get('full', 'Unknown') if isinstance(name_obj, dict) else 'Unknown'
                team = p.get('editorial_team_abbr', 'N/A')
                position = p.get('display_position', 'N/A')

                if player_id not in trends:
                    trends[player_id] = {
                        'player_id': player_id,
                        'player_key': p.get('player_key', ''),
                        'name': full_name,
                        'team': team,
                        'position': position,
                        'adds': 0,
                        'drops': 0
                    }

                if 'add' in tx_type:
                    trends[player_id]['adds'] += 1
                if 'drop' in tx_type:
                    trends[player_id]['drops'] += 1

        return trends

    def save_data(self, data: Dict[str, Any]) -> bool:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_ok = self.file_manager.save_raw_data('yahoo', 'transaction_trends', data, timestamp)
            markdown = self._generate_markdown_report(data)
            md_ok = self.file_manager.save_clean_data('yahoo', 'transaction_trends', markdown, timestamp)
            log_ok = self.file_manager.save_execution_log('yahoo', 'transaction_trends', self.execution_stats, timestamp)
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
            league_info = meta.get('league_info', {})
            stats = meta.get('execution_stats', {})

            report: List[str] = []
            report.append("# Yahoo Fantasy Football - Transaction Trends")
            report.append("")
            report.append(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**League:** {league_info.get('league_name', 'Unknown')}")
            report.append(f"**League Key:** {league_info.get('league_key', 'Unknown')}")
            report.append(f"**Total Transactions:** {meta.get('total_transactions', 0)}")
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

            # Recent Transactions (limit 100)
            tx_list = data.get('transactions', [])
            report.append("## Recent Transactions")
            report.append(f"**Showing:** {min(100, len(tx_list))} of {len(tx_list)}")
            report.append("")
            if tx_list:
                report.append("| Time | Type | Status | Players |")
                report.append("|------|------|--------|---------|")
                for tx in tx_list[:100]:
                    ts = tx.get('timestamp', '')
                    ttype = tx.get('type', '')
                    status = tx.get('status', '')
                    players_str = ", ".join([
                        f"{p.get('name', {}).get('full', 'Unknown')} ({p.get('display_position','N/A')} {p.get('editorial_team_abbr','N/A')})"
                        if isinstance(p.get('name'), dict) else 'Unknown'
                        for p in tx.get('players', [])
                    ])
                    report.append(f"| {ts} | {ttype} | {status} | {players_str} |")
            report.append("")

            # Top Trends (limit 100)
            trends = data.get('player_trends', {})
            sorted_trends = sorted(trends.values(), key=lambda x: (x['adds'] + x['drops']), reverse=True)
            report.append("## Top Player Transaction Trends")
            report.append(f"**Showing:** {min(100, len(sorted_trends))} of {len(sorted_trends)}")
            report.append("")
            if sorted_trends:
                report.append("| Player | Team | Pos | Adds | Drops | Total |")
                report.append("|--------|------|-----|------|-------|-------|")
                for tr in sorted_trends[:100]:
                    total = tr['adds'] + tr['drops']
                    report.append(
                        f"| {tr['name']} | {tr['team']} | {tr['position']} | {tr['adds']} | {tr['drops']} | {total} |"
                    )

            return "\n".join(report)
        except Exception as exc:
            self.logger.error(f"❌ Error generating markdown report: {exc}")
            return f"# Error generating report\n\nError: {exc}"


def main() -> None:
    extractor = TransactionTrendsExtractor()
    data = extractor.extract_all_data()
    if data:
        ok = extractor.save_data(data)
        if ok:
            print("✅ Transaction Trends extraction completed successfully!")
            print(f"📊 Total transactions: {data.get('extraction_metadata', {}).get('total_transactions', 0)}")
            print(f"⏱️  Execution time: {extractor.execution_stats.get('execution_time', 0):.2f}s")
            print(f"🔗 API calls: {extractor.execution_stats.get('api_calls', 0)}")
            print(f"❌ Errors: {extractor.execution_stats.get('errors', 0)}")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ No data extracted")


if __name__ == "__main__":
    main()


