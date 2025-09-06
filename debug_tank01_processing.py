#!/usr/bin/env python3
"""
Debug Tank01 data processing
"""

import json
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def debug_tank01_processing():
    """Debug Tank01 data processing"""
    
    print("🔍 DEBUGGING TANK01 DATA PROCESSING")
    print("=" * 50)
    
    # Load raw Tank01 roster data
    tank01_file = "data_collection/outputs/tank01/my_roster/20250905_140736_my_roster_raw_data.json"
    with open(tank01_file, 'r') as f:
        tank01_data = json.load(f)
    
    matched_players = tank01_data.get("matched_players", [])
    print(f"Found {len(matched_players)} matched players")
    
    if matched_players:
        sample = matched_players[0]
        print(f"\nSample player keys: {list(sample.keys())}")
        
        if 'tank01_data' in sample:
            tank01_player_data = sample['tank01_data']
            print(f"Tank01 data keys: {list(tank01_player_data.keys())}")
            
            if 'fantasy_projections' in tank01_player_data:
                fantasy_projections = tank01_player_data['fantasy_projections']
                print(f"Fantasy projections keys: {list(fantasy_projections.keys())}")
                print(f"Fantasy points: {fantasy_projections.get('fantasyPoints', 'N/A')}")
                print(f"Fantasy points type: {type(fantasy_projections.get('fantasyPoints', 'N/A'))}")
                
                # Test the processing logic
                print(f"\n--- TESTING PROCESSING LOGIC ---")
                projection_data = {
                    "fantasyPoints": fantasy_projections.get("fantasyPoints"),
                    "fantasyPointsDefault": fantasy_projections.get("fantasyPointsDefault"),
                    "week_1": {
                        "fantasy_points": fantasy_projections.get("fantasyPoints"),
                        "fantasy_points_default": fantasy_projections.get("fantasyPointsDefault")
                    }
                }
                print(f"Processed projection data: {projection_data}")
                print(f"Fantasy points from processed: {projection_data.get('fantasyPoints', 'N/A')}")
                print(f"Week 1 fantasy points from processed: {projection_data.get('week_1', {}).get('fantasy_points', 'N/A')}")

if __name__ == "__main__":
    import sys
    debug_tank01_processing()
