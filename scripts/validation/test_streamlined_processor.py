#!/usr/bin/env python3
"""
Test Streamlined Comprehensive Data Processor

Tests the updated comprehensive data processor with streamlined data approach
and validates token usage.
"""

import os
import sys
import json
import tiktoken
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from ai_agents.comprehensive_data_processor import ComprehensiveDataProcessor
from config.player_limits import DEFAULT_PLAYER_LIMITS

def calculate_tokens(text: str) -> int:
    """Calculate tokens using tiktoken"""
    try:
        encoding = tiktoken.get_encoding('cl100k_base')
        return len(encoding.encode(text))
    except ImportError:
        # Fallback to rough estimate
        return len(text) // 4

def test_streamlined_processor():
    """Test the streamlined comprehensive data processor"""
    
    print("🧪 TESTING STREAMLINED COMPREHENSIVE DATA PROCESSOR")
    print("=" * 60)
    
    try:
        # Initialize processor
        data_dir = os.path.join(project_root, "data_collection", "outputs")
        processor = ComprehensiveDataProcessor(data_dir, DEFAULT_PLAYER_LIMITS)
        
        # Process all data
        print("Processing comprehensive data...")
        comprehensive_data = processor.process_all_data()
        
        if not comprehensive_data:
            print("❌ Failed to process comprehensive data")
            return False
        
        print("✅ Comprehensive data processed successfully")
        
        # Calculate token usage
        print("\n📊 TOKEN USAGE ANALYSIS")
        print("-" * 40)
        
        # Convert to JSON for token calculation
        comprehensive_json = json.dumps(comprehensive_data, indent=2)
        total_tokens = calculate_tokens(comprehensive_json)
        
        print(f"Total tokens: {total_tokens:,}")
        print(f"Token limit: 200,000")
        
        if total_tokens <= 200000:
            remaining = 200000 - total_tokens
            print(f"✅ Within limit! {remaining:,} tokens remaining")
        else:
            excess = total_tokens - 200000
            print(f"❌ Over limit by {excess:,} tokens")
        
        # Analyze sections
        print(f"\n📈 SECTION BREAKDOWN")
        print("-" * 40)
        
        sections = {
            'my_roster': comprehensive_data.get('my_roster', {}),
            'opponent_roster': comprehensive_data.get('opponent_roster', {}),
            'available_players': comprehensive_data.get('available_players', {}),
            'nfl_matchups': comprehensive_data.get('nfl_matchups', {}),
            'season_context': comprehensive_data.get('season_context', {}),
            'league_metadata': comprehensive_data.get('league_metadata', {})
        }
        
        for section_name, section_data in sections.items():
            section_json = json.dumps(section_data, indent=2)
            section_tokens = calculate_tokens(section_json)
            percentage = (section_tokens / total_tokens) * 100
            print(f"{section_name:20s}: {section_tokens:8,} tokens ({percentage:5.1f}%)")
        
        # Validate player data structure
        print(f"\n🔍 DATA VALIDATION")
        print("-" * 40)
        
        # Check my roster
        my_roster = comprehensive_data.get('my_roster', {})
        my_players = my_roster.get('players_by_position', {})
        my_total = sum(len(players) for position_group in my_players.values() 
                      for players in position_group.values() if isinstance(players, list))
        print(f"My roster players: {my_total}")
        
        # Check opponent roster
        opponent_roster = comprehensive_data.get('opponent_roster', {})
        opp_players = opponent_roster.get('players_by_position', {})
        opp_total = sum(len(players) for position_group in opp_players.values() 
                       for players in position_group.values() if isinstance(players, list))
        print(f"Opponent roster players: {opp_total}")
        
        # Check available players
        available_players = comprehensive_data.get('available_players', {})
        avail_players = available_players.get('players_by_position', {})
        avail_total = sum(len(players) for players in avail_players.values() if isinstance(players, list))
        print(f"Available players: {avail_total}")
        
        # Check sample player structure
        if my_players:
            first_position = list(my_players.keys())[0]
            first_group = list(my_players[first_position].values())[0]
            if first_group and len(first_group) > 0:
                sample_player = first_group[0]
                print(f"\nSample player structure:")
                print(f"  Name: {sample_player.get('name', 'Unknown')}")
                print(f"  Position: {sample_player.get('position', 'Unknown')}")
                print(f"  Team: {sample_player.get('team', 'Unknown')}")
                print(f"  Fantasy points: {sample_player.get('fantasy_points', 'N/A')}")
                print(f"  Keys: {list(sample_player.keys())}")
                
                # Check for essential fields
                essential_fields = ['name', 'position', 'team', 'bye_week', 'injury_status', 
                                  'percent_owned', 'fantasy_points', 'fantasy_points_default']
                missing_fields = [field for field in essential_fields if field not in sample_player]
                if missing_fields:
                    print(f"  ⚠️  Missing essential fields: {missing_fields}")
                else:
                    print(f"  ✅ All essential fields present")
        
        # Save test output
        output_dir = os.path.join(project_root, "data_collection", "outputs", "validation_tests", "2025", "09", "08")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{timestamp}_streamlined_processor_test.json")
        
        with open(output_file, 'w') as f:
            json.dump(comprehensive_data, f, indent=2)
        
        print(f"\n💾 Test output saved to: {output_file}")
        
        return total_tokens <= 200000
        
    except Exception as e:
        print(f"❌ Error testing streamlined processor: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_streamlined_processor()
    
    if success:
        print(f"\n🎉 SUCCESS: Streamlined processor is working within token limits!")
    else:
        print(f"\n❌ FAILED: Streamlined processor needs further optimization")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
