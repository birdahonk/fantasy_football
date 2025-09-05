#!/usr/bin/env python3
"""
Fresh Data Collection Script

Runs all API data collection scripts to gather fresh data for analysis.
This should be run before any AI analysis to ensure we have current data.
"""

import os
import sys
import subprocess
from datetime import datetime
import pytz

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def collect_fresh_data():
    """Collect fresh data from all APIs"""
    print("🔄 Starting Fresh Data Collection")
    print("=" * 60)
    
    pacific_tz = pytz.timezone('US/Pacific')
    start_time = datetime.now(pacific_tz)
    
    # Scripts to run (in order of importance)
    scripts = [
        # Yahoo API scripts
        ("data_collection/scripts/yahoo/my_roster.py", "Yahoo My Roster"),
        ("data_collection/scripts/yahoo/available_players.py", "Yahoo Available Players"),
        ("data_collection/scripts/yahoo/opponent_rosters.py", "Yahoo Opponent Rosters"),
        ("data_collection/scripts/yahoo/team_matchups.py", "Yahoo Team Matchups"),
        ("data_collection/scripts/yahoo/transaction_trends.py", "Yahoo Transaction Trends"),
        
        # Sleeper API scripts
        ("data_collection/scripts/sleeper/my_roster.py", "Sleeper My Roster"),
        ("data_collection/scripts/sleeper/available_players.py", "Sleeper Available Players"),
        ("data_collection/scripts/sleeper/trending.py", "Sleeper Trending"),
        
        # Tank01 API scripts
        ("data_collection/scripts/tank01/my_roster.py", "Tank01 My Roster"),
        ("data_collection/scripts/tank01/available_players.py", "Tank01 Available Players")
    ]
    
    results = {
        "timestamp": start_time.isoformat(),
        "scripts_run": [],
        "successful": 0,
        "failed": 0,
        "total_scripts": len(scripts)
    }
    
    for script_path, description in scripts:
        print(f"\n🔄 Running {description}...")
        
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            results["scripts_run"].append({
                "script": script_path,
                "description": description,
                "status": "not_found",
                "error": "Script file not found"
            })
            results["failed"] += 1
            continue
        
        try:
            # Run the script from the project root
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=project_root,  # Run from project root, not script directory
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                results["scripts_run"].append({
                    "script": script_path,
                    "description": description,
                    "status": "success",
                    "output": result.stdout[-200:] if result.stdout else ""  # Last 200 chars
                })
                results["successful"] += 1
            else:
                print(f"❌ {description} failed: {result.stderr}")
                results["scripts_run"].append({
                    "script": script_path,
                    "description": description,
                    "status": "failed",
                    "error": result.stderr[-200:] if result.stderr else "Unknown error"
                })
                results["failed"] += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out")
            results["scripts_run"].append({
                "script": script_path,
                "description": description,
                "status": "timeout",
                "error": "Script execution timed out"
            })
            results["failed"] += 1
        except Exception as e:
            print(f"💥 {description} crashed: {e}")
            results["scripts_run"].append({
                "script": script_path,
                "description": description,
                "status": "error",
                "error": str(e)
            })
            results["failed"] += 1
    
    end_time = datetime.now(pacific_tz)
    total_time = (end_time - start_time).total_seconds()
    
    print(f"\n" + "=" * 60)
    print("📊 DATA COLLECTION SUMMARY")
    print("=" * 60)
    print(f"Total Scripts: {results['total_scripts']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['successful']/results['total_scripts']*100):.1f}%")
    print(f"Total Time: {total_time:.1f} seconds")
    
    # Save results
    import json
    timestamp = end_time.strftime("%Y%m%d_%H%M%S")
    results_file = f"data_collection/outputs/data_collection_{timestamp}.json"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    if results["successful"] > 0:
        print(f"\n✅ Data collection completed! {results['successful']} scripts successful.")
        print("You can now run AI analysis on the fresh data.")
    else:
        print(f"\n❌ Data collection failed! All {results['failed']} scripts failed.")
        print("Please check the errors above and try again.")
    
    return results["successful"] > 0

if __name__ == "__main__":
    success = collect_fresh_data()
    sys.exit(0 if success else 1)
