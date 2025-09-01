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
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

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

            result: Dict[str, Any] = {
                'extraction_metadata': {
                    'league_info': league_info,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'total_transactions': len(transactions),
                    'execution_stats': self.execution_stats
                },
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


