#!/usr/bin/env python3
"""
Tank01 Weekly Projections Archive Collection Script

This script collects and stores weekly fantasy projections from Tank01 API for historical analysis.
It runs on multiple days during the week to capture projections before they reset.

Collection Schedule:
- Thursday Afternoon: Thursday night players
- Sunday Morning: Sunday players  
- Monday Afternoon: Monday night players

Purpose: Store projection data for post-game analysis comparing actual vs. projected performance.
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

# Add the shared utilities to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "shared"))

from tank01_client import SimpleTank01Client
from file_utils import DataFileManager
from api_usage_manager import APIUsageManager

def get_current_time_pacific():
    """Get current time in Pacific Time Zone."""
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific)

def format_timestamp_pacific(timestamp):
    """Convert RapidAPI reset timestamp to Pacific Time Zone."""
    if not timestamp:
        return "Unknown"
    
    try:
        # Convert to Pacific Time
        pacific = pytz.timezone('US/Pacific')
        dt = datetime.fromtimestamp(timestamp, tz=pacific)
        return dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    except Exception:
        return f"Invalid timestamp: {timestamp}"

class Tank01WeeklyProjectionsArchiver:
    """
    Archive weekly fantasy projections from Tank01 API for historical analysis.
    
    This script collects projections at different times during the week to ensure
    we capture all projection data before the API resets to the next week.
    """
    
    def __init__(self):
        """Initialize the projections archiver."""
        self.logger = logging.getLogger(__name__)
        self.file_manager = DataFileManager()
        
        # Initialize Tank01 client
        self.tank01 = SimpleTank01Client()
        if not self.tank01.is_available():
            raise ValueError("Tank01 client not available. Check RAPIDAPI_KEY environment variable.")
        
        # Initialize centralized API usage manager
        self.usage_manager = APIUsageManager(self.tank01, "Tank01")
        
        # Track execution stats
        self.stats = {
            "start_time": datetime.now(),
            "api_calls": 0,
            "errors": 0,
            "projections_collected": 0,
            "players_processed": 0
        }
        
        self.logger.info("Tank01 Weekly Projections Archiver initialized")
    
    def _extract_season_context(self) -> Dict[str, Any]:
        """
        Extract season and week context.
        
        Returns:
            Dict containing season context information
        """
        season_context = {
            "nfl_season": "2025",
            "current_week": 1,
            "season_phase": "Regular Season",
            "data_source": "Tank01 API",
            "collection_timestamp": get_current_time_pacific().isoformat(),
            "verification_notes": []
        }
        
        try:
            # For now, we'll use a simple week detection
            # In a real implementation, this could be more sophisticated
            current_date = get_current_time_pacific()
            season_start = datetime(2025, 9, 4, tzinfo=current_date.tzinfo)  # Approximate season start
            
            # Calculate week number (simplified)
            days_since_start = (current_date - season_start).days
            week_number = max(1, (days_since_start // 7) + 1)
            
            season_context['current_week'] = min(week_number, 18)  # Cap at 18 weeks
            season_context['verification_notes'].append(f"Week calculated from season start: {week_number}")
            
        except Exception as e:
            self.logger.warning(f"Could not calculate week number: {e}")
            season_context['verification_notes'].append(f"Week calculation failed: {str(e)}")
        
        return season_context
    
    def _get_weekly_projections(self, week: int, season: int = 2025) -> Dict[str, Any]:
        """
        Get weekly projections from Tank01 API.
        
        Args:
            week: NFL week number
            season: NFL season year
            
        Returns:
            Dict containing weekly projections
        """
        try:
            self.logger.info(f"Fetching weekly projections for Week {week}, Season {season}")
            
            # Get weekly projections
            projections = self.tank01.get_weekly_projections(week, season)
            
            if not projections:
                self.logger.error("Failed to get weekly projections")
                return {}
            
            self.stats["api_calls"] += 1
            
            # Count projections collected
            if 'body' in projections:
                self.stats["projections_collected"] = len(projections['body'])
                self.logger.info(f"Collected {self.stats['projections_collected']} player projections")
            
            return projections
            
        except Exception as e:
            self.logger.error(f"Error getting weekly projections: {e}")
            self.stats["errors"] += 1
            return {}
    
    def _process_projections_data(self, projections: Dict[str, Any], season_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure projections data for archiving.
        
        Args:
            projections: Raw projections data from Tank01 API
            season_context: Season and week context
            
        Returns:
            Processed projections data
        """
        processed_data = {
            "collection_metadata": {
                "source": "Tank01 API - Weekly Projections Archive",
                "collection_timestamp": get_current_time_pacific().isoformat(),
                "nfl_season": season_context.get('nfl_season', '2025'),
                "week": season_context.get('current_week', 1),
                "execution_stats": self.stats
            },
            "season_context": season_context,
            "projections": {},
            "tank01_api_usage": {
                "session_usage": self.tank01.get_api_usage(),
                "efficiency_metrics": {
                    "api_calls": self.stats["api_calls"],
                    "projections_collected": self.stats["projections_collected"],
                    "collection_efficiency": self.stats["projections_collected"] / max(1, self.stats["api_calls"]),
                    "errors": self.stats["errors"],
                    "collection_timestamp_pacific": get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')
                }
            }
        }
        
        # Process individual player projections
        if 'body' in projections and isinstance(projections['body'], list):
            for player in projections['body']:
                player_id = player.get('playerID')
                if player_id:
                    processed_data['projections'][player_id] = {
                        'player_id': player_id,
                        'player_name': player.get('longName', 'Unknown'),
                        'position': player.get('position', 'Unknown'),
                        'team': player.get('team', 'Unknown'),
                        'fantasyPoints': player.get('fantasyPoints'),
                        'fantasyPointsDefault': player.get('fantasyPointsDefault'),
                        'Passing': player.get('Passing', {}),
                        'Rushing': player.get('Rushing', {}),
                        'Receiving': player.get('Receiving', {}),
                        'Defense': player.get('Defense', {}),
                        'isTeamDefense': player.get('isTeamDefense', False)
                    }
                    self.stats["players_processed"] += 1
        
        return processed_data
    
    def _generate_markdown_report(self, processed_data: Dict[str, Any]) -> str:
        """
        Generate a markdown report of the archived projections.
        
        Args:
            processed_data: Processed projections data
            
        Returns:
            Markdown report string
        """
        report = []
        report.append("# Tank01 NFL - Weekly Projections Archive")
        report.append("")
        
        # Header with execution stats
        end_time = get_current_time_pacific()
        execution_time = (end_time - self.stats["start_time"]).total_seconds()
        
        metadata = processed_data.get('collection_metadata', {})
        season_context = processed_data.get('season_context', {})
        
        report.append(f"**Collection Date:** {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        report.append(f"**NFL Season:** {season_context.get('nfl_season', 'Unknown')}")
        report.append(f"**Week:** {season_context.get('current_week', 'Unknown')}")
        report.append(f"**Projections Collected:** {self.stats['projections_collected']}")
        report.append(f"**Players Processed:** {self.stats['players_processed']}")
        report.append(f"**API Calls:** {self.stats['api_calls']}")
        report.append(f"**Execution Time:** {execution_time:.2f}s")
        report.append(f"**Errors:** {self.stats['errors']}")
        report.append("")
        
        # Tank01 API Usage Info
        report.append("## Tank01 API Usage")
        usage_info = self.usage_manager.get_usage_info()
        report.append(f"- **Current Time (Pacific):** {usage_info.get('current_time_formatted', 'Unknown')}")
        report.append(f"- **Calls Made This Session:** {self.stats['api_calls']}")
        report.append(f"- **Daily Limit:** {usage_info.get('daily_limit', 'Unknown')}")
        report.append(f"- **Remaining Calls Today:** {usage_info.get('remaining_calls', 'Unknown')}")
        report.append(f"- **Usage Percentage:** {usage_info.get('percentage_used', 0):.1f}%")
        report.append(f"- **Data Source:** {usage_info.get('data_source', 'Unknown')}")
        if usage_info.get('reset_time_pacific'):
            report.append(f"- **Limit Resets:** {usage_info.get('reset_time_pacific')}")
        report.append(f"- **Client Available:** {usage_info.get('available', False)}")
        report.append("")
        
        # Projections summary
        projections = processed_data.get('projections', {})
        if projections:
            report.append("## Projections Summary")
            report.append(f"Total players with projections: {len(projections)}")
            report.append("")
            
            # Group by position
            position_counts = {}
            for player_data in projections.values():
                pos = player_data.get('position', 'Unknown')
                position_counts[pos] = position_counts.get(pos, 0) + 1
            
            report.append("### Projections by Position")
            for position, count in sorted(position_counts.items()):
                report.append(f"- **{position}**: {count} players")
            report.append("")
            
            # Sample projections (top 10 by fantasy points)
            report.append("### Top 10 Projected Players")
            sorted_players = sorted(
                projections.values(),
                key=lambda x: float(x.get('fantasyPoints', 0)) if x.get('fantasyPoints') else 0,
                reverse=True
            )[:10]
            
            report.append("| Player | Pos | Team | Fantasy Points |")
            report.append("|--------|-----|------|----------------|")
            
            for player in sorted_players:
                name = player.get('player_name', 'Unknown')
                pos = player.get('position', 'N/A')
                team = player.get('team', 'N/A')
                fp = player.get('fantasyPoints', 0)
                report.append(f"| {name} | {pos} | {team} | {fp} |")
            
            report.append("")
        else:
            report.append("## No Projections Collected")
            report.append("No projection data was successfully collected.")
        
        return "\n".join(report)
    
    def archive_weekly_projections(self, phase: str = "manual") -> Dict[str, Any]:
        """
        Archive weekly projections for the current week.
        
        Args:
            phase: Collection phase ("thursday_afternoon", "sunday_morning", "monday_afternoon", "manual")
            
        Returns:
            Dict containing archiving results
        """
        self.logger.info(f"Starting Tank01 weekly projections archive (phase: {phase})")
        
        # Get season context
        season_context = self._extract_season_context()
        current_week = season_context.get('current_week', 1)
        season = int(season_context.get('nfl_season', '2025'))
        
        # Get weekly projections
        projections = self._get_weekly_projections(current_week, season)
        if not projections:
            self.logger.error("No projections data collected")
            return {"error": "No projections data collected"}
        
        # Process projections data
        processed_data = self._process_projections_data(projections, season_context)
        
        # Generate markdown report
        markdown_report = self._generate_markdown_report(processed_data)
        
        # Save outputs with week-specific naming
        timestamp = self.file_manager.generate_timestamp()
        week_prefix = f"{timestamp}_wk{current_week:02d}_{phase}_"
        
        # Create projections archive directory
        archive_dir = Path("data_collection/outputs/tank01/projections_archive")
        week_dir = archive_dir / str(season) / f"week_{current_week:02d}"
        week_dir.mkdir(parents=True, exist_ok=True)
        
        # Save files
        clean_file = self.file_manager.save_clean_data(
            "tank01", "projections_archive", markdown_report, week_prefix, 
            custom_dir=str(week_dir)
        )
        raw_file = self.file_manager.save_raw_data(
            "tank01", "projections_archive", processed_data, week_prefix,
            custom_dir=str(week_dir)
        )
        
        output_files = {
            "clean": clean_file,
            "raw": raw_file
        }
        
        self.logger.info(f"Tank01 weekly projections archive complete")
        self.logger.info(f"Projections collected: {self.stats['projections_collected']}")
        self.logger.info(f"Players processed: {self.stats['players_processed']}")
        self.logger.info(f"API calls: {self.stats['api_calls']}")
        self.logger.info(f"Output files: {output_files}")
        
        return {
            "success": True,
            "projections_collected": self.stats['projections_collected'],
            "players_processed": self.stats['players_processed'],
            "api_calls": self.stats["api_calls"],
            "output_files": output_files,
            "phase": phase,
            "week": current_week,
            "season": season
        }

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Tank01 Weekly Projections Archive Collection')
    parser.add_argument('--phase', choices=['thursday_afternoon', 'sunday_morning', 'monday_afternoon', 'manual'], 
                       default='manual', help='Collection phase')
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        archiver = Tank01WeeklyProjectionsArchiver()
        result = archiver.archive_weekly_projections(args.phase)
        
        if result.get("success"):
            print(f"✅ Tank01 weekly projections archive successful!")
            print(f"   Phase: {result['phase']}")
            print(f"   Week: {result['week']}")
            print(f"   Season: {result['season']}")
            print(f"   Projections collected: {result['projections_collected']}")
            print(f"   Players processed: {result['players_processed']}")
            print(f"   API calls: {result['api_calls']}")
            print(f"   Output files: {result['output_files']}")
        else:
            print(f"❌ Tank01 weekly projections archive failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Tank01 weekly projections archive failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
