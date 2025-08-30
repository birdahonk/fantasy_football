#!/usr/bin/env python3
"""
Free Agent Analysis Script
Evaluates available players and suggests roster improvements
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

class FreeAgentAnalyzer:
    """Analyzes free agents and suggests roster improvements"""
    
    def __init__(self):
        self.api = YahooFantasyAPI()
        self.current_week = get_current_week()
        
        # Position scoring tiers (rough estimates)
        self.position_tiers = {
            'QB': {'elite': 25, 'good': 20, 'average': 15, 'poor': 10},
            'RB': {'elite': 20, 'good': 15, 'average': 10, 'poor': 5},
            'WR': {'elite': 18, 'good': 14, 'average': 9, 'poor': 4},
            'TE': {'elite': 15, 'good': 12, 'average': 8, 'poor': 3},
            'K': {'elite': 12, 'good': 10, 'average': 8, 'poor': 5},
            'DEF': {'elite': 15, 'good': 12, 'average': 8, 'poor': 3}
        }
        
        # Position depth requirements
        self.depth_requirements = {
            'QB': {'min': 2, 'optimal': 2},
            'RB': {'min': 4, 'optimal': 5},
            'WR': {'min': 4, 'optimal': 6},
            'TE': {'min': 2, 'optimal': 3},
            'K': {'min': 2, 'optimal': 2},
            'DEF': {'min': 2, 'optimal': 2}
        }
    
    def analyze_free_agents(self, roster_data: List[Dict[str, Any]], free_agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze available free agents compared to current roster"""
        try:
            analysis = {
                'total_free_agents': len(free_agents),
                'position_analysis': {},
                'upgrade_opportunities': [],
                'depth_improvements': [],
                'backup_additions': [],
                'recommendations': []
            }
            
            # Analyze each position
            for position in self.position_tiers.keys():
                position_analysis = self._analyze_position(
                    position, 
                    roster_data, 
                    free_agents
                )
                analysis['position_analysis'][position] = position_analysis
            
            # Identify upgrade opportunities
            analysis['upgrade_opportunities'] = self._identify_upgrade_opportunities(
                roster_data, 
                free_agents
            )
            
            # Identify depth improvements
            analysis['depth_improvements'] = self._identify_depth_improvements(
                roster_data, 
                free_agents
            )
            
            # Identify backup additions
            analysis['backup_additions'] = self._identify_backup_additions(
                roster_data, 
                free_agents
            )
            
            # Generate overall recommendations
            analysis['recommendations'] = self._generate_overall_recommendations(analysis)
            
            logger.info(f"Free agent analysis completed: {len(analysis['upgrade_opportunities'])} upgrades, {len(analysis['depth_improvements'])} depth improvements")
            return analysis
            
        except Exception as e:
            logger.error(f"Free agent analysis failed: {e}")
            return {}
    
    def _analyze_position(self, position: str, roster: List[Dict], free_agents: List[Dict]) -> Dict[str, Any]:
        """Analyze a specific position for opportunities"""
        try:
            # Get current roster players at this position
            roster_players = [p for p in roster if p.get('position') == position]
            current_count = len(roster_players)
            
            # Get available free agents at this position
            available_players = [p for p in free_agents if p.get('position') == position]
            
            # Sort by ownership percentage (higher = more valuable)
            available_players.sort(key=lambda x: float(x.get('percent_owned', 0)), reverse=True)
            
            # Assess current depth
            depth_status = self._assess_position_depth(position, current_count)
            
            # Find top available players
            top_available = available_players[:5] if len(available_players) >= 5 else available_players
            
            # Calculate upgrade potential
            upgrade_potential = self._calculate_upgrade_potential(
                roster_players, 
                top_available
            )
            
            return {
                'current_count': current_count,
                'depth_status': depth_status,
                'available_count': len(available_players),
                'top_available': top_available,
                'upgrade_potential': upgrade_potential,
                'recommendation': self._get_position_recommendation(
                    position, 
                    current_count, 
                    depth_status, 
                    upgrade_potential
                )
            }
            
        except Exception as e:
            logger.error(f"Position analysis failed for {position}: {e}")
            return {}
    
    def _assess_position_depth(self, position: str, current_count: int) -> str:
        """Assess if current position depth is adequate"""
        requirements = self.depth_requirements.get(position, {'min': 1, 'optimal': 1})
        
        if current_count < requirements['min']:
            return 'CRITICAL'
        elif current_count < requirements['optimal']:
            return 'LOW'
        elif current_count == requirements['optimal']:
            return 'OPTIMAL'
        else:
            return 'EXCESS'
    
    def _calculate_upgrade_potential(self, roster_players: List[Dict], available_players: List[Dict]) -> Dict[str, Any]:
        """Calculate potential for upgrading current roster players"""
        try:
            if not available_players:
                return {'score': 0, 'description': 'No available players'}
            
            # Simple scoring based on ownership percentage
            # Higher ownership generally indicates better players
            best_available_ownership = float(available_players[0].get('percent_owned', 0))
            
            # Calculate average roster player "value" (simplified)
            roster_values = []
            for player in roster_players:
                # Use ownership as proxy for value, or default to 50%
                value = float(player.get('percent_owned', 50))
                roster_values.append(value)
            
            avg_roster_value = sum(roster_values) / len(roster_values) if roster_values else 0
            
            # Calculate upgrade potential
            upgrade_score = (best_available_ownership - avg_roster_value) / 100
            
            if upgrade_score > 0.2:
                description = 'HIGH - Significant upgrade potential'
            elif upgrade_score > 0.1:
                description = 'MEDIUM - Moderate upgrade potential'
            elif upgrade_score > 0:
                description = 'LOW - Minor upgrade potential'
            else:
                description = 'NONE - No upgrade potential'
            
            return {
                'score': upgrade_score,
                'description': description,
                'best_available_ownership': best_available_ownership,
                'avg_roster_value': avg_roster_value
            }
            
        except Exception as e:
            logger.error(f"Upgrade potential calculation failed: {e}")
            return {'score': 0, 'description': 'Error calculating upgrade potential'}
    
    def _get_position_recommendation(self, position: str, current_count: int, depth_status: str, upgrade_potential: Dict) -> str:
        """Get recommendation for a specific position"""
        if depth_status == 'CRITICAL':
            return f"🚨 ADD {position} - Critical depth need"
        elif depth_status == 'LOW':
            return f"⚠️ Consider adding {position} for depth"
        elif upgrade_potential['score'] > 0.1:
            return f"📈 Evaluate {position} upgrades"
        else:
            return f"✅ {position} depth is adequate"
    
    def _identify_upgrade_opportunities(self, roster: List[Dict], free_agents: List[Dict]) -> List[Dict[str, Any]]:
        """Identify specific players who could upgrade current roster"""
        try:
            opportunities = []
            
            # Group players by position
            roster_by_position = {}
            for player in roster:
                pos = player.get('position', 'Unknown')
                if pos not in roster_by_position:
                    roster_by_position[pos] = []
                roster_by_position[pos].append(player)
            
            # Find upgrade opportunities for each position
            for position, players in roster_by_position.items():
                available_at_position = [p for p in free_agents if p.get('position') == position]
                
                if not available_at_position:
                    continue
                
                # Sort available players by ownership (proxy for value)
                available_at_position.sort(key=lambda x: float(x.get('percent_owned', 0)), reverse=True)
                
                # Compare each available player to current roster
                for available_player in available_at_position[:3]:  # Top 3 available
                    for roster_player in players:
                        if self._is_upgrade(available_player, roster_player):
                            opportunities.append({
                                'position': position,
                                'add_player': available_player,
                                'drop_player': roster_player,
                                'upgrade_reason': self._get_upgrade_reason(available_player, roster_player),
                                'priority': self._calculate_upgrade_priority(available_player, roster_player)
                            })
            
            # Sort by priority
            opportunities.sort(key=lambda x: x['priority'], reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Upgrade opportunity identification failed: {e}")
            return []
    
    def _is_upgrade(self, available_player: Dict, roster_player: Dict) -> bool:
        """Determine if available player is an upgrade over roster player"""
        try:
            # Simple heuristic: higher ownership percentage = better player
            available_ownership = float(available_player.get('percent_owned', 0))
            roster_ownership = float(roster_player.get('percent_owned', 50))
            
            # Consider it an upgrade if ownership is significantly higher
            return available_ownership > (roster_ownership * 1.2)
            
        except Exception as e:
            logger.error(f"Upgrade comparison failed: {e}")
            return False
    
    def _get_upgrade_reason(self, available_player: Dict, roster_player: Dict) -> str:
        """Get reason why available player is an upgrade"""
        try:
            available_ownership = float(available_player.get('percent_owned', 0))
            roster_ownership = float(roster_player.get('percent_owned', 50))
            
            ownership_diff = available_ownership - roster_ownership
            
            if ownership_diff > 20:
                return f"Significantly higher ownership ({ownership_diff:.1f}% difference)"
            elif ownership_diff > 10:
                return f"Higher ownership ({ownership_diff:.1f}% difference)"
            else:
                return f"Moderately higher ownership ({ownership_diff:.1f}% difference)"
                
        except Exception as e:
            logger.error(f"Upgrade reason generation failed: {e}")
            return "Higher ownership percentage"
    
    def _calculate_upgrade_priority(self, available_player: Dict, roster_player: Dict) -> float:
        """Calculate priority score for upgrade opportunity"""
        try:
            # Higher ownership difference = higher priority
            available_ownership = float(available_player.get('percent_owned', 0))
            roster_ownership = float(roster_player.get('percent_owned', 50))
            
            ownership_diff = available_ownership - roster_ownership
            
            # Position priority multiplier
            position = available_player.get('position', 'Unknown')
            position_multiplier = self.position_tiers.get(position, {}).get('elite', 1) / 20
            
            return ownership_diff * position_multiplier
            
        except Exception as e:
            logger.error(f"Upgrade priority calculation failed: {e}")
            return 0.0
    
    def _identify_depth_improvements(self, roster: List[Dict], free_agents: List[Dict]) -> List[Dict[str, Any]]:
        """Identify opportunities to improve position depth"""
        try:
            improvements = []
            
            # Check each position for depth needs
            for position, requirements in self.depth_requirements.items():
                current_count = len([p for p in roster if p.get('position') == position])
                
                if current_count < requirements['optimal']:
                    # Find best available players at this position
                    available_at_position = [p for p in free_agents if p.get('position') == position]
                    available_at_position.sort(key=lambda x: float(x.get('percent_owned', 0)), reverse=True)
                    
                    if available_at_position:
                        improvements.append({
                            'position': position,
                            'current_depth': current_count,
                            'optimal_depth': requirements['optimal'],
                            'recommended_player': available_at_position[0],
                            'reason': f"Add {position} depth (currently {current_count}, optimal {requirements['optimal']})"
                        })
            
            return improvements
            
        except Exception as e:
            logger.error(f"Depth improvement identification failed: {e}")
            return []
    
    def _identify_backup_additions(self, roster: List[Dict], free_agents: List[Dict]) -> List[Dict[str, Any]]:
        """Identify backup players to add for critical positions"""
        try:
            backups = []
            
            # Check critical positions that need backups
            critical_positions = ['QB', 'TE', 'K', 'DEF']
            
            for position in critical_positions:
                current_count = len([p for p in roster if p.get('position') == position])
                
                if current_count < 2:  # Need backup
                    available_at_position = [p for p in free_agents if p.get('position') == position]
                    available_at_position.sort(key=lambda x: float(x.get('percent_owned', 0)), reverse=True)
                    
                    if available_at_position:
                        backups.append({
                            'position': position,
                            'current_count': current_count,
                            'backup_player': available_at_position[0],
                            'reason': f"Add backup {position} (currently {current_count})"
                        })
            
            return backups
            
        except Exception as e:
            logger.error(f"Backup addition identification failed: {e}")
            return []
    
    def _generate_overall_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on analysis"""
        recommendations = []
        
        # Critical needs
        critical_positions = []
        for position, pos_analysis in analysis.get('position_analysis', {}).items():
            if pos_analysis.get('depth_status') == 'CRITICAL':
                critical_positions.append(position)
        
        if critical_positions:
            recommendations.append(f"🚨 CRITICAL: Add players at {', '.join(critical_positions)} positions immediately")
        
        # Upgrade opportunities
        upgrade_count = len(analysis.get('upgrade_opportunities', []))
        if upgrade_count > 0:
            recommendations.append(f"📈 {upgrade_count} potential upgrade opportunities identified")
        
        # Depth improvements
        depth_count = len(analysis.get('depth_improvements', []))
        if depth_count > 0:
            recommendations.append(f"📊 {depth_count} depth improvement opportunities available")
        
        # Backup needs
        backup_count = len(analysis.get('backup_additions', []))
        if backup_count > 0:
            recommendations.append(f"🔄 {backup_count} backup players recommended")
        
        # Overall strategy
        if critical_positions:
            recommendations.append("🎯 PRIORITY: Address critical depth needs before considering upgrades")
        elif upgrade_count > 0:
            recommendations.append("🎯 PRIORITY: Focus on high-value upgrade opportunities")
        elif depth_count > 0:
            recommendations.append("🎯 PRIORITY: Improve position depth for better roster flexibility")
        else:
            recommendations.append("✅ Roster appears well-balanced - monitor for emerging opportunities")
        
        return recommendations
    
    def suggest_add_drop_transactions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest specific add/drop transactions"""
        try:
            transactions = []
            
            # Convert upgrade opportunities to transactions
            for opportunity in analysis.get('upgrade_opportunities', []):
                transactions.append({
                    'type': 'UPGRADE',
                    'action': 'ADD',
                    'player': opportunity['add_player'],
                    'reason': opportunity['upgrade_reason'],
                    'priority': opportunity['priority'],
                    'drop_candidate': opportunity['drop_player']
                })
            
            # Convert depth improvements to transactions
            for improvement in analysis.get('depth_improvements', []):
                transactions.append({
                    'type': 'DEPTH',
                    'action': 'ADD',
                    'player': improvement['recommended_player'],
                    'reason': improvement['reason'],
                    'priority': 0.5,  # Lower priority than upgrades
                    'drop_candidate': None
                })
            
            # Convert backup additions to transactions
            for backup in analysis.get('backup_additions', []):
                transactions.append({
                    'type': 'BACKUP',
                    'action': 'ADD',
                    'player': backup['backup_player'],
                    'reason': backup['reason'],
                    'priority': 0.3,  # Lower priority
                    'drop_candidate': None
                })
            
            # Sort by priority
            transactions.sort(key=lambda x: x['priority'], reverse=True)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Transaction suggestion generation failed: {e}")
            return []
    
    def generate_transaction_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive transaction recommendation report"""
        try:
            # Get transaction suggestions
            transactions = self.suggest_add_drop_transactions(analysis)
            
            # Generate markdown report
            report = self._format_transaction_report(analysis, transactions)
            
            # Save report
            filename = f"1-pregame_free_agent_analysis.md"
            saved_file = save_markdown_report(report, filename)
            
            logger.info(f"Transaction report generated and saved: {saved_file}")
            return report
            
        except Exception as e:
            logger.error(f"Transaction report generation failed: {e}")
            return f"Error generating transaction report: {e}"
    
    def _format_transaction_report(self, analysis: Dict[str, Any], transactions: List[Dict[str, Any]]) -> str:
        """Format transaction analysis into markdown report"""
        report = f"""# 🔍 Free Agent Analysis Report - Week {self.current_week}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Free Agents Analyzed:** {analysis.get('total_free_agents', 0)}

---

## 📊 Position Analysis Summary

"""
        
        # Position analysis table
        report += """
| Position | Current Depth | Status | Available | Top Player | Recommendation |
|----------|---------------|--------|-----------|------------|----------------|
"""
        
        for position, pos_analysis in analysis.get('position_analysis', {}).items():
            current = pos_analysis.get('current_count', 0)
            status = pos_analysis.get('depth_status', 'Unknown')
            available = pos_analysis.get('available_count', 0)
            top_player = pos_analysis.get('top_available', [{}])[0].get('name', 'None') if pos_analysis.get('top_available') else 'None'
            rec = pos_analysis.get('recommendation', 'Unknown')
            
            report += f"| {position} | {current} | {status} | {available} | {top_player} | {rec} |\n"
        
        report += "\n---\n## 🚀 Upgrade Opportunities\n"
        
        # Upgrade opportunities
        upgrade_opportunities = analysis.get('upgrade_opportunities', [])
        if upgrade_opportunities:
            report += """
| Priority | Position | Add Player | Drop Player | Reason |
|----------|----------|------------|-------------|---------|
"""
            
            for opp in upgrade_opportunities[:10]:  # Top 10
                priority = f"{opp['priority']:.1f}"
                position = opp['position']
                add_player = opp['add_player'].get('name', 'Unknown')
                drop_player = opp['drop_player'].get('name', 'Unknown')
                reason = opp['upgrade_reason']
                
                report += f"| {priority} | {position} | {add_player} | {drop_player} | {reason} |\n"
        else:
            report += "No significant upgrade opportunities identified.\n"
        
        report += "\n---\n## 📊 Depth Improvements\n"
        
        # Depth improvements
        depth_improvements = analysis.get('depth_improvements', [])
        if depth_improvements:
            for improvement in depth_improvements:
                position = improvement['position']
                current = improvement['current_depth']
                optimal = improvement['optimal_depth']
                player = improvement['recommended_player'].get('name', 'Unknown')
                reason = improvement['reason']
                
                report += f"- **{position}**: {reason} - Consider adding **{player}**\n"
        else:
            report += "All positions have adequate depth.\n"
        
        report += "\n---\n## 🔄 Backup Additions\n"
        
        # Backup additions
        backup_additions = analysis.get('backup_additions', [])
        if backup_additions:
            for backup in backup_additions:
                position = backup['position']
                current = backup['current_count']
                player = backup['backup_player'].get('name', 'Unknown')
                reason = backup['reason']
                
                report += f"- **{position}**: {reason} - Consider adding **{player}**\n"
        else:
            report += "All critical positions have adequate backups.\n"
        
        report += "\n---\n## 💡 Recommended Transactions\n"
        
        # Transaction recommendations
        if transactions:
            report += """
| Priority | Type | Action | Player | Position | Team | Reason |
|----------|------|--------|--------|----------|------|---------|
"""
            
            for txn in transactions[:15]:  # Top 15
                priority = f"{txn['priority']:.1f}"
                txn_type = txn['type']
                action = txn['action']
                player = txn['player'].get('name', 'Unknown')
                position = txn['player'].get('position', 'Unknown')
                team = txn['player'].get('team', 'Unknown')
                reason = txn['reason'][:50] + "..." if len(txn['reason']) > 50 else txn['reason']
                
                report += f"| {priority} | {txn_type} | {action} | {player} | {position} | {team} | {reason} |\n"
        else:
            report += "No specific transactions recommended at this time.\n"
        
        report += "\n---\n## 🎯 Strategic Recommendations\n"
        
        # Overall recommendations
        for rec in analysis.get('recommendations', []):
            report += f"- {rec}\n"
        
        report += f"""

---

*Report generated by Fantasy Football AI General Manager*  
*Week {self.current_week} Free Agent Analysis*
"""
        
        return report
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete free agent analysis"""
        try:
            logger.info("Starting full free agent analysis")
            
            # Get current roster
            roster_data = self.api.get_current_roster()
            if not roster_data:
                logger.error("Failed to get roster data")
                return {'error': 'Failed to get roster data'}
            
            # Get available free agents
            free_agents = self.api.get_available_players()
            if not free_agents:
                logger.error("Failed to get free agent data")
                return {'error': 'Failed to get free agent data'}
            
            # Analyze free agents
            analysis = self.analyze_free_agents(roster_data, free_agents)
            
            # Generate report
            report = self.generate_transaction_report(analysis)
            
            # Return analysis summary
            analysis_summary = {
                'roster_count': len(roster_data),
                'free_agent_count': len(free_agents),
                'report_file': report,
                'upgrade_opportunities': len(analysis.get('upgrade_opportunities', [])),
                'depth_improvements': len(analysis.get('depth_improvements', [])),
                'backup_additions': len(analysis.get('backup_additions', []))
            }
            
            logger.info("Full free agent analysis completed successfully")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Full free agent analysis failed: {e}")
            return {'error': str(e)}

def main():
    """Test the free agent analyzer"""
    try:
        print("🔍 Testing Free Agent Analyzer...")
        
        analyzer = FreeAgentAnalyzer()
        results = analyzer.run_full_analysis()
        
        if 'error' not in results:
            print("✅ Free agent analysis completed successfully!")
            print(f"📊 Analyzed {results['roster_count']} roster players")
            print(f"🔍 Analyzed {results['free_agent_count']} free agents")
            print(f"📄 Report generated and saved")
            
            # Show summary
            print(f"\n🚀 Opportunities Found:")
            print(f"   Upgrades: {results['upgrade_opportunities']}")
            print(f"   Depth improvements: {results['depth_improvements']}")
            print(f"   Backup additions: {results['backup_additions']}")
        else:
            print(f"❌ Free agent analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main test failed: {e}")

if __name__ == "__main__":
    main()
