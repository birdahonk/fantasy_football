#!/usr/bin/env python3
"""
Tank01 NFL API - Transaction Trends Data Enrichment

This script enriches Yahoo Fantasy transaction trends data with Tank01 API data.
It reads the Yahoo transaction trends to get the list of players being added/dropped
in the user's league, then enriches that data with Tank01 news, projections, and
market intelligence.

Purpose: Enrich Yahoo transaction trends with Tank01 data for analyst agent
Output: Organized markdown file + raw JSON data with enriched transaction trends
Focus: League-specific player analysis with market intelligence
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

from tank01_client import SimpleTank01Client
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager


class Tank01TransactionTrendsEnricher:
    """Enrich Yahoo transaction trends with Tank01 API data for league-specific analysis."""

    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.tank01 = SimpleTank01Client()
        self.formatter = MarkdownFormatter()
        self.file_manager = DataFileManager()

        self.execution_stats: Dict[str, Any] = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'errors': 0,
            'yahoo_transactions_processed': 0,
            'players_enriched': 0,
            'news_items_found': 0
        }

    def enrich_yahoo_transaction_trends(self) -> Dict[str, Any]:
        """Enrich Yahoo transaction trends with Tank01 API data."""
        try:
            self.logger.info("Starting Yahoo transaction trends enrichment with Tank01 data...")
            
            # Load Yahoo transaction trends data
            yahoo_data = self._load_yahoo_transaction_trends()
            if not yahoo_data:
                raise Exception("Could not load Yahoo transaction trends data")
            
            # Extract player names from Yahoo transactions
            league_players = self._extract_league_players(yahoo_data)
            self.execution_stats['yahoo_transactions_processed'] = len(league_players)
            
            # Get Tank01 player database for matching
            tank01_players = self._get_tank01_player_database()
            
            # Match league players to Tank01 players
            matched_players = self._match_players_to_tank01(league_players, tank01_players)
            
            # Enrich each matched player with Tank01 data
            enriched_players = self._enrich_players_with_tank01_data(matched_players)
            self.execution_stats['players_enriched'] = len(enriched_players)
            
            # Compile results
            result = {
                'yahoo_data': yahoo_data,
                'league_players': league_players,
                'enriched_players': enriched_players,
                'enrichment_summary': self._create_enrichment_summary(enriched_players),
                'api_usage': self.tank01.get_api_usage()
            }
            
            self.execution_stats['api_calls'] = self.tank01.get_api_usage()['calls_made_this_session']
            
            self.logger.info(f"Successfully enriched {self.execution_stats['players_enriched']} players with Tank01 data")
            
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
                self.logger.info(f"Transaction content: {str(transaction)[:200]}...")
                
                if not isinstance(transaction, dict):
                    self.logger.warning(f"Transaction {i+1} is not a dict: {type(transaction)}")
                    continue
                    
                try:
                    transaction_type = transaction.get('type', 'Unknown')
                except AttributeError as e:
                    self.logger.error(f"Error getting transaction type: {e}")
                    self.logger.error(f"Transaction is actually: {type(transaction)} - {transaction}")
                    continue
                transaction_time = transaction.get('timestamp', 'Unknown')
                
                # Extract players from the transaction
                transaction_players = transaction.get('players', [])
                
                # Handle case where players might be a string or other format
                if isinstance(transaction_players, str):
                    self.logger.warning(f"Transaction players is a string: {transaction_players}")
                    continue
                elif not isinstance(transaction_players, list):
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

    def _get_tank01_player_database(self) -> Dict[str, Any]:
        """Get Tank01 player database for matching."""
        try:
            players_response = self.tank01.get_player_list()
            
            players = {}
            if players_response and 'body' in players_response:
                for player in players_response['body']:
                    player_id = player.get('playerID', 'Unknown')
                    players[player_id] = {
                        'player_id': player_id,
                        'name': player.get('longName', 'Unknown'),
                        'team': player.get('team', 'Unknown'),
                        'position': player.get('pos', 'Unknown'),
                        'yahoo_id': player.get('yahooPlayerID', 'Unknown'),
                        'sleeper_id': player.get('sleeperBotID', 'Unknown')
                    }
            
            return players
            
        except Exception as e:
            self.logger.error(f"Error getting Tank01 player database: {e}")
            return {}

    def _match_players_to_tank01(self, league_players: List[Dict[str, Any]], tank01_players: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match league players to Tank01 players."""
        try:
            matched_players = []
            
            for league_player in league_players:
                player_name = league_player['name']
                player_team = league_player['team']
                player_position = league_player['position']
                
                # Try to find matching Tank01 player
                tank01_match = None
                
                # Strategy 1: Exact name and team match
                for tank01_id, tank01_player in tank01_players.items():
                    if (tank01_player['name'].lower() == player_name.lower() and 
                        tank01_player['team'].upper() == player_team.upper()):
                        tank01_match = tank01_player
                        break
                
                # Strategy 2: Partial name match with team
                if not tank01_match:
                    for tank01_id, tank01_player in tank01_players.items():
                        if (player_name.lower() in tank01_player['name'].lower() and 
                            tank01_player['team'].upper() == player_team.upper()):
                            tank01_match = tank01_player
                            break
                
                # Strategy 3: Name match only (if team doesn't match)
                if not tank01_match:
                    for tank01_id, tank01_player in tank01_players.items():
                        if tank01_player['name'].lower() == player_name.lower():
                            tank01_match = tank01_player
                            break
                
                # Create enriched player data
                enriched_player = {
                    'yahoo_data': league_player,
                    'tank01_data': tank01_match,
                    'match_status': 'matched' if tank01_match else 'unmatched',
                    'match_confidence': 'high' if tank01_match and tank01_match['team'].upper() == player_team.upper() else 'medium' if tank01_match else 'none'
                }
                
                matched_players.append(enriched_player)
            
            return matched_players
            
        except Exception as e:
            self.logger.error(f"Error matching players to Tank01: {e}")
            return []

    def _enrich_players_with_tank01_data(self, matched_players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich matched players with additional Tank01 data."""
        try:
            enriched_players = []
            
            for player in matched_players:
                if player['match_status'] == 'matched' and player['tank01_data']:
                    tank01_player = player['tank01_data']
                    player_id = tank01_player['player_id']
                    
                    # Get news for this specific player
                    player_news = self._get_player_news(player_id)
                    
                    # Get weekly projections for this player
                    projections = self._get_player_projections(player_id)
                    
                    # Add enrichment data
                    player['tank01_enrichment'] = {
                        'news': player_news,
                        'projections': projections,
                        'enrichment_time': datetime.now().isoformat()
                    }
                    
                    self.execution_stats['news_items_found'] += len(player_news.get('news_items', []))
                
                enriched_players.append(player)
            
            return enriched_players
            
        except Exception as e:
            self.logger.error(f"Error enriching players with Tank01 data: {e}")
            return matched_players

    def _analyze_news_trends(self, news_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze news data for transaction trends."""
        trends = []
        
        try:
            news_items = news_data.get('news_items', [])
            
            # Look for keywords that might indicate transactions
            transaction_keywords = [
                'signed', 'released', 'waived', 'traded', 'activated', 'injured',
                'suspended', 'practice squad', 'IR', 'PUP', 'designated to return',
                'free agent', 'contract', 'extension', 'restructure'
            ]
            
            for item in news_items:
                title = item.get('title', '').lower()
                for keyword in transaction_keywords:
                    if keyword in title:
                        trends.append({
                            'category': 'news',
                            'type': 'transaction_indicator',
                            'title': item.get('title', 'Unknown'),
                            'keyword': keyword,
                            'player_id': item.get('player_id', 'Unknown'),
                            'link': item.get('link', 'Unknown'),
                            'confidence': 'medium'
                        })
                        break
            
            # Look for injury-related news
            injury_keywords = ['injury', 'injured', 'out', 'questionable', 'doubtful', 'IR']
            for item in news_items:
                title = item.get('title', '').lower()
                for keyword in injury_keywords:
                    if keyword in title:
                        trends.append({
                            'category': 'news',
                            'type': 'injury_update',
                            'title': item.get('title', 'Unknown'),
                            'keyword': keyword,
                            'player_id': item.get('player_id', 'Unknown'),
                            'link': item.get('link', 'Unknown'),
                            'confidence': 'high'
                        })
                        break
            
        except Exception as e:
            self.logger.error(f"Error analyzing news trends: {e}")
        
        return trends

    def _analyze_player_trends(self, player_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze player data for transaction trends."""
        trends = []
        
        try:
            players = player_data.get('players', [])
            
            # Look for players with multiple team IDs (potential trades)
            team_changes = {}
            for player in players:
                player_id = player.get('player_id', 'Unknown')
                team = player.get('team', 'Unknown')
                
                if player_id not in team_changes:
                    team_changes[player_id] = []
                team_changes[player_id].append(team)
            
            # Identify potential team changes
            for player_id, teams in team_changes.items():
                if len(set(teams)) > 1:
                    trends.append({
                        'category': 'player',
                        'type': 'team_change',
                        'player_id': player_id,
                        'teams': list(set(teams)),
                        'confidence': 'low'
                    })
            
        except Exception as e:
            self.logger.error(f"Error analyzing player trends: {e}")
        
        return trends

    def _analyze_team_trends(self, team_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze team data for transaction trends."""
        trends = []
        
        try:
            teams = team_data.get('teams', [])
            
            # Look for teams with significant changes in performance
            for team in teams:
                wins = int(team.get('wins', 0))
                losses = int(team.get('loss', 0))
                
                # Teams with poor records might be more likely to make transactions
                if wins < 3 and losses > 5:
                    trends.append({
                        'category': 'team',
                        'type': 'struggling_team',
                        'team': team.get('team_abv', 'Unknown'),
                        'record': f"{wins}-{losses}",
                        'confidence': 'medium'
                    })
            
        except Exception as e:
            self.logger.error(f"Error analyzing team trends: {e}")
        
        return trends

    def _summarize_player_database(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize player database for reporting."""
        try:
            players = player_data.get('players', [])
            
            # Count by position
            position_counts = {}
            for player in players:
                pos = player.get('position', 'Unknown')
                position_counts[pos] = position_counts.get(pos, 0) + 1
            
            return {
                'total_players': len(players),
                'position_breakdown': position_counts,
                'sample_players': players[:5] if players else []
            }
            
        except Exception as e:
            self.logger.error(f"Error summarizing player database: {e}")
            return {'error': str(e)}

    def _summarize_team_info(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize team information for reporting."""
        try:
            teams = team_data.get('teams', [])
            
            # Count by division
            division_counts = {}
            for team in teams:
                div = team.get('division', 'Unknown')
                division_counts[div] = division_counts.get(div, 0) + 1
            
            return {
                'total_teams': len(teams),
                'division_breakdown': division_counts,
                'sample_teams': teams[:5] if teams else []
            }
            
        except Exception as e:
            self.logger.error(f"Error summarizing team info: {e}")
            return {'error': str(e)}

    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report of enriched transaction trends."""
        try:
            report = []
            
            # Header
            report.append("# Yahoo Transaction Trends - Tank01 Enrichment")
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
                    tank01_data = player.get('tank01_data', {})
                    tank01_enrichment = player.get('tank01_enrichment', {})
                    
                    player_name = yahoo_data.get('name', 'Unknown')
                    position = yahoo_data.get('position', 'Unknown')
                    team = yahoo_data.get('team', 'Unknown')
                    transaction_type = yahoo_data.get('transaction_type', 'Unknown')
                    match_confidence = player.get('match_confidence', 'Unknown')
                    
                    report.append(f"### {i+1}. {player_name} ({position}, {team})")
                    report.append(f"- **Transaction Type:** {transaction_type}")
                    report.append(f"- **Match Confidence:** {match_confidence}")
                    report.append(f"- **Tank01 Player ID:** {tank01_data.get('player_id', 'Unknown')}")
                    
                    # News summary
                    news_data = tank01_enrichment.get('news', {})
                    news_items = news_data.get('news_items', [])
                    if news_items:
                        report.append(f"- **Recent News:** {len(news_items)} items")
                        # Show first news item
                        first_news = news_items[0]
                        report.append(f"  - {first_news.get('title', 'No title')[:100]}...")
                    else:
                        report.append("- **Recent News:** No news found")
                    
                    report.append("")
            else:
                report.append("## Enriched Players")
                report.append("No players were successfully matched and enriched.")
                report.append("")
            
            # Fantasy Football Context
            report.append("## Fantasy Football Context")
            report.append("")
            report.append("### Key Insights")
            report.append("- News analysis provides real-time transaction indicators")
            report.append("- Player movement patterns can indicate roster changes")
            report.append("- Team performance context helps identify transaction likelihood")
            report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating markdown report: {e}")
            return f"# Error generating report: {e}"

    def run(self) -> bool:
        """Run the complete transaction trends enrichment process."""
        try:
            self.logger.info("Starting Yahoo transaction trends enrichment with Tank01 data...")
            
            # Enrich Yahoo data with Tank01 data
            data = self.enrich_yahoo_transaction_trends()
            
            # Generate timestamp
            timestamp = self.file_manager.generate_timestamp()
            
            # Generate markdown report
            markdown_report = self.generate_markdown_report(data)
            
            # Save outputs
            clean_file = self.file_manager.save_clean_data(
                "tank01", "transaction_trends", markdown_report, timestamp
            )
            
            raw_file = self.file_manager.save_raw_data(
                "tank01", "transaction_trends", data, timestamp
            )
            
            # Save execution log
            self.execution_stats['end_time'] = datetime.now()
            self.execution_stats['duration'] = (
                self.execution_stats['end_time'] - self.execution_stats['start_time']
            ).total_seconds()
            
            log_file = self.file_manager.save_execution_log(
                "tank01", "transaction_trends", self.execution_stats, timestamp
            )
            
            self.logger.info(f"Yahoo transaction trends enrichment completed successfully!")
            self.logger.info(f"Clean data saved to: {clean_file}")
            self.logger.info(f"Raw data saved to: {raw_file}")
            self.logger.info(f"Execution log saved to: {log_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Tank01 transaction trends extraction failed: {e}")
            self.execution_stats['errors'] += 1
            return False

    def _get_player_news(self, player_id: str) -> Dict[str, Any]:
        """Get news for a specific player."""
        try:
            news_response = self.tank01.get_news(
                fantasy_news=True,
                max_items=10,
                player_id=player_id
            )
            
            news_items = []
            if news_response and 'body' in news_response:
                for item in news_response['body']:
                    news_items.append({
                        'title': item.get('title', 'Unknown'),
                        'link': item.get('link', 'Unknown'),
                        'image': item.get('image', 'Unknown'),
                        'player_id': item.get('playerID', 'Unknown')
                    })
            
            return {
                'news_items': news_items,
                'total_items': len(news_items),
                'player_id': player_id
            }
            
        except Exception as e:
            self.logger.error(f"Error getting player news for {player_id}: {e}")
            return {
                'news_items': [],
                'total_items': 0,
                'player_id': player_id,
                'error': str(e)
            }

    def _get_player_projections(self, player_id: str) -> Dict[str, Any]:
        """Get weekly projections for a specific player."""
        try:
            # For now, return a placeholder since Tank01 doesn't have direct projections
            # In a real implementation, you might get this from another API or calculate it
            return {
                'player_id': player_id,
                'projections': {
                    'week_1': 'Not available',
                    'season': 'Not available'
                },
                'note': 'Projections not available from Tank01 API'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting player projections for {player_id}: {e}")
            return {
                'player_id': player_id,
                'projections': {},
                'error': str(e)
            }

    def _create_enrichment_summary(self, enriched_players: List[Dict[str, Any]]) -> Dict[str, Any]:
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
            
            return {
                'total_players_processed': total_players,
                'matched_players': matched_players,
                'unmatched_players': unmatched_players,
                'match_rate': f"{(matched_players/total_players*100):.1f}%" if total_players > 0 else "0%",
                'high_confidence_matches': high_confidence_matches,
                'medium_confidence_matches': medium_confidence_matches,
                'transaction_types': transaction_types,
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


def main():
    """Main execution function."""
    enricher = Tank01TransactionTrendsEnricher()
    success = enricher.run()
    
    if success:
        print("✅ Tank01 transaction trends extraction completed successfully!")
        sys.exit(0)
    else:
        print("❌ Tank01 transaction trends extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
