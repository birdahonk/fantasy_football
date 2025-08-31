#!/usr/bin/env python3
"""
Test Tank01 Fantasy Projections

Test the fantasy projections endpoint with real player data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tank01_client import Tank01Client

def test_fantasy_projections():
    """Test fantasy projections with a known player."""
    print("🏈 Testing Tank01 Fantasy Projections")
    print("=" * 50)
    
    try:
        # Initialize client
        client = Tank01Client()
        
        # Test with the player ID from your example (3121422)
        # This appears to be a real player ID from the RapidAPI example
        test_player_id = "3121422"
        
        print(f"🔍 Testing fantasy projections for player ID: {test_player_id}")
        
        # Get fantasy projections
        projections = client.get_fantasy_projections(test_player_id)
        
        if projections:
            print("✅ Fantasy projections retrieved successfully!")
            
            # Check response structure
            if isinstance(projections, dict):
                print(f"📊 Response keys: {list(projections.keys())}")
                
                # Look for common fantasy data fields
                if 'body' in projections:
                    body = projections['body']
                    if isinstance(body, list) and body:
                        first_game = body[0]
                        print(f"📈 Sample game data keys: {list(first_game.keys()) if isinstance(first_game, dict) else 'Not dict'}")
                        
                        # Look for fantasy points
                        if isinstance(first_game, dict):
                            fantasy_fields = [k for k in first_game.keys() if 'fantasy' in k.lower() or 'points' in k.lower()]
                            if fantasy_fields:
                                print(f"🎯 Fantasy-related fields found: {fantasy_fields}")
                            
                            # Show some sample data
                            sample_fields = ['playerName', 'team', 'fantasyPoints', 'projectedFantasyPoints']
                            for field in sample_fields:
                                if field in first_game:
                                    print(f"   {field}: {first_game[field]}")
            
            # Save debug data
            client.save_debug_data(projections, "tank01_fantasy_projections.json")
            print(f"💾 Debug data saved to debug_tank01_fantasy_projections.json")
            
        else:
            print("❌ No projections data received")
        
        # Show usage
        usage = client.get_usage_info()
        print(f"\n📊 API Usage: {usage['calls_made_this_session']}/{usage['monthly_limit']} calls")
        
    except Exception as e:
        print(f"❌ Error testing fantasy projections: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run fantasy projections test."""
    test_fantasy_projections()
    print("\n✅ Fantasy projections test completed!")

if __name__ == "__main__":
    main()
