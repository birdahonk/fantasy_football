#!/usr/bin/env python3
"""
Matchup Analysis Script
Analyzes weekly matchups and provides lineup optimization recommendations
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

class MatchupAnalyzer:
    """Analyzes weekly matchups and provides lineup optimization"""
    
    def __init__(self):
        self.api = YahooFantasyAPI()
        self.current_week = get_current_week()
        
        # Position scoring weights for matchup analysis
        self.position_weights = {
            'QB': 1.2,    # Quarterbacks are most important
            'RB': 1.1,    # Running backs are very important
            'WR': 1.0,    # Wide receivers are standard weight
            'TE': 0.9,    # Tight ends slightly less important
            'K': 0.7,     # Kickers less important
            'DEF': 0.8    # Defense moderately important
        }
        
        # Matchup difficulty indicators
        self.difficulty_levels = {
            'EASY': '🟢 Easy matchup - favorable for your players',
            'MEDIUM': '🟡 Medium matchup - competitive game',
            'HARD': '🔴 Hard matchup - challenging for your players',
            'VERY_HARD': '⚫ Very hard matchup - consider alternatives'
        }
    
    def analyze_opponent_strength(self, opponent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze opponent's team strength and identify key players"""
        try:
            analysis = {
                'team_name': opponent_data.get('team_name', 'Unknown'),
                'total_players': len(opponent_data.get('roster', [])),
                'position_distribution': {},
                'key_players': [],
                'weaknesses': [],
                'strengths': [],
                'overall_strength': 'MEDIUM',
                'risk_assessment': 'MEDIUM'
            }
            
            roster = opponent_data.get('roster', [])
            
            # Analyze position distribution
            for player in roster:
                position = player.get('position', 'Unknown')
                if position not in analysis['position_distribution']:
                    analysis['position_distribution'][position] = 0
                analysis['position_distribution'][position] += 1
            
            # Identify key players (high ownership = generally better)
            for player in roster:
                ownership = float(player.get('percent_owned', 0))
                if ownership > 80:  # High ownership players
                    analysis['key_players'].append({
                        'name': player.get('name', 'Unknown'),
                        'position': player.get('position', 'Unknown'),
                        'team': player.get('team', 'Unknown'),
                        'ownership': ownership,
                        'threat_level': 'HIGH'
                    })
                elif ownership > 60:  # Medium ownership players
                    analysis['key_players'].append({
                        'name': player.get('name', 'Unknown'),
                        'position': player.get('position', 'Unknown'),
                        'team': player.get('team', 'Unknown'),
                        'ownership': ownership,
                        'threat_level': 'MEDIUM'
                    })
            
            # Assess team strengths and weaknesses
            analysis['strengths'] = self._identify_team_strengths(roster)
            analysis['weaknesses'] = self._identify_team_weaknesses(roster)
            
            # Calculate overall strength
            analysis['overall_strength'] = self._calculate_team_strength(roster)
            analysis['risk_assessment'] = self._assess_opponent_risk(roster)
            
            logger.info(f"Opponent analysis completed for {analysis['team_name']}: {analysis['overall_strength']} strength")
            return analysis
            
        except Exception as e:
            logger.error(f"Opponent strength analysis failed: {e}")
            return {}
    
    def _identify_team_strengths(self, roster: List[Dict[str, Any]]) -> List[str]:
        """Identify opponent team strengths"""
        strengths = []
        
        # Count high-ownership players by position
        position_strengths = {}
        for player in roster:
            position = player.get('position', 'Unknown')
            ownership = float(player.get('percent_owned', 0))
            
            if position not in position_strengths:
                position_strengths[position] = []
            position_strengths[position].append(ownership)
        
        # Identify strong positions
        for position, ownerships in position_strengths.items():
            avg_ownership = sum(ownerships) / len(ownerships)
            if avg_ownership > 70:
                strengths.append(f"Strong {position} depth (avg {avg_ownership:.1f}% ownership)")
            elif avg_ownership > 50:
                strengths.append(f"Solid {position} group (avg {avg_ownership:.1f}% ownership)")
        
        # Check for elite players
        elite_count = len([p for p in roster if float(p.get('percent_owned', 0)) > 90])
        if elite_count > 0:
            strengths.append(f"{elite_count} elite player(s) with >90% ownership")
        
        return strengths
    
    def _identify_team_weaknesses(self, roster: List[Dict[str, Any]]) -> List[str]:
        """Identify opponent team weaknesses"""
        weaknesses = []
        
        # Check for thin positions
        position_counts = {}
        for player in roster:
            position = player.get('position', 'Unknown')
            if position not in position_counts:
                position_counts[position] = 0
            position_counts[position] += 1
        
        # Identify weak positions
        for position, count in position_counts.items():
            if position in ['QB', 'TE', 'K', 'DEF'] and count < 2:
                weaknesses.append(f"Thin {position} depth ({count} player)")
            elif position in ['RB', 'WR'] and count < 3:
                weaknesses.append(f"Limited {position} depth ({count} players)")
        
        # Check for low-ownership players
        low_ownership_count = len([p for p in roster if float(p.get('percent_owned', 0)) < 30])
        if low_ownership_count > 0:
            weaknesses.append(f"{low_ownership_count} player(s) with <30% ownership")
        
        return weaknesses
    
    def _calculate_team_strength(self, roster: List[Dict[str, Any]]) -> str:
        """Calculate overall team strength rating"""
        try:
            if not roster:
                return 'UNKNOWN'
            
            # Calculate weighted average ownership
            total_weighted_ownership = 0
            total_weight = 0
            
            for player in roster:
                position = player.get('position', 'Unknown')
                ownership = float(player.get('percent_owned', 50))
                weight = self.position_weights.get(position, 1.0)
                
                total_weighted_ownership += ownership * weight
                total_weight += weight
            
            avg_weighted_ownership = total_weighted_ownership / total_weight if total_weight > 0 else 50
            
            # Determine strength level
            if avg_weighted_ownership > 80:
                return 'VERY_STRONG'
            elif avg_weighted_ownership > 70:
                return 'STRONG'
            elif avg_weighted_ownership > 60:
                return 'MEDIUM'
            elif avg_weighted_ownership > 50:
                return 'WEAK'
            else:
                return 'VERY_WEAK'
                
        except Exception as e:
            logger.error(f"Team strength calculation failed: {e}")
            return 'MEDIUM'
    
    def _assess_opponent_risk(self, roster: List[Dict[str, Any]]) -> str:
        """Assess risk level of opponent team"""
        try:
            # Count high-threat players
            high_threat = len([p for p in roster if float(p.get('percent_owned', 0)) > 85])
            medium_threat = len([p for p in roster if 60 < float(p.get('percent_owned', 0)) <= 85])
            
            if high_threat >= 3:
                return 'HIGH'
            elif high_threat >= 1 or medium_threat >= 3:
                return 'MEDIUM'
            else:
                return 'LOW'
                
        except Exception as e:
            logger.error(f"Opponent risk assessment failed: {e}")
            return 'MEDIUM'
    
    def optimize_lineup(self, roster_data: List[Dict[str, Any]], opponent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize lineup based on opponent analysis"""
        try:
            optimization = {
                'recommended_starters': [],
                'bench_recommendations': [],
                'position_strategies': {},
                'matchup_advantages': [],
                'risk_mitigation': [],
                'overall_strategy': 'Standard lineup - no major changes needed'
            }
            
            # Analyze opponent to understand matchup
            opponent_analysis = self.analyze_opponent_strength(opponent_data)
            
            # Group roster by position
            roster_by_position = {}
            for player in roster_data:
                position = player.get('position', 'Unknown')
                if position not in roster_by_position:
                    roster_by_position[position] = []
                roster_by_position[position].append(player)
            
            # Analyze each position for optimization
            for position, players in roster_by_position.items():
                position_strategy = self._optimize_position(
                    position, 
                    players, 
                    opponent_analysis
                )
                optimization['position_strategies'][position] = position_strategy
                
                # Add recommended starters
                optimization['recommended_starters'].extend(
                    position_strategy.get('recommended_starters', [])
                )
                
                # Add bench recommendations
                optimization['bench_recommendations'].extend(
                    position_strategy.get('bench_recommendations', [])
                )
            
            # Identify matchup advantages
            optimization['matchup_advantages'] = self._identify_matchup_advantages(
                roster_data, 
                opponent_analysis
            )
            
            # Generate risk mitigation strategies
            optimization['risk_mitigation'] = self._generate_risk_mitigation(
                roster_data, 
                opponent_analysis
            )
            
            # Determine overall strategy
            optimization['overall_strategy'] = self._determine_overall_strategy(
                optimization, 
                opponent_analysis
            )
            
            logger.info(f"Lineup optimization completed: {len(optimization['recommended_starters'])} recommended starters")
            return optimization
            
        except Exception as e:
            logger.error(f"Lineup optimization failed: {e}")
            return {}
    
    def _optimize_position(self, position: str, players: List[Dict], opponent_analysis: Dict) -> Dict[str, Any]:
        """Optimize lineup for a specific position"""
        try:
            strategy = {
                'position': position,
                'recommended_starters': [],
                'bench_recommendations': [],
                'strategy': 'Standard approach',
                'reasoning': []
            }
            
            # Sort players by estimated value (ownership as proxy)
            sorted_players = sorted(
                players, 
                key=lambda x: float(x.get('percent_owned', 50)), 
                reverse=True
            )
            
            # Determine how many to start based on position
            start_count = self._get_position_start_count(position)
            
            # Select starters
            for i, player in enumerate(sorted_players):
                if i < start_count:
                    strategy['recommended_starters'].append({
                        'player': player,
                        'reason': f"Top {position} option #{i+1}",
                        'confidence': 'HIGH' if i == 0 else 'MEDIUM'
                    })
                else:
                    strategy['bench_recommendations'].append({
                        'player': player,
                        'reason': f"Bench {position} option #{i-start_count+1}",
                        'priority': 'HIGH' if i == start_count else 'MEDIUM'
                    })
            
            # Adjust strategy based on opponent
            if opponent_analysis.get('overall_strength') in ['VERY_STRONG', 'STRONG']:
                strategy['strategy'] = f'Aggressive {position} approach - opponent is strong'
                strategy['reasoning'].append("Opponent has strong team - maximize scoring potential")
            elif opponent_analysis.get('overall_strength') in ['VERY_WEAK', 'WEAK']:
                strategy['strategy'] = f'Conservative {position} approach - opponent is weak'
                strategy['reasoning'].append("Opponent is weak - focus on consistent, safe options")
            
            return strategy
            
        except Exception as e:
            logger.error(f"Position optimization failed for {position}: {e}")
            return {}
    
    def _get_position_start_count(self, position: str) -> int:
        """Get recommended number of starters for a position"""
        if position == 'QB':
            return 1
        elif position == 'RB':
            return 2  # Assuming 2 RB slots
        elif position == 'WR':
            return 3  # Assuming 3 WR slots
        elif position == 'TE':
            return 1
        elif position == 'K':
            return 1
        elif position == 'DEF':
            return 1
        else:
            return 1
    
    def _identify_matchup_advantages(self, roster: List[Dict], opponent_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify specific matchup advantages"""
        advantages = []
        
        # Check for positions where you have depth advantage
        for position, players in self._group_by_position(roster).items():
            opponent_players = [p for p in opponent_analysis.get('roster', []) if p.get('position') == position]
            
            if len(players) > len(opponent_players):
                advantages.append({
                    'type': 'DEPTH',
                    'position': position,
                    'advantage': f"More {position} depth ({len(players)} vs {len(opponent_players)})",
                    'impact': 'MEDIUM'
                })
        
        # Check for elite player advantages
        your_elite = [p for p in roster if float(p.get('percent_owned', 0)) > 90]
        opponent_elite = [p for p in opponent_analysis.get('roster', []) if float(p.get('percent_owned', 0)) > 90]
        
        if len(your_elite) > len(opponent_elite):
            advantages.append({
                'type': 'ELITE_PLAYERS',
                'position': 'Overall',
                'advantage': f"More elite players ({len(your_elite)} vs {len(opponent_elite)})",
                'impact': 'HIGH'
            })
        
        return advantages
    
    def _group_by_position(self, roster: List[Dict]) -> Dict[str, List[Dict]]:
        """Group roster players by position"""
        grouped = {}
        for player in roster:
            position = player.get('position', 'Unknown')
            if position not in grouped:
                grouped[position] = []
            grouped[position].append(player)
        return grouped
    
    def _generate_risk_mitigation(self, roster: List[Dict], opponent_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate strategies to mitigate matchup risks"""
        mitigation = []
        
        # Check for injury risks
        injured_players = [p for p in roster if p.get('status') in ['Q', 'D', 'O']]
        if injured_players:
            mitigation.append({
                'risk': 'INJURY',
                'players': [p.get('name') for p in injured_players],
                'strategy': 'Monitor closely and have healthy backups ready',
                'priority': 'HIGH'
            })
        
        # Check for tough opponent
        if opponent_analysis.get('overall_strength') in ['VERY_STRONG', 'STRONG']:
            mitigation.append({
                'risk': 'STRONG_OPPONENT',
                'players': 'All players',
                'strategy': 'Focus on high-ceiling players and consider boom/bust options',
                'priority': 'MEDIUM'
            })
        
        # Check for position mismatches
        opponent_strengths = opponent_analysis.get('strengths', [])
        for strength in opponent_strengths:
            if 'Strong' in strength and 'depth' in strength:
                position = strength.split()[1]  # Extract position from "Strong RB depth"
                mitigation.append({
                    'risk': 'POSITION_MISMATCH',
                    'players': f'{position} players',
                    'strategy': f'Maximize {position} scoring potential to counter opponent strength',
                    'priority': 'MEDIUM'
                })
        
        return mitigation
    
    def _determine_overall_strategy(self, optimization: Dict, opponent_analysis: Dict) -> str:
        """Determine overall lineup strategy"""
        opponent_strength = opponent_analysis.get('overall_strength', 'MEDIUM')
        risk_level = opponent_analysis.get('risk_assessment', 'MEDIUM')
        
        if opponent_strength in ['VERY_STRONG', 'STRONG'] and risk_level == 'HIGH':
            return "Aggressive strategy - opponent is strong, need high-ceiling plays"
        elif opponent_strength in ['VERY_WEAK', 'WEAK']:
            return "Conservative strategy - opponent is weak, focus on consistent scoring"
        elif risk_level == 'HIGH':
            return "Balanced strategy with risk management - opponent has high-threat players"
        else:
            return "Standard strategy - competitive matchup, play your best players"
    
    def identify_matchup_advantages(self, roster_data: List[Dict], opponent_data: Dict) -> List[Dict[str, Any]]:
        """Identify favorable matchups and advantages"""
        try:
            advantages = []
            
            # Get opponent analysis
            opponent_analysis = self.analyze_opponent_strength(opponent_data)
            
            # Check for depth advantages
            for position, players in self._group_by_position(roster_data).items():
                opponent_players = [p for p in opponent_data.get('roster', []) if p.get('position') == position]
                
                if len(players) > len(opponent_players):
                    advantages.append({
                        'type': 'DEPTH',
                        'position': position,
                        'description': f"More {position} depth than opponent",
                        'advantage': f"{len(players)} vs {len(opponent_players)} players",
                        'impact': 'MEDIUM'
                    })
            
            # Check for elite player advantages
            your_elite = [p for p in roster_data if float(p.get('percent_owned', 0)) > 90]
            opponent_elite = [p for p in opponent_data.get('roster', []) if float(p.get('percent_owned', 0)) > 90]
            
            if len(your_elite) > len(opponent_elite):
                advantages.append({
                    'type': 'ELITE_PLAYERS',
                    'position': 'Overall',
                    'description': 'More elite players than opponent',
                    'advantage': f"{len(your_elite)} vs {len(opponent_elite)} elite players",
                    'impact': 'HIGH'
                })
            
            # Check for health advantages
            your_healthy = len([p for p in roster_data if p.get('status') not in ['Q', 'D', 'O']])
            opponent_healthy = len([p for p in opponent_data.get('roster', []) if p.get('status') not in ['Q', 'D', 'O']])
            
            if your_healthy > opponent_healthy:
                advantages.append({
                    'type': 'HEALTH',
                    'position': 'Overall',
                    'description': 'Healthier roster than opponent',
                    'advantage': f"{your_healthy} vs {opponent_healthy} healthy players",
                    'impact': 'MEDIUM'
                })
            
            return advantages
            
        except Exception as e:
            logger.error(f"Matchup advantage identification failed: {e}")
            return []
    
    def generate_matchup_report(self, roster_data: List[Dict], opponent_data: Dict) -> str:
        """Generate comprehensive matchup analysis report"""
        try:
            # Analyze opponent
            opponent_analysis = self.analyze_opponent_strength(opponent_data)
            
            # Optimize lineup
            optimization = self.optimize_lineup(roster_data, opponent_data)
            
            # Identify advantages
            advantages = self.identify_matchup_advantages(roster_data, opponent_data)
            
            # Generate markdown report
            report = self._format_matchup_report(
                roster_data, 
                opponent_data, 
                opponent_analysis, 
                optimization, 
                advantages
            )
            
            # Save report
            filename = f"1-pregame_matchup_analysis.md"
            saved_file = save_markdown_report(report, filename)
            
            logger.info(f"Matchup report generated and saved: {saved_file}")
            return report
            
        except Exception as e:
            logger.error(f"Matchup report generation failed: {e}")
            return f"Error generating matchup report: {e}"
    
    def _format_matchup_report(self, roster: List[Dict], opponent: Dict, opponent_analysis: Dict, optimization: Dict, advantages: List[Dict]) -> str:
        """Format matchup analysis into markdown report"""
        report = f"""# 🥊 Matchup Analysis Report - Week {self.current_week}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Your Team:** {len(roster)} players  
**Opponent:** {opponent.get('team_name', 'Unknown')} ({len(opponent.get('roster', []))} players)

---

## 🎯 Opponent Analysis

### 📊 Team Overview
- **Team Name:** {opponent.get('team_name', 'Unknown')}
- **Overall Strength:** {opponent_analysis.get('overall_strength', 'Unknown')}
- **Risk Level:** {opponent_analysis.get('risk_assessment', 'Unknown')}
- **Key Players:** {len(opponent_analysis.get('key_players', []))}

### 🏆 Team Strengths
"""
        
        for strength in opponent_analysis.get('strengths', []):
            report += f"- {strength}\n"
        
        report += "\n### 🚨 Team Weaknesses\n"
        for weakness in opponent_analysis.get('weaknesses', []):
            report += f"- {weakness}\n"
        
        report += "\n### ⭐ Key Players to Watch\n"
        for player in opponent_analysis.get('key_players', [])[:5]:  # Top 5
            threat_emoji = "🔴" if player['threat_level'] == 'HIGH' else "🟡"
            report += f"- {threat_emoji} **{player['name']}** ({player['position']}) - {player['team']} - {player['ownership']:.1f}% owned\n"
        
        report += "\n---\n## 🚀 Lineup Optimization\n"
        
        # Position strategies
        for position, strategy in optimization.get('position_strategies', {}).items():
            report += f"\n### {position} Strategy\n"
            report += f"- **Approach:** {strategy.get('strategy', 'Unknown')}\n"
            report += f"- **Recommended Starters:** {len(strategy.get('recommended_starters', []))}\n"
            report += f"- **Bench Options:** {len(strategy.get('bench_recommendations', []))}\n"
            
            if strategy.get('reasoning'):
                report += "- **Reasoning:**\n"
                for reason in strategy['reasoning']:
                    report += f"  - {reason}\n"
        
        report += "\n### 💡 Overall Strategy\n"
        report += f"{optimization.get('overall_strategy', 'No strategy determined')}\n"
        
        report += "\n---\n## 🎯 Matchup Advantages\n"
        
        if advantages:
            for advantage in advantages:
                impact_emoji = "🔴" if advantage['impact'] == 'HIGH' else "🟡" if advantage['impact'] == 'MEDIUM' else "🟢"
                report += f"- {impact_emoji} **{advantage['type']}**: {advantage['description']}\n"
                report += f"  - Advantage: {advantage['advantage']}\n"
                report += f"  - Impact: {advantage['impact']}\n\n"
        else:
            report += "No significant matchup advantages identified.\n"
        
        report += "\n---\n## 🚨 Risk Mitigation\n"
        
        for mitigation in optimization.get('risk_mitigation', []):
            priority_emoji = "🔴" if mitigation['priority'] == 'HIGH' else "🟡" if mitigation['priority'] == 'MEDIUM' else "🟢"
            report += f"- {priority_emoji} **{mitigation['risk']}**: {mitigation['strategy']}\n"
            if isinstance(mitigation['players'], list):
                report += f"  - Affected: {', '.join(mitigation['players'])}\n"
            else:
                report += f"  - Affected: {mitigation['players']}\n"
            report += f"  - Priority: {mitigation['priority']}\n\n"
        
        report += "\n---\n## 📋 Recommended Starting Lineup\n"
        
        # Show recommended starters by position
        starters_by_position = {}
        for starter in optimization.get('recommended_starters', []):
            player = starter['player']
            position = player.get('position', 'Unknown')
            if position not in starters_by_position:
                starters_by_position[position] = []
            starters_by_position[position].append(starter)
        
        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            if position in starters_by_position:
                report += f"\n### {position}\n"
                for starter in starters_by_position[position]:
                    player = starter['player']
                    confidence = starter['confidence']
                    reason = starter['reason']
                    
                    confidence_emoji = "🟢" if confidence == 'HIGH' else "🟡"
                    report += f"- {confidence_emoji} **{player.get('name', 'Unknown')}** ({player.get('team', 'Unknown')}) - {reason}\n"
        
        report += f"""

---

*Report generated by Fantasy Football AI General Manager*  
*Week {self.current_week} Matchup Analysis*
"""
        
        return report
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete matchup analysis"""
        try:
            logger.info("Starting full matchup analysis")
            
            # Get current roster
            roster_data = self.api.get_current_roster()
            if not roster_data:
                logger.error("Failed to get roster data")
                return {'error': 'Failed to get roster data'}
            
            # Get opponent roster
            opponent_data = self.api.get_opponent_roster(self.current_week)
            if not opponent_data:
                logger.error("Failed to get opponent data")
                return {'error': 'Failed to get opponent data'}
            
            # Generate report
            report = self.generate_matchup_report(roster_data, opponent_data)
            
            # Return analysis summary
            analysis_summary = {
                'roster_count': len(roster_data),
                'opponent_name': opponent_data.get('team_name', 'Unknown'),
                'opponent_count': len(opponent_data.get('roster', [])),
                'report_file': report
            }
            
            logger.info("Full matchup analysis completed successfully")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Full matchup analysis failed: {e}")
            return {'error': str(e)}

def main():
    """Test the matchup analyzer"""
    try:
        print("🥊 Testing Matchup Analyzer...")
        
        analyzer = MatchupAnalyzer()
        results = analyzer.run_full_analysis()
        
        if 'error' not in results:
            print("✅ Matchup analysis completed successfully!")
            print(f"📊 Analyzed {results['roster_count']} roster players")
            print(f"🥊 Analyzed opponent: {results['opponent_name']} ({results['opponent_count']} players)")
            print(f"📄 Report generated and saved")
        else:
            print(f"❌ Matchup analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main test failed: {e}")

if __name__ == "__main__":
    main()
