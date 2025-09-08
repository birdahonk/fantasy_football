#!/usr/bin/env python3
"""
Debug roster data extraction
"""

import sys
from pathlib import Path
import json

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_agent import AnalystAgent
from ai_agents.analyst_tools import AnalystTools

def debug_roster_data():
    """Debug what's happening with roster data"""
    
    print("🔍 DEBUGGING ROSTER DATA EXTRACTION")
    print("=" * 40)
    
    # Initialize tools
    tools = AnalystTools()
    
    # Get roster analysis
    print("1. Getting roster analysis...")
    roster_analysis = tools.analyze_recent_data()
    
    print(f"Roster analysis keys: {list(roster_analysis.keys())}")
    
    if "roster_analysis" in roster_analysis:
        print(f"Roster analysis structure:")
        for api, data in roster_analysis["roster_analysis"].items():
            print(f"  {api}: {type(data)}")
            if isinstance(data, dict):
                print(f"    Keys: {list(data.keys())}")
                if "players" in data:
                    print(f"    Players count: {len(data['players'])}")
                    if data["players"]:
                        print(f"    Sample player: {data['players'][0].keys()}")
    
    # Test roster summary extraction
    print("\n2. Testing roster summary extraction...")
    agent = AnalystAgent()
    my_roster_summary = agent._extract_roster_summary(roster_analysis)
    
    print(f"Roster summary structure:")
    print(json.dumps(my_roster_summary, indent=2))
    
    # Check if my_roster is empty
    if "my_roster" in my_roster_summary:
        print(f"\nMy roster APIs: {list(my_roster_summary['my_roster'].keys())}")
        for api, data in my_roster_summary["my_roster"].items():
            print(f"  {api}: {data.get('total_players', 0)} players")
            if data.get('players'):
                print(f"    Sample: {data['players'][0]}")
    else:
        print("❌ No 'my_roster' key found in summary!")

if __name__ == "__main__":
    debug_roster_data()
