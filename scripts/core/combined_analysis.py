#!/usr/bin/env python3
"""
Combined Yahoo + Sleeper Analysis

This module combines Yahoo Fantasy free agent data with Sleeper trending insights
to provide enhanced recommendations and analysis.

Key Features:
- Yahoo free agent data (top 50 players)
- Sleeper trending analysis integration
- Enhanced recommendations with trending insights
- Professional markdown report generation

Author: Fantasy Football Optimizer
Date: January 2025
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from external.sleeper_client import SleeperClient
from core.sleeper_integration import SleeperIntegration
from oauth.oauth2_client import YahooOAuth2Client
from core.data_retriever import YahooDataRetriever


class CombinedAnalyzer:
    """Combined analyzer for Yahoo + Sleeper data."""
    
    def __init__(self, yahoo_client_path: str = "scripts/config/yahoo_oauth2_tokens.json"):
        """
        Initialize the combined analyzer.
        
        Args:
            yahoo_client_path: Path to Yahoo OAuth client config (for Sleeper integration)
        """
        # Initialize clients
        self.sleeper_client = SleeperClient()
        self.sleeper_integration = SleeperIntegration(yahoo_client_path)
        
        # Initialize Yahoo client (no path needed for constructor)
        try:
            self.yahoo_client = YahooDataRetriever()
        except Exception as e:
            logging.error(f"Failed to initialize Yahoo client: {e}")
            self.yahoo_client = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Cache for performance
        self._sleeper_players_cache = None
        self._trending_cache = None
    
    def get_enhanced_free_agents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get Yahoo free agents enhanced with Sleeper trending data.
        
        Args:
            limit: Number of free agents to analyze
            
        Returns:
            List of enhanced free agent data
        """
        if not self.yahoo_client:
            raise ValueError("Yahoo client not initialized")
        
        # Get Yahoo free agents (method handles pagination automatically)
        yahoo_free_agents = self.yahoo_client.get_free_agents(count=limit)
        if not yahoo_free_agents:
            self.logger.warning("No Yahoo free agents retrieved")
            return []
        
        top_free_agents = yahoo_free_agents
        self.logger.info(f"Analyzing top {len(top_free_agents)} Yahoo free agents")
        
        # Get Sleeper trending data
        trending_analysis = self.sleeper_integration.get_trending_analysis()
        
        # Get all Sleeper players for matching
        sleeper_players = self.sleeper_client.get_nfl_players()
        
        # Enhance each free agent with Sleeper data
        enhanced_agents = []
        
        for yahoo_player in top_free_agents:
            enhanced_player = self._enhance_player_with_sleeper_data(
                yahoo_player, sleeper_players, trending_analysis
            )
            enhanced_agents.append(enhanced_player)
        
        return enhanced_agents
    
    def _enhance_player_with_sleeper_data(
        self, 
        yahoo_player: Dict[str, Any], 
        sleeper_players: Dict[str, Dict[str, Any]], 
        trending_analysis: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Enhance a Yahoo player with Sleeper data.
        
        Args:
            yahoo_player: Yahoo player data
            sleeper_players: All Sleeper players data
            trending_analysis: Sleeper trending analysis
            
        Returns:
            Enhanced player data
        """
        enhanced = yahoo_player.copy()
        
        # Find matching Sleeper player
        sleeper_match = self._find_matching_sleeper_player(
            yahoo_player, sleeper_players
        )
        
        if sleeper_match:
            # Add Sleeper metadata
            enhanced["sleeper_data"] = {
                "player_id": sleeper_match.get("player_id"),
                "age": sleeper_match.get("age"),
                "height": sleeper_match.get("height"),
                "weight": sleeper_match.get("weight"),
                "years_exp": sleeper_match.get("years_exp"),
                "injury_status": sleeper_match.get("injury_status"),
                "injury_body_part": sleeper_match.get("injury_body_part"),
                "injury_notes": sleeper_match.get("injury_notes")
            }
            
            # Check trending status
            trending_info = self._get_player_trending_info(
                sleeper_match.get("player_id"), trending_analysis
            )
            enhanced["trending"] = trending_info
        else:
            enhanced["sleeper_data"] = None
            enhanced["trending"] = {"status": "not_found", "recommendation": "Unknown"}
        
        # Generate recommendation
        enhanced["recommendation"] = self._generate_recommendation(enhanced)
        
        return enhanced
    
    def _find_matching_sleeper_player(
        self, 
        yahoo_player: Dict[str, Any], 
        sleeper_players: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find matching Sleeper player for Yahoo player."""
        yahoo_name = yahoo_player.get("name", "").strip()
        yahoo_position = yahoo_player.get("position", "")
        yahoo_team = yahoo_player.get("team", "")
        
        if not yahoo_name:
            return None
        
        # Try exact name match first
        for sleeper_player in sleeper_players.values():
            sleeper_full_name = sleeper_player.get("full_name", "")
            if sleeper_full_name and sleeper_full_name.lower() == yahoo_name.lower():
                # Verify position and team if available
                if yahoo_position and sleeper_player.get("position") != yahoo_position:
                    continue
                if yahoo_team and sleeper_player.get("team") != yahoo_team:
                    continue
                return sleeper_player
        
        # Try partial name matching
        name_parts = yahoo_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0].lower()
            last_name = name_parts[-1].lower()
            
            for sleeper_player in sleeper_players.values():
                sleeper_first = (sleeper_player.get("first_name") or "").lower()
                sleeper_last = (sleeper_player.get("last_name") or "").lower()
                
                if sleeper_first == first_name and sleeper_last == last_name:
                    # Verify position if available
                    if yahoo_position and sleeper_player.get("position") != yahoo_position:
                        continue
                    return sleeper_player
        
        return None
    
    def _get_player_trending_info(
        self, 
        player_id: str, 
        trending_analysis: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get trending information for a player."""
        if not player_id:
            return {"status": "no_id", "recommendation": "Unknown"}
        
        # Check hot adds
        for player in trending_analysis.get("hot_adds", []):
            if player.get("player_id") == player_id:
                return {
                    "status": "hot_add",
                    "count": player.get("trending_count", 0),
                    "recommendation": "🔥 HIGH PRIORITY - Trending up rapidly!"
                }
        
        # Check hot drops
        for player in trending_analysis.get("hot_drops", []):
            if player.get("player_id") == player_id:
                return {
                    "status": "hot_drop",
                    "count": player.get("trending_count", 0),
                    "recommendation": "🚨 AVOID - Being dropped rapidly"
                }
        
        # Check mixed signals
        for player in trending_analysis.get("mixed_signals", []):
            if player.get("player_id") == player_id:
                net_adds = player.get("net_adds", 0)
                if net_adds > 0:
                    return {
                        "status": "mixed_positive",
                        "net_adds": net_adds,
                        "recommendation": "⚖️ RESEARCH - Mixed signals but net positive"
                    }
                else:
                    return {
                        "status": "mixed_negative", 
                        "net_adds": net_adds,
                        "recommendation": "⚖️ CAUTION - Mixed signals, net negative"
                    }
        
        return {"status": "stable", "recommendation": "📊 STABLE - No significant trending activity"}
    
    def _generate_recommendation(self, enhanced_player: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall recommendation for a player."""
        trending = enhanced_player.get("trending", {})
        sleeper_data = enhanced_player.get("sleeper_data", {})
        yahoo_rank = enhanced_player.get("overall_rank", 999)
        
        # Base priority on Yahoo rank
        if yahoo_rank <= 10:
            base_priority = "HIGH"
        elif yahoo_rank <= 25:
            base_priority = "MEDIUM"
        else:
            base_priority = "LOW"
        
        # Adjust based on trending
        trending_status = trending.get("status", "stable")
        if trending_status == "hot_add":
            priority = "URGENT"
            reason = f"Top {yahoo_rank} player trending up rapidly"
        elif trending_status == "hot_drop":
            priority = "AVOID"
            reason = "Being dropped rapidly - likely injury or performance issues"
        elif trending_status == "mixed_positive":
            priority = "HIGH" if base_priority in ["HIGH", "MEDIUM"] else "MEDIUM"
            reason = f"Top {yahoo_rank} player with net positive trending"
        elif trending_status == "mixed_negative":
            priority = "LOW"
            reason = "Mixed signals with net negative trending"
        else:
            priority = base_priority
            reason = f"Top {yahoo_rank} available player"
        
        # Check injury status
        injury_status = None
        if sleeper_data:
            injury_status = sleeper_data.get("injury_status")
            if injury_status:
                if priority not in ["AVOID"]:
                    priority = "CAUTION"
                reason += f" (Injury: {injury_status})"
        
        return {
            "priority": priority,
            "reason": reason,
            "trending_recommendation": trending.get("recommendation", "Unknown")
        }
    
    def _format_table(self, headers: List[str], rows: List[List[str]]) -> List[str]:
        """Format a table with proper column alignment."""
        if not rows:
            return []
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Format header
        header_line = "| " + " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers)) + " |"
        separator_line = "|" + "|".join("-" * (col_widths[i] + 2) for i in range(len(headers))) + "|"
        
        # Format rows
        formatted_rows = []
        for row in rows:
            formatted_row = "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
            formatted_rows.append(formatted_row)
        
        return [header_line, separator_line] + formatted_rows
    
    def generate_combined_report(self, limit: int = 50, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive combined analysis report.
        
        Args:
            limit: Number of free agents to analyze
            output_path: Optional path to save the report
            
        Returns:
            Markdown report as string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set default output path if not provided
        if output_path is None:
            Path("analysis/combined_reports").mkdir(parents=True, exist_ok=True)
            output_path = f"analysis/combined_reports/{timestamp}_yahoo_sleeper_free_agents.md"
        
        # Get enhanced free agents
        enhanced_agents = self.get_enhanced_free_agents(limit)
        
        if not enhanced_agents:
            return "No free agents data available for analysis."
        
        # Categorize players by recommendation priority
        urgent_picks = [p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "URGENT"]
        high_priority = [p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "HIGH"]
        medium_priority = [p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "MEDIUM"]
        caution_players = [p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "CAUTION"]
        avoid_players = [p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "AVOID"]
        
        # Build report
        report_lines = [
            f"# 🎯 Yahoo + Sleeper Free Agent Analysis",
            f"",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Data Sources**: Yahoo Fantasy Sports API + Sleeper NFL API  ",
            f"**Analysis Scope**: Top {limit} Yahoo free agents enhanced with Sleeper trending data",
            f"",
            f"---",
            f"",
            f"## 📊 EXECUTIVE SUMMARY",
            f"",
            f"- **🔥 URGENT PICKUPS**: {len(urgent_picks)} players trending up rapidly",
            f"- **⭐ HIGH PRIORITY**: {len(high_priority)} top-ranked available players",
            f"- **📈 MEDIUM PRIORITY**: {len(medium_priority)} solid depth options",
            f"- **⚠️ CAUTION**: {len(caution_players)} players with injury concerns",
            f"- **🚨 AVOID**: {len(avoid_players)} players being dropped rapidly",
            f"",
            f"---",
            f"",
        ]
        
        # Urgent Pickups Section
        if urgent_picks:
            report_lines.extend([
                f"## 🔥 URGENT PICKUPS - Act Fast!",
                f"",
                f"These players are trending up rapidly and should be your top waiver wire targets:",
                f"",
            ])
            
            headers = ["Rank", "Player", "Pos", "Team", "Trending", "Injury", "Reason"]
            rows = []
            
            for player in urgent_picks:
                rank = player.get("overall_rank", "N/A")
                name = player.get("name", "Unknown")
                position = player.get("position", "N/A")
                team = player.get("team", "N/A")
                trending_count = player.get("trending", {}).get("count", 0)
                injury = player.get("sleeper_data", {}).get("injury_status") or "Healthy"
                reason = player.get("recommendation", {}).get("reason", "")
                
                trending_display = f"🔥 +{trending_count:,}" if trending_count else "🔥 Hot"
                injury_display = f"⚠️ {injury}" if injury != "Healthy" else "✅"
                
                rows.append([str(rank), name, position, team, trending_display, injury_display, reason])
            
            table_lines = self._format_table(headers, rows)
            report_lines.extend(table_lines)
            report_lines.extend([f"", f"---", f""])
        
        # High Priority Section
        if high_priority:
            report_lines.extend([
                f"## ⭐ HIGH PRIORITY TARGETS",
                f"",
                f"Top-ranked players available with positive or stable trending:",
                f"",
            ])
            
            headers = ["Rank", "Player", "Pos", "Team", "Age", "Exp", "Status", "Recommendation"]
            rows = []
            
            for player in high_priority[:10]:  # Limit to top 10
                rank = player.get("overall_rank", "N/A")
                name = player.get("name", "Unknown")
                position = player.get("position", "N/A")
                team = player.get("team", "N/A")
                age = player.get("sleeper_data", {}).get("age") or "N/A"
                exp = player.get("sleeper_data", {}).get("years_exp") or "N/A"
                trending_rec = player.get("trending", {}).get("recommendation", "")
                reason = player.get("recommendation", {}).get("reason", "")
                
                # Shorten trending recommendation for table
                status_short = trending_rec.split(" - ")[0] if " - " in trending_rec else trending_rec
                
                rows.append([str(rank), name, position, team, str(age), str(exp), status_short, reason])
            
            table_lines = self._format_table(headers, rows)
            report_lines.extend(table_lines)
            report_lines.extend([f"", f"---", f""])
        
        # Avoid Players Section
        if avoid_players:
            report_lines.extend([
                f"## 🚨 PLAYERS TO AVOID",
                f"",
                f"These players are being dropped rapidly - avoid picking them up:",
                f"",
            ])
            
            headers = ["Rank", "Player", "Pos", "Team", "Dropped", "Reason"]
            rows = []
            
            for player in avoid_players:
                rank = player.get("overall_rank", "N/A")
                name = player.get("name", "Unknown")
                position = player.get("position", "N/A")
                team = player.get("team", "N/A")
                drop_count = player.get("trending", {}).get("count", 0)
                reason = player.get("recommendation", {}).get("reason", "")
                
                drop_display = f"📉 -{drop_count:,}" if drop_count else "📉 Dropping"
                
                rows.append([str(rank), name, position, team, drop_display, reason])
            
            table_lines = self._format_table(headers, rows)
            report_lines.extend(table_lines)
            report_lines.extend([f"", f"---", f""])
        
        # Summary and Action Items
        report_lines.extend([
            f"## 💡 ACTION ITEMS",
            f"",
            f"### 🎯 **Immediate Waiver Claims**",
        ])
        
        if urgent_picks:
            for i, player in enumerate(urgent_picks[:3], 1):
                name = player.get("name", "Unknown")
                position = player.get("position", "N/A")
                reason = player.get("recommendation", {}).get("reason", "")
                report_lines.append(f"{i}. **{name}** ({position}) - {reason}")
        else:
            report_lines.append("No urgent pickups identified at this time.")
        
        report_lines.extend([
            f"",
            f"### 📊 **Key Insights**",
            f"- **Trending Data**: Based on {len(enhanced_agents)} analyzed players with Sleeper trending data",
            f"- **Match Rate**: {len([p for p in enhanced_agents if p.get('sleeper_data')])}/{len(enhanced_agents)} players matched with Sleeper database",
            f"- **Data Freshness**: Trending data reflects last 24 hours of waiver activity",
            f"",
            f"### ⚠️ **Important Notes**",
            f"- Injury status from Sleeper API (may be more current than Yahoo)",
            f"- Trending data shows what thousands of fantasy managers are doing",
            f"- Always verify player status before making waiver claims",
            f"",
            f"---",
            f"",
            f"*Report generated by Fantasy Football Optimizer combining Yahoo Fantasy Sports API + Sleeper NFL API*"
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    f.write(report_content)
                self.logger.info(f"Combined analysis report saved to {output_path}")
            except Exception as e:
                self.logger.error(f"Failed to save report: {e}")
        
        return report_content


def main():
    """Test the combined analyzer."""
    print("🎯 Testing Combined Yahoo + Sleeper Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = CombinedAnalyzer()
    
    # Generate combined report
    print("\n📊 Generating Combined Free Agent Analysis...")
    
    try:
        report_content = analyzer.generate_combined_report(limit=50)
        
        print("✅ Analysis completed successfully!")
        print(f"📄 Report length: {len(report_content)} characters")
        
        # Show quick summary
        enhanced_agents = analyzer.get_enhanced_free_agents(50)
        urgent = len([p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "URGENT"])
        high = len([p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "HIGH"])
        avoid = len([p for p in enhanced_agents if p.get("recommendation", {}).get("priority") == "AVOID"])
        
        print(f"\n🔥 Quick Summary:")
        print(f"  • URGENT pickups: {urgent}")
        print(f"  • HIGH priority: {high}")
        print(f"  • AVOID players: {avoid}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Combined analysis test completed!")


if __name__ == "__main__":
    main()
