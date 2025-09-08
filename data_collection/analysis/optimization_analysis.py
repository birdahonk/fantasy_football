#!/usr/bin/env python3
"""
Comprehensive analysis of optimization opportunities
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_tools import AnalystTools
import tiktoken

def analyze_current_week_opponent_savings():
    """Calculate token savings from only including current week opponent"""
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("CURRENT WEEK OPPONENT OPTIMIZATION ANALYSIS")
    print("=" * 50)
    
    # Get my team info
    roster_analysis = analysis_data.get("roster_analysis", {})
    yahoo_roster = roster_analysis.get("yahoo", {})
    my_team_key = "461.l.595012.t.3"  # From the matchup data we saw
    
    # Get matchup data
    league_context = analysis_data.get("league_context", {})
    matchups = league_context.get("matchups", {})
    matchup_analysis = matchups.get("matchup_analysis", {})
    
    # Find my matchup
    my_matchup = None
    if "matchups" in matchup_analysis:
        for matchup in matchup_analysis["matchups"]:
            if isinstance(matchup, dict) and "teams" in matchup:
                for team in matchup["teams"]:
                    if team.get("team_key") == my_team_key:
                        my_matchup = matchup
                        break
    
    if my_matchup:
        print(f"My Team: birdahonkers ({my_team_key})")
        print("My Matchup:")
        for team in my_matchup["teams"]:
            if team.get("team_key") != my_team_key:
                print(f"  vs {team.get('name')} ({team.get('team_key')})")
                opponent_team_key = team.get("team_key")
                break
    else:
        print("Could not find my matchup")
        return
    
    # Get current opponent analysis
    opponents = league_context.get("opponents", {})
    opponent_analysis = opponents.get("opponent_analysis", {})
    
    print(f"\nCurrent Opponent Analysis:")
    print(f"  Total teams: {len(opponent_analysis)}")
    
    # Calculate current token usage
    current_opponent_json = json.dumps(opponent_analysis, indent=2)
    current_tokens = len(encoding.encode(current_opponent_json))
    print(f"  Current tokens: {current_tokens:,}")
    
    # Calculate if we only included current opponent
    if opponent_team_key and opponent_team_key in opponent_analysis:
        current_opponent_only = {opponent_team_key: opponent_analysis[opponent_team_key]}
        current_opponent_json = json.dumps(current_opponent_only, indent=2)
        current_opponent_tokens = len(encoding.encode(current_opponent_json))
        print(f"  Current opponent only: {current_opponent_tokens:,}")
        print(f"  Savings: {current_tokens - current_opponent_tokens:,} tokens ({((current_tokens - current_opponent_tokens) / current_tokens * 100):.1f}%)")
    else:
        print("  Could not find current opponent in analysis")

def analyze_missing_sleeper_tank01_data():
    """Analyze what Sleeper and Tank01 data we're missing"""
    print("\n\nMISSING SLEEPER/TANK01 DATA ANALYSIS")
    print("=" * 40)
    
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Check available players
    available_players = analysis_data.get("available_players", {})
    print("Available Players Data:")
    for api, data in available_players.items():
        if data and "error" not in data:
            data_json = json.dumps(data, indent=2)
            tokens = len(encoding.encode(data_json))
            total_players = sum(len(players) for players in data.get("top_players_by_position", {}).values() if isinstance(players, list))
            print(f"  {api.upper()}: {tokens:,} tokens, {total_players} players")
        else:
            print(f"  {api.upper()}: NO DATA")
    
    # Check roster analysis
    roster_analysis = analysis_data.get("roster_analysis", {})
    print("\nRoster Analysis Data:")
    for api, data in roster_analysis.items():
        if data and "error" not in data:
            data_json = json.dumps(data, indent=2)
            tokens = len(encoding.encode(data_json))
            print(f"  {api.upper()}: {tokens:,} tokens")
        else:
            print(f"  {api.upper()}: NO DATA")
    
    # Check what files exist but aren't being used
    print("\nFiles that exist but aren't being analyzed:")
    import glob
    import os
    
    sleeper_files = glob.glob("data_collection/outputs/sleeper/**/*_raw_data.json", recursive=True)
    tank01_files = glob.glob("data_collection/outputs/tank01/**/*_raw_data.json", recursive=True)
    
    print("Sleeper files:")
    for file in sleeper_files:
        file_size = os.path.getsize(file)
        print(f"  {file}: {file_size:,} bytes")
    
    print("Tank01 files:")
    for file in tank01_files:
        file_size = os.path.getsize(file)
        print(f"  {file}: {file_size:,} bytes")

def calculate_optimization_scenarios():
    """Calculate different optimization scenarios"""
    print("\n\nOPTIMIZATION SCENARIOS")
    print("=" * 30)
    
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Current state
    current_json = json.dumps(analysis_data, indent=2)
    current_tokens = len(encoding.encode(current_json))
    print(f"Current total: {current_tokens:,} tokens")
    
    # Scenario 1: Only current week opponent
    print("\nScenario 1: Only Current Week Opponent")
    print("-" * 40)
    
    # Get my team key and find opponent
    my_team_key = "461.l.595012.t.3"
    league_context = analysis_data.get("league_context", {})
    matchups = league_context.get("matchups", {})
    matchup_analysis = matchups.get("matchup_analysis", {})
    
    opponent_team_key = None
    if "matchups" in matchup_analysis:
        for matchup in matchup_analysis["matchups"]:
            if isinstance(matchup, dict) and "teams" in matchup:
                for team in matchup["teams"]:
                    if team.get("team_key") == my_team_key:
                        for other_team in matchup["teams"]:
                            if other_team.get("team_key") != my_team_key:
                                opponent_team_key = other_team.get("team_key")
                                break
                        break
    
    if opponent_team_key:
        # Create optimized version with only current opponent
        optimized_data = analysis_data.copy()
        opponents = optimized_data.get("league_context", {}).get("opponents", {})
        if "opponent_analysis" in opponents:
            # Keep only current opponent
            current_opponent_only = {opponent_team_key: opponents["opponent_analysis"].get(opponent_team_key, {})}
            opponents["opponent_analysis"] = current_opponent_only
        
        optimized_json = json.dumps(optimized_data, indent=2)
        optimized_tokens = len(encoding.encode(optimized_json))
        savings = current_tokens - optimized_tokens
        print(f"  Optimized tokens: {optimized_tokens:,}")
        print(f"  Savings: {savings:,} tokens ({savings/current_tokens*100:.1f}%)")
        print(f"  Status: {'✅ Within Limit' if optimized_tokens <= 200000 else '❌ Over Limit'}")
    
    # Scenario 2: Add Sleeper and Tank01 available players
    print("\nScenario 2: Add Missing Sleeper/Tank01 Data")
    print("-" * 40)
    
    # This would require modifying the analyst_tools to include Sleeper and Tank01
    # For now, just show what we're missing
    print("  Missing: Sleeper available players data")
    print("  Missing: Tank01 available players data")
    print("  These would add significant value but also tokens")

if __name__ == "__main__":
    analyze_current_week_opponent_savings()
    analyze_missing_sleeper_tank01_data()
    calculate_optimization_scenarios()
