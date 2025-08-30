#!/usr/bin/env python3
"""
Main Fantasy Football Analyzer
Orchestrates all analysis scripts and provides unified interface
"""

import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import analysis scripts
from yahoo_connect import YahooFantasyAPI
from roster_analyzer import RosterAnalyzer
from free_agent_analyzer import FreeAgentAnalyzer
from matchup_analyzer import MatchupAnalyzer
from performance_tracker import PerformanceTracker

# Import utilities
from utils import (
    save_markdown_report, 
    get_current_week, 
    create_historical_file,
    load_historical_file,
    ensure_directories
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FantasyFootballAnalyzer:
    """Main orchestrator for all fantasy football analysis"""
    
    def __init__(self):
        self.api = YahooFantasyAPI()
        self.roster_analyzer = RosterAnalyzer()
        self.free_agent_analyzer = FreeAgentAnalyzer()
        self.matchup_analyzer = MatchupAnalyzer()
        self.performance_tracker = PerformanceTracker()
        
        # Ensure all directories exist
        ensure_directories()
        
        logger.info("Fantasy Football Analyzer initialized")
    
    def run_roster_analysis(self) -> Dict[str, Any]:
        """Run complete roster analysis"""
        try:
            logger.info("Starting roster analysis")
            results = self.roster_analyzer.run_full_analysis()
            
            if 'error' not in results:
                logger.info("Roster analysis completed successfully")
                return {
                    'status': 'success',
                    'analysis_type': 'roster',
                    'roster_count': results.get('roster_count', 0),
                    'health_summary': results.get('health_summary', {}),
                    'gaps_summary': results.get('gaps_summary', {}),
                    'message': f"Roster analysis completed: {results.get('roster_count', 0)} players analyzed"
                }
            else:
                logger.error(f"Roster analysis failed: {results.get('error')}")
                return {
                    'status': 'error',
                    'analysis_type': 'roster',
                    'message': f"Roster analysis failed: {results.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Roster analysis error: {e}")
            return {
                'status': 'error',
                'analysis_type': 'roster',
                'message': f"Roster analysis error: {str(e)}"
            }
    
    def run_free_agent_analysis(self) -> Dict[str, Any]:
        """Run complete free agent analysis"""
        try:
            logger.info("Starting free agent analysis")
            results = self.free_agent_analyzer.run_full_analysis()
            
            if 'error' not in results:
                logger.info("Free agent analysis completed successfully")
                return {
                    'status': 'success',
                    'analysis_type': 'free_agents',
                    'roster_count': results.get('roster_count', 0),
                    'free_agent_count': results.get('free_agent_count', 0),
                    'upgrade_opportunities': results.get('upgrade_opportunities', 0),
                    'depth_improvements': results.get('depth_improvements', 0),
                    'backup_additions': results.get('backup_additions', 0),
                    'message': f"Free agent analysis completed: {results.get('upgrade_opportunities', 0)} upgrade opportunities found"
                }
            else:
                logger.error(f"Free agent analysis failed: {results.get('error')}")
                return {
                    'status': 'error',
                    'analysis_type': 'free_agents',
                    'message': f"Free agent analysis failed: {results.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Free agent analysis error: {e}")
            return {
                'status': 'error',
                'analysis_type': 'free_agents',
                'message': f"Free agent analysis error: {str(e)}"
            }
    
    def run_matchup_analysis(self) -> Dict[str, Any]:
        """Run complete matchup analysis"""
        try:
            logger.info("Starting matchup analysis")
            results = self.matchup_analyzer.run_full_analysis()
            
            if 'error' not in results:
                logger.info("Matchup analysis completed successfully")
                return {
                    'status': 'success',
                    'analysis_type': 'matchup',
                    'roster_count': results.get('roster_count', 0),
                    'opponent_name': results.get('opponent_name', 'Unknown'),
                    'opponent_count': results.get('opponent_count', 0),
                    'message': f"Matchup analysis completed: {results.get('opponent_name', 'Unknown')} analyzed"
                }
            else:
                logger.error(f"Matchup analysis failed: {results.get('error')}")
                return {
                    'status': 'error',
                    'analysis_type': 'matchup',
                    'message': f"Matchup analysis failed: {results.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Matchup analysis error: {e}")
            return {
                'status': 'error',
                'analysis_type': 'matchup',
                'message': f"Matchup analysis error: {str(e)}"
            }
    
    def run_performance_analysis(self, week: Optional[int] = None) -> Dict[str, Any]:
        """Run performance analysis for a specific week"""
        try:
            if week is None:
                week = get_current_week() - 1  # Previous week
            
            logger.info(f"Starting performance analysis for week {week}")
            results = self.performance_tracker.run_full_analysis(week)
            
            if 'error' not in results:
                logger.info(f"Performance analysis completed successfully for week {week}")
                return {
                    'status': 'success',
                    'analysis_type': 'performance',
                    'week': results.get('week', week),
                    'message': f"Performance analysis completed for week {week}"
                }
            else:
                logger.error(f"Performance analysis failed: {results.get('error')}")
                return {
                    'status': 'error',
                    'analysis_type': 'performance',
                    'week': week,
                    'message': f"Performance analysis failed: {results.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {
                'status': 'error',
                'analysis_type': 'performance',
                'week': week,
                'message': f"Performance analysis error: {str(e)}"
            }
    
    def run_full_weekly_analysis(self) -> Dict[str, Any]:
        """Run complete weekly analysis (roster + free agents + matchup)"""
        try:
            logger.info("Starting full weekly analysis")
            
            results = {
                'status': 'success',
                'analysis_type': 'full_weekly',
                'timestamp': datetime.now().isoformat(),
                'analyses': {},
                'summary': {}
            }
            
            # Run roster analysis
            roster_results = self.run_roster_analysis()
            results['analyses']['roster'] = roster_results
            
            # Run free agent analysis
            free_agent_results = self.run_free_agent_analysis()
            results['analyses']['free_agents'] = free_agent_results
            
            # Run matchup analysis
            matchup_results = self.run_matchup_analysis()
            results['analyses']['matchup'] = matchup_results()
            
            # Generate summary
            results['summary'] = self._generate_weekly_summary(results['analyses'])
            
            # Save full analysis results
            self._save_weekly_analysis_results(results)
            
            logger.info("Full weekly analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Full weekly analysis error: {e}")
            return {
                'status': 'error',
                'analysis_type': 'full_weekly',
                'message': f"Full weekly analysis error: {str(e)}"
            }
    
    def _generate_weekly_summary(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all weekly analyses"""
        try:
            summary = {
                'total_analyses': len(analyses),
                'successful_analyses': 0,
                'failed_analyses': 0,
                'key_findings': [],
                'recommendations': []
            }
            
            # Count successful vs failed analyses
            for analysis_type, results in analyses.items():
                if results.get('status') == 'success':
                    summary['successful_analyses'] += 1
                else:
                    summary['failed_analyses'] += 1
            
            # Extract key findings from successful analyses
            if analyses.get('roster', {}).get('status') == 'success':
                roster_data = analyses['roster']
                if roster_data.get('health_summary'):
                    health = roster_data['health_summary']
                    summary['key_findings'].append(f"Roster Health: {health.get('healthy_players', 0)} healthy, {len(health.get('risk_players', []))} at risk")
                
                if roster_data.get('gaps_summary'):
                    gaps = roster_data['gaps_summary']
                    if gaps.get('critical_needs'):
                        summary['key_findings'].append(f"Critical Needs: {len(gaps['critical_needs'])} positions require immediate attention")
            
            if analyses.get('free_agents', {}).get('status') == 'success':
                fa_data = analyses['free_agents']
                summary['key_findings'].append(f"Free Agent Opportunities: {fa_data.get('upgrade_opportunities', 0)} upgrades, {fa_data.get('depth_improvements', 0)} depth improvements")
            
            if analyses.get('matchup', {}).get('status') == 'success':
                matchup_data = analyses['matchup']
                summary['key_findings'].append(f"Matchup Analysis: {matchup_data.get('opponent_name', 'Unknown')} analyzed")
            
            # Generate overall recommendations
            summary['recommendations'] = self._generate_overall_recommendations(analyses)
            
            return summary
            
        except Exception as e:
            logger.error(f"Weekly summary generation failed: {e}")
            return {}
    
    def _generate_overall_recommendations(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on all analyses"""
        recommendations = []
        
        # Check roster health
        if analyses.get('roster', {}).get('status') == 'success':
            roster_data = analyses['roster']
            if roster_data.get('health_summary'):
                health = roster_data['health_summary']
                if health.get('out_players', 0) > 0:
                    recommendations.append("🚨 Address injured/out players immediately")
                
                if health.get('questionable_players', 0) > 0:
                    recommendations.append("⚠️ Monitor questionable players closely")
        
        # Check free agent opportunities
        if analyses.get('free_agents', {}).get('status') == 'success':
            fa_data = analyses['free_agents']
            if fa_data.get('upgrade_opportunities', 0) > 0:
                recommendations.append("📈 Evaluate upgrade opportunities for roster improvement")
            
            if fa_data.get('depth_improvements', 0) > 0:
                recommendations.append("📊 Consider adding depth to thin positions")
        
        # Check matchup strategy
        if analyses.get('matchup', {}).get('status') == 'success':
            recommendations.append("🥊 Review matchup analysis for lineup optimization")
        
        # Overall assessment
        if len(recommendations) == 0:
            recommendations.append("✅ Roster appears well-balanced - maintain current strategy")
        else:
            recommendations.append("🎯 Prioritize recommendations based on urgency and impact")
        
        return recommendations
    
    def _save_weekly_analysis_results(self, results: Dict[str, Any]) -> None:
        """Save weekly analysis results to historical data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weekly_analysis_{timestamp}.json"
            
            create_historical_file(filename, results)
            logger.info(f"Weekly analysis results saved: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save weekly analysis results: {e}")
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get current status of all analysis components"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'current_week': get_current_week(),
                'components': {
                    'yahoo_api': 'unknown',
                    'roster_analyzer': 'unknown',
                    'free_agent_analyzer': 'unknown',
                    'matchup_analyzer': 'unknown',
                    'performance_tracker': 'unknown'
                },
                'last_analysis': None,
                'system_health': 'unknown'
            }
            
            # Check Yahoo API connection
            try:
                if self.api.authenticate():
                    status['components']['yahoo_api'] = 'connected'
                else:
                    status['components']['yahoo_api'] = 'failed'
            except Exception as e:
                status['components']['yahoo_api'] = f'error: {str(e)}'
            
            # Check if analysis files exist
            try:
                from pathlib import Path
                analysis_dir = Path('analysis')
                if analysis_dir.exists():
                    week_dirs = [d for d in analysis_dir.iterdir() if d.is_dir() and d.name.startswith('week_')]
                    if week_dirs:
                        latest_week = max(week_dirs, key=lambda x: x.name)
                        status['last_analysis'] = f"Week {latest_week.name}"
            except Exception as e:
                logger.error(f"Failed to check analysis files: {e}")
            
            # Determine overall system health
            connected_components = sum(1 for status in status['components'].values() if status == 'connected')
            total_components = len(status['components'])
            
            if connected_components == total_components:
                status['system_health'] = 'healthy'
            elif connected_components > total_components / 2:
                status['system_health'] = 'degraded'
            else:
                status['system_health'] = 'unhealthy'
            
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                'status': 'error',
                'message': f"Status check failed: {str(e)}"
            }
    
    def run_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Run a specific analysis command"""
        try:
            command = command.lower().strip()
            
            if command in ['roster', 'analyze_roster', 'roster_analysis']:
                return self.run_roster_analysis()
            
            elif command in ['free_agents', 'free_agent_analysis', 'check_free_agents']:
                return self.run_free_agent_analysis()
            
            elif command in ['matchup', 'matchup_analysis', 'analyze_matchup']:
                return self.run_matchup_analysis()
            
            elif command in ['performance', 'performance_analysis', 'track_performance']:
                week = kwargs.get('week')
                return self.run_performance_analysis(week)
            
            elif command in ['full', 'full_analysis', 'weekly_analysis']:
                return self.run_full_weekly_analysis()
            
            elif command in ['status', 'system_status', 'health_check']:
                return self.get_analysis_status()
            
            else:
                return {
                    'status': 'error',
                    'message': f"Unknown command: {command}. Available commands: roster, free_agents, matchup, performance, full, status"
                }
                
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                'status': 'error',
                'message': f"Command execution failed: {str(e)}"
            }

def main():
    """Main entry point for command line usage"""
    parser = argparse.ArgumentParser(description='Fantasy Football Analysis Tool')
    parser.add_argument('command', help='Analysis command to run')
    parser.add_argument('--week', type=int, help='Week number for analysis')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        analyzer = FantasyFootballAnalyzer()
        results = analyzer.run_command(args.command, week=args.week)
        
        # Print results
        if results.get('status') == 'success':
            print(f"✅ {results.get('message', 'Analysis completed successfully')}")
            
            # Print additional details if available
            if 'summary' in results:
                summary = results['summary']
                print(f"\n📊 Summary:")
                print(f"   Successful analyses: {summary.get('successful_analyses', 0)}")
                print(f"   Failed analyses: {summary.get('failed_analyses', 0)}")
                
                if summary.get('key_findings'):
                    print(f"\n🔍 Key Findings:")
                    for finding in summary['key_findings']:
                        print(f"   - {finding}")
                
                if summary.get('recommendations'):
                    print(f"\n💡 Recommendations:")
                    for rec in summary['recommendations']:
                        print(f"   - {rec}")
        else:
            print(f"❌ {results.get('message', 'Analysis failed')}")
        
        # Exit with appropriate code
        sys.exit(0 if results.get('status') == 'success' else 1)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Main execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
