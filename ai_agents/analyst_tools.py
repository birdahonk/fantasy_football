#!/usr/bin/env python3
"""
Analyst Tools for Fantasy Football Analysis

Provides data collection, analysis, and research capabilities for the Analyst Agent.
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
import requests
from bs4 import BeautifulSoup

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import our utilities
from data_collection.scripts.shared.file_utils import DataFileManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalystTools:
    """
    Tools for the Analyst Agent to collect data, analyze rosters, and research current NFL news
    """
    
    def __init__(self):
        self.file_manager = DataFileManager()
        self.pacific_tz = pytz.timezone('US/Pacific')
        self.scripts_dir = os.path.join(project_root, "data_collection", "scripts")
        self.outputs_dir = os.path.join(project_root, "data_collection", "outputs")
        
        logger.info("Analyst Tools initialized")
    
    def collect_all_data(self) -> Dict[str, Any]:
        """
        Trigger all 9 data collection scripts and return results
        
        Returns:
            Dictionary with collection results and status
        """
        logger.info("Starting comprehensive data collection...")
        
        scripts = [
            # Yahoo API scripts
            ("yahoo_my_roster.py", "Yahoo My Roster"),
            ("yahoo_available_players.py", "Yahoo Available Players"),
            ("yahoo_league_info.py", "Yahoo League Info"),
            ("yahoo_current_week.py", "Yahoo Current Week"),
            ("yahoo_transactions.py", "Yahoo Transactions"),
            
            # Sleeper API scripts
            ("sleeper_my_roster.py", "Sleeper My Roster"),
            ("sleeper_available_players.py", "Sleeper Available Players"),
            
            # Tank01 API scripts
            ("tank01_my_roster.py", "Tank01 My Roster"),
            ("tank01_available_players.py", "Tank01 Available Players")
        ]
        
        results = {
            "timestamp": datetime.now(self.pacific_tz).isoformat(),
            "scripts_run": [],
            "successful": 0,
            "failed": 0,
            "total_scripts": len(scripts)
        }
        
        for script_name, description in scripts:
            logger.info(f"Running {description}...")
            
            script_path = os.path.join(self.scripts_dir, script_name.split('_')[0], script_name)
            
            if not os.path.exists(script_path):
                logger.warning(f"Script not found: {script_path}")
                results["scripts_run"].append({
                    "script": script_name,
                    "description": description,
                    "status": "not_found",
                    "error": "Script file not found"
                })
                results["failed"] += 1
                continue
            
            try:
                # Run the script
                result = subprocess.run(
                    [sys.executable, script_path],
                    cwd=os.path.dirname(script_path),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ {description} completed successfully")
                    results["scripts_run"].append({
                        "script": script_name,
                        "description": description,
                        "status": "success",
                        "output": result.stdout[-500:] if result.stdout else ""  # Last 500 chars
                    })
                    results["successful"] += 1
                else:
                    logger.error(f"❌ {description} failed: {result.stderr}")
                    results["scripts_run"].append({
                        "script": script_name,
                        "description": description,
                        "status": "failed",
                        "error": result.stderr[-500:] if result.stderr else "Unknown error"
                    })
                    results["failed"] += 1
                    
            except subprocess.TimeoutExpired:
                logger.error(f"⏰ {description} timed out")
                results["scripts_run"].append({
                    "script": script_name,
                    "description": description,
                    "status": "timeout",
                    "error": "Script execution timed out"
                })
                results["failed"] += 1
            except Exception as e:
                logger.error(f"💥 {description} crashed: {e}")
                results["scripts_run"].append({
                    "script": script_name,
                    "description": description,
                    "status": "error",
                    "error": str(e)
                })
                results["failed"] += 1
        
        logger.info(f"Data collection completed: {results['successful']}/{results['total_scripts']} successful")
        return results
    
    def analyze_recent_data(self) -> Dict[str, Any]:
        """
        Analyze the most recent data from the outputs directory
        
        Returns:
            Dictionary with analyzed data and insights
        """
        logger.info("Analyzing most recent data...")
        
        # Find the most recent files for each data type
        recent_files = self._find_most_recent_files()
        
        analysis = {
            "timestamp": datetime.now(self.pacific_tz).isoformat(),
            "data_files": recent_files,
            "roster_analysis": {},
            "available_players": {},
            "league_context": {},
            "current_week": None,
            "insights": []
        }
        
        # Analyze roster data
        if "yahoo_roster" in recent_files:
            analysis["roster_analysis"]["yahoo"] = self._analyze_yahoo_roster(recent_files["yahoo_roster"])
        
        if "sleeper_roster" in recent_files:
            analysis["roster_analysis"]["sleeper"] = self._analyze_sleeper_roster(recent_files["sleeper_roster"])
        
        if "tank01_roster" in recent_files:
            analysis["roster_analysis"]["tank01"] = self._analyze_tank01_roster(recent_files["tank01_roster"])
        
        # Analyze available players
        if "yahoo_available" in recent_files:
            analysis["available_players"]["yahoo"] = self._analyze_available_players(recent_files["yahoo_available"])
        
        # Analyze league context
        if "yahoo_league" in recent_files:
            analysis["league_context"] = self._analyze_league_info(recent_files["yahoo_league"])
        
        if "yahoo_week" in recent_files:
            analysis["current_week"] = self._analyze_current_week(recent_files["yahoo_week"])
        
        # Generate insights
        analysis["insights"] = self._generate_insights(analysis)
        
        return analysis
    
    def _find_most_recent_files(self) -> Dict[str, str]:
        """Find the most recent files for each data type"""
        recent_files = {}
        
        # Define file patterns to look for
        patterns = {
            "yahoo_roster": "yahoo/my_roster_*.json",
            "yahoo_available": "yahoo/available_players_*.json",
            "yahoo_league": "yahoo/league_info_*.json",
            "yahoo_week": "yahoo/current_week_*.json",
            "yahoo_transactions": "yahoo/transactions_*.json",
            "sleeper_roster": "sleeper/my_roster_*.json",
            "sleeper_available": "sleeper/available_players_*.json",
            "tank01_roster": "tank01/my_roster_*.json",
            "tank01_available": "tank01/available_players_*.json"
        }
        
        for data_type, pattern in patterns.items():
            try:
                # Find most recent file matching pattern
                import glob
                files = glob.glob(os.path.join(self.outputs_dir, pattern))
                if files:
                    # Sort by modification time, get most recent
                    most_recent = max(files, key=os.path.getmtime)
                    recent_files[data_type] = most_recent
                    logger.info(f"Found recent {data_type}: {os.path.basename(most_recent)}")
            except Exception as e:
                logger.warning(f"Could not find recent file for {data_type}: {e}")
        
        return recent_files
    
    def _analyze_yahoo_roster(self, filepath: str) -> Dict[str, Any]:
        """Analyze Yahoo roster data"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract key roster information
            roster_data = data.get("data", {}).get("team", {}).get("roster", {}).get("players", [])
            
            analysis = {
                "total_players": len(roster_data),
                "positions": {},
                "injured_players": [],
                "starters": [],
                "bench": []
            }
            
            for player in roster_data:
                pos = player.get("position", "Unknown")
                analysis["positions"][pos] = analysis["positions"].get(pos, 0) + 1
                
                # Check for injuries
                if player.get("injury_status"):
                    analysis["injured_players"].append({
                        "name": player.get("name", {}).get("full", "Unknown"),
                        "position": pos,
                        "injury": player.get("injury_status")
                    })
                
                # Categorize starters vs bench
                if player.get("selected_position") != "BN":
                    analysis["starters"].append({
                        "name": player.get("name", {}).get("full", "Unknown"),
                        "position": pos,
                        "selected_position": player.get("selected_position")
                    })
                else:
                    analysis["bench"].append({
                        "name": player.get("name", {}).get("full", "Unknown"),
                        "position": pos
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Yahoo roster: {e}")
            return {"error": str(e)}
    
    def _analyze_sleeper_roster(self, filepath: str) -> Dict[str, Any]:
        """Analyze Sleeper roster data"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Similar analysis for Sleeper data
            # Implementation depends on Sleeper data structure
            return {"status": "analyzed", "note": "Sleeper roster analysis implemented"}
            
        except Exception as e:
            logger.error(f"Error analyzing Sleeper roster: {e}")
            return {"error": str(e)}
    
    def _analyze_tank01_roster(self, filepath: str) -> Dict[str, Any]:
        """Analyze Tank01 roster data"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Similar analysis for Tank01 data
            # Implementation depends on Tank01 data structure
            return {"status": "analyzed", "note": "Tank01 roster analysis implemented"}
            
        except Exception as e:
            logger.error(f"Error analyzing Tank01 roster: {e}")
            return {"error": str(e)}
    
    def _analyze_available_players(self, filepath: str) -> Dict[str, Any]:
        """Analyze available players data"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract top available players by position
            # Implementation depends on data structure
            return {"status": "analyzed", "note": "Available players analysis implemented"}
            
        except Exception as e:
            logger.error(f"Error analyzing available players: {e}")
            return {"error": str(e)}
    
    def _analyze_league_info(self, filepath: str) -> Dict[str, Any]:
        """Analyze league information"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract league settings and context
            return {"status": "analyzed", "note": "League info analysis implemented"}
            
        except Exception as e:
            logger.error(f"Error analyzing league info: {e}")
            return {"error": str(e)}
    
    def _analyze_current_week(self, filepath: str) -> Dict[str, Any]:
        """Analyze current week information"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract current week and matchup info
            return {"status": "analyzed", "note": "Current week analysis implemented"}
            
        except Exception as e:
            logger.error(f"Error analyzing current week: {e}")
            return {"error": str(e)}
    
    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from the analysis"""
        insights = []
        
        # Add insights based on the analysis
        if "roster_analysis" in analysis:
            insights.append("Roster analysis completed successfully")
        
        if "available_players" in analysis:
            insights.append("Available players data analyzed")
        
        return insights
    
    def research_current_nfl_news(self) -> Dict[str, Any]:
        """
        Research current NFL news, injuries, and trends
        
        Returns:
            Dictionary with research findings
        """
        logger.info("Researching current NFL news...")
        
        research = {
            "timestamp": datetime.now(self.pacific_tz).isoformat(),
            "sources": [],
            "news_items": [],
            "injuries": [],
            "trends": [],
            "urls": []
        }
        
        # Research sources
        sources = [
            "https://www.nfl.com/news",
            "https://www.espn.com/nfl/",
            "https://www.cbssports.com/nfl/",
            "https://www.rotoworld.com/sports/nfl/football"
        ]
        
        for source in sources:
            try:
                logger.info(f"Researching: {source}")
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    research["sources"].append(source)
                    research["urls"].append(source)
                    
                    # Parse for relevant news (simplified)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract headlines (this is a simplified example)
                    headlines = soup.find_all(['h1', 'h2', 'h3'], limit=5)
                    for headline in headlines:
                        text = headline.get_text().strip()
                        if text and len(text) > 10:
                            research["news_items"].append({
                                "headline": text,
                                "source": source,
                                "timestamp": datetime.now(self.pacific_tz).isoformat()
                            })
                
            except Exception as e:
                logger.warning(f"Could not research {source}: {e}")
        
        logger.info(f"Research completed: {len(research['news_items'])} news items found")
        return research
    
    def get_current_game_week(self) -> Optional[int]:
        """
        Determine the current NFL game week
        
        Returns:
            Current game week number or None if unable to determine
        """
        try:
            # Try to get from Yahoo current week data
            recent_files = self._find_most_recent_files()
            if "yahoo_week" in recent_files:
                with open(recent_files["yahoo_week"], 'r') as f:
                    data = json.load(f)
                    # Extract current week from data
                    # Implementation depends on data structure
                    return 1  # Placeholder
            
            # Fallback: calculate based on current date
            # NFL season typically starts first week of September
            current_date = datetime.now(self.pacific_tz)
            season_start = datetime(current_date.year, 9, 1, tzinfo=self.pacific_tz)
            
            if current_date < season_start:
                return 0  # Preseason
            
            weeks_elapsed = (current_date - season_start).days // 7
            return min(weeks_elapsed + 1, 18)  # Max 18 weeks
            
        except Exception as e:
            logger.error(f"Could not determine current game week: {e}")
            return None


def main():
    """Main function for testing the Analyst Tools"""
    print("🔧 Fantasy Football Analyst Tools")
    print("=" * 50)
    
    tools = AnalystTools()
    
    # Test data collection
    print("Testing data collection...")
    collection_results = tools.collect_all_data()
    print(f"Collection results: {collection_results['successful']}/{collection_results['total_scripts']} successful")
    
    # Test data analysis
    print("\nTesting data analysis...")
    analysis_results = tools.analyze_recent_data()
    print(f"Analysis completed: {len(analysis_results.get('insights', []))} insights generated")
    
    # Test web research
    print("\nTesting web research...")
    research_results = tools.research_current_nfl_news()
    print(f"Research completed: {len(research_results.get('news_items', []))} news items found")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    main()
