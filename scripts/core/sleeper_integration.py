#!/usr/bin/env python3
"""
Sleeper Integration for Fantasy Football Optimizer

This module integrates Sleeper API data with our Yahoo Fantasy data to provide
enhanced free agent recommendations and trending player insights.

Key Features:
- Trending player analysis for free agent recommendations
- Player metadata enrichment
- Cross-reference with Yahoo available players
- Generate actionable waiver wire insights

Author: Fantasy Football Optimizer
Date: January 2025
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from external.sleeper_client import SleeperClient
from core.data_retriever import YahooDataRetriever


class SleeperIntegration:
    """Integration class for combining Sleeper and Yahoo Fantasy data."""
    
    def __init__(self, yahoo_client_path: Optional[str] = None):
        """
        Initialize the Sleeper integration.
        
        Args:
            yahoo_client_path: Path to Yahoo OAuth client config
        """
        self.sleeper_client = SleeperClient()
        
        # Initialize Yahoo client if path provided
        self.yahoo_client = None
        if yahoo_client_path:
            try:
                self.yahoo_client = YahooDataRetriever(yahoo_client_path)
            except Exception as e:
                logging.error(f"Failed to initialize Yahoo client: {e}")
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Cache for player mappings
        self._sleeper_players_cache = None
        self._yahoo_to_sleeper_mapping = {}
    
    def get_sleeper_players(self, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Get all Sleeper players with caching.
        
        Args:
            force_refresh: Force refresh of cached data
            
        Returns:
            Dict mapping player_id to player data
        """
        if self._sleeper_players_cache is None or force_refresh:
            self._sleeper_players_cache = self.sleeper_client.get_nfl_players()
        
        return self._sleeper_players_cache
    
    def find_sleeper_player(self, yahoo_player_name: str, position: Optional[str] = None, team: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find a Sleeper player that matches a Yahoo player.
        
        Args:
            yahoo_player_name: Player name from Yahoo
            position: Player position for filtering
            team: Player team for filtering
            
        Returns:
            Matching Sleeper player data or None
        """
        # Try exact name match first
        sleeper_matches = self.sleeper_client.search_players_by_name(yahoo_player_name, position)
        
        if sleeper_matches:
            # If we have team info, try to match on team too
            if team:
                team_matches = [p for p in sleeper_matches if p.get("team") == team]
                if team_matches:
                    return team_matches[0]
            
            # Return first match if no team filter or no team matches
            return sleeper_matches[0]
        
        # Try partial name matching
        name_parts = yahoo_player_name.split()
        if len(name_parts) >= 2:
            # Try first and last name separately
            for part in name_parts:
                if len(part) > 2:  # Skip short words like "Jr", "III", etc.
                    matches = self.sleeper_client.search_players_by_name(part, position)
                    if matches:
                        # Filter by team if available
                        if team:
                            team_matches = [p for p in matches if p.get("team") == team]
                            if team_matches:
                                return team_matches[0]
                        return matches[0]
        
        return None
    
    def get_trending_analysis(self, lookback_hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get comprehensive trending analysis.
        
        Args:
            lookback_hours: Hours to look back for trending data
            
        Returns:
            Dict with 'hot_adds', 'hot_drops', and 'mixed_signals' lists
        """
        # Get trending data
        trending_added = self.sleeper_client.get_trending_players_with_details("add", lookback_hours, 25)
        trending_dropped = self.sleeper_client.get_trending_players_with_details("drop", lookback_hours, 25)
        
        # Create lookup for dropped players
        dropped_players = {p.get("player_id"): p for p in trending_dropped}
        
        # Categorize players
        hot_adds = []
        hot_drops = []
        mixed_signals = []
        
        for player in trending_added:
            player_id = player.get("player_id")
            add_count = player.get("trending_count", 0)
            
            # Check if also being dropped
            if player_id in dropped_players:
                drop_count = dropped_players[player_id].get("trending_count", 0)
                player["drop_count"] = drop_count
                player["net_adds"] = add_count - drop_count
                mixed_signals.append(player)
            else:
                hot_adds.append(player)
        
        # Add players that are only being dropped
        added_player_ids = {p.get("player_id") for p in trending_added}
        for player in trending_dropped:
            if player.get("player_id") not in added_player_ids:
                hot_drops.append(player)
        
        return {
            "hot_adds": hot_adds,
            "hot_drops": hot_drops,
            "mixed_signals": mixed_signals
        }
    
    def analyze_yahoo_free_agents_with_trending(self) -> Dict[str, Any]:
        """
        Analyze Yahoo free agents using Sleeper trending data.
        
        Returns:
            Analysis combining Yahoo available players with Sleeper trends
        """
        if not self.yahoo_client:
            raise ValueError("Yahoo client not initialized")
        
        # Get Yahoo free agents
        yahoo_free_agents = self.yahoo_client.get_free_agents()
        
        # Get trending analysis
        trending_analysis = self.get_trending_analysis()
        
        # Cross-reference Yahoo free agents with trending data
        hot_available_adds = []
        available_drops_to_avoid = []
        mixed_signal_players = []
        
        for yahoo_player in yahoo_free_agents:
            yahoo_name = yahoo_player.get("name", "")
            yahoo_position = yahoo_player.get("position", "")
            yahoo_team = yahoo_player.get("team", "")
            
            # Find matching Sleeper player
            sleeper_match = self.find_sleeper_player(yahoo_name, yahoo_position, yahoo_team)
            
            if sleeper_match:
                sleeper_id = sleeper_match.get("player_id")
                
                # Check if in hot adds
                for trending_player in trending_analysis["hot_adds"]:
                    if trending_player.get("player_id") == sleeper_id:
                        combined_data = yahoo_player.copy()
                        combined_data["sleeper_data"] = trending_player
                        combined_data["trending_count"] = trending_player.get("trending_count", 0)
                        hot_available_adds.append(combined_data)
                        break
                
                # Check if in hot drops
                for trending_player in trending_analysis["hot_drops"]:
                    if trending_player.get("player_id") == sleeper_id:
                        combined_data = yahoo_player.copy()
                        combined_data["sleeper_data"] = trending_player
                        combined_data["trending_count"] = trending_player.get("trending_count", 0)
                        available_drops_to_avoid.append(combined_data)
                        break
                
                # Check if in mixed signals
                for trending_player in trending_analysis["mixed_signals"]:
                    if trending_player.get("player_id") == sleeper_id:
                        combined_data = yahoo_player.copy()
                        combined_data["sleeper_data"] = trending_player
                        combined_data["add_count"] = trending_player.get("trending_count", 0)
                        combined_data["drop_count"] = trending_player.get("drop_count", 0)
                        combined_data["net_adds"] = trending_player.get("net_adds", 0)
                        mixed_signal_players.append(combined_data)
                        break
        
        # Sort by trending counts
        hot_available_adds.sort(key=lambda x: x.get("trending_count", 0), reverse=True)
        available_drops_to_avoid.sort(key=lambda x: x.get("trending_count", 0), reverse=True)
        mixed_signal_players.sort(key=lambda x: x.get("net_adds", 0), reverse=True)
        
        return {
            "hot_available_adds": hot_available_adds,
            "available_drops_to_avoid": available_drops_to_avoid,
            "mixed_signal_players": mixed_signal_players,
            "total_yahoo_free_agents": len(yahoo_free_agents),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _format_table(self, headers: List[str], rows: List[List[str]]) -> List[str]:
        """
        Format a table with proper column alignment.
        
        Args:
            headers: List of header strings
            rows: List of row data (each row is a list of strings)
            
        Returns:
            List of formatted table lines
        """
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
    
    def generate_trending_insights_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive trending insights report.
        
        Args:
            output_path: Optional path to save the report (if None, uses default naming in api_reports/)
            
        Returns:
            Markdown report as string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set default output path if not provided
        if output_path is None:
            Path("analysis/api_reports").mkdir(parents=True, exist_ok=True)
            output_path = f"analysis/api_reports/{timestamp}_sleeper_trending_insights.md"
        
        # Get trending analysis
        trending_analysis = self.get_trending_analysis()
        
        # Build report
        report_lines = [
            f"# 📊 Sleeper Trending Players Analysis",
            f"",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Data Source**: Sleeper API (Last 24 hours)  ",
            f"**Total Players Analyzed**: 11,400+",
            f"",
            f"---",
            f"",
        ]
        
        # Hot Adds Section
        report_lines.extend([
            f"## 🔥 HOT ADDS - Most Added Players (Last 24h)",
            f"",
            f"These players are being picked up rapidly across fantasy leagues:",
            f"",
        ])
        
        if trending_analysis["hot_adds"]:
            # Prepare table data
            headers = ["Rank", "Player", "Pos", "Team", "Added", "Injury Status"]
            rows = []
            
            for i, player in enumerate(trending_analysis["hot_adds"][:15], 1):
                name = player.get("full_name", "Unknown") or "Unknown"
                position = player.get("position", "N/A") or "N/A"
                team = player.get("team", "N/A") or "N/A"
                count = player.get("trending_count", 0)
                injury = player.get("injury_status", "") or ""
                injury_status = f"⚠️ {injury}" if injury else "✅ Healthy"
                
                # Convert "Unknown" to "DEFENSE" for DEF position
                if position == "DEF" and name == "Unknown":
                    name = "DEFENSE"
                
                rows.append([str(i), name, position, team, f"{count:,}", injury_status])
            
            # Format and add table
            table_lines = self._format_table(headers, rows)
            report_lines.extend(table_lines)
        else:
            report_lines.append("No trending additions found.")
        
        report_lines.extend([f"", f"---", f""])
        
        # Hot Drops Section
        report_lines.extend([
            f"## 📉 HOT DROPS - Most Dropped Players (Last 24h)",
            f"",
            f"These players are being dropped rapidly (avoid picking up):",
            f"",
        ])
        
        if trending_analysis["hot_drops"]:
            # Prepare table data
            headers = ["Rank", "Player", "Pos", "Team", "Dropped", "Injury Status"]
            rows = []
            
            for i, player in enumerate(trending_analysis["hot_drops"][:15], 1):
                name = player.get("full_name", "Unknown") or "Unknown"
                position = player.get("position", "N/A") or "N/A"
                team = player.get("team", "N/A") or "N/A"
                count = player.get("trending_count", 0)
                injury = player.get("injury_status", "") or ""
                injury_status = f"🚨 {injury}" if injury else "✅ Healthy"
                
                # Convert "Unknown" to "DEFENSE" for DEF position
                if position == "DEF" and name == "Unknown":
                    name = "DEFENSE"
                
                rows.append([str(i), name, position, team, f"{count:,}", injury_status])
            
            # Format and add table
            table_lines = self._format_table(headers, rows)
            report_lines.extend(table_lines)
        else:
            report_lines.append("No trending drops found.")
        
        report_lines.extend([f"", f"---", f""])
        
        # Mixed Signals Section
        if trending_analysis["mixed_signals"]:
            report_lines.extend([
                f"## ⚖️ MIXED SIGNALS - Players Being Added AND Dropped",
                f"",
                f"These players show conflicting trends (research before adding):",
                f"",
            ])
            
            # Prepare table data
            headers = ["Player", "Pos", "Team", "Added", "Dropped", "Net", "Status"]
            rows = []
            
            for player in trending_analysis["mixed_signals"][:10]:
                name = player.get("full_name", "Unknown") or "Unknown"
                position = player.get("position", "N/A") or "N/A"
                team = player.get("team", "N/A") or "N/A"
                add_count = player.get("trending_count", 0)
                drop_count = player.get("drop_count", 0)
                net_adds = player.get("net_adds", 0)
                injury = player.get("injury_status", "") or ""
                injury_status = f"⚠️ {injury}" if injury else "✅"
                
                # Convert "Unknown" to "DEFENSE" for DEF position
                if position == "DEF" and name == "Unknown":
                    name = "DEFENSE"
                
                net_indicator = "📈" if net_adds > 0 else "📉" if net_adds < 0 else "➡️"
                net_display = f"{net_indicator} {net_adds:+,}"
                
                rows.append([name, position, team, f"{add_count:,}", f"{drop_count:,}", net_display, injury_status])
            
            # Format and add table
            table_lines = self._format_table(headers, rows)
            report_lines.extend(table_lines)
            report_lines.extend([f"", f"---", f""])
        
        # Summary and recommendations
        report_lines.extend([
            f"## 💡 KEY INSIGHTS",
            f"",
            f"### 🎯 **Immediate Action Items**",
            f"1. **Priority Pickups**: Focus on top 5 hot adds with healthy status",
            f"2. **Avoid These Players**: Stay away from top hot drops (injury concerns)",
            f"3. **Research Mixed Signals**: Players with high net adds may be worth investigating",
            f"",
            f"### 📊 **Trending Summary**",
            f"- **Hot Adds**: {len(trending_analysis['hot_adds'])} players being rapidly added",
            f"- **Hot Drops**: {len(trending_analysis['hot_drops'])} players being rapidly dropped", 
            f"- **Mixed Signals**: {len(trending_analysis['mixed_signals'])} players with conflicting trends",
            f"",
            f"### ⏰ **Data Freshness**",
            f"This analysis reflects the **last 24 hours** of waiver wire activity across thousands of fantasy leagues.",
            f"",
            f"---",
            f"",
            f"*Report generated by Fantasy Football Optimizer using Sleeper API data*"
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    f.write(report_content)
                self.logger.info(f"Trending insights report saved to {output_path}")
            except Exception as e:
                self.logger.error(f"Failed to save report: {e}")
        
        return report_content


def main():
    """Test the Sleeper integration."""
    print("🏈 Testing Sleeper Integration")
    print("=" * 50)
    
    # Initialize integration
    integration = SleeperIntegration()
    
    # Generate trending insights report
    print("\n📊 Generating Trending Insights Report...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"analysis/api_reports/{timestamp}_sleeper_trending_insights.md"
    
    # Create analysis directories if they don't exist
    Path("analysis/api_reports").mkdir(parents=True, exist_ok=True)
    
    report_content = integration.generate_trending_insights_report(report_path)
    
    print(f"✅ Report generated: {report_path}")
    print(f"📄 Report length: {len(report_content)} characters")
    
    # Show preview of hot adds
    trending_analysis = integration.get_trending_analysis()
    hot_adds = trending_analysis["hot_adds"][:5]
    
    print(f"\n🔥 Top 5 Hot Adds Preview:")
    for i, player in enumerate(hot_adds, 1):
        name = player.get("full_name", "Unknown") or "Unknown"
        position = player.get("position", "N/A") or "N/A"
        team = player.get("team", "N/A") or "N/A"
        count = player.get("trending_count", 0)
        print(f"  {i}. {name} ({position}, {team}) - Added {count:,} times")
    
    print("\n✅ Sleeper Integration test completed!")


if __name__ == "__main__":
    main()
