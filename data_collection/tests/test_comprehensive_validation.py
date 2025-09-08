#!/usr/bin/env python3
"""
Comprehensive validation test for the new data processing system
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_agent import AnalystAgent
from ai_agents.comprehensive_data_processor import ComprehensiveDataProcessor

def test_comprehensive_validation():
    """Test comprehensive data processing and validation"""
    
    print("🔍 COMPREHENSIVE DATA VALIDATION TEST")
    print("=" * 60)
    
    # Use default limits
    custom_limits = {
        "QB": 20,
        "RB": 20,
        "WR": 20,
        "TE": 20,
        "K": 20,
        "DEF": 10,
        "FLEX": 15
    }
    
    print(f"Player limits: {custom_limits}")
    
    # Test 1: Validate data processor
    print(f"\n📊 Testing Comprehensive Data Processor...")
    data_processor = ComprehensiveDataProcessor(
        data_dir=os.path.join(project_root, "data_collection", "outputs"),
        player_limits=custom_limits
    )
    
    try:
        comprehensive_data = data_processor.process_all_data()
        
        print(f"✅ Data processor initialized successfully")
        print(f"   League metadata: {comprehensive_data.get('league_metadata', {}).get('league_name', 'Unknown')}")
        print(f"   My roster players: {comprehensive_data.get('my_roster', {}).get('total_players', 0)}")
        print(f"   Opponent roster players: {comprehensive_data.get('opponent_roster', {}).get('total_players', 0)}")
        print(f"   Available players: {comprehensive_data.get('available_players', {}).get('total_players', 0)}")
        print(f"   Total tokens: {comprehensive_data.get('total_tokens', 0):,}")
        
        # Validate data structure
        validate_data_structure(comprehensive_data)
        
    except Exception as e:
        print(f"❌ Data processor failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Validate analyst agent
    print(f"\n🤖 Testing Analyst Agent with Comprehensive Data...")
    agent = AnalystAgent(model_provider="anthropic", model_name="claude-opus-4-1-20250805")
    
    try:
        result = agent.analyze_with_comprehensive_data(
            user_prompt="Analyze my roster and provide specific add/drop recommendations for Week 1. For each player on my roster, provide a detailed summary based on the web research and news links provided in their Tank01 data. Include their projected fantasy points from Tank01. Focus on my starting lineup and identify the best available players to add.",
            player_limits=custom_limits,
            collect_data=False,
            model_selection=False
        )
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Analysis type: {result.get('analysis_type', 'unknown')}")
        print(f"   Model used: {result.get('model_provider')} - {result.get('model_name')}")
        print(f"   Total tokens: {result.get('total_tokens', 0):,}")
        
        # Validate output files
        validate_output_files(result)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

def validate_data_structure(comprehensive_data: dict):
    """Validate the structure of comprehensive data"""
    
    print(f"\n🔍 Validating Data Structure...")
    
    # Check required top-level keys
    required_keys = ['season_context', 'league_metadata', 'my_roster', 'opponent_roster', 'available_players', 'transaction_trends']
    for key in required_keys:
        if key not in comprehensive_data:
            print(f"   ❌ Missing required key: {key}")
        else:
            print(f"   ✅ Found key: {key}")
    
    # Check league metadata
    league_metadata = comprehensive_data.get('league_metadata', {})
    if league_metadata:
        print(f"   ✅ League name: {league_metadata.get('league_name', 'Unknown')}")
        print(f"   ✅ Team name: {league_metadata.get('team_name', 'Unknown')}")
        print(f"   ✅ Current week: {league_metadata.get('current_week', 'Unknown')}")
    
    # Check roster data
    my_roster = comprehensive_data.get('my_roster', {})
    if my_roster.get('total_players', 0) > 0:
        print(f"   ✅ My roster has {my_roster.get('total_players', 0)} players")
        # Check if players have Tank01 data
        players_by_position = my_roster.get('players_by_position', {})
        tank01_count = 0
        for position, players in players_by_position.items():
            for player in players:
                if player.get('tank01_data') and player['tank01_data'].get('projection'):
                    tank01_count += 1
        print(f"   ✅ {tank01_count} roster players have Tank01 data")
    else:
        print(f"   ❌ My roster has no players")
    
    # Check opponent data
    opponent_roster = comprehensive_data.get('opponent_roster', {})
    if opponent_roster.get('total_players', 0) > 0:
        print(f"   ✅ Opponent roster has {opponent_roster.get('total_players', 0)} players")
        print(f"   ✅ Opponent name: {opponent_roster.get('opponent_name', 'Unknown')}")
    else:
        print(f"   ❌ Opponent roster has no players")
    
    # Check available players
    available_players = comprehensive_data.get('available_players', {})
    if available_players.get('total_players', 0) > 0:
        print(f"   ✅ Available players: {available_players.get('total_players', 0)}")
        # Check if players have Tank01 data
        players_by_position = available_players.get('players_by_position', {})
        tank01_count = 0
        for position, players in players_by_position.items():
            for player in players:
                if player.get('tank01_data') and player['tank01_data'].get('projection'):
                    tank01_count += 1
        print(f"   ✅ {tank01_count} available players have Tank01 data")
    else:
        print(f"   ❌ Available players has no players")

def validate_output_files(result: dict):
    """Validate the output files"""
    
    print(f"\n📁 Validating Output Files...")
    
    saved_files = result.get('saved_files', {})
    
    # Check JSON file
    if 'json' in saved_files:
        json_file = saved_files['json']
        if os.path.exists(json_file):
            print(f"   ✅ JSON file created: {os.path.basename(json_file)}")
            # Check file size
            size = os.path.getsize(json_file)
            print(f"   ✅ JSON file size: {size:,} bytes")
        else:
            print(f"   ❌ JSON file not found: {json_file}")
    
    # Check markdown file
    if 'markdown' in saved_files:
        markdown_file = saved_files['markdown']
        if os.path.exists(markdown_file):
            print(f"   ✅ Markdown file created: {os.path.basename(markdown_file)}")
            # Check file size
            size = os.path.getsize(markdown_file)
            print(f"   ✅ Markdown file size: {size:,} bytes")
        else:
            print(f"   ❌ Markdown file not found: {markdown_file}")
    
    # Check player data file
    if 'player_data' in saved_files:
        player_data_file = saved_files['player_data']
        if os.path.exists(player_data_file):
            print(f"   ✅ Player data file created: {os.path.basename(player_data_file)}")
            # Check file size
            size = os.path.getsize(player_data_file)
            print(f"   ✅ Player data file size: {size:,} bytes")
        else:
            print(f"   ❌ Player data file not found: {player_data_file}")

if __name__ == "__main__":
    import os
    test_comprehensive_validation()
