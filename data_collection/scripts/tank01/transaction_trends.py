#!/usr/bin/env python3
"""
Tank01 NFL API - Transaction Trends Data Extraction

This script extracts transaction trends data from the Tank01 API by analyzing
news, player information, and team data to infer fantasy football transaction
patterns and trends.

Purpose: Extract transaction trends and market intelligence from Tank01 API
Output: Organized markdown file + raw JSON data with transaction trends
Focus: News analysis, player movement patterns, and market trends
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from tank01_client import SimpleTank01Client
from data_formatter import MarkdownFormatter
from file_utils import DataFileManager


class Tank01TransactionTrendsExtractor:
    """Extract transaction trends from Tank01 API using news and player data analysis."""

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
            'news_items_analyzed': 0,
            'players_analyzed': 0,
            'trends_identified': 0
        }

    def extract_transaction_trends(self) -> Dict[str, Any]:
        """Extract transaction trends from Tank01 API data."""
        try:
            self.logger.info("Starting Tank01 transaction trends extraction...")
            
            # Get current season context
            season_context = self._get_current_season_context()
            
            # Get fantasy news for trending analysis
            fantasy_news = self._get_fantasy_news()
            
            # Get player database for context
            player_database = self._get_player_database()
            
            # Get team information for context
            team_info = self._get_team_information()
            
            # Analyze trends from the data
            trends_analysis = self._analyze_transaction_trends(
                fantasy_news, player_database, team_info
            )
            
            # Compile results
            result = {
                'season_context': season_context,
                'fantasy_news': fantasy_news,
                'player_database_summary': self._summarize_player_database(player_database),
                'team_information_summary': self._summarize_team_info(team_info),
                'trends_analysis': trends_analysis,
                'api_usage': self.tank01.get_api_usage()
            }
            
            self.execution_stats['api_calls'] = self.tank01.get_api_usage()['calls_made_this_session']
            self.execution_stats['news_items_analyzed'] = len(fantasy_news.get('news_items', []))
            self.execution_stats['players_analyzed'] = len(player_database.get('players', []))
            self.execution_stats['trends_identified'] = len(trends_analysis.get('trends', []))
            
            self.logger.info(f"Successfully extracted transaction trends with {self.execution_stats['trends_identified']} trends identified")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting transaction trends: {e}")
            self.execution_stats['errors'] += 1
            raise

    def _get_current_season_context(self) -> Dict[str, Any]:
        """Get current NFL season context."""
        try:
            # Use today's date to determine current week
            today = datetime.now()
            
            # For now, we'll use a simple week calculation
            # In a real implementation, you'd get this from the NFL API
            current_week = 1  # Default to week 1
            season = "2025"
            
            return {
                'current_week': current_week,
                'season': season,
                'season_type': 'Regular Season',
                'extraction_date': today.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting season context: {e}")
            return {
                'current_week': 1,
                'season': '2025',
                'season_type': 'Regular Season',
                'extraction_date': datetime.now().isoformat()
            }

    def _get_fantasy_news(self) -> Dict[str, Any]:
        """Get fantasy football news for trend analysis."""
        try:
            # Get general fantasy news
            news_response = self.tank01.get_news(
                fantasy_news=True,
                max_items=50
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
                'extraction_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting fantasy news: {e}")
            return {
                'news_items': [],
                'total_items': 0,
                'extraction_time': datetime.now().isoformat(),
                'error': str(e)
            }

    def _get_player_database(self) -> Dict[str, Any]:
        """Get player database for context analysis."""
        try:
            # Get player list for context
            players_response = self.tank01.get_player_list()
            
            players = []
            if players_response and 'body' in players_response:
                for player in players_response['body'][:100]:  # Limit to first 100 for analysis
                    players.append({
                        'player_id': player.get('playerID', 'Unknown'),
                        'name': player.get('longName', 'Unknown'),
                        'team': player.get('team', 'Unknown'),
                        'position': player.get('pos', 'Unknown'),
                        'yahoo_id': player.get('yahooPlayerID', 'Unknown'),
                        'sleeper_id': player.get('sleeperBotID', 'Unknown')
                    })
            
            return {
                'players': players,
                'total_players': len(players),
                'extraction_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting player database: {e}")
            return {
                'players': [],
                'total_players': 0,
                'extraction_time': datetime.now().isoformat(),
                'error': str(e)
            }

    def _get_team_information(self) -> Dict[str, Any]:
        """Get team information for context analysis."""
        try:
            # Get team information
            teams_response = self.tank01.get_nfl_teams(
                sort_by='standings',
                rosters=False,
                schedules=False,
                top_performers=True,
                team_stats=True,
                team_stats_season='2024'
            )
            
            teams = []
            if teams_response and 'body' in teams_response:
                for team in teams_response['body']:
                    teams.append({
                        'team_id': team.get('teamID', 'Unknown'),
                        'team_abv': team.get('teamAbv', 'Unknown'),
                        'team_name': team.get('teamName', 'Unknown'),
                        'team_city': team.get('teamCity', 'Unknown'),
                        'wins': team.get('wins', '0'),
                        'losses': team.get('loss', '0'),
                        'ties': team.get('tie', '0'),
                        'division': team.get('division', 'Unknown'),
                        'conference': team.get('conference', 'Unknown')
                    })
            
            return {
                'teams': teams,
                'total_teams': len(teams),
                'extraction_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting team information: {e}")
            return {
                'teams': [],
                'total_teams': 0,
                'extraction_time': datetime.now().isoformat(),
                'error': str(e)
            }

    def _analyze_transaction_trends(self, news_data: Dict[str, Any], 
                                  player_data: Dict[str, Any], 
                                  team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction trends from the collected data."""
        try:
            trends = []
            
            # Analyze news for transaction indicators
            news_trends = self._analyze_news_trends(news_data)
            trends.extend(news_trends)
            
            # Analyze player data for movement patterns
            player_trends = self._analyze_player_trends(player_data)
            trends.extend(player_trends)
            
            # Analyze team data for context
            team_trends = self._analyze_team_trends(team_data)
            trends.extend(team_trends)
            
            return {
                'trends': trends,
                'total_trends': len(trends),
                'analysis_time': datetime.now().isoformat(),
                'trend_categories': {
                    'news_based': len([t for t in trends if t.get('category') == 'news']),
                    'player_based': len([t for t in trends if t.get('category') == 'player']),
                    'team_based': len([t for t in trends if t.get('category') == 'team'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing transaction trends: {e}")
            return {
                'trends': [],
                'total_trends': 0,
                'analysis_time': datetime.now().isoformat(),
                'error': str(e)
            }

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
        """Generate a comprehensive markdown report of transaction trends."""
        try:
            report = []
            
            # Header
            report.append("# Tank01 Transaction Trends Analysis")
            report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"**Week:** {data['season_context']['current_week']}")
            report.append(f"**Season:** {data['season_context']['season']}")
            report.append("")
            
            # API Usage
            api_usage = data.get('api_usage', {})
            report.append("## API Usage")
            report.append(f"- **Calls Made:** {api_usage.get('calls_made_this_session', 'Unknown')}")
            report.append(f"- **Daily Limit:** {api_usage.get('daily_limit', 'Unknown')}")
            report.append(f"- **Remaining:** {api_usage.get('remaining_calls', 'Unknown')}")
            report.append("")
            
            # Data Summary
            report.append("## Data Summary")
            report.append(f"- **News Items Analyzed:** {data['fantasy_news']['total_items']}")
            report.append(f"- **Players Analyzed:** {data['player_database_summary']['total_players']}")
            report.append(f"- **Teams Analyzed:** {data['team_information_summary']['total_teams']}")
            report.append(f"- **Trends Identified:** {data['trends_analysis']['total_trends']}")
            report.append("")
            
            # Transaction Trends
            trends = data['trends_analysis']['trends']
            if trends:
                report.append("## Transaction Trends Identified")
                report.append("")
                
                # Group trends by category
                news_trends = [t for t in trends if t.get('category') == 'news']
                player_trends = [t for t in trends if t.get('category') == 'player']
                team_trends = [t for t in trends if t.get('category') == 'team']
                
                if news_trends:
                    report.append("### News-Based Trends")
                    for trend in news_trends[:10]:  # Limit to top 10
                        report.append(f"- **{trend.get('type', 'Unknown').replace('_', ' ').title()}:** {trend.get('title', 'Unknown')}")
                        report.append(f"  - Player ID: {trend.get('player_id', 'Unknown')}")
                        report.append(f"  - Confidence: {trend.get('confidence', 'Unknown')}")
                        report.append("")
                
                if player_trends:
                    report.append("### Player-Based Trends")
                    for trend in player_trends[:5]:  # Limit to top 5
                        report.append(f"- **{trend.get('type', 'Unknown').replace('_', ' ').title()}:** Player {trend.get('player_id', 'Unknown')}")
                        report.append(f"  - Teams: {', '.join(trend.get('teams', []))}")
                        report.append(f"  - Confidence: {trend.get('confidence', 'Unknown')}")
                        report.append("")
                
                if team_trends:
                    report.append("### Team-Based Trends")
                    for trend in team_trends[:5]:  # Limit to top 5
                        report.append(f"- **{trend.get('type', 'Unknown').replace('_', ' ').title()}:** {trend.get('team', 'Unknown')}")
                        report.append(f"  - Record: {trend.get('record', 'Unknown')}")
                        report.append(f"  - Confidence: {trend.get('confidence', 'Unknown')}")
                        report.append("")
            else:
                report.append("## Transaction Trends")
                report.append("No significant transaction trends identified in the current data.")
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
        """Run the complete transaction trends extraction process."""
        try:
            self.logger.info("Starting Tank01 transaction trends extraction...")
            
            # Extract data
            data = self.extract_transaction_trends()
            
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
            
            self.logger.info(f"Tank01 transaction trends extraction completed successfully!")
            self.logger.info(f"Clean data saved to: {clean_file}")
            self.logger.info(f"Raw data saved to: {raw_file}")
            self.logger.info(f"Execution log saved to: {log_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Tank01 transaction trends extraction failed: {e}")
            self.execution_stats['errors'] += 1
            return False


def main():
    """Main execution function."""
    extractor = Tank01TransactionTrendsExtractor()
    success = extractor.run()
    
    if success:
        print("✅ Tank01 transaction trends extraction completed successfully!")
        sys.exit(0)
    else:
        print("❌ Tank01 transaction trends extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
