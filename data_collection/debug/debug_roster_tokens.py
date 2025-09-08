#!/usr/bin/env python3
"""
Debug why opponent roster tokens are much higher than my roster tokens
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_tools import AnalystTools
import tiktoken

def debug_roster_token_discrepancy():
    """Debug the token discrepancy between my roster and opponent roster"""
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("ROSTER TOKEN DISCREPANCY DEBUG")
    print("=" * 40)
    
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    # My roster analysis
    print("\n1. MY ROSTER ANALYSIS")
    print("-" * 25)
    roster_analysis = analysis_data.get("roster_analysis", {})
    yahoo_roster = roster_analysis.get("yahoo", {})
    
    if yahoo_roster:
        yahoo_json = json.dumps(yahoo_roster, indent=2)
        yahoo_tokens = len(encoding.encode(yahoo_json))
        print(f"Yahoo roster tokens: {yahoo_tokens:,}")
        print(f"Yahoo roster structure: {list(yahoo_roster.keys())}")
        
        # Count players
        starters = yahoo_roster.get("starters", [])
        bench = yahoo_roster.get("bench", [])
        total_players = len(starters) + len(bench)
        print(f"Total players: {total_players} ({len(starters)} starters, {len(bench)} bench)")
        
        # Show sample player structure
        if starters:
            sample_player = starters[0]
            sample_json = json.dumps(sample_player, indent=2)
            sample_tokens = len(encoding.encode(sample_json))
            print(f"Sample starter tokens: {sample_tokens}")
            print(f"Sample starter fields: {list(sample_player.keys())}")
    
    # Opponent roster analysis
    print("\n2. OPPONENT ROSTER ANALYSIS")
    print("-" * 30)
    league_context = analysis_data.get("league_context", {})
    opponents = league_context.get("opponents", {})
    opponent_analysis = opponents.get("opponent_analysis", {})
    
    if opponent_analysis:
        print(f"Number of opponent teams: {len(opponent_analysis)}")
        
        # Find current opponent (Kissyface - team 5)
        current_opponent = None
        for team_name, team_data in opponent_analysis.items():
            if isinstance(team_data, dict) and team_data.get("team_key") == "461.l.595012.t.5":
                current_opponent = team_data
                print(f"Found current opponent: {team_name}")
                break
        
        if current_opponent:
            opponent_json = json.dumps(current_opponent, indent=2)
            opponent_tokens = len(encoding.encode(opponent_json))
            print(f"Current opponent tokens: {opponent_tokens:,}")
            print(f"Current opponent structure: {list(current_opponent.keys())}")
            
            # Count players
            total_players = current_opponent.get("total_players", 0)
            print(f"Total players: {total_players}")
            
            # Show position counts
            position_counts = current_opponent.get("position_counts", {})
            print(f"Position counts: {position_counts}")
            
            # Check if there's detailed player data
            if "players" in current_opponent:
                players = current_opponent["players"]
                print(f"Detailed players data: {len(players)} players")
                if players:
                    sample_player = players[0]
                    sample_json = json.dumps(sample_player, indent=2)
                    sample_tokens = len(encoding.encode(sample_json))
                    print(f"Sample opponent player tokens: {sample_tokens}")
                    print(f"Sample opponent player fields: {list(sample_player.keys())}")
        else:
            print("Could not find current opponent")
            
            # Show what we do have
            print("\nAvailable opponent teams:")
            for team_name, team_data in opponent_analysis.items():
                if isinstance(team_data, dict):
                    team_json = json.dumps(team_data, indent=2)
                    team_tokens = len(encoding.encode(team_json))
                    total_players = team_data.get("total_players", 0)
                    print(f"  {team_name}: {team_tokens:,} tokens, {total_players} players")
    
    # Check the raw opponent data file
    print("\n3. RAW OPPONENT DATA FILE")
    print("-" * 30)
    
    import glob
    import os
    
    opponent_files = glob.glob("data_collection/outputs/yahoo/opponent_rosters/**/*_raw_data.json", recursive=True)
    if opponent_files:
        latest_file = max(opponent_files, key=os.path.getctime)
        print(f"Latest opponent file: {os.path.basename(latest_file)}")
        
        with open(latest_file, 'r') as f:
            raw_data = json.load(f)
        
        print(f"Raw file structure: {list(raw_data.keys())}")
        
        # Check teams
        teams = raw_data.get("teams", [])
        print(f"Number of teams in raw file: {len(teams)}")
        
        # Check rosters
        rosters = raw_data.get("rosters", {})
        print(f"Number of rosters in raw file: {len(rosters)}")
        
        # Check one team's roster
        if teams and rosters:
            first_team = teams[0]
            team_key = first_team.get("team_key")
            team_roster = rosters.get(team_key, [])
            print(f"First team ({first_team.get('name')}): {len(team_roster)} players")
            print(f"Team roster type: {type(team_roster)}")
            print(f"Team roster content: {team_roster}")
            
            if team_roster and "players" in team_roster and len(team_roster["players"]) > 0:
                sample_player = team_roster["players"][0]
                sample_json = json.dumps(sample_player, indent=2)
                sample_tokens = len(encoding.encode(sample_json))
                print(f"Sample raw player tokens: {sample_tokens}")
                print(f"Sample raw player fields: {list(sample_player.keys())}")
            else:
                print("No players in team roster")

if __name__ == "__main__":
    debug_roster_token_discrepancy()
