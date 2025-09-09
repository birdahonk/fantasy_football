#!/usr/bin/env python3
"""
Post-Game Analysis Data Processor

This script processes historical projection data and actual game stats to prepare
data for post-game analysis by the Quant AI agent.

Data Sources:
- Tank01 projections archive (previous week)
- Player game stats (my roster, opponent roster, available players)
- Yahoo matchup data

Purpose: Prepare structured data for AI analysis comparing projections vs. actual performance.
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

class PostGameAnalysisDataProcessor:
    """
    Process historical data for post-game analysis.
    
    This script combines projection data with actual game stats to prepare
    comprehensive data for AI analysis.
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = logging.getLogger(__name__)
        self.file_manager = DataFileManager()
        
        # Track execution stats
        self.stats = {
            "start_time": datetime.now(),
            "projections_loaded": 0,
            "my_roster_stats_loaded": 0,
            "opponent_stats_loaded": 0,
            "available_stats_loaded": 0,
            "matchup_data_loaded": 0,
            "players_analyzed": 0,
            "errors": 0
        }
        
        self.logger.info("Post-Game Analysis Data Processor initialized")
    
    def _find_latest_projections_archive(self, week: int, season: int = 2025) -> Optional[Dict[str, Any]]:
        """
        Find the latest projections archive for a specific week.
        
        Args:
            week: NFL week number
            season: NFL season year
            
        Returns:
            Projections archive data or None
        """
        try:
            archive_dir = Path(f"data_collection/outputs/tank01/projections_archive/{season}/week_{week:02d}")
            
            if not archive_dir.exists():
                self.logger.warning(f"No projections archive found for Week {week}, Season {season}")
                return None
            
            # Find the latest raw JSON file
            json_files = list(archive_dir.glob("*_projections_archive_raw.json"))
            if not json_files:
                self.logger.warning(f"No projection files found in {archive_dir}")
                return None
            
            # Sort by modification time (newest first)
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading projections from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading projections archive: {e}")
            self.stats["errors"] += 1
            return None
    
    def _find_latest_stats_data(self, data_type: str, week: int) -> Optional[Dict[str, Any]]:
        """
        Find the latest stats data for a specific type and week.
        
        Args:
            data_type: Type of stats data ("my_roster_stats", "opponent_roster_stats", "available_players_stats")
            week: NFL week number
            
        Returns:
            Stats data or None
        """
        try:
            stats_dir = Path(f"data_collection/outputs/tank01/{data_type}")
            
            if not stats_dir.exists():
                self.logger.warning(f"No {data_type} directory found")
                return None
            
            # Find files with the specified week
            pattern = f"*_wk{week:02d}_*_raw.json"
            json_files = list(stats_dir.glob(f"**/{pattern}"))
            
            if not json_files:
                self.logger.warning(f"No {data_type} files found for Week {week}")
                return None
            
            # Sort by modification time (newest first)
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading {data_type} from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading {data_type}: {e}")
            self.stats["errors"] += 1
            return None
    
    def _find_latest_matchup_data(self, week: int) -> Optional[Dict[str, Any]]:
        """
        Find the latest matchup data for a specific week.
        
        Args:
            week: NFL week number
            
        Returns:
            Matchup data or None
        """
        try:
            matchup_dir = Path("data_collection/outputs/yahoo/team_matchups")
            
            if not matchup_dir.exists():
                self.logger.warning("No matchup directory found")
                return None
            
            # Find files with the specified week
            pattern = f"*_wk{week:02d}_*_raw.json"
            json_files = list(matchup_dir.glob(f"**/{pattern}"))
            
            if not json_files:
                self.logger.warning(f"No matchup files found for Week {week}")
                return None
            
            # Sort by modification time (newest first)
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Loading matchup data from: {latest_file}")
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading matchup data: {e}")
            self.stats["errors"] += 1
            return None
    
    def _match_projection_to_stats(self, projection: Dict[str, Any], stats_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Match a projection to corresponding stats data.
        
        Args:
            projection: Projection data for a player
            stats_data: List of stats data for players
            
        Returns:
            Matched stats data or None
        """
        projection_player_id = projection.get('player_id')
        projection_name = projection.get('player_name', '')
        
        # Try to match by Tank01 player ID first
        for stats_player in stats_data:
            tank01_data = stats_player.get('tank01_data', {})
            if tank01_data.get('playerID') == projection_player_id:
                return stats_player
        
        # Try to match by name as fallback
        for stats_player in stats_player in stats_data:
            yahoo_player = stats_player.get('yahoo_player', {})
            yahoo_name = yahoo_player.get('name', {}).get('full', '')
            
            if yahoo_name and projection_name and yahoo_name.lower() == projection_name.lower():
                return stats_player
        
        return None
    
    def _calculate_performance_metrics(self, projection: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate performance metrics comparing projection vs. actual stats.
        
        Args:
            projection: Projection data for a player
            stats: Actual stats data for a player
            
        Returns:
            Performance metrics
        """
        metrics = {
            "projected_fantasy_points": 0,
            "actual_fantasy_points": 0,
            "performance_difference": 0,
            "performance_percentage": 0,
            "over_under": "even"
        }
        
        try:
            # Get projected fantasy points
            projected_fp = projection.get('fantasyPoints', 0)
            if isinstance(projected_fp, (int, float)):
                metrics["projected_fantasy_points"] = float(projected_fp)
            
            # Get actual fantasy points from stats
            game_stats = stats.get('game_stats', {})
            season_totals = game_stats.get('season_totals', {})
            actual_fp = season_totals.get('fantasy_points', 0)
            if isinstance(actual_fp, (int, float)):
                metrics["actual_fantasy_points"] = float(actual_fp)
            
            # Calculate differences
            metrics["performance_difference"] = metrics["actual_fantasy_points"] - metrics["projected_fantasy_points"]
            
            if metrics["projected_fantasy_points"] > 0:
                metrics["performance_percentage"] = (metrics["actual_fantasy_points"] / metrics["projected_fantasy_points"]) * 100
            
            # Determine over/under
            if metrics["performance_difference"] > 0.5:
                metrics["over_under"] = "over"
            elif metrics["performance_difference"] < -0.5:
                metrics["over_under"] = "under"
            else:
                metrics["over_under"] = "even"
                
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            self.stats["errors"] += 1
        
        return metrics
    
    def _process_roster_analysis(self, projections: Dict[str, Any], stats_data: List[Dict[str, Any]], roster_type: str) -> Dict[str, Any]:
        """
        Process analysis for a specific roster type.
        
        Args:
            projections: Projections data
            stats_data: Stats data for the roster
            roster_type: Type of roster ("my_roster", "opponent_roster", "available_players")
            
        Returns:
            Processed roster analysis
        """
        roster_analysis = {
            "roster_type": roster_type,
            "total_players": len(stats_data),
            "players_analyzed": 0,
            "total_projected_points": 0,
            "total_actual_points": 0,
            "total_performance_difference": 0,
            "over_performers": [],
            "under_performers": [],
            "even_performers": [],
            "player_analysis": []
        }
        
        projections_dict = projections.get('projections', {})
        
        for stats_player in stats_data:
            try:
                # Try to find matching projection
                tank01_data = stats_player.get('tank01_data', {})
                player_id = tank01_data.get('playerID')
                
                if not player_id or player_id not in projections_dict:
                    continue
                
                projection = projections_dict[player_id]
                
                # Calculate performance metrics
                metrics = self._calculate_performance_metrics(projection, stats_player)
                
                # Update totals
                roster_analysis["total_projected_points"] += metrics["projected_fantasy_points"]
                roster_analysis["total_actual_points"] += metrics["actual_fantasy_points"]
                roster_analysis["total_performance_difference"] += metrics["performance_difference"]
                roster_analysis["players_analyzed"] += 1
                
                # Categorize performance
                player_analysis = {
                    "player_name": projection.get('player_name', 'Unknown'),
                    "position": projection.get('position', 'Unknown'),
                    "team": projection.get('team', 'Unknown'),
                    "projected_fantasy_points": metrics["projected_fantasy_points"],
                    "actual_fantasy_points": metrics["actual_fantasy_points"],
                    "performance_difference": metrics["performance_difference"],
                    "performance_percentage": metrics["performance_percentage"],
                    "over_under": metrics["over_under"]
                }
                
                roster_analysis["player_analysis"].append(player_analysis)
                
                # Categorize by performance
                if metrics["over_under"] == "over":
                    roster_analysis["over_performers"].append(player_analysis)
                elif metrics["over_under"] == "under":
                    roster_analysis["under_performers"].append(player_analysis)
                else:
                    roster_analysis["even_performers"].append(player_analysis)
                
                self.stats["players_analyzed"] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing player analysis: {e}")
                self.stats["errors"] += 1
                continue
        
        return roster_analysis
    
    def process_post_game_data(self, week: int, season: int = 2025) -> Dict[str, Any]:
        """
        Process all post-game data for analysis.
        
        Args:
            week: NFL week number
            season: NFL season year
            
        Returns:
            Processed post-game analysis data
        """
        self.logger.info(f"Starting post-game data processing for Week {week}, Season {season}")
        
        # Load projections archive
        projections = self._find_latest_projections_archive(week, season)
        if not projections:
            self.logger.error("No projections archive found")
            return {"error": "No projections archive found"}
        
        self.stats["projections_loaded"] = 1
        
        # Load stats data
        my_roster_stats = self._find_latest_stats_data("my_roster_stats", week)
        opponent_stats = self._find_latest_stats_data("opponent_roster_stats", week)
        available_stats = self._find_latest_stats_data("available_players_stats", week)
        matchup_data = self._find_latest_matchup_data(week)
        
        if my_roster_stats:
            self.stats["my_roster_stats_loaded"] = 1
        if opponent_stats:
            self.stats["opponent_stats_loaded"] = 1
        if available_stats:
            self.stats["available_stats_loaded"] = 1
        if matchup_data:
            self.stats["matchup_data_loaded"] = 1
        
        # Process roster analyses
        processed_data = {
            "analysis_metadata": {
                "source": "Post-Game Analysis Data Processor",
                "processing_timestamp": get_current_time_pacific().isoformat(),
                "week": week,
                "season": season,
                "execution_stats": self.stats
            },
            "projections_summary": {
                "total_projections": len(projections.get('projections', {})),
                "collection_timestamp": projections.get('collection_metadata', {}).get('collection_timestamp', 'Unknown')
            },
            "roster_analyses": {},
            "matchup_data": matchup_data,
            "summary": {
                "total_players_analyzed": 0,
                "total_projected_points": 0,
                "total_actual_points": 0,
                "overall_performance_difference": 0
            }
        }
        
        # Process my roster analysis
        if my_roster_stats and 'matched_players' in my_roster_stats:
            my_roster_analysis = self._process_roster_analysis(
                projections, 
                my_roster_stats['matched_players'], 
                "my_roster"
            )
            processed_data["roster_analyses"]["my_roster"] = my_roster_analysis
            
            # Update summary
            processed_data["summary"]["total_players_analyzed"] += my_roster_analysis["players_analyzed"]
            processed_data["summary"]["total_projected_points"] += my_roster_analysis["total_projected_points"]
            processed_data["summary"]["total_actual_points"] += my_roster_analysis["total_actual_points"]
            processed_data["summary"]["overall_performance_difference"] += my_roster_analysis["total_performance_difference"]
        
        # Process opponent roster analysis
        if opponent_stats and 'matched_players' in opponent_stats:
            opponent_roster_analysis = self._process_roster_analysis(
                projections, 
                opponent_stats['matched_players'], 
                "opponent_roster"
            )
            processed_data["roster_analyses"]["opponent_roster"] = opponent_roster_analysis
        
        # Process available players analysis
        if available_stats and 'matched_players' in available_stats:
            available_players_analysis = self._process_roster_analysis(
                projections, 
                available_stats['matched_players'], 
                "available_players"
            )
            processed_data["roster_analyses"]["available_players"] = available_players_analysis
        
        # Save processed data
        timestamp = self.file_manager.generate_timestamp()
        week_prefix = f"{timestamp}_wk{week:02d}_"
        
        # Create analysis output directory
        analysis_dir = Path("data_collection/outputs/analysis/post_game")
        week_dir = analysis_dir / str(season) / f"week_{week:02d}"
        week_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw data
        raw_file = self.file_manager.save_raw_data(
            "analysis", "post_game_processed", processed_data, week_prefix,
            custom_dir=str(week_dir)
        )
        
        self.logger.info(f"Post-game data processing complete")
        self.logger.info(f"Players analyzed: {self.stats['players_analyzed']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info(f"Output file: {raw_file}")
        
        return {
            "success": True,
            "players_analyzed": self.stats['players_analyzed'],
            "errors": self.stats["errors"],
            "output_file": raw_file,
            "week": week,
            "season": season
        }

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Post-Game Analysis Data Processor')
    parser.add_argument('--week', type=int, default=1, help='NFL week number')
    parser.add_argument('--season', type=int, default=2025, help='NFL season year')
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        processor = PostGameAnalysisDataProcessor()
        result = processor.process_post_game_data(args.week, args.season)
        
        if result.get("success"):
            print(f"✅ Post-game data processing successful!")
            print(f"   Week: {result['week']}")
            print(f"   Season: {result['season']}")
            print(f"   Players analyzed: {result['players_analyzed']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Output file: {result['output_file']}")
        else:
            print(f"❌ Post-game data processing failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Post-game data processing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
