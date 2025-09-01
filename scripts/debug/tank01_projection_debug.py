#!/usr/bin/env python3
"""
Debug Tank01 projection parsing to understand why projections aren't being extracted.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.external.tank01_client import Tank01Client

def debug_tank01_projections():
    """Debug Tank01 projection parsing."""
    print("🔍 TANK01 PROJECTION PARSING DEBUG")
    print("=" * 50)
    
    try:
        # Initialize Tank01 client
        tank01_client = Tank01Client()
        
        # Test with Joe Burrow (we know his Tank01 ID is 3915511)
        player_id = "3915511"
        player_name = "Joe Burrow"
        
        print(f"📊 Getting projections for {player_name} (ID: {player_id})")
        
        # Get fantasy projections
        projections = tank01_client.get_fantasy_projections(
            player_id=player_id,
            scoring_settings={'fantasyPoints': 'true'}
        )
        
        if not projections:
            print("❌ No projections returned")
            return
        
        print(f"✅ Projections retrieved. Keys: {list(projections.keys())}")
        
        if 'body' in projections:
            proj_data = projections['body']
            print(f"📋 Body type: {type(proj_data)}")
            
            if isinstance(proj_data, dict):
                print(f"📋 Body keys: {list(proj_data.keys())}")
                
                # Extract projected points
                total_points = 0
                valid_games = 0
                
                print("\n🎯 PARSING PROJECTION DATA:")
                print("-" * 30)
                
                for game_key, game_data in proj_data.items():
                    print(f"Game {game_key}: {type(game_data)}")
                    
                    if isinstance(game_data, dict):
                        print(f"  Keys: {list(game_data.keys())}")
                        
                        if 'fantasyPoints' in game_data:
                            fantasy_points = game_data.get('fantasyPoints')
                            print(f"  Fantasy Points: {fantasy_points} (type: {type(fantasy_points)})")
                            
                            if fantasy_points:
                                try:
                                    pts = float(fantasy_points)
                                    if pts > 0:  # Only count positive projections
                                        total_points += pts
                                        valid_games += 1
                                        print(f"    ✅ Added {pts} points")
                                    else:
                                        print(f"    ❌ Skipped {pts} (non-positive)")
                                except (ValueError, TypeError) as e:
                                    print(f"    ❌ Error converting to float: {e}")
                        else:
                            print("  ❌ No 'fantasyPoints' key")
                    else:
                        print(f"  ❌ Game data is not dict: {game_data}")
                
                print(f"\n📊 SUMMARY:")
                print(f"Total points: {total_points}")
                print(f"Valid games: {valid_games}")
                
                if valid_games > 0:
                    avg_points = total_points / valid_games
                    print(f"Average projected points: {avg_points:.1f}")
                else:
                    print("❌ No valid games found")
            else:
                print(f"❌ Body is not dict: {proj_data}")
        else:
            print("❌ No 'body' key in projections")
        
        # Save raw response for analysis
        debug_dir = Path("analysis/debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        raw_file = debug_dir / f"tank01_projection_{player_name.replace(' ', '_')}_raw.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(projections, f, indent=2, default=str)
        
        print(f"\n✅ Raw projection data saved to: {raw_file}")
        
    except Exception as e:
        print(f"❌ Error debugging Tank01 projections: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tank01_projections()
