#!/usr/bin/env python3
"""
External API Manager

This module coordinates all external APIs (Yahoo Fantasy Sports, Sleeper NFL, Tank01 NFL)
to provide a unified interface for fantasy football data retrieval and analysis.

APIs Managed:
- Yahoo Fantasy Sports API (OAuth 2.0) - Official league data
- Sleeper NFL API (Free) - Trending players and injury data
- Tank01 NFL API (RapidAPI) - Fantasy projections, news, and stats

Author: Fantasy Football Optimizer
Date: August 2025
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import our API clients
from scripts.core.data_retriever import YahooDataRetriever
from scripts.external.sleeper_client import SleeperClient
from scripts.external.tank01_client import Tank01Client
from scripts.core.sleeper_integration import SleeperIntegration
from scripts.core.combined_analysis import CombinedAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ExternalAPIManager:
    """
    Unified manager for all external fantasy football APIs.
    
    Coordinates data retrieval from:
    - Yahoo Fantasy Sports API (official league data)
    - Sleeper NFL API (trending players, injury data)
    - Tank01 NFL API (fantasy projections, news, stats)
    """
    
    def __init__(self):
        """Initialize the External API Manager with all API clients."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing External API Manager")
        
        # Initialize API clients
        try:
            self.yahoo_client = YahooDataRetriever()
            self.logger.info("✅ Yahoo Fantasy Sports API client initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Yahoo client: {e}")
            self.yahoo_client = None
        
        try:
            self.sleeper_client = SleeperClient()
            self.sleeper_integration = SleeperIntegration()
            self.logger.info("✅ Sleeper NFL API client initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Sleeper client: {e}")
            self.sleeper_client = None
            self.sleeper_integration = None
        
        try:
            self.tank01_client = Tank01Client()
            self.logger.info("✅ Tank01 NFL API client initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Tank01 client: {e}")
            self.tank01_client = None
        
        try:
            self.combined_analyzer = CombinedAnalyzer()
            self.logger.info("✅ Combined analyzer initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize combined analyzer: {e}")
            self.combined_analyzer = None
        
        # Track API usage and status
        self.api_status = {
            'yahoo': self.yahoo_client is not None,
            'sleeper': self.sleeper_client is not None,
            'tank01': self.tank01_client is not None
        }
        
        self.logger.info(f"🎯 API Status: Yahoo={self.api_status['yahoo']}, "
                        f"Sleeper={self.api_status['sleeper']}, Tank01={self.api_status['tank01']}")
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Get current status of all API integrations.
        
        Returns:
            Dict containing API status, usage, and capabilities
        """
        status = {
            'apis': self.api_status.copy(),
            'timestamp': datetime.now().isoformat(),
            'capabilities': {
                'yahoo': {
                    'available': self.api_status['yahoo'],
                    'features': ['league_data', 'rosters', 'free_agents', 'matchups'] if self.api_status['yahoo'] else []
                },
                'sleeper': {
                    'available': self.api_status['sleeper'],
                    'features': ['trending_players', 'injury_data', 'player_metadata'] if self.api_status['sleeper'] else []
                },
                'tank01': {
                    'available': self.api_status['tank01'],
                    'features': ['fantasy_projections', 'news', 'depth_charts', 'team_stats'] if self.api_status['tank01'] else []
                }
            }
        }
        
        # Add usage information if available
        if self.tank01_client:
            try:
                tank01_usage = self.tank01_client.get_usage_info()
                status['usage'] = {
                    'tank01': tank01_usage
                }
            except Exception as e:
                self.logger.error(f"Failed to get Tank01 usage info: {e}")
        
        return status
    
    def get_comprehensive_league_data(self) -> Dict[str, Any]:
        """
        Get comprehensive league data from Yahoo Fantasy Sports API.
        
        Returns:
            Dict containing all league data (teams, rosters, matchups, free agents)
        """
        if not self.api_status['yahoo']:
            self.logger.error("Yahoo API not available")
            return {}
        
        try:
            self.logger.info("🏈 Retrieving comprehensive league data from Yahoo")
            
            # Get all core Yahoo data using correct method names
            league_key = self.yahoo_client.get_league_key()
            teams = self.yahoo_client.get_all_league_teams()
            opponent_rosters = self.yahoo_client.get_opponent_rosters()
            free_agents = self.yahoo_client.get_free_agents()
            top_available = self.yahoo_client.get_top_available_players()
            research_data = self.yahoo_client.get_research_data()
            
            return {
                'league_key': league_key,
                'teams': teams,
                'opponent_rosters': opponent_rosters,
                'free_agents': free_agents,
                'top_available': top_available,
                'research_data': research_data,
                'timestamp': datetime.now().isoformat(),
                'source': 'yahoo_fantasy_api'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive league data: {e}")
            return {}
    
    def get_trending_insights(self, lookback_hours: int = 24, limit: int = 50) -> Dict[str, Any]:
        """
        Get trending player insights from Sleeper NFL API.
        
        Args:
            lookback_hours: Hours to look back for trending data
            limit: Maximum number of trending players to retrieve
            
        Returns:
            Dict containing trending player data and insights
        """
        if not self.api_status['sleeper']:
            self.logger.error("Sleeper API not available")
            return {}
        
        try:
            self.logger.info(f"📈 Getting trending insights (last {lookback_hours}h, limit {limit})")
            
            # Get trending analysis
            trending_data = self.sleeper_integration.get_trending_analysis(
                lookback_hours=lookback_hours
            )
            
            return {
                'trending_data': trending_data,
                'lookback_hours': lookback_hours,
                'limit': limit,
                'timestamp': datetime.now().isoformat(),
                'source': 'sleeper_nfl_api'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get trending insights: {e}")
            return {}
    
    def get_fantasy_projections(self, player_ids: List[str] = None, week: int = None) -> Dict[str, Any]:
        """
        Get fantasy projections from Tank01 NFL API.
        
        Args:
            player_ids: Optional list of Tank01 player IDs
            week: Optional week number for weekly projections
            
        Returns:
            Dict containing fantasy projection data
        """
        if not self.api_status['tank01']:
            self.logger.error("Tank01 API not available")
            return {}
        
        try:
            projections = {}
            
            if week:
                self.logger.info(f"🎯 Getting weekly projections for week {week}")
                weekly_data = self.tank01_client.get_weekly_projections(week=week)
                projections['weekly'] = weekly_data
            
            if player_ids:
                self.logger.info(f"🎯 Getting individual projections for {len(player_ids)} players")
                individual_projections = {}
                for player_id in player_ids:
                    try:
                        proj = self.tank01_client.get_fantasy_projections(player_id)
                        if proj:
                            individual_projections[player_id] = proj
                    except Exception as e:
                        self.logger.error(f"Failed to get projections for player {player_id}: {e}")
                
                projections['individual'] = individual_projections
            
            return {
                'projections': projections,
                'timestamp': datetime.now().isoformat(),
                'source': 'tank01_nfl_api'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get fantasy projections: {e}")
            return {}
    
    def get_nfl_news(self, fantasy_focus: bool = True, max_items: int = 20) -> Dict[str, Any]:
        """
        Get NFL news from Tank01 API.
        
        Args:
            fantasy_focus: Whether to focus on fantasy-relevant news
            max_items: Maximum number of news items
            
        Returns:
            Dict containing NFL news data
        """
        if not self.api_status['tank01']:
            self.logger.error("Tank01 API not available")
            return {}
        
        try:
            self.logger.info(f"📰 Getting NFL news (fantasy_focus={fantasy_focus}, max_items={max_items})")
            
            news_data = self.tank01_client.get_news(
                fantasy_news=fantasy_focus,
                max_items=max_items
            )
            
            return {
                'news': news_data,
                'fantasy_focus': fantasy_focus,
                'max_items': max_items,
                'timestamp': datetime.now().isoformat(),
                'source': 'tank01_nfl_api'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get NFL news: {e}")
            return {}
    
    def get_combined_free_agent_analysis(self, top_n: int = 50) -> Dict[str, Any]:
        """
        Get combined free agent analysis using Yahoo + Sleeper data.
        
        Args:
            top_n: Number of top free agents to analyze
            
        Returns:
            Dict containing combined analysis data
        """
        if not (self.api_status['yahoo'] and self.api_status['sleeper']):
            self.logger.error("Both Yahoo and Sleeper APIs required for combined analysis")
            return {}
        
        try:
            self.logger.info(f"🔄 Running combined free agent analysis (top {top_n})")
            
            # Get enhanced free agents
            enhanced_free_agents = self.combined_analyzer.get_enhanced_free_agents(limit=top_n)
            
            return {
                'enhanced_free_agents': enhanced_free_agents,
                'top_n': top_n,
                'timestamp': datetime.now().isoformat(),
                'sources': ['yahoo_fantasy_api', 'sleeper_nfl_api']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get combined free agent analysis: {e}")
            return {}
    
    def generate_comprehensive_report(self, output_dir: str = "analysis/comprehensive") -> str:
        """
        Generate a comprehensive report combining data from all APIs.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report file
        """
        try:
            self.logger.info("📊 Generating comprehensive multi-API report")
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_path / f"{timestamp}_comprehensive_multi_api_report.md"
            
            # Collect data from all available APIs
            report_data = {
                'api_status': self.get_api_status(),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.api_status['yahoo']:
                report_data['yahoo_data'] = self.get_comprehensive_league_data()
            
            if self.api_status['sleeper']:
                report_data['trending_data'] = self.get_trending_insights()
            
            if self.api_status['tank01']:
                report_data['news_data'] = self.get_nfl_news()
            
            if self.api_status['yahoo'] and self.api_status['sleeper']:
                report_data['combined_analysis'] = self.get_combined_free_agent_analysis()
            
            # Generate markdown report
            report_content = self._generate_markdown_report(report_data)
            
            # Write report to file
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"✅ Comprehensive report saved to {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive report: {e}")
            return ""
    
    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """
        Generate markdown report content from collected data.
        
        Args:
            data: Dictionary containing all collected data
            
        Returns:
            Formatted markdown report content
        """
        report = []
        
        # Header
        report.append("# 🏈 Comprehensive Multi-API Fantasy Football Report")
        report.append("")
        report.append(f"**Generated**: {data['timestamp']}")
        report.append("")
        
        # API Status
        report.append("## 📊 API Status")
        report.append("")
        api_status = data['api_status']
        for api_name, available in api_status['apis'].items():
            status_emoji = "✅" if available else "❌"
            report.append(f"- **{api_name.title()} API**: {status_emoji} {'Available' if available else 'Unavailable'}")
        
        report.append("")
        
        # Capabilities
        report.append("## 🎯 Available Capabilities")
        report.append("")
        for api_name, info in api_status['capabilities'].items():
            if info['available']:
                report.append(f"### {api_name.title()} API")
                for feature in info['features']:
                    report.append(f"- {feature.replace('_', ' ').title()}")
                report.append("")
        
        # Usage Information
        if 'usage' in api_status:
            report.append("## 📈 API Usage")
            report.append("")
            for api_name, usage_info in api_status['usage'].items():
                if api_name == 'tank01':
                    report.append(f"### Tank01 API")
                    report.append(f"- Calls made this session: {usage_info.get('calls_made_this_session', 0)}")
                    report.append(f"- Monthly limit: {usage_info.get('monthly_limit', 0)}")
                    report.append(f"- Remaining calls: {usage_info.get('remaining_calls', 0)}")
                    report.append(f"- Usage percentage: {usage_info.get('percentage_used', 0):.1f}%")
                    report.append("")
        
        # Yahoo Data Summary
        if 'yahoo_data' in data and data['yahoo_data']:
            yahoo_data = data['yahoo_data']
            report.append("## 🏈 Yahoo Fantasy League Summary")
            report.append("")
            
            if 'league_key' in yahoo_data:
                league_key = yahoo_data['league_key']
                report.append(f"- **League Key**: {league_key}")
                report.append("")
            
            if 'teams' in yahoo_data and isinstance(yahoo_data['teams'], list):
                teams = yahoo_data['teams']
                report.append(f"- **Teams in League**: {len(teams)}")
                report.append("")
            
            if 'free_agents' in yahoo_data:
                free_agents = yahoo_data['free_agents']
                if isinstance(free_agents, list):
                    report.append(f"- **Available Free Agents**: {len(free_agents)}")
                    report.append("")
            
            if 'top_available' in yahoo_data:
                top_available = yahoo_data['top_available']
                if isinstance(top_available, list):
                    report.append(f"- **Top Available Players**: {len(top_available)}")
                    report.append("")
            
            if 'opponent_rosters' in yahoo_data:
                opponent_rosters = yahoo_data['opponent_rosters']
                if isinstance(opponent_rosters, dict):
                    report.append(f"- **Opponent Teams with Rosters**: {len(opponent_rosters)}")
                    report.append("")
        
        # Trending Insights Summary
        if 'trending_data' in data and data['trending_data']:
            trending = data['trending_data']['trending_data']
            report.append("## 📈 Trending Player Insights")
            report.append("")
            
            if 'hot_adds' in trending:
                hot_adds = trending['hot_adds']
                report.append(f"- **Hot Adds**: {len(hot_adds)} players trending up")
            
            if 'hot_drops' in trending:
                hot_drops = trending['hot_drops']
                report.append(f"- **Hot Drops**: {len(hot_drops)} players trending down")
            
            report.append("")
        
        # News Summary
        if 'news_data' in data and data['news_data']:
            news = data['news_data']['news']
            if 'body' in news and isinstance(news['body'], list):
                report.append("## 📰 Latest NFL News")
                report.append("")
                report.append(f"- **News Items Retrieved**: {len(news['body'])}")
                
                # Show first few headlines
                for i, item in enumerate(news['body'][:3]):
                    if isinstance(item, dict) and 'title' in item:
                        report.append(f"- {item['title'][:100]}...")
                
                report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append("*Report generated by External API Manager*")
        report.append("*Integrating Yahoo Fantasy Sports + Sleeper NFL + Tank01 NFL APIs*")
        
        return "\n".join(report)
    
    def test_all_apis(self) -> Dict[str, Any]:
        """
        Test all API connections and return status.
        
        Returns:
            Dict containing test results for each API
        """
        self.logger.info("🧪 Testing all API connections")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Test Yahoo API
        if self.api_status['yahoo']:
            try:
                league_key = self.yahoo_client.get_league_key()
                results['tests']['yahoo'] = {
                    'status': 'success' if league_key else 'failed',
                    'message': 'League key retrieved' if league_key else 'No league data',
                    'data_available': bool(league_key)
                }
            except Exception as e:
                results['tests']['yahoo'] = {
                    'status': 'error',
                    'message': str(e),
                    'data_available': False
                }
        else:
            results['tests']['yahoo'] = {
                'status': 'unavailable',
                'message': 'Client not initialized',
                'data_available': False
            }
        
        # Test Sleeper API
        if self.api_status['sleeper']:
            try:
                trending = self.sleeper_client.get_trending_players(lookback_hours=24, limit=5)
                results['tests']['sleeper'] = {
                    'status': 'success' if trending else 'failed',
                    'message': 'Trending data retrieved' if trending else 'No trending data',
                    'data_available': bool(trending)
                }
            except Exception as e:
                results['tests']['sleeper'] = {
                    'status': 'error',
                    'message': str(e),
                    'data_available': False
                }
        else:
            results['tests']['sleeper'] = {
                'status': 'unavailable',
                'message': 'Client not initialized',
                'data_available': False
            }
        
        # Test Tank01 API
        if self.api_status['tank01']:
            try:
                news = self.tank01_client.get_news(fantasy_news=True, max_items=1)
                results['tests']['tank01'] = {
                    'status': 'success' if news else 'failed',
                    'message': 'News data retrieved' if news else 'No news data',
                    'data_available': bool(news)
                }
            except Exception as e:
                results['tests']['tank01'] = {
                    'status': 'error',
                    'message': str(e),
                    'data_available': False
                }
        else:
            results['tests']['tank01'] = {
                'status': 'unavailable',
                'message': 'Client not initialized',
                'data_available': False
            }
        
        # Summary
        successful_tests = sum(1 for test in results['tests'].values() if test['status'] == 'success')
        total_tests = len(results['tests'])
        results['summary'] = {
            'successful': successful_tests,
            'total': total_tests,
            'success_rate': (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        self.logger.info(f"🧪 API Tests Complete: {successful_tests}/{total_tests} successful")
        
        return results


def main():
    """Test the External API Manager."""
    print("🏈 External API Manager Test Suite")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = ExternalAPIManager()
        
        # Test all APIs
        print("\n🧪 Testing API Connections...")
        test_results = manager.test_all_apis()
        
        print(f"\n📊 Test Results:")
        for api_name, result in test_results['tests'].items():
            status_emoji = {
                'success': '✅',
                'failed': '⚠️',
                'error': '❌',
                'unavailable': '🚫'
            }.get(result['status'], '❓')
            
            print(f"   {status_emoji} {api_name.title()}: {result['message']}")
        
        print(f"\n📈 Success Rate: {test_results['summary']['success_rate']:.1f}% "
              f"({test_results['summary']['successful']}/{test_results['summary']['total']})")
        
        # Generate comprehensive report if APIs are working
        if test_results['summary']['successful'] > 0:
            print("\n📊 Generating comprehensive report...")
            report_path = manager.generate_comprehensive_report()
            if report_path:
                print(f"✅ Report saved to: {report_path}")
            else:
                print("❌ Failed to generate report")
        
        # Show API status
        print("\n🎯 API Status:")
        status = manager.get_api_status()
        for api_name, available in status['apis'].items():
            status_emoji = "✅" if available else "❌"
            print(f"   {status_emoji} {api_name.title()} API")
        
    except Exception as e:
        print(f"❌ Error testing External API Manager: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ External API Manager test completed!")


if __name__ == "__main__":
    main()
