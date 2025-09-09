#!/usr/bin/env python3
"""
Quant Post-Game Analysis AI Agent

This AI agent analyzes post-game performance data comparing projections vs. actual results
to provide strategic insights and recommendations for fantasy football management.

Analysis includes:
- Performance vs. projections analysis
- Roster comparison (my team vs. opponent)
- Over/under performer identification
- Strategic recommendations
- Waiver wire insights
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pytz

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "data_collection", "scripts", "shared"))

from file_utils import DataFileManager

def get_current_time_pacific():
    """Get current time in Pacific Time Zone."""
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific)

class QuantPostGameAnalysisAgent:
    """
    AI agent for post-game fantasy football analysis.
    
    This agent analyzes performance data to provide strategic insights
    and recommendations based on projection vs. actual performance.
    """
    
    def __init__(self):
        """Initialize the Quant analysis agent."""
        self.logger = logging.getLogger(__name__)
        self.file_manager = DataFileManager()
        
        # Track execution stats
        self.stats = {
            "start_time": datetime.now(),
            "data_loaded": False,
            "players_analyzed": 0,
            "insights_generated": 0,
            "recommendations_generated": 0,
            "errors": 0
        }
        
        self.logger.info("Quant Post-Game Analysis Agent initialized")
    
    def _find_latest_processed_data(self, week: int, season: int = 2025) -> Optional[Dict[str, Any]]:
        """
        Find the latest processed post-game data.
        
        Args:
            week: NFL week number
            season: NFL season year
            
        Returns:
            Processed data or None
        """
        try:
            analysis_dir = Path(f"data_collection/outputs/analysis/post_game/{season}/week_{week:02d}")
            
            if not analysis_dir.exists():
                self.logger.warning(f"No analysis directory found for Week {week}, Season {season}")
                return None
            
            # Find the latest processed data file
            pattern = f"*_wk{week:02d}_*_post_game_processed_raw.json"
            json_files = list(analysis_dir.glob(pattern))
            
            if not json_files:
                self.logger.warning(f"No processed data files found for Week {week}")
                return None
            
            # Sort by modification time (newest first)
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading processed data from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading processed data: {e}")
            self.stats["errors"] += 1
            return None
    
    def _analyze_roster_performance(self, roster_analysis: Dict[str, Any], roster_name: str) -> Dict[str, Any]:
        """
        Analyze performance for a specific roster.
        
        Args:
            roster_analysis: Roster analysis data
            roster_name: Name of the roster
            
        Returns:
            Analysis insights
        """
        insights = {
            "roster_name": roster_name,
            "total_players": roster_analysis.get("total_players", 0),
            "players_analyzed": roster_analysis.get("players_analyzed", 0),
            "total_projected_points": roster_analysis.get("total_projected_points", 0),
            "total_actual_points": roster_analysis.get("total_actual_points", 0),
            "performance_difference": roster_analysis.get("total_performance_difference", 0),
            "performance_percentage": 0,
            "over_performers_count": len(roster_analysis.get("over_performers", [])),
            "under_performers_count": len(roster_analysis.get("under_performers", [])),
            "even_performers_count": len(roster_analysis.get("even_performers", [])),
            "top_over_performers": [],
            "top_under_performers": [],
            "insights": [],
            "recommendations": []
        }
        
        # Calculate performance percentage
        if insights["total_projected_points"] > 0:
            insights["performance_percentage"] = (insights["total_actual_points"] / insights["total_projected_points"]) * 100
        
        # Get top over/under performers
        over_performers = roster_analysis.get("over_performers", [])
        under_performers = roster_analysis.get("under_performers", [])
        
        # Sort by performance difference
        over_performers_sorted = sorted(over_performers, key=lambda x: x.get("performance_difference", 0), reverse=True)
        under_performers_sorted = sorted(under_performers, key=lambda x: x.get("performance_difference", 0))
        
        insights["top_over_performers"] = over_performers_sorted[:3]
        insights["top_under_performers"] = under_performers_sorted[:3]
        
        # Generate insights
        if insights["performance_percentage"] > 110:
            insights["insights"].append(f"🔥 Exceptional week! {roster_name} exceeded projections by {insights['performance_percentage']:.1f}%")
        elif insights["performance_percentage"] > 105:
            insights["insights"].append(f"✅ Strong performance! {roster_name} beat projections by {insights['performance_percentage']:.1f}%")
        elif insights["performance_percentage"] < 90:
            insights["insights"].append(f"⚠️ Disappointing week! {roster_name} fell short of projections by {100 - insights['performance_percentage']:.1f}%")
        elif insights["performance_percentage"] < 95:
            insights["insights"].append(f"📉 Below expectations! {roster_name} underperformed projections by {100 - insights['performance_percentage']:.1f}%")
        else:
            insights["insights"].append(f"📊 Solid week! {roster_name} performed close to projections ({insights['performance_percentage']:.1f}%)")
        
        # Generate recommendations
        if insights["over_performers_count"] > insights["under_performers_count"]:
            insights["recommendations"].append("🎯 Consider starting your over-performers more consistently")
        elif insights["under_performers_count"] > insights["over_performers_count"]:
            insights["recommendations"].append("🔄 Consider benching or trading under-performers")
        
        if insights["top_over_performers"]:
            top_over = insights["top_over_performers"][0]
            insights["recommendations"].append(f"⭐ {top_over['player_name']} was your best performer (+{top_over['performance_difference']:.1f} points)")
        
        if insights["top_under_performers"]:
            top_under = insights["top_under_performers"][0]
            insights["recommendations"].append(f"⚠️ {top_under['player_name']} was your biggest disappointment ({top_under['performance_difference']:.1f} points)")
        
        return insights
    
    def _compare_rosters(self, my_roster_insights: Dict[str, Any], opponent_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare my roster performance vs. opponent roster performance.
        
        Args:
            my_roster_insights: My roster analysis insights
            opponent_insights: Opponent roster analysis insights
            
        Returns:
            Roster comparison analysis
        """
        comparison = {
            "my_total_points": my_roster_insights.get("total_actual_points", 0),
            "opponent_total_points": opponent_insights.get("total_actual_points", 0),
            "point_difference": 0,
            "my_performance_percentage": my_roster_insights.get("performance_percentage", 0),
            "opponent_performance_percentage": opponent_insights.get("performance_percentage", 0),
            "performance_gap": 0,
            "winner": "tie",
            "insights": [],
            "recommendations": []
        }
        
        # Calculate differences
        comparison["point_difference"] = comparison["my_total_points"] - comparison["opponent_total_points"]
        comparison["performance_gap"] = comparison["my_performance_percentage"] - comparison["opponent_performance_percentage"]
        
        # Determine winner
        if comparison["point_difference"] > 5:
            comparison["winner"] = "me"
        elif comparison["point_difference"] < -5:
            comparison["winner"] = "opponent"
        else:
            comparison["winner"] = "close"
        
        # Generate insights
        if comparison["winner"] == "me":
            comparison["insights"].append(f"🏆 Victory! You outscored your opponent by {comparison['point_difference']:.1f} points")
        elif comparison["winner"] == "opponent":
            comparison["insights"].append(f"😞 Defeat! Your opponent outscored you by {abs(comparison['point_difference']):.1f} points")
        else:
            comparison["insights"].append(f"🤝 Close matchup! Only {abs(comparison['point_difference']):.1f} points difference")
        
        if comparison["performance_gap"] > 5:
            comparison["insights"].append(f"📈 You significantly outperformed projections compared to your opponent")
        elif comparison["performance_gap"] < -5:
            comparison["insights"].append(f"📉 Your opponent significantly outperformed projections compared to you")
        
        # Generate recommendations
        if comparison["winner"] == "opponent" and comparison["performance_gap"] < -5:
            comparison["recommendations"].append("🔍 Analyze your opponent's strategy - they're consistently beating projections")
        elif comparison["winner"] == "me" and comparison["performance_gap"] > 5:
            comparison["recommendations"].append("🎯 Keep up the great work! Your strategy is working well")
        
        return comparison
    
    def _generate_waiver_wire_insights(self, available_players_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate waiver wire insights from available players analysis.
        
        Args:
            available_players_analysis: Available players analysis data
            
        Returns:
            Waiver wire insights
        """
        insights = {
            "total_available_analyzed": available_players_analysis.get("players_analyzed", 0),
            "top_available_over_performers": [],
            "top_available_under_performers": [],
            "waiver_recommendations": [],
            "sleeper_picks": []
        }
        
        over_performers = available_players_analysis.get("over_performers", [])
        under_performers = available_players_analysis.get("under_performers", [])
        
        # Sort by performance difference
        over_performers_sorted = sorted(over_performers, key=lambda x: x.get("performance_difference", 0), reverse=True)
        under_performers_sorted = sorted(under_performers, key=lambda x: x.get("performance_difference", 0))
        
        insights["top_available_over_performers"] = over_performers_sorted[:5]
        insights["top_available_under_performers"] = under_performers_sorted[:5]
        
        # Generate waiver recommendations
        for player in over_performers_sorted[:3]:
            if player.get("performance_difference", 0) > 5:
                insights["waiver_recommendations"].append(f"🔥 {player['player_name']} ({player['position']}) - +{player['performance_difference']:.1f} points over projection")
        
        # Generate sleeper picks
        for player in over_performers_sorted[3:6]:
            if player.get("performance_difference", 0) > 2:
                insights["sleeper_picks"].append(f"💎 {player['player_name']} ({player['position']}) - {player['performance_percentage']:.1f}% of projection")
        
        return insights
    
    def _generate_comprehensive_analysis(self, processed_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive markdown analysis report.
        
        Args:
            processed_data: Processed post-game analysis data
            
        Returns:
            Markdown analysis report
        """
        report = []
        report.append("# 🏈 Quant Post-Game Analysis Report")
        report.append("")
        
        # Header with metadata
        metadata = processed_data.get("analysis_metadata", {})
        summary = processed_data.get("summary", {})
        
        report.append(f"**Analysis Date:** {get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        report.append(f"**Week:** {metadata.get('week', 'Unknown')}")
        report.append(f"**Season:** {metadata.get('season', 'Unknown')}")
        report.append(f"**Total Players Analyzed:** {summary.get('total_players_analyzed', 0)}")
        report.append(f"**Total Projected Points:** {summary.get('total_projected_points', 0):.1f}")
        report.append(f"**Total Actual Points:** {summary.get('total_actual_points', 0):.1f}")
        report.append(f"**Overall Performance Difference:** {summary.get('overall_performance_difference', 0):.1f}")
        report.append("")
        
        # Roster analyses
        roster_analyses = processed_data.get("roster_analyses", {})
        
        # My roster analysis
        if "my_roster" in roster_analyses:
            my_roster_insights = self._analyze_roster_performance(roster_analyses["my_roster"], "My Roster")
            self.stats["insights_generated"] += 1
            
            report.append("## 🎯 My Roster Performance Analysis")
            report.append("")
            report.append(f"**Players Analyzed:** {my_roster_insights['players_analyzed']}")
            report.append(f"**Total Projected Points:** {my_roster_insights['total_projected_points']:.1f}")
            report.append(f"**Total Actual Points:** {my_roster_insights['total_actual_points']:.1f}")
            report.append(f"**Performance Percentage:** {my_roster_insights['performance_percentage']:.1f}%")
            report.append(f"**Performance Difference:** {my_roster_insights['performance_difference']:.1f} points")
            report.append("")
            
            # Over/under performers
            report.append("### 📊 Performance Breakdown")
            report.append(f"- **Over Performers:** {my_roster_insights['over_performers_count']}")
            report.append(f"- **Under Performers:** {my_roster_insights['under_performers_count']}")
            report.append(f"- **Even Performers:** {my_roster_insights['even_performers_count']}")
            report.append("")
            
            # Top performers
            if my_roster_insights["top_over_performers"]:
                report.append("### 🔥 Top Over Performers")
                for i, player in enumerate(my_roster_insights["top_over_performers"], 1):
                    report.append(f"{i}. **{player['player_name']}** ({player['position']}) - +{player['performance_difference']:.1f} points")
                report.append("")
            
            if my_roster_insights["top_under_performers"]:
                report.append("### ⚠️ Top Under Performers")
                for i, player in enumerate(my_roster_insights["top_under_performers"], 1):
                    report.append(f"{i}. **{player['player_name']}** ({player['position']}) - {player['performance_difference']:.1f} points")
                report.append("")
            
            # Insights and recommendations
            if my_roster_insights["insights"]:
                report.append("### 💡 Key Insights")
                for insight in my_roster_insights["insights"]:
                    report.append(f"- {insight}")
                report.append("")
            
            if my_roster_insights["recommendations"]:
                report.append("### 🎯 Recommendations")
                for recommendation in my_roster_insights["recommendations"]:
                    report.append(f"- {recommendation}")
                report.append("")
        
        # Opponent comparison
        if "opponent_roster" in roster_analyses:
            opponent_insights = self._analyze_roster_performance(roster_analyses["opponent_roster"], "Opponent Roster")
            
            if "my_roster" in roster_analyses:
                my_roster_insights = self._analyze_roster_performance(roster_analyses["my_roster"], "My Roster")
                comparison = self._compare_rosters(my_roster_insights, opponent_insights)
                
                report.append("## ⚔️ Roster Comparison")
                report.append("")
                report.append(f"**My Total Points:** {comparison['my_total_points']:.1f}")
                report.append(f"**Opponent Total Points:** {comparison['opponent_total_points']:.1f}")
                report.append(f"**Point Difference:** {comparison['point_difference']:.1f}")
                report.append(f"**Performance Gap:** {comparison['performance_gap']:.1f}%")
                report.append("")
                
                if comparison["insights"]:
                    report.append("### 📈 Comparison Insights")
                    for insight in comparison["insights"]:
                        report.append(f"- {insight}")
                    report.append("")
                
                if comparison["recommendations"]:
                    report.append("### 🎯 Strategic Recommendations")
                    for recommendation in comparison["recommendations"]:
                        report.append(f"- {recommendation}")
                    report.append("")
        
        # Waiver wire insights
        if "available_players" in roster_analyses:
            waiver_insights = self._generate_waiver_wire_insights(roster_analyses["available_players"])
            
            report.append("## 🔄 Waiver Wire Insights")
            report.append("")
            report.append(f"**Available Players Analyzed:** {waiver_insights['total_available_analyzed']}")
            report.append("")
            
            if waiver_insights["waiver_recommendations"]:
                report.append("### 🔥 Top Waiver Targets")
                for recommendation in waiver_insights["waiver_recommendations"]:
                    report.append(f"- {recommendation}")
                report.append("")
            
            if waiver_insights["sleeper_picks"]:
                report.append("### 💎 Sleeper Picks")
                for pick in waiver_insights["sleeper_picks"]:
                    report.append(f"- {pick}")
                report.append("")
        
        # Summary
        report.append("## 📋 Summary")
        report.append("")
        report.append("This analysis provides insights into your fantasy football performance compared to projections.")
        report.append("Use these insights to make informed decisions about your roster, waiver wire moves, and trade opportunities.")
        report.append("")
        report.append("**Remember:** Past performance doesn't guarantee future results, but patterns can inform strategy.")
        
        return "\n".join(report)
    
    def analyze_post_game_performance(self, week: int, season: int = 2025) -> Dict[str, Any]:
        """
        Analyze post-game performance and generate comprehensive report.
        
        Args:
            week: NFL week number
            season: NFL season year
            
        Returns:
            Analysis results
        """
        self.logger.info(f"Starting Quant post-game analysis for Week {week}, Season {season}")
        
        # Load processed data
        processed_data = self._find_latest_processed_data(week, season)
        if not processed_data:
            self.logger.error("No processed data found")
            return {"error": "No processed data found"}
        
        self.stats["data_loaded"] = True
        self.stats["players_analyzed"] = processed_data.get("summary", {}).get("total_players_analyzed", 0)
        
        # Generate comprehensive analysis
        analysis_report = self._generate_comprehensive_analysis(processed_data)
        
        # Save analysis report
        timestamp = self.file_manager.generate_timestamp()
        week_prefix = f"{timestamp}_wk{week:02d}_"
        
        # Create analysis output directory
        analysis_dir = Path("data_collection/outputs/analysis/post_game")
        week_dir = analysis_dir / str(season) / f"week_{week:02d}"
        week_dir.mkdir(parents=True, exist_ok=True)
        
        # Save markdown report
        clean_file = self.file_manager.save_clean_data(
            "analysis", "quant_post_game_analysis", analysis_report, week_prefix,
            custom_dir=str(week_dir)
        )
        
        # Save raw analysis data
        analysis_data = {
            "analysis_metadata": {
                "source": "Quant Post-Game Analysis Agent",
                "analysis_timestamp": get_current_time_pacific().isoformat(),
                "week": week,
                "season": season,
                "execution_stats": self.stats
            },
            "processed_data": processed_data,
            "analysis_report": analysis_report
        }
        
        raw_file = self.file_manager.save_raw_data(
            "analysis", "quant_post_game_analysis", analysis_data, week_prefix,
            custom_dir=str(week_dir)
        )
        
        output_files = {
            "clean": clean_file,
            "raw": raw_file
        }
        
        self.logger.info(f"Quant post-game analysis complete")
        self.logger.info(f"Players analyzed: {self.stats['players_analyzed']}")
        self.logger.info(f"Insights generated: {self.stats['insights_generated']}")
        self.logger.info(f"Output files: {output_files}")
        
        return {
            "success": True,
            "players_analyzed": self.stats['players_analyzed'],
            "insights_generated": self.stats['insights_generated'],
            "output_files": output_files,
            "week": week,
            "season": season
        }

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Quant Post-Game Analysis Agent')
    parser.add_argument('--week', type=int, default=1, help='NFL week number')
    parser.add_argument('--season', type=int, default=2025, help='NFL season year')
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        agent = QuantPostGameAnalysisAgent()
        result = agent.analyze_post_game_performance(args.week, args.season)
        
        if result.get("success"):
            print(f"✅ Quant post-game analysis successful!")
            print(f"   Week: {result['week']}")
            print(f"   Season: {result['season']}")
            print(f"   Players analyzed: {result['players_analyzed']}")
            print(f"   Insights generated: {result['insights_generated']}")
            print(f"   Output files: {result['output_files']}")
        else:
            print(f"❌ Quant post-game analysis failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Quant post-game analysis failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
