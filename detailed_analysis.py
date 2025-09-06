#!/usr/bin/env python3
"""
Detailed analysis of what's actually being sent to the LLM
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_tools import AnalystTools
import tiktoken

def analyze_league_context():
    """Analyze what's in the league context section"""
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("DETAILED LEAGUE CONTEXT ANALYSIS")
    print("=" * 50)
    
    league_context = analysis_data.get("league_context", {})
    
    for section_name, section_data in league_context.items():
        section_json = json.dumps(section_data, indent=2)
        section_tokens = len(encoding.encode(section_json))
        
        print(f"\n{section_name.upper()}:")
        print(f"  Tokens: {section_tokens:,}")
        
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if isinstance(value, (list, dict)):
                    value_json = json.dumps(value, indent=2)
                    value_tokens = len(encoding.encode(value_json))
                    print(f"    {key}: {value_tokens:,} tokens")
                    
                    # If it's a list, show how many items
                    if isinstance(value, list):
                        print(f"      ({len(value)} items)")
                        
                        # Show sample of first few items
                        if len(value) > 0 and isinstance(value[0], dict):
                            sample = value[:2]  # First 2 items
                            sample_json = json.dumps(sample, indent=2)
                            sample_tokens = len(encoding.encode(sample_json))
                            print(f"      Sample (first 2): {sample_tokens:,} tokens")
                            
                            # Show what fields are in each item
                            if sample:
                                fields = list(sample[0].keys())
                                print(f"      Fields per item: {fields}")

def analyze_available_players_detail():
    """Analyze available players in detail"""
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("\n\nDETAILED AVAILABLE PLAYERS ANALYSIS")
    print("=" * 50)
    
    available_players = analysis_data.get("available_players", {})
    
    for api, data in available_players.items():
        print(f"\n{api.upper()}:")
        
        if "top_players_by_position" in data:
            positions = data["top_players_by_position"]
            total_players = sum(len(players) for players in positions.values() if isinstance(players, list))
            print(f"  Total players: {total_players}")
            
            for position, players in positions.items():
                if isinstance(players, list) and players:
                    position_json = json.dumps(players, indent=2)
                    position_tokens = len(encoding.encode(position_json))
                    print(f"    {position}: {len(players)} players, {position_tokens:,} tokens")
                    
                    # Show sample player structure
                    if players:
                        sample_player = players[0]
                        sample_json = json.dumps(sample_player, indent=2)
                        sample_tokens = len(encoding.encode(sample_json))
                        print(f"      Sample player: {sample_tokens} tokens")
                        print(f"      Player fields: {list(sample_player.keys())}")

def analyze_roster_analysis():
    """Analyze roster analysis in detail"""
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("\n\nDETAILED ROSTER ANALYSIS")
    print("=" * 50)
    
    roster_analysis = analysis_data.get("roster_analysis", {})
    
    for api, data in roster_analysis.items():
        print(f"\n{api.upper()}:")
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    value_json = json.dumps(value, indent=2)
                    value_tokens = len(encoding.encode(value_json))
                    print(f"  {key}: {value_tokens:,} tokens")
                    
                    if isinstance(value, list) and value:
                        print(f"    ({len(value)} items)")
                        
                        # Show sample
                        if len(value) > 0 and isinstance(value[0], dict):
                            sample = value[:1]  # First item
                            sample_json = json.dumps(sample, indent=2)
                            sample_tokens = len(encoding.encode(sample_json))
                            print(f"    Sample: {sample_tokens} tokens")

if __name__ == "__main__":
    analyze_league_context()
    analyze_available_players_detail()
    analyze_roster_analysis()
