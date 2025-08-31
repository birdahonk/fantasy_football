#!/usr/bin/env python3
"""
Performance Tracking Script
Tracks post-game performance and analyzes projection accuracy
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

class PerformanceTracker:
    """Tracks and analyzes fantasy football performance"""
    
    def __init__(self):
        self.api = YahooFantasyAPI()
        self.current_week = get_current_week()
        
        # Performance thresholds
        self.performance_thresholds = {
            'QB': {'excellent': 25, 'good': 20, 'average': 15, 'poor': 10},
            'RB': {'excellent': 20, 'good': 15, 'average': 10, 'poor': 5},
            'WR': {'excellent': 18, 'good': 14, 'average': 9, 'poor': 4},
            'TE': {'excellent': 15, 'good': 12, 'average': 8, 'poor': 3},
            'K': {'excellent': 12, 'good': 10, 'average': 8, 'poor': 5},
            'DEF': {'excellent': 15, 'good': 12, 'average': 8, 'poor': 3}
        }
    
    def compare_projections_to_actual(self, projections: List[Dict], actual: List[Dict]) -> Dict[str, Any]:
        """Compare pre-game projections to actual performance"""
        try:
            comparison = {
                'total_players': len(projections),
                'projection_accuracy': {},
                'overperformers': [],
                'underperformers': [],
                'accurate_projections': [],
                'accuracy_summary': {},
                'lessons_learned': []
            }
            
            # Match projections to actual results
            for projection in projections:
                player_name = projection.get('name', 'Unknown')
                projected_points = float(projection.get('projected_points', 0))
                
                # Find matching actual result
                actual_result = None
                for actual_player in actual:
                    if actual_player.get('name') == player_name:
                        actual_result = actual_player
                        break
                
                if actual_result:
                    actual_points = float(actual_result.get('actual_points', 0))
                    variance = actual_points - projected_points
                    accuracy_percentage = self._calculate_accuracy_percentage(projected_points, actual_points)
                    
                    player_comparison = {
                        'name': player_name,
                        'position': projection.get('position', 'Unknown'),
                        'projected': projected_points,
                        'actual': actual_points,
                        'variance': variance,
                        'accuracy_percentage': accuracy_percentage,
                        'performance_rating': self._rate_performance(projection.get('position', 'Unknown'), actual_points)
                    }
                    
                    # Categorize performance
                    if variance > 5:  # Significantly overperformed
                        comparison['overperformers'].append(player_comparison)
                    elif variance < -5:  # Significantly underperformed
                        comparison['underperformers'].append(player_comparison)
                    else:  # Accurate projection
                        comparison['accurate_projections'].append(player_comparison)
                    
                    # Track accuracy by position
                    position = projection.get('position', 'Unknown')
                    if position not in comparison['projection_accuracy']:
                        comparison['projection_accuracy'][position] = []
                    comparison['projection_accuracy'][position].append(player_comparison)
            
            # Calculate accuracy summary
            comparison['accuracy_summary'] = self._calculate_accuracy_summary(comparison['projection_accuracy'])
            
            # Generate lessons learned
            comparison['lessons_learned'] = self._generate_lessons_learned(comparison)
            
            logger.info(f"Projection comparison completed: {len(comparison['overperformers'])} overperformers, {len(comparison['underperformers'])} underperformers")
            return comparison
            
        except Exception as e:
            logger.error(f"Projection comparison failed: {e}")
            return {}
    
    def _calculate_accuracy_percentage(self, projected: float, actual: float) -> float:
        """Calculate projection accuracy percentage"""
        try:
            if projected == 0:
                return 0.0
            
            # Calculate percentage difference
            percentage_diff = abs(actual - projected) / projected * 100
            
            # Convert to accuracy percentage (100% = perfect projection)
            accuracy = max(0, 100 - percentage_diff)
            
            return round(accuracy, 1)
            
        except Exception as e:
            logger.error(f"Accuracy percentage calculation failed: {e}")
            return 0.0
    
    def _rate_performance(self, position: str, points: float) -> str:
        """Rate player performance based on position and points"""
        try:
            thresholds = self.performance_thresholds.get(position, {})
            
            if points >= thresholds.get('excellent', 20):
                return '🏆 EXCELLENT'
            elif points >= thresholds.get('good', 15):
                return '✅ GOOD'
            elif points >= thresholds.get('average', 10):
                return '➡️ AVERAGE'
            elif points >= thresholds.get('poor', 5):
                return '⚠️ POOR'
            else:
                return '🚨 VERY POOR'
                
        except Exception as e:
            logger.error(f"Performance rating failed: {e}")
            return 'UNKNOWN'
    
    def _calculate_accuracy_summary(self, position_accuracy: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate accuracy summary by position"""
        try:
            summary = {}
            
            for position, players in position_accuracy.items():
                if not players:
                    continue
                
                total_accuracy = sum(p['accuracy_percentage'] for p in players)
                avg_accuracy = total_accuracy / len(players)
                
                # Count over/under performers
                overperformers = len([p for p in players if p['variance'] > 5])
                underperformers = len([p for p in players if p['variance'] < -5])
                accurate = len([p for p in players if -5 <= p['variance'] <= 5])
                
                summary[position] = {
                    'avg_accuracy': round(avg_accuracy, 1),
                    'total_players': len(players),
                    'overperformers': overperformers,
                    'underperformers': underperformers,
                    'accurate': accurate,
                    'accuracy_rating': self._rate_accuracy(avg_accuracy)
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Accuracy summary calculation failed: {e}")
            return {}
    
    def _rate_accuracy(self, accuracy_percentage: float) -> str:
        """Rate projection accuracy"""
        if accuracy_percentage >= 90:
            return '🏆 EXCELLENT'
        elif accuracy_percentage >= 80:
            return '✅ GOOD'
        elif accuracy_percentage >= 70:
            return '➡️ AVERAGE'
        elif accuracy_percentage >= 60:
            return '⚠️ POOR'
        else:
            return '🚨 VERY POOR'
    
    def _generate_lessons_learned(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate lessons learned from projection analysis"""
        lessons = []
        
        # Analyze overperformers
        if comparison['overperformers']:
            over_count = len(comparison['overperformers'])
            lessons.append(f"📈 {over_count} player(s) significantly exceeded projections - consider higher expectations next week")
            
            # Identify patterns
            positions = [p['position'] for p in comparison['overperformers']]
            if len(set(positions)) == 1:
                lessons.append(f"🎯 {positions[0]} position consistently overperformed - projections may be too conservative")
        
        # Analyze underperformers
        if comparison['underperformers']:
            under_count = len(comparison['underperformers'])
            lessons.append(f"📉 {under_count} player(s) significantly underperformed projections - investigate causes")
            
            # Check for injury impacts
            injured_underperformers = [p for p in comparison['underperformers'] if p.get('status') in ['Q', 'D', 'O']]
            if injured_underperformers:
                lessons.append(f"🏥 {len(injured_underperformers)} underperforming player(s) had health concerns - factor injuries into projections")
        
        # Overall accuracy assessment
        total_players = comparison['total_players']
        accurate_count = len(comparison['accurate_projections'])
        accuracy_rate = (accurate_count / total_players * 100) if total_players > 0 else 0
        
        if accuracy_rate >= 80:
            lessons.append(f"🎯 Projections were very accurate ({accuracy_rate:.1f}% within 5 points) - system working well")
        elif accuracy_rate >= 60:
            lessons.append(f"⚠️ Projections were moderately accurate ({accuracy_rate:.1f}% within 5 points) - room for improvement")
        else:
            lessons.append(f"🚨 Projections were poor ({accuracy_rate:.1f}% within 5 points) - significant improvement needed")
        
        return lessons
    
    def track_player_performance(self, player_id: str, weeks: int = 5) -> Dict[str, Any]:
        """Track individual player performance over multiple weeks"""
        try:
            tracking = {
                'player_id': player_id,
                'weeks_analyzed': weeks,
                'performance_trend': 'UNKNOWN',
                'weekly_scores': [],
                'consistency_rating': 'UNKNOWN',
                'trend_analysis': [],
                'recommendations': []
            }
            
            # Load historical performance data
            historical_data = self._load_player_historical_data(player_id, weeks)
            
            if not historical_data:
                tracking['trend_analysis'].append("Insufficient historical data for trend analysis")
                return tracking
            
            # Analyze weekly performance
            for week_data in historical_data:
                tracking['weekly_scores'].append({
                    'week': week_data.get('week'),
                    'points': week_data.get('points', 0),
                    'projection': week_data.get('projection', 0),
                    'accuracy': week_data.get('accuracy', 0)
                })
            
            # Calculate performance trend
            if len(tracking['weekly_scores']) >= 3:
                recent_scores = [w['points'] for w in tracking['weekly_scores'][-3:]]
                older_scores = [w['points'] for w in tracking['weekly_scores'][:-3]]
                
                if len(older_scores) > 0:
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores)
                    
                    if recent_avg > older_avg * 1.2:
                        tracking['performance_trend'] = '📈 IMPROVING'
                        tracking['trend_analysis'].append("Player showing significant improvement in recent weeks")
                    elif recent_avg < older_avg * 0.8:
                        tracking['performance_trend'] = '📉 DECLINING'
                        tracking['trend_analysis'].append("Player showing decline in recent weeks")
                    else:
                        tracking['performance_trend'] = '➡️ STABLE'
                        tracking['trend_analysis'].append("Player performance is stable")
            
            # Calculate consistency rating
            if len(tracking['weekly_scores']) >= 2:
                scores = [w['points'] for w in tracking['weekly_scores']]
                variance = max(scores) - min(scores)
                avg_score = sum(scores) / len(scores)
                
                if variance <= avg_score * 0.3:
                    tracking['consistency_rating'] = '🟢 VERY CONSISTENT'
                elif variance <= avg_score * 0.5:
                    tracking['consistency_rating'] = '🟡 CONSISTENT'
                elif variance <= avg_score * 0.8:
                    tracking['consistency_rating'] = '🟠 INCONSISTENT'
                else:
                    tracking['consistency_rating'] = '🔴 VERY INCONSISTENT'
                
                tracking['trend_analysis'].append(f"Score variance: {variance:.1f} points (avg: {avg_score:.1f})")
            
            # Generate recommendations
            tracking['recommendations'] = self._generate_player_recommendations(tracking)
            
            logger.info(f"Player performance tracking completed for {player_id}")
            return tracking
            
        except Exception as e:
            logger.error(f"Player performance tracking failed for {player_id}: {e}")
            return {}
    
    def _load_player_historical_data(self, player_id: str, weeks: int) -> List[Dict[str, Any]]:
        """Load historical performance data for a player"""
        try:
            # This would typically load from database or historical files
            # For now, return mock data structure
            historical_data = []
            
            # Try to load from historical files
            for week in range(max(1, self.current_week - weeks), self.current_week):
                filename = f'week_{week}_performance.json'
                week_data = load_historical_file(filename)
                
                if week_data and 'players' in week_data:
                    player_data = next((p for p in week_data['players'] if p.get('player_id') == player_id), None)
                    if player_data:
                        historical_data.append({
                            'week': week,
                            'points': player_data.get('actual_points', 0),
                            'projection': player_data.get('projected_points', 0),
                            'accuracy': player_data.get('accuracy', 0)
                        })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical data loading failed for {player_id}: {e}")
            return []
    
    def _generate_player_recommendations(self, tracking: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on player performance tracking"""
        recommendations = []
        
        trend = tracking.get('performance_trend', 'UNKNOWN')
        consistency = tracking.get('consistency_rating', 'UNKNOWN')
        
        if 'IMPROVING' in trend:
            recommendations.append("🎯 Player is improving - consider higher projections and increased usage")
        elif 'DECLINING' in trend:
            recommendations.append("⚠️ Player is declining - investigate causes and consider reduced expectations")
        
        if 'VERY CONSISTENT' in consistency:
            recommendations.append("🟢 Very consistent player - reliable for weekly lineups")
        elif 'VERY INCONSISTENT' in consistency:
            recommendations.append("🔴 Very inconsistent player - high risk/reward, consider as flex option only")
        
        # Check for projection accuracy trends
        if tracking.get('weekly_scores'):
            recent_accuracy = [w['accuracy'] for w in tracking['weekly_scores'][-3:]]
            if recent_accuracy and all(acc > 80 for acc in recent_accuracy):
                recommendations.append("📊 Projections have been very accurate recently - trust the system")
            elif recent_accuracy and all(acc < 60 for acc in recent_accuracy):
                recommendations.append("📊 Projections have been poor recently - manual adjustment may be needed")
        
        return recommendations
    
    def assess_team_performance(self, week: int) -> Dict[str, Any]:
        """Assess overall team performance for a specific week"""
        try:
            assessment = {
                'week': week,
                'total_points': 0,
                'projected_total': 0,
                'actual_vs_projected': 0,
                'position_performance': {},
                'key_performers': [],
                'disappointments': [],
                'team_grade': 'UNKNOWN',
                'improvement_areas': []
            }
            
            # Load week performance data
            week_data = self._load_week_performance_data(week)
            
            if not week_data:
                assessment['improvement_areas'].append("No performance data available for this week")
                return assessment
            
            # Calculate team totals
            for player in week_data.get('players', []):
                projected = float(player.get('projected_points', 0))
                actual = float(player.get('actual_points', 0))
                
                assessment['projected_total'] += projected
                assessment['total_points'] += actual
                
                # Track position performance
                position = player.get('position', 'Unknown')
                if position not in assessment['position_performance']:
                    assessment['position_performance'][position] = {
                        'total_projected': 0,
                        'total_actual': 0,
                        'player_count': 0
                    }
                
                assessment['position_performance'][position]['total_projected'] += projected
                assessment['position_performance'][position]['total_actual'] += actual
                assessment['position_performance'][position]['player_count'] += 1
            
            # Calculate overall variance
            assessment['actual_vs_projected'] = assessment['total_points'] - assessment['projected_total']
            
            # Identify key performers and disappointments
            for player in week_data.get('players', []):
                projected = float(player.get('projected_points', 0))
                actual = float(player.get('actual_points', 0))
                variance = actual - projected
                
                if variance > 10:  # Significantly overperformed
                    assessment['key_performers'].append({
                        'name': player.get('name', 'Unknown'),
                        'position': player.get('position', 'Unknown'),
                        'projected': projected,
                        'actual': actual,
                        'variance': variance
                    })
                elif variance < -10:  # Significantly underperformed
                    assessment['disappointments'].append({
                        'name': player.get('name', 'Unknown'),
                        'position': player.get('position', 'Unknown'),
                        'projected': projected,
                        'actual': actual,
                        'variance': variance
                    })
            
            # Calculate team grade
            assessment['team_grade'] = self._calculate_team_grade(assessment)
            
            # Identify improvement areas
            assessment['improvement_areas'] = self._identify_improvement_areas(assessment)
            
            logger.info(f"Team performance assessment completed for week {week}")
            return assessment
            
        except Exception as e:
            logger.error(f"Team performance assessment failed for week {week}: {e}")
            return {}
    
    def _load_week_performance_data(self, week: int) -> Optional[Dict[str, Any]]:
        """Load performance data for a specific week"""
        try:
            filename = f'week_{week}_performance.json'
            return load_historical_file(filename)
        except Exception as e:
            logger.error(f"Week performance data loading failed for week {week}: {e}")
            return None
    
    def _calculate_team_grade(self, assessment: Dict[str, Any]) -> str:
        """Calculate overall team grade for the week"""
        try:
            if assessment['projected_total'] == 0:
                return 'UNKNOWN'
            
            # Calculate percentage of projected points achieved
            percentage = (assessment['total_points'] / assessment['projected_total']) * 100
            
            if percentage >= 120:
                return '🏆 A+ (Exceptional)'
            elif percentage >= 110:
                return '✅ A (Excellent)'
            elif percentage >= 100:
                return '🟢 B+ (Good)'
            elif percentage >= 90:
                return '🟡 B (Average)'
            elif percentage >= 80:
                return '🟠 C (Below Average)'
            else:
                return '🔴 D (Poor)'
                
        except Exception as e:
            logger.error(f"Team grade calculation failed: {e}")
            return 'UNKNOWN'
    
    def _identify_improvement_areas(self, assessment: Dict[str, Any]) -> List[str]:
        """Identify areas where team performance can improve"""
        areas = []
        
        # Check overall performance
        if assessment['actual_vs_projected'] < 0:
            areas.append(f"📉 Team underperformed projections by {abs(assessment['actual_vs_projected']):.1f} points")
        
        # Check position performance
        for position, perf in assessment['position_performance'].items():
            if perf['total_actual'] < perf['total_projected'] * 0.8:  # 20% below projection
                variance = perf['total_projected'] - perf['total_actual']
                areas.append(f"📊 {position} position underperformed by {variance:.1f} points")
        
        # Check for too many disappointments
        if len(assessment['disappointments']) > len(assessment['key_performers']):
            areas.append(f"⚠️ More players underperformed ({len(assessment['disappointments'])}) than overperformed ({len(assessment['key_performers'])})")
        
        # Check for consistency issues
        if assessment['team_grade'] in ['C', 'D']:
            areas.append("🔍 Overall team performance needs improvement - review lineup decisions and player evaluations")
        
        return areas
    
    def generate_performance_report(self, week: int) -> str:
        """Generate comprehensive performance analysis report"""
        try:
            # Assess team performance
            team_assessment = self.assess_team_performance(week)
            
            # Generate markdown report
            report = self._format_performance_report(team_assessment)
            
            # Save report
            filename = f"2-postgame_performance_analysis.md"
            saved_file = save_markdown_report(report, filename, week)
            
            logger.info(f"Performance report generated and saved: {saved_file}")
            return report
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {e}")
            return f"Error generating performance report: {e}"
    
    def _format_performance_report(self, assessment: Dict[str, Any]) -> str:
        """Format performance assessment into markdown report"""
        report = f"""# 📊 Performance Analysis Report - Week {assessment.get('week', 'Unknown')}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Team Grade:** {assessment.get('team_grade', 'Unknown')}

---

## 🎯 Overall Performance Summary

### 📈 Team Totals
- **Projected Points:** {assessment.get('projected_total', 0):.1f}
- **Actual Points:** {assessment.get('total_points', 0):.1f}
- **Variance:** {assessment.get('actual_vs_projected', 0):.1f} points
- **Performance:** {'✅ Exceeded' if assessment.get('actual_vs_projected', 0) > 0 else '📉 Below'} projections

---

## 🏆 Key Performers

"""
        
        if assessment.get('key_performers'):
            report += """
| Player | Position | Projected | Actual | Variance |
|--------|----------|-----------|--------|----------|
"""
            for performer in assessment['key_performers'][:5]:  # Top 5
                name = performer['name']
                position = performer['position']
                projected = performer['projected']
                actual = performer['actual']
                variance = performer['variance']
                
                report += f"| {name} | {position} | {projected:.1f} | {actual:.1f} | +{variance:.1f} |\n"
        else:
            report += "No players significantly exceeded projections this week.\n"
        
        report += "\n---\n## 📉 Disappointments\n"
        
        if assessment.get('disappointments'):
            report += """
| Player | Position | Projected | Actual | Variance |
|--------|----------|-----------|--------|----------|
"""
            for disappointment in assessment['disappointments'][:5]:  # Top 5
                name = disappointment['name']
                position = disappointment['position']
                projected = disappointment['projected']
                actual = disappointment['actual']
                variance = disappointment['variance']
                
                report += f"| {name} | {position} | {projected:.1f} | {actual:.1f} | {variance:.1f} |\n"
        else:
            report += "No players significantly underperformed projections this week.\n"
        
        report += "\n---\n## 📊 Position Performance Breakdown\n"
        
        for position, perf in assessment.get('position_performance', {}).items():
            projected = perf['total_projected']
            actual = perf['total_actual']
            variance = actual - projected
            percentage = (actual / projected * 100) if projected > 0 else 0
            
            performance_emoji = "✅" if percentage >= 100 else "⚠️" if percentage >= 80 else "📉"
            
            report += f"\n### {position}\n"
            report += f"- **Projected:** {projected:.1f} points\n"
            report += f"- **Actual:** {actual:.1f} points\n"
            report += f"- **Variance:** {variance:.1f} points\n"
            report += f"- **Performance:** {performance_emoji} {percentage:.1f}% of projection\n"
        
        report += "\n---\n## 🔍 Areas for Improvement\n"
        
        for area in assessment.get('improvement_areas', []):
            report += f"- {area}\n"
        
        report += f"""

---

*Report generated by Fantasy Football AI General Manager*  
*Week {assessment.get('week', 'Unknown')} Performance Analysis*
"""
        
        return report
    
    def run_full_analysis(self, week: Optional[int] = None) -> Dict[str, Any]:
        """Run complete performance analysis"""
        try:
            if week is None:
                week = self.current_week - 1  # Analyze previous week
            
            logger.info(f"Starting full performance analysis for week {week}")
            
            # Generate performance report
            report = self.generate_performance_report(week)
            
            # Return analysis summary
            analysis_summary = {
                'week': week,
                'report_file': report,
                'analysis_type': 'post_game_performance'
            }
            
            logger.info(f"Full performance analysis completed successfully for week {week}")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Full performance analysis failed: {e}")
            return {'error': str(e)}

def main():
    """Test the performance tracker"""
    try:
        print("📊 Testing Performance Tracker...")
        
        tracker = PerformanceTracker()
        results = tracker.run_full_analysis()
        
        if 'error' not in results:
            print("✅ Performance analysis completed successfully!")
            print(f"📊 Analyzed week {results['week']}")
            print(f"📄 Report generated and saved")
        else:
            print(f"❌ Performance analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main test failed: {e}")

if __name__ == "__main__":
    main()
