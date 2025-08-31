#!/usr/bin/env python3
"""
Quick test script to verify Tank01 player matching is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.core.comprehensive_team_analyzer import ComprehensiveTeamAnalyzer

def main():
    """Test Tank01 player matching with known players."""
    print("🏈 Testing Tank01 Player Matching")
    print("=" * 40)
    
    try:
        analyzer = ComprehensiveTeamAnalyzer()
        
        # Test players from your roster
        test_players = [
            ("Joe Burrow", "CIN"),
            ("Christian McCaffrey", "SF"),
            ("Brian Thomas Jr.", "JAX"),
            ("Tee Higgins", "CIN"),
            ("Pat Freiermuth", "PIT")
        ]
        
        print(f"🔍 Testing {len(test_players)} players...")
        print()
        
        successful_matches = 0
        
        for player_name, team in test_players:
            print(f"Testing: {player_name} ({team})")
            
            tank01_id = analyzer.get_tank01_player_id(player_name, team)
            
            if tank01_id:
                print(f"  ✅ Found Tank01 ID: {tank01_id}")
                successful_matches += 1
            else:
                print(f"  ❌ No Tank01 ID found")
            print()
        
        print(f"📊 Results: {successful_matches}/{len(test_players)} players matched ({successful_matches/len(test_players)*100:.1f}%)")
        
        if successful_matches >= len(test_players) * 0.8:  # 80% success rate
            print("🎉 Tank01 player matching is working well!")
            return True
        else:
            print("⚠️ Tank01 player matching needs improvement")
            return False
        
    except Exception as e:
        print(f"❌ Error testing Tank01 matching: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
