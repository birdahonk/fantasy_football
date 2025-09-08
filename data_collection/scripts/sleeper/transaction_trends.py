#!/usr/bin/env python3
"""
Sleeper NFL API - Transaction Trends Data Enrichment

This script enriches Yahoo Fantasy transaction trends data with Sleeper API data.
It reads the Yahoo transaction trends to get the list of players being added/dropped
in the user's league, then enriches that data with Sleeper trending data, player
information, and market intelligence.

Purpose: Enrich Yahoo transaction trends with Sleeper data for analyst agent
Output: Organized markdown file + raw JSON data with enriched transaction trends
Focus: League-specific player analysis with trending market intelligence
"""

import os
import sys
import json
import logging
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from sleeper_client import SimpleSleeperClient
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager


class SleeperTransactionTrendsEnricher:
    """Enrich Yahoo transaction trends with Sleeper API data for league-specific analysis."""

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
            'yahoo_transactions_processed': 0,
            'players_enriched': 0,
            'trending_data_found': 0
        }

    def enrich_yahoo_transaction_trends(self) -> Dict[str, Any]:
        """Enrich Yahoo transaction trends with Sleeper API data."""
        try:
            self.logger.info("Starting Yahoo transaction trends enrichment with Sleeper data...")
            
            # Load Yahoo transaction trends data
            yahoo_data = self._load_yahoo_transaction_trends()
            if not yahoo_data:
                raise Exception("Could not load Yahoo transaction trends data")
            
            # Extract player names from Yahoo transactions
            league_players = self._extract_league_players(yahoo_data)
            self.execution_stats['yahoo_transactions_processed'] = len(league_players)
            
            # Get Sleeper player database for matching
            sleeper_players = self._get_sleeper_player_database()
            
            # Get Sleeper trending data
            trending_data = self._get_sleeper_trending_data()
            
            # Match league players to Sleeper players
            matched_players = self._match_players_to_sleeper(league_players, sleeper_players)
            
            # Enrich each matched player with Sleeper data
            enriched_players = self._enrich_players_with_sleeper_data(matched_players, trending_data)
            self.execution_stats['players_enriched'] = len(enriched_players)
            
            # Compile results
            result = {
                'yahoo_data': yahoo_data,
                'league_players': league_players,
                'enriched_players': enriched_players,
                'trending_data': trending_data,
                'enrichment_summary': self._create_enrichment_summary(enriched_players, trending_data),
                'api_usage': {
                    'calls_made_this_session': self.execution_stats.get('api_calls', 0),
                    'daily_limit': 'Unlimited (Free API)',
                    'remaining_calls': 'Unlimited (Free API)'
                }
            }
            
            self.execution_stats['api_calls'] = self.execution_stats.get('api_calls', 0)
            
            self.logger.info(f"Successfully enriched {self.execution_stats['players_enriched']} players with Sleeper data")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error enriching Yahoo transaction trends: {e}")
            self.execution_stats['errors'] += 1
            raise

    def _load_yahoo_transaction_trends(self) -> Optional[Dict[str, Any]]:
        """Load the latest Yahoo transaction trends data."""
        try:
            # Find the latest Yahoo transaction trends file
            yahoo_files = glob.glob("../../outputs/yahoo/transaction_trends/**/*_raw_data.json", recursive=True)
            if not yahoo_files:
                self.logger.error("No Yahoo transaction trends files found")
                return None
            
            # Get the most recent file
            latest_file = max(yahoo_files, key=os.path.getctime)
            self.logger.info(f"Loading Yahoo data from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading Yahoo transaction trends: {e}")
            return None

    def _extract_league_players(self, yahoo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract unique players from Yahoo transaction data."""
        try:
            players = []
            transactions = yahoo_data.get('transactions', [])
            
            self.logger.info(f"Found {len(transactions)} transactions to process")
            
            for i, transaction in enumerate(transactions):
                self.logger.info(f"Processing transaction {i+1}: {type(transaction)}")
                
                if not isinstance(transaction, dict):
                    self.logger.warning(f"Transaction {i+1} is not a dict: {type(transaction)}")
                    continue
                    
                try:
                    transaction_type = transaction.get('type', 'Unknown')
                except AttributeError as e:
                    self.logger.error(f"Error getting transaction type: {e}")
                    continue
                transaction_time = transaction.get('timestamp', 'Unknown')
                
                # Extract players from the transaction
                transaction_players = transaction.get('players', [])
                
                # Handle case where players might not be a list
                if not isinstance(transaction_players, list):
                    self.logger.warning(f"Transaction players is not a list: {type(transaction_players)}")
                    continue
                
                for player_data in transaction_players:
                    # Debug: check if player_data is a dict
                    if not isinstance(player_data, dict):
                        self.logger.warning(f"Player data is not a dict: {type(player_data)} - {player_data}")
                        continue
                    
                    # Get player name
                    name_info = player_data.get('name', {})
                    if not isinstance(name_info, dict):
                        self.logger.warning(f"Name info is not a dict: {type(name_info)} - {name_info}")
                        continue
                        
                    player_name = name_info.get('full', 'Unknown')
                    
                    # Get position and team
                    position = player_data.get('display_position', 'Unknown')
                    team = player_data.get('editorial_team_abbr', 'Unknown')
                    
                    # Get transaction details
                    transaction_details = player_data.get('transaction_data', [])
                    
                    # Handle case where transaction_details might not be a list
                    if not isinstance(transaction_details, list):
                        self.logger.warning(f"Transaction details is not a list: {type(transaction_details)}")
                        transaction_details = []
                    
                    for detail in transaction_details:
                        if not isinstance(detail, dict):
                            self.logger.warning(f"Transaction detail is not a dict: {type(detail)} - {detail}")
                            continue
                            
                        action_type = detail.get('type', 'Unknown')
                        
                        players.append({
                            'name': player_name,
                            'position': position,
                            'team': team,
                            'transaction_type': f"{transaction_type}_{action_type}",
                            'transaction_time': transaction_time,
                            'yahoo_data': {
                                'transaction': transaction,
                                'player': player_data,
                                'transaction_detail': detail
                            }
                        })
            
            # Remove duplicates while preserving transaction context
            unique_players = {}
            for player in players:
                key = f"{player['name']}_{player['team']}"
                if key not in unique_players:
                    unique_players[key] = player
                else:
                    # Merge transaction types if player appears multiple times
                    existing = unique_players[key]
                    if player['transaction_type'] != existing['transaction_type']:
                        existing['transaction_type'] = 'mixed'
            
            self.logger.info(f"Extracted {len(unique_players)} unique players from {len(transactions)} transactions")
            return list(unique_players.values())
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error extracting league players: {e}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    def _get_sleeper_player_database(self) -> Dict[str, Any]:
        """Get Sleeper player database for matching."""
        try:
            players_response = self.sleeper.get_nfl_players()
            self.execution_stats['api_calls'] += 1
            
            players = {}
            if players_response:
                for player_id, player_data in players_response.items():
                    players[player_id] = {
                        'player_id': player_id,
                        'name': player_data.get('full_name', 'Unknown'),
                        'first_name': player_data.get('first_name', 'Unknown'),
                        'last_name': player_data.get('last_name', 'Unknown'),
                        'team': player_data.get('team', 'Unknown'),
                        'position': player_data.get('position', 'Unknown'),
                        'age': player_data.get('age', 'Unknown'),
                        'years_exp': player_data.get('years_exp', 'Unknown'),
                        'injury_status': player_data.get('injury_status', 'Unknown'),
                        'news_updated': player_data.get('news_updated', 'Unknown')
                    }
            
            return players
            
        except Exception as e:
            self.logger.error(f"Error getting Sleeper player database: {e}")
            return {}

    def _get_sleeper_trending_data(self) -> Dict[str, Any]:
        """Get Sleeper trending data (adds, drops, waivers)."""
        try:
            trending_data = {}
            
            # Get trending adds
            trending_adds = self.sleeper.get_trending_players("add")
            self.execution_stats['api_calls'] += 1
            trending_data['trending_adds'] = trending_adds or []
            
            # Get trending drops
            trending_drops = self.sleeper.get_trending_players("drop")
            self.execution_stats['api_calls'] += 1
            trending_data['trending_drops'] = trending_drops or []
            
            # Get trending waivers
            trending_waivers = self.sleeper.get_trending_players("waiver")
            self.execution_stats['api_calls'] += 1
            trending_data['trending_waivers'] = trending_waivers or []
            
            # Get NFL state for context
            nfl_state = self.sleeper.get_nfl_state()
            self.execution_stats['api_calls'] += 1
            trending_data['nfl_state'] = nfl_state or {}
            
            self.execution_stats['trending_data_found'] = len(trending_data.get('trending_adds', [])) + len(trending_data.get('trending_drops', [])) + len(trending_data.get('trending_waivers', []))
            
            return trending_data
            
        except Exception as e:
            self.logger.error(f"Error getting Sleeper trending data: {e}")
            return {}

    def _match_players_to_sleeper(self, league_players: List[Dict[str, Any]], sleeper_players: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match league players to Sleeper players."""
        try:
            matched_players = []
            
            for league_player in league_players:
                player_name = league_player['name']
                player_team = league_player['team']
                player_position = league_player['position']
                
                # Try to find matching Sleeper player
                sleeper_match = None
                
                # Strategy 1: Exact name and team match
                for sleeper_id, sleeper_player in sleeper_players.items():
                    sleeper_team = sleeper_player.get('team')
                    if (sleeper_player['name'].lower() == player_name.lower() and 
                        sleeper_team and sleeper_team.upper() == player_team.upper()):
                        sleeper_match = sleeper_player
                        break
                
                # Strategy 2: Partial name match with team
                if not sleeper_match:
                    for sleeper_id, sleeper_player in sleeper_players.items():
                        sleeper_team = sleeper_player.get('team')
                        if (player_name.lower() in sleeper_player['name'].lower() and 
                            sleeper_team and sleeper_team.upper() == player_team.upper()):
                            sleeper_match = sleeper_player
                            break
                
                # Strategy 3: Name match only (if team doesn't match)
                if not sleeper_match:
                    for sleeper_id, sleeper_player in sleeper_players.items():
                        if sleeper_player['name'].lower() == player_name.lower():
                            sleeper_match = sleeper_player
                            break
                
                # Create enriched player data
                enriched_player = {
                    'yahoo_data': league_player,
                    'sleeper_data': sleeper_match,
                    'match_status': 'matched' if sleeper_match else 'unmatched',
                    'match_confidence': 'high' if sleeper_match and sleeper_match.get('team') and sleeper_match['team'].upper() == player_team.upper() else 'medium' if sleeper_match else 'none'
                }
                
                matched_players.append(enriched_player)
            
            return matched_players
            
        except Exception as e:
            self.logger.error(f"Error matching players to Sleeper: {e}")
            return []

    def _enrich_players_with_sleeper_data(self, matched_players: List[Dict[str, Any]], trending_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich matched players with additional Sleeper data."""
        try:
            enriched_players = []
            
            # Create lookup for trending data
            trending_adds = {item.get('player_id'): item for item in trending_data.get('trending_adds', [])}
            trending_drops = {item.get('player_id'): item for item in trending_data.get('trending_drops', [])}
            trending_waivers = {item.get('player_id'): item for item in trending_data.get('trending_waivers', [])}
            
            for player in matched_players:
                if player['match_status'] == 'matched' and player['sleeper_data']:
                    sleeper_player = player['sleeper_data']
                    player_id = sleeper_player['player_id']
                    
                    # Check if player is trending
                    trending_info = {
                        'is_trending_add': player_id in trending_adds,
                        'is_trending_drop': player_id in trending_drops,
                        'is_trending_waiver': player_id in trending_waivers,
                        'trending_add_data': trending_adds.get(player_id),
                        'trending_drop_data': trending_drops.get(player_id),
                        'trending_waiver_data': trending_waivers.get(player_id)
                    }
                    
                    # Add enrichment data
                    player['sleeper_enrichment'] = {
                        'trending_info': trending_info,
                        'player_details': {
                            'age': sleeper_player.get('age'),
                            'years_exp': sleeper_player.get('years_exp'),
                            'injury_status': sleeper_player.get('injury_status'),
                            'news_updated': sleeper_player.get('news_updated')
                        },
                        'enrichment_time': datetime.now().isoformat()
                    }
                
                enriched_players.append(player)
            
            return enriched_players
            
        except Exception as e:
            self.logger.error(f"Error enriching players with Sleeper data: {e}")
            return matched_players

    def _create_enrichment_summary(self, enriched_players: List[Dict[str, Any]], trending_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the enrichment process."""
        try:
            total_players = len(enriched_players)
            matched_players = len([p for p in enriched_players if p['match_status'] == 'matched'])
            unmatched_players = total_players - matched_players
            
            high_confidence_matches = len([p for p in enriched_players if p.get('match_confidence') == 'high'])
            medium_confidence_matches = len([p for p in enriched_players if p.get('match_confidence') == 'medium'])
            
            # Analyze transaction types
            transaction_types = {}
            for player in enriched_players:
                yahoo_data = player.get('yahoo_data', {})
                trans_type = yahoo_data.get('transaction_type', 'Unknown')
                transaction_types[trans_type] = transaction_types.get(trans_type, 0) + 1
            
            # Analyze trending data
            trending_summary = {
                'total_trending_adds': len(trending_data.get('trending_adds', [])),
                'total_trending_drops': len(trending_data.get('trending_drops', [])),
                'total_trending_waivers': len(trending_data.get('trending_waivers', [])),
                'nfl_state': trending_data.get('nfl_state', {})
            }
            
            return {
                'total_players_processed': total_players,
                'matched_players': matched_players,
                'unmatched_players': unmatched_players,
                'match_rate': f"{(matched_players/total_players*100):.1f}%" if total_players > 0 else "0%",
                'high_confidence_matches': high_confidence_matches,
                'medium_confidence_matches': medium_confidence_matches,
                'transaction_types': transaction_types,
                'trending_summary': trending_summary,
                'enrichment_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating enrichment summary: {e}")
            return {
                'total_players_processed': 0,
                'matched_players': 0,
                'unmatched_players': 0,
                'match_rate': '0%',
                'error': str(e)
            }

    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report of enriched transaction trends."""
        try:
            report = []
            
            # Header
            report.append("# Yahoo Transaction Trends - Sleeper Enrichment")
            report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # League Information
            yahoo_data = data.get('yahoo_data', {})
            league_info = yahoo_data.get('extraction_metadata', {}).get('league_info', {})
            report.append(f"**League:** {league_info.get('league_name', 'Unknown')}")
            report.append(f"**League Key:** {league_info.get('league_key', 'Unknown')}")
            report.append("")
            
            # Enrichment Summary
            enrichment_summary = data.get('enrichment_summary', {})
            report.append("## Enrichment Summary")
            report.append(f"- **Total Players Processed:** {enrichment_summary.get('total_players_processed', 0)}")
            report.append(f"- **Players Matched:** {enrichment_summary.get('matched_players', 0)}")
            report.append(f"- **Players Unmatched:** {enrichment_summary.get('unmatched_players', 0)}")
            report.append(f"- **Match Rate:** {enrichment_summary.get('match_rate', '0%')}")
            report.append(f"- **High Confidence Matches:** {enrichment_summary.get('high_confidence_matches', 0)}")
            report.append(f"- **Medium Confidence Matches:** {enrichment_summary.get('medium_confidence_matches', 0)}")
            report.append("")
            
            # Transaction Types
            transaction_types = enrichment_summary.get('transaction_types', {})
            if transaction_types:
                report.append("### Transaction Types")
                for trans_type, count in transaction_types.items():
                    report.append(f"- **{trans_type}:** {count}")
                report.append("")
            
            # Trending Data Summary
            trending_summary = enrichment_summary.get('trending_summary', {})
            report.append("## Sleeper Trending Data")
            report.append(f"- **Trending Adds:** {trending_summary.get('total_trending_adds', 0)}")
            report.append(f"- **Trending Drops:** {trending_summary.get('total_trending_drops', 0)}")
            report.append(f"- **Trending Waivers:** {trending_summary.get('total_trending_waivers', 0)}")
            
            nfl_state = trending_summary.get('nfl_state', {})
            if nfl_state:
                report.append(f"- **Current Week:** {nfl_state.get('week', 'Unknown')}")
                report.append(f"- **Season:** {nfl_state.get('season', 'Unknown')}")
                report.append(f"- **Season Type:** {nfl_state.get('season_type', 'Unknown')}")
            report.append("")
            
            # API Usage
            api_usage = data.get('api_usage', {})
            report.append("## API Usage")
            report.append(f"- **Calls Made:** {api_usage.get('calls_made_this_session', 'Unknown')}")
            report.append(f"- **Daily Limit:** {api_usage.get('daily_limit', 'Unknown')}")
            report.append(f"- **Remaining:** {api_usage.get('remaining_calls', 'Unknown')}")
            report.append("")
            
            # Enriched Players Summary
            enriched_players = data.get('enriched_players', [])
            matched_players = [p for p in enriched_players if p.get('match_status') == 'matched']
            
            report.append("## Enriched Players Summary")
            report.append(f"- **Total Players:** {len(enriched_players)}")
            report.append(f"- **Successfully Matched:** {len(matched_players)}")
            report.append(f"- **Unmatched:** {len(enriched_players) - len(matched_players)}")
            report.append("")
            
            # Top Enriched Players
            if matched_players:
                report.append("## Top Enriched Players")
                report.append("")
                
                # Show top 10 matched players with their enrichment data
                for i, player in enumerate(matched_players[:10]):
                    yahoo_data = player.get('yahoo_data', {})
                    sleeper_data = player.get('sleeper_data', {})
                    sleeper_enrichment = player.get('sleeper_enrichment', {})
                    
                    player_name = yahoo_data.get('name', 'Unknown')
                    position = yahoo_data.get('position', 'Unknown')
                    team = yahoo_data.get('team', 'Unknown')
                    transaction_type = yahoo_data.get('transaction_type', 'Unknown')
                    match_confidence = player.get('match_confidence', 'Unknown')
                    
                    report.append(f"### {i+1}. {player_name} ({position}, {team})")
                    report.append(f"- **Transaction Type:** {transaction_type}")
                    report.append(f"- **Match Confidence:** {match_confidence}")
                    report.append(f"- **Sleeper Player ID:** {sleeper_data.get('player_id', 'Unknown')}")
                    
                    # Trending info
                    trending_info = sleeper_enrichment.get('trending_info', {})
                    if trending_info.get('is_trending_add'):
                        add_data = trending_info.get('trending_add_data', {})
                        report.append(f"- **Trending Add:** Yes (count: {add_data.get('count', 'Unknown')})")
                    if trending_info.get('is_trending_drop'):
                        drop_data = trending_info.get('trending_drop_data', {})
                        report.append(f"- **Trending Drop:** Yes (count: {drop_data.get('count', 'Unknown')})")
                    if trending_info.get('is_trending_waiver'):
                        waiver_data = trending_info.get('trending_waiver_data', {})
                        report.append(f"- **Trending Waiver:** Yes (count: {waiver_data.get('count', 'Unknown')})")
                    
                    # Player details
                    player_details = sleeper_enrichment.get('player_details', {})
                    if player_details.get('injury_status') and player_details.get('injury_status') != 'Unknown':
                        report.append(f"- **Injury Status:** {player_details.get('injury_status')}")
                    if player_details.get('age') and player_details.get('age') != 'Unknown':
                        report.append(f"- **Age:** {player_details.get('age')}")
                    if player_details.get('years_exp') and player_details.get('years_exp') != 'Unknown':
                        report.append(f"- **Experience:** {player_details.get('years_exp')} years")
                    
                    report.append("")
            else:
                report.append("## Enriched Players")
                report.append("No players were successfully matched and enriched.")
                report.append("")
            
            # Fantasy Football Context
            report.append("## Fantasy Football Context")
            report.append("")
            report.append("### Key Insights")
            report.append("- Sleeper trending data shows real-time market movement")
            report.append("- Player injury status and experience provide roster context")
            report.append("- Trending adds/drops indicate league-wide player value changes")
            report.append("- Cross-platform data helps identify undervalued players")
            report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating markdown report: {e}")
            return f"# Error generating report: {e}"

    def run(self) -> bool:
        """Run the complete transaction trends enrichment process."""
        try:
            self.logger.info("Starting Yahoo transaction trends enrichment with Sleeper data...")
            
            # Enrich Yahoo data with Sleeper data
            data = self.enrich_yahoo_transaction_trends()
            
            # Generate timestamp
            timestamp = self.file_manager.generate_timestamp()
            
            # Generate markdown report
            markdown_report = self.generate_markdown_report(data)
            
            # Save outputs
            clean_file = self.file_manager.save_clean_data(
                "sleeper", "transaction_trends", markdown_report, timestamp
            )
            
            raw_file = self.file_manager.save_raw_data(
                "sleeper", "transaction_trends", data, timestamp
            )
            
            # Save execution log
            self.execution_stats['end_time'] = datetime.now()
            self.execution_stats['duration'] = (
                self.execution_stats['end_time'] - self.execution_stats['start_time']
            ).total_seconds()
            
            log_file = self.file_manager.save_execution_log(
                "sleeper", "transaction_trends", self.execution_stats, timestamp
            )
            
            self.logger.info(f"Yahoo transaction trends enrichment completed successfully!")
            self.logger.info(f"Clean data saved to: {clean_file}")
            self.logger.info(f"Raw data saved to: {raw_file}")
            self.logger.info(f"Execution log saved to: {log_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Yahoo transaction trends enrichment failed: {e}")
            self.execution_stats['errors'] += 1
            return False


def main():
    """Main execution function."""
    enricher = SleeperTransactionTrendsEnricher()
    success = enricher.run()
    
    if success:
        print("✅ Sleeper transaction trends enrichment completed successfully!")
        sys.exit(0)
    else:
        print("❌ Sleeper transaction trends enrichment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
