#!/usr/bin/env python3
"""
Roster Analysis Script
Analyzes current roster health, performance, and identifies issues
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

# Import local utilities and Yahoo API
from utils import (
    save_markdown_report, 
    get_current_week, 
    create_historical_file,
    load_historical_file
)
from yahoo_connect import YahooFantasyAPI

# Configure logging
logger = logging.getLogger(__name__)

class RosterAnalyzer:
    """Analyzes fantasy football roster health and performance"""
    
    def __init__(self):
        self.api = YahooFantasyAPI()
        self.current_week = get_current_week()
        
        # Position priorities for analysis
        self.position_priorities = {
            'QB': 1,
            'RB': 2,
            'WR': 3,
            'TE': 4,
            'K': 5,
            'DEF': 6
        }
        
        # Risk indicators
        self.risk_indicators = {
            'Q': 'Questionable',
            'D': 'Doubtful',
            'O': 'Out',
            'IR': 'Injured Reserve',
            'PUP': 'Physically Unable to Perform',
            'SUSP': 'Suspended'
        }
    
    def analyze_roster_health(self, roster_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall roster health and identify issues"""
        try:
            analysis = {
                'total_players': len(roster_data),
                'healthy_players': 0,
                'questionable_players': 0,
                'out_players': 0,
                'bye_week_players': 0,
                'position_distribution': {},
                'risk_players': [],
                'recommendations': []
            }
            
            # Analyze each player
            for player in roster_data:
                position = player.get('position', 'Unknown')
                status = player.get('status', '')
                
                # Count position distribution
                if position not in analysis['position_distribution']:
                    analysis['position_distribution'][position] = 0
                analysis['position_distribution'][position] += 1
                
                # Check player status
                if status in ['Q', 'D', 'O', 'IR', 'PUP', 'SUSP']:
                    analysis['risk_players'].append({
                        'name': player.get('name', 'Unknown'),
                        'position': position,
                        'status': status,
                        'risk_level': self._assess_risk_level(status)
                    })
                    
                    if status == 'Q':
                        analysis['questionable_players'] += 1
                    elif status in ['O', 'IR', 'PUP', 'SUSP']:
                        analysis['out_players'] += 1
                else:
                    analysis['healthy_players'] += 1
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_health_recommendations(analysis)
            
            logger.info(f"Roster health analysis completed: {analysis['healthy_players']} healthy, {len(analysis['risk_players'])} at risk")
            return analysis
            
        except Exception as e:
            logger.error(f"Roster health analysis failed: {e}")
            return {}
    
    def _assess_risk_level(self, status: str) -> str:
        """Assess risk level based on player status"""
        if status in ['O', 'IR', 'PUP', 'SUSP']:
            return 'HIGH'
        elif status == 'D':
            return 'MEDIUM'
        elif status == 'Q':
            return 'LOW'
        else:
            return 'NONE'
    
    def _generate_health_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on roster health analysis"""
        recommendations = []
        
        # Check for critical issues
        if analysis['out_players'] > 0:
            recommendations.append(f"🚨 {analysis['out_players']} player(s) are OUT - consider replacements")
        
        if analysis['questionable_players'] > 0:
            recommendations.append(f"⚠️ {analysis['questionable_players']} player(s) are QUESTIONABLE - monitor closely")
        
        # Check position depth
        for position, count in analysis['position_distribution'].items():
            if position in ['QB', 'TE', 'K', 'DEF'] and count < 2:
                recommendations.append(f"📊 {position} depth is thin ({count} player) - consider adding backup")
            elif position in ['RB', 'WR'] and count < 4:
                recommendations.append(f"📊 {position} depth is limited ({count} players) - monitor for opportunities")
        
        # Overall health assessment
        health_percentage = (analysis['healthy_players'] / analysis['total_players']) * 100
        if health_percentage < 70:
            recommendations.append(f"🏥 Overall roster health is {health_percentage:.1f}% - significant issues detected")
        elif health_percentage < 85:
            recommendations.append(f"⚠️ Overall roster health is {health_percentage:.1f}% - minor issues present")
        else:
            recommendations.append(f"✅ Overall roster health is {health_percentage:.1f}% - looking good!")
        
        return recommendations
    
    def assess_player_performance(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess individual player performance and trends"""
        try:
            assessment = {
                'name': player_data.get('name', 'Unknown'),
                'position': player_data.get('position', 'Unknown'),
                'team': player_data.get('team', 'Unknown'),
                'status': player_data.get('status', 'Unknown'),
                'performance_score': 0,
                'trend': 'Unknown',
                'strengths': [],
                'concerns': [],
                'recommendation': 'Hold'
            }
            
            # Analyze player stats if available
            stats = {k: v for k, v in player_data.items() if k.startswith('stat_')}
            
            if stats:
                # Calculate basic performance metrics
                total_stats = sum(float(v) for v in stats.values() if str(v).replace('.', '').isdigit())
                assessment['performance_score'] = total_stats
                
                # Determine trend (this would be enhanced with historical data)
                if total_stats > 20:
                    assessment['trend'] = '📈 Strong'
                    assessment['strengths'].append('High statistical output')
                elif total_stats > 10:
                    assessment['trend'] = '➡️ Stable'
                    assessment['strengths'].append('Consistent performance')
                else:
                    assessment['trend'] = '📉 Declining'
                    assessment['concerns'].append('Low statistical output')
            
            # Assess based on position and status
            if assessment['status'] in ['Q', 'D', 'O']:
                assessment['concerns'].append(f"Health status: {assessment['status']}")
                assessment['recommendation'] = 'Monitor'
            
            if assessment['status'] in ['O', 'IR', 'PUP', 'SUSP']:
                assessment['concerns'].append('Player is unavailable')
                assessment['recommendation'] = 'Replace'
            
            # Position-specific analysis
            if assessment['position'] == 'QB' and assessment['performance_score'] < 15:
                assessment['concerns'].append('QB scoring below expectations')
            
            if assessment['position'] in ['RB', 'WR'] and assessment['performance_score'] < 8:
                assessment['concerns'].append(f'{assessment["position"]} production below par')
            
            return assessment
            
        except Exception as e:
            logger.error(f"Player performance assessment failed for {player_data.get('name', 'Unknown')}: {e}")
            return {}
    
    def identify_roster_gaps(self, roster_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify positions that need improvement or additional depth"""
        try:
            gaps = {
                'critical_needs': [],
                'depth_needs': [],
                'backup_needs': [],
                'recommendations': []
            }
            
            # Count players by position
            position_counts = {}
            for player in roster_data:
                position = player.get('position', 'Unknown')
                if position not in position_counts:
                    position_counts[position] = 0
                position_counts[position] += 1
            
            # Analyze each position
            for position, count in position_counts.items():
                if position == 'QB':
                    if count < 2:
                        gaps['backup_needs'].append(f"{position}: Need backup QB")
                    elif count < 1:
                        gaps['critical_needs'].append(f"{position}: CRITICAL - No QB on roster")
                
                elif position in ['RB', 'WR']:
                    if count < 3:
                        gaps['critical_needs'].append(f"{position}: Need more {position} depth")
                    elif count < 4:
                        gaps['depth_needs'].append(f"{position}: Could use additional {position}")
                
                elif position == 'TE':
                    if count < 2:
                        gaps['backup_needs'].append(f"{position}: Need backup TE")
                    elif count < 1:
                        gaps['critical_needs'].append(f"{position}: CRITICAL - No TE on roster")
                
                elif position in ['K', 'DEF']:
                    if count < 2:
                        gaps['backup_needs'].append(f"{position}: Need backup {position}")
                    elif count < 1:
                        gaps['critical_needs'].append(f"{position}: CRITICAL - No {position} on roster")
            
            # Generate recommendations
            if gaps['critical_needs']:
                gaps['recommendations'].append("🚨 CRITICAL: Address these needs immediately")
                gaps['recommendations'].extend(gaps['critical_needs'])
            
            if gaps['depth_needs']:
                gaps['recommendations'].append("⚠️ DEPTH: Consider adding these positions")
                gaps['recommendations'].extend(gaps['depth_needs'])
            
            if gaps['backup_needs']:
                gaps['recommendations'].append("📊 BACKUP: Add depth for these positions")
                gaps['recommendations'].extend(gaps['backup_needs'])
            
            logger.info(f"Roster gap analysis completed: {len(gaps['critical_needs'])} critical, {len(gaps['depth_needs'])} depth needs")
            return gaps
            
        except Exception as e:
            logger.error(f"Roster gap identification failed: {e}")
            return {}
    
    def generate_roster_report(self, roster_data: List[Dict[str, Any]]) -> str:
        """Generate comprehensive roster analysis report"""
        try:
            # Perform all analyses
            health_analysis = self.analyze_roster_health(roster_data)
            player_assessments = [self.assess_player_performance(player) for player in roster_data]
            gap_analysis = self.identify_roster_gaps(roster_data)
            
            # Generate markdown report
            report = self._format_roster_report(
                health_analysis, 
                player_assessments, 
                gap_analysis,
                roster_data
            )
            
            # Save report
            filename = f"1-pregame_roster_analysis.md"
            saved_file = save_markdown_report(report, filename)
            
            logger.info(f"Roster report generated and saved: {saved_file}")
            return report
            
        except Exception as e:
            logger.error(f"Roster report generation failed: {e}")
            return f"Error generating roster report: {e}"
    
    def _format_roster_report(self, health: Dict, assessments: List[Dict], gaps: Dict, roster: List[Dict]) -> str:
        """Format roster analysis into markdown report"""
        report = f"""# 🏈 Roster Analysis Report - Week {self.current_week}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Players:** {health.get('total_players', 0)}

---

## 📊 Roster Health Overview

### 🟢 Healthy Players: {health.get('healthy_players', 0)}
### 🟡 Questionable: {health.get('questionable_players', 0)}
### 🔴 Out/Injured: {health.get('out_players', 0)}

### 📈 Position Distribution
"""
        
        # Position distribution table
        for position, count in health.get('position_distribution', {}).items():
            report += f"- **{position}:** {count} player(s)\n"
        
        report += "\n### 🚨 Risk Assessment\n"
        
        # Risk players
        for player in health.get('risk_players', []):
            risk_emoji = "🔴" if player['risk_level'] == 'HIGH' else "🟡" if player['risk_level'] == 'MEDIUM' else "🟠"
            report += f"- {risk_emoji} **{player['name']}** ({player['position']}) - {player['status']} - {player['risk_level']} Risk\n"
        
        report += "\n### 💡 Health Recommendations\n"
        for rec in health.get('recommendations', []):
            report += f"- {rec}\n"
        
        report += "\n---\n## 🔍 Individual Player Analysis\n"
        
        # Player assessments table
        report += """
| Player | Position | Team | Status | Trend | Recommendation |
|--------|----------|------|--------|-------|----------------|
"""
        
        for assessment in assessments:
            if assessment:
                name = assessment.get('name', 'Unknown')
                position = assessment.get('position', 'Unknown')
                team = assessment.get('team', 'Unknown')
                status = assessment.get('status', 'Unknown')
                trend = assessment.get('trend', 'Unknown')
                rec = assessment.get('recommendation', 'Unknown')
                
                report += f"| {name} | {position} | {team} | {status} | {trend} | {rec} |\n"
        
        report += "\n---\n## 🕳️ Roster Gaps & Needs\n"
        
        # Gap analysis
        if gaps.get('critical_needs'):
            report += "\n### 🚨 Critical Needs\n"
            for need in gaps['critical_needs']:
                report += f"- {need}\n"
        
        if gaps.get('depth_needs'):
            report += "\n### ⚠️ Depth Needs\n"
            for need in gaps['depth_needs']:
                report += f"- {need}\n"
        
        if gaps.get('backup_needs'):
            report += "\n### 📊 Backup Needs\n"
            for need in gaps['backup_needs']:
                report += f"- {need}\n"
        
        report += "\n### 💡 Gap Recommendations\n"
        for rec in gaps.get('recommendations', []):
            report += f"- {rec}\n"
        
        report += "\n---\n## 📋 Current Roster\n"
        
        # Current roster table
        report += """
| Player | Position | Team | Status | Roster Slot |
|--------|----------|------|--------|-------------|
"""
        
        for player in roster:
            name = player.get('name', 'Unknown')
            position = player.get('position', 'Unknown')
            team = player.get('team', 'Unknown')
            status = player.get('status', 'Unknown')
            slot = player.get('roster_slot', 'Unknown')
            
            report += f"| {name} | {position} | {team} | {status} | {slot} |\n"
        
        report += f"""

---

*Report generated by Fantasy Football AI General Manager*  
*Week {self.current_week} Analysis*
"""
        
        return report
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete roster analysis"""
        try:
            logger.info("Starting full roster analysis")
            
            # Get current roster
            roster_data = self.api.get_current_roster()
            if not roster_data:
                logger.error("Failed to get roster data")
                return {'error': 'Failed to get roster data'}
            
            # Generate report
            report = self.generate_roster_report(roster_data)
            
            # Return analysis summary
            analysis_summary = {
                'roster_count': len(roster_data),
                'report_file': report,
                'health_summary': self.analyze_roster_health(roster_data),
                'gaps_summary': self.identify_roster_gaps(roster_data)
            }
            
            logger.info("Full roster analysis completed successfully")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Full roster analysis failed: {e}")
            return {'error': str(e)}

def main():
    """Test the roster analyzer"""
    try:
        print("🏈 Testing Roster Analyzer...")
        
        analyzer = RosterAnalyzer()
        results = analyzer.run_full_analysis()
        
        if 'error' not in results:
            print("✅ Roster analysis completed successfully!")
            print(f"📊 Analyzed {results['roster_count']} players")
            print(f"📄 Report generated and saved")
            
            # Show health summary
            health = results['health_summary']
            print(f"\n🏥 Roster Health:")
            print(f"   Healthy: {health.get('healthy_players', 0)}")
            print(f"   Questionable: {health.get('questionable_players', 0)}")
            print(f"   Out: {health.get('out_players', 0)}")
            
            # Show gap summary
            gaps = results['gaps_summary']
            if gaps.get('critical_needs'):
                print(f"\n🚨 Critical Needs: {len(gaps['critical_needs'])}")
                for need in gaps['critical_needs'][:3]:  # Show first 3
                    print(f"   - {need}")
        else:
            print(f"❌ Roster analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main test failed: {e}")

if __name__ == "__main__":
    main()
