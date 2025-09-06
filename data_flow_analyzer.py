#!/usr/bin/env python3
"""
Analyze what data is actually being sent from each API
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_tools import AnalystTools
import tiktoken

def analyze_data_flow():
    """Analyze what data flows from each API to the LLM"""
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("DATA FLOW ANALYSIS - WHAT'S ACTUALLY SENT TO LLM")
    print("=" * 60)
    
    # Check what's in roster_analysis
    print("\n1. ROSTER ANALYSIS:")
    print("-" * 30)
    roster_analysis = analysis_data.get("roster_analysis", {})
    for api, data in roster_analysis.items():
        if data:  # Only show non-empty data
            data_json = json.dumps(data, indent=2)
            tokens = len(encoding.encode(data_json))
            print(f"  {api.upper()}: {tokens:,} tokens")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (list, dict)) and value:
                        value_json = json.dumps(value, indent=2)
                        value_tokens = len(encoding.encode(value_json))
                        print(f"    {key}: {value_tokens:,} tokens")
        else:
            print(f"  {api.upper()}: NO DATA")
    
    # Check what's in available_players
    print("\n2. AVAILABLE PLAYERS:")
    print("-" * 30)
    available_players = analysis_data.get("available_players", {})
    for api, data in available_players.items():
        if data and "error" not in data:  # Only show non-empty, non-error data
            data_json = json.dumps(data, indent=2)
            tokens = len(encoding.encode(data_json))
            print(f"  {api.upper()}: {tokens:,} tokens")
            if "top_players_by_position" in data:
                total_players = sum(len(players) for players in data["top_players_by_position"].values() if isinstance(players, list))
                print(f"    Players: {total_players}")
        else:
            print(f"  {api.upper()}: NO DATA")
    
    # Check what's in league_context
    print("\n3. LEAGUE CONTEXT:")
    print("-" * 30)
    league_context = analysis_data.get("league_context", {})
    for section, data in league_context.items():
        if data and "error" not in data:
            data_json = json.dumps(data, indent=2)
            tokens = len(encoding.encode(data_json))
            print(f"  {section.upper()}: {tokens:,} tokens")
        else:
            print(f"  {section.upper()}: NO DATA")

def analyze_current_week_opponent():
    """Analyze how to identify current week opponent"""
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    print("\n\nCURRENT WEEK OPPONENT ANALYSIS")
    print("=" * 40)
    
    # Check matchup data
    league_context = analysis_data.get("league_context", {})
    matchups = league_context.get("matchups", {})
    
    if "matchup_analysis" in matchups:
        matchup_data = matchups["matchup_analysis"]
        print(f"Current Week: {matchup_data.get('current_week', 'Unknown')}")
        print(f"Total Matchups: {matchup_data.get('total_matchups', 0)}")
        
        if "matchups" in matchup_data:
            print("\nAll Matchups:")
            for i, matchup in enumerate(matchup_data["matchups"]):
                if isinstance(matchup, dict):
                    print(f"  {i+1}. {matchup}")
        
        # Try to find my team's matchup
        print("\nLooking for my team's matchup...")
        # This would need to be enhanced to identify which matchup is mine
        # based on team_key or team_name from roster data

def check_missing_data():
    """Check what data we're missing from Sleeper and Tank01"""
    print("\n\nMISSING DATA ANALYSIS")
    print("=" * 30)
    
    # Check what files exist
    import glob
    import os
    
    data_dirs = [
        "data_collection/outputs/yahoo",
        "data_collection/outputs/sleeper", 
        "data_collection/outputs/tank01"
    ]
    
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            print(f"\n{data_dir.upper()}:")
            for subdir in os.listdir(data_dir):
                subdir_path = os.path.join(data_dir, subdir)
                if os.path.isdir(subdir_path):
                    json_files = glob.glob(os.path.join(subdir_path, "*_raw_data.json"))
                    if json_files:
                        latest_file = max(json_files, key=os.path.getctime)
                        file_size = os.path.getsize(latest_file)
                        print(f"  {subdir}: {file_size:,} bytes - {os.path.basename(latest_file)}")
                    else:
                        print(f"  {subdir}: NO JSON FILES")

if __name__ == "__main__":
    analyze_data_flow()
    analyze_current_week_opponent()
    check_missing_data()
