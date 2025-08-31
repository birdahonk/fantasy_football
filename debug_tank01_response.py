#!/usr/bin/env python3
"""
Debug Tank01 fantasy points response structure.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.external.tank01_client import Tank01Client

def main():
    """Debug Tank01 fantasy points response."""
    print("🔍 Debugging Tank01 Fantasy Points Response")
    print("=" * 50)
    
    try:
        client = Tank01Client()
        
        # Test with Joe Burrow
        joe_burrow_id = "3915511"
        
        print(f"📊 Getting fantasy projections for Joe Burrow (ID: {joe_burrow_id})")
        
        projections = client.get_fantasy_projections(
            player_id=joe_burrow_id,
            scoring_settings={
                'fantasyPoints': 'true',  # CRITICAL: Enable fantasy points!
                'passYards': 0.04,
                'passTD': 4,
                'passInterceptions': -2,
                'rushYards': 0.1,
                'rushTD': 6,
                'receivingYards': 0.1,
                'receivingTD': 6,
                'pointsPerReception': 1,
                'fumbles': -2
            }
        )
        
        if projections and 'body' in projections:
            print("✅ Fantasy projections retrieved!")
            body = projections['body']
            
            if isinstance(body, dict):
                print(f"📄 Found {len(body)} games")
                
                # Look at the first few games
                game_keys = list(body.keys())[:3]
                
                for game_key in game_keys:
                    print(f"\n🏈 Game: {game_key}")
                    game_data = body[game_key]
                    
                    if isinstance(game_data, dict):
                        print(f"   Keys: {list(game_data.keys())}")
                        
                        # Look for fantasy points
                        if 'fantasyPoints' in game_data:
                            print(f"   ✅ fantasyPoints: {game_data['fantasyPoints']}")
                        else:
                            print("   ❌ No 'fantasyPoints' field")
                        
                        if 'fantasyPointsDefault' in game_data:
                            print(f"   ✅ fantasyPointsDefault: {game_data['fantasyPointsDefault']}")
                        else:
                            print("   ❌ No 'fantasyPointsDefault' field")
                        
                        # Show all top-level fields
                        print("   📋 All fields:")
                        for key, value in game_data.items():
                            if isinstance(value, (str, int, float)):
                                print(f"      {key}: {value}")
                            else:
                                print(f"      {key}: {type(value)}")
            
            # Save full response for examination
            client.save_debug_data(projections, "joe_burrow_debug.json")
            print(f"\n💾 Full response saved to debug_joe_burrow_debug.json")
        else:
            print("❌ No projections data received")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
