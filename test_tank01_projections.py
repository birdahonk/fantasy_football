#!/usr/bin/env python3
"""
Quick test to verify Tank01 fantasy projections are working.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.external.tank01_client import Tank01Client

def main():
    """Test Tank01 fantasy projections."""
    print("🏈 Testing Tank01 Fantasy Projections")
    print("=" * 40)
    
    try:
        client = Tank01Client()
        
        # Test with Joe Burrow's ID from our matching test
        joe_burrow_id = "3915511"
        
        print(f"📊 Testing fantasy projections for Joe Burrow (ID: {joe_burrow_id})")
        
        projections = client.get_fantasy_projections(
            player_id=joe_burrow_id,
            scoring_settings={
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
            
            print(f"📄 Response type: {type(body)}")
            if isinstance(body, dict):
                print(f"📄 Keys available: {list(body.keys())}")
                # Look for fantasy points
                for field in ['projectedFantasyPoints', 'fantasyPoints', 'totalPoints', 'points']:
                    if field in body:
                        print(f"🎯 Found {field}: {body[field]}")
            elif isinstance(body, list):
                print(f"📄 List with {len(body)} items")
                if body:
                    first_item = body[0]
                    if isinstance(first_item, dict):
                        print(f"📄 First item keys: {list(first_item.keys())}")
            
            # Save for debugging
            client.save_debug_data(projections, "joe_burrow_projections.json")
            print("💾 Debug data saved to debug_joe_burrow_projections.json")
        else:
            print("❌ No projections data received")
        
        # Test game stats as backup
        print(f"\n📈 Testing game stats for Joe Burrow (ID: {joe_burrow_id})")
        
        game_stats = client.get_player_game_stats(
            player_id=joe_burrow_id,
            season="2024"
        )
        
        if game_stats and 'body' in game_stats:
            print("✅ Game stats retrieved!")
            body = game_stats['body']
            
            print(f"📄 Response type: {type(body)}")
            if isinstance(body, list):
                print(f"📄 {len(body)} games found")
                if body:
                    recent_game = body[0]
                    if isinstance(recent_game, dict):
                        print(f"📄 Recent game keys: {list(recent_game.keys())}")
                        for field in ['fantasyPoints', 'points', 'totalPoints']:
                            if field in recent_game:
                                print(f"🎯 Found {field}: {recent_game[field]}")
            
            # Save for debugging
            client.save_debug_data(game_stats, "joe_burrow_game_stats.json")
            print("💾 Debug data saved to debug_joe_burrow_game_stats.json")
        else:
            print("❌ No game stats data received")
        
        print(f"\n📊 API Usage: {client.get_usage_info()['calls_made_this_session']}/1000 calls used")
        
    except Exception as e:
        print(f"❌ Error testing projections: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
