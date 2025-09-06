#!/usr/bin/env python3
"""
Data Compilation Validation - Test data gathering and organization without AI model calls
"""

import sys
import json
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.comprehensive_data_processor import ComprehensiveDataProcessor

def test_data_compilation():
    """Test comprehensive data compilation and organization"""
    
    print("🔍 COMPREHENSIVE DATA COMPILATION VALIDATION")
    print("=" * 70)
    
    # Use default limits
    from config.player_limits import DEFAULT_PLAYER_LIMITS
    custom_limits = DEFAULT_PLAYER_LIMITS
    
    print(f"Player limits: {custom_limits}")
    
    # Initialize data processor
    print(f"\n📊 Initializing Comprehensive Data Processor...")
    data_processor = ComprehensiveDataProcessor(
        data_dir=os.path.join(project_root, "data_collection", "outputs"),
        player_limits=custom_limits
    )
    
    # Process all data
    print(f"\n🔄 Processing all data sources...")
    try:
        comprehensive_data = data_processor.process_all_data()
        print(f"✅ Data processing completed successfully!")
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Validate and display results
    print(f"\n📋 VALIDATION RESULTS")
    print("=" * 50)
    
    # 1. League Metadata
    validate_league_metadata(comprehensive_data)
    
    # 2. My Roster Data
    validate_my_roster_data(comprehensive_data)
    
    # 3. Opponent Roster Data
    validate_opponent_roster_data(comprehensive_data)
    
    # 4. Available Players Data
    validate_available_players_data(comprehensive_data)
    
    # 5. Transaction Trends Data
    validate_transaction_trends_data(comprehensive_data)
    
    # 6. Data Files
    validate_data_files(comprehensive_data)
    
    # 7. Save sample outputs
    save_sample_outputs(comprehensive_data)
    
    print(f"\n✅ DATA COMPILATION VALIDATION COMPLETE!")

def validate_league_metadata(comprehensive_data):
    """Validate league metadata"""
    print(f"\n🏈 LEAGUE METADATA VALIDATION")
    print("-" * 30)
    
    league_metadata = comprehensive_data.get("league_metadata", {})
    season_context = comprehensive_data.get("season_context", {})
    
    print(f"League Name: {league_metadata.get('league_name', '❌ MISSING')}")
    print(f"Team Name: {league_metadata.get('team_name', '❌ MISSING')}")
    print(f"Current Week: {league_metadata.get('current_week', '❌ MISSING')}")
    print(f"NFL Season: {season_context.get('nfl_season', '❌ MISSING')}")
    print(f"Season Phase: {season_context.get('season_phase', '❌ MISSING')}")
    
    # Check if we have the required data
    required_fields = ['league_name', 'team_name', 'current_week', 'nfl_season']
    missing_fields = [field for field in required_fields if not league_metadata.get(field) and not season_context.get(field)]
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
    else:
        print(f"✅ All required league metadata present")

def validate_my_roster_data(comprehensive_data):
    """Validate my roster data"""
    print(f"\n👤 MY ROSTER DATA VALIDATION")
    print("-" * 30)
    
    my_roster = comprehensive_data.get("my_roster", {})
    players_by_position = my_roster.get("players_by_position", {})
    total_players = my_roster.get("total_players", 0)
    team_name = my_roster.get("team_name", "Unknown")
    league_name = my_roster.get("league_name", "Unknown")
    
    print(f"Total Roster Players: {total_players}")
    print(f"Team Name: {team_name}")
    print(f"League Name: {league_name}")
    
    if total_players == 0:
        print(f"❌ No roster players found!")
        return
    
    # Check starting lineup
    starting_lineup = players_by_position.get("starting_lineup", {})
    bench_players = players_by_position.get("bench_players", {})
    
    print(f"  Starting Lineup: {sum(len(players) for players in starting_lineup.values())} players")
    for position, players in starting_lineup.items():
        print(f"    {position}: {len(players)} players")
        
        # Check enrichment data for first few players
        for i, player in enumerate(players[:2]):  # Check first 2 players per position
            print(f"      Player {i+1}: {player.get('yahoo_data', {}).get('name', {}).get('full', 'Unknown')}")
            
            # Check Tank01 data
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                projection = player['tank01_data']['projection']
                # Check for different projection formats
                fantasy_points = (projection.get('fantasyPoints') or 
                                projection.get('fantasy_points') or 
                                projection.get('week_1', {}).get('fantasy_points') or 
                                'N/A')
                print(f"        ✅ Tank01: {fantasy_points} projected points")
            else:
                print(f"        ❌ Tank01: No projection data")
            
            # Check Sleeper data
            if player.get('sleeper_data'):
                print(f"        ✅ Sleeper: {player['sleeper_data'].get('player_id', 'N/A')} ID")
            else:
                print(f"        ❌ Sleeper: No data")
    
    print(f"  Bench Players: {sum(len(players) for players in bench_players.values())} players")
    for position, players in bench_players.items():
        print(f"    {position}: {len(players)} players")
        
        # Check enrichment data for first few players
        for i, player in enumerate(players[:2]):  # Check first 2 players per position
            print(f"      Player {i+1}: {player.get('yahoo_data', {}).get('name', {}).get('full', 'Unknown')}")
            
            # Check Tank01 data
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                projection = player['tank01_data']['projection']
                # Check for different projection formats
                fantasy_points = (projection.get('fantasyPoints') or 
                                projection.get('fantasy_points') or 
                                projection.get('week_1', {}).get('fantasy_points') or 
                                'N/A')
                print(f"        ✅ Tank01: {fantasy_points} projected points")
            else:
                print(f"        ❌ Tank01: No projection data")
            
            # Check Sleeper data
            if player.get('sleeper_data'):
                print(f"        ✅ Sleeper: {player['sleeper_data'].get('player_id', 'N/A')} ID")
            else:
                print(f"        ❌ Sleeper: No data")
    
    # Count total enriched players
    tank01_enriched_count = 0
    sleeper_enriched_count = 0
    
    for players in starting_lineup.values():
        for player in players:
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                tank01_enriched_count += 1
            if player.get('sleeper_data'):
                sleeper_enriched_count += 1
    
    for players in bench_players.values():
        for player in players:
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                tank01_enriched_count += 1
            if player.get('sleeper_data'):
                sleeper_enriched_count += 1
    
    print(f"\nEnrichment Summary:")
    print(f"  Tank01 enriched: {tank01_enriched_count}/{total_players} players")
    print(f"  Sleeper enriched: {sleeper_enriched_count}/{total_players} players")
    
    if tank01_enriched_count == 0:
        print(f"❌ CRITICAL: No roster players have Tank01 data!")
    else:
        print(f"✅ {tank01_enriched_count} roster players have Tank01 data")

def validate_opponent_roster_data(comprehensive_data):
    """Validate opponent roster data"""
    print(f"\n⚔️ OPPONENT ROSTER DATA VALIDATION")
    print("-" * 30)
    
    opponent_roster = comprehensive_data.get("opponent_roster", {})
    players_by_position = opponent_roster.get("players_by_position", {})
    total_players = opponent_roster.get("total_players", 0)
    opponent_name = opponent_roster.get("opponent_name", "Unknown")
    
    print(f"Opponent Name: {opponent_name}")
    print(f"Total Opponent Players: {total_players}")
    
    if total_players == 0:
        print(f"❌ No opponent players found!")
        return
    
    # Check starting lineup
    starting_lineup = players_by_position.get("starting_lineup", {})
    bench_players = players_by_position.get("bench_players", {})
    
    print(f"  Starting Lineup: {sum(len(players) for players in starting_lineup.values())} players")
    for position, players in starting_lineup.items():
        print(f"    {position}: {len(players)} players")
        
        # Check enrichment data for first player
        if players:
            player = players[0]
            print(f"      Sample: {player.get('yahoo_data', {}).get('name', {}).get('full', 'Unknown')}")
            
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                projection = player['tank01_data']['projection']
                fantasy_points = projection.get('fantasyPoints', 'N/A')
                print(f"        ✅ Tank01: {fantasy_points} projected points")
            else:
                print(f"        ❌ Tank01: No projection data")
            
            if player.get('sleeper_data'):
                print(f"        ✅ Sleeper: {player['sleeper_data'].get('player_id', 'N/A')} ID")
            else:
                print(f"        ❌ Sleeper: No data")
    
    print(f"  Bench Players: {sum(len(players) for players in bench_players.values())} players")
    for position, players in bench_players.items():
        print(f"    {position}: {len(players)} players")
        
        # Check enrichment data for first player
        if players:
            player = players[0]
            print(f"      Sample: {player.get('yahoo_data', {}).get('name', {}).get('full', 'Unknown')}")
            
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                projection = player['tank01_data']['projection']
                fantasy_points = projection.get('fantasyPoints', 'N/A')
                print(f"        ✅ Tank01: {fantasy_points} projected points")
            else:
                print(f"        ❌ Tank01: No projection data")
            
            if player.get('sleeper_data'):
                print(f"        ✅ Sleeper: {player['sleeper_data'].get('player_id', 'N/A')} ID")
            else:
                print(f"        ❌ Sleeper: No data")
    
    print(f"✅ Opponent roster data loaded successfully")

def validate_available_players_data(comprehensive_data):
    """Validate available players data"""
    print(f"\n🆓 AVAILABLE PLAYERS DATA VALIDATION")
    print("-" * 30)
    
    available_players = comprehensive_data.get("available_players", {})
    players_by_position = available_players.get("players_by_position", {})
    total_players = available_players.get("total_players", 0)
    
    print(f"Total Available Players: {total_players}")
    
    if total_players == 0:
        print(f"❌ No available players found!")
        return
    
    # Count players by position
    tank01_enriched_count = 0
    sleeper_enriched_count = 0
    
    for position, players in players_by_position.items():
        print(f"  {position}: {len(players)} players")
        
        # Check enrichment data for first player
        if players:
            player = players[0]
            print(f"    Sample: {player.get('yahoo_data', {}).get('name', {}).get('full', 'Unknown')}")
            
            if player.get('tank01_data') and player['tank01_data'].get('projection'):
                tank01_enriched_count += 1
                projection = player['tank01_data']['projection']
                # Check for different projection formats
                fantasy_points = (projection.get('fantasyPoints') or 
                                projection.get('fantasy_points') or 
                                projection.get('week_1', {}).get('fantasy_points') or 
                                'N/A')
                print(f"      ✅ Tank01: {fantasy_points} projected points")
            else:
                print(f"      ❌ Tank01: No projection data")
            
            if player.get('sleeper_data'):
                sleeper_enriched_count += 1
                print(f"      ✅ Sleeper: {player['sleeper_data'].get('player_id', 'N/A')} ID")
            else:
                print(f"      ❌ Sleeper: No data")
    
    print(f"\nEnrichment Summary:")
    print(f"  Tank01 enriched: {tank01_enriched_count}/{total_players} players")
    print(f"  Sleeper enriched: {sleeper_enriched_count}/{total_players} players")
    
    if tank01_enriched_count == 0:
        print(f"❌ CRITICAL: No available players have Tank01 data!")
    else:
        print(f"✅ {tank01_enriched_count} available players have Tank01 data")

def validate_transaction_trends_data(comprehensive_data):
    """Validate transaction trends data"""
    print(f"\n📈 TRANSACTION TRENDS DATA VALIDATION")
    print("-" * 30)
    
    transaction_trends = comprehensive_data.get("transaction_trends", {})
    
    if not transaction_trends:
        print(f"❌ No transaction trends data found!")
        return
    
    print(f"✅ Transaction trends data loaded")
    print(f"  Keys: {list(transaction_trends.keys())}")
    
    # Check for specific transaction data
    if 'transaction_trends' in transaction_trends:
        trends = transaction_trends['transaction_trends']
        print(f"  Transaction trends count: {len(trends) if isinstance(trends, list) else 'N/A'}")
    else:
        print(f"  No 'transaction_trends' key found")

def validate_data_files(comprehensive_data):
    """Validate data files"""
    print(f"\n📁 DATA FILES VALIDATION")
    print("-" * 30)
    
    data_files = comprehensive_data.get("data_files", {})
    
    required_files = [
        'yahoo_roster', 'sleeper_roster', 'tank01_roster',
        'yahoo_opponents', 'yahoo_available', 'sleeper_available', 'tank01_available',
        'yahoo_transactions'
    ]
    
    for file_type in required_files:
        file_path = data_files.get(file_type)
        if file_path and os.path.exists(file_path):
            print(f"  ✅ {file_type}: {os.path.basename(file_path)}")
        else:
            print(f"  ❌ {file_type}: Missing or not found")
    
    print(f"\nTotal data files: {len([f for f in data_files.values() if f and os.path.exists(f)])}")

def save_sample_outputs(comprehensive_data):
    """Save sample outputs for inspection"""
    print(f"\n💾 SAVING SAMPLE OUTPUTS")
    print("-" * 30)
    
    # Create validation test output directory
    from datetime import datetime
    import pytz
    
    pacific_tz = pytz.timezone('US/Pacific')
    timestamp = datetime.now(pacific_tz).strftime("%Y%m%d_%H%M%S")
    
    validation_dir = os.path.join(project_root, "data_collection", "outputs", "validation_tests")
    os.makedirs(validation_dir, exist_ok=True)
    
    # Save comprehensive data as JSON
    sample_file = os.path.join(validation_dir, f"{timestamp}_comprehensive_data.json")
    with open(sample_file, 'w') as f:
        json.dump(comprehensive_data, f, indent=2)
    
    print(f"✅ Sample data saved to: {sample_file}")
    
    # Save player data samples
    save_player_samples(comprehensive_data, validation_dir, timestamp)

def save_player_samples(comprehensive_data, validation_dir, timestamp):
    """Save player data samples for inspection"""
    
    # My roster sample
    my_roster = comprehensive_data.get("my_roster", {})
    if my_roster.get("total_players", 0) > 0:
        sample_file = os.path.join(validation_dir, f"{timestamp}_my_roster_sample.json")
        with open(sample_file, 'w') as f:
            json.dump(my_roster, f, indent=2)
        print(f"✅ My roster sample saved to: {sample_file}")
    
    # Opponent roster sample
    opponent_roster = comprehensive_data.get("opponent_roster", {})
    if opponent_roster.get("total_players", 0) > 0:
        sample_file = os.path.join(validation_dir, f"{timestamp}_opponent_roster_sample.json")
        with open(sample_file, 'w') as f:
            json.dump(opponent_roster, f, indent=2)
        print(f"✅ Opponent roster sample saved to: {sample_file}")
    
    # Available players sample (first 3 per position)
    available_players = comprehensive_data.get("available_players", {})
    if available_players.get("total_players", 0) > 0:
        sample_available = {}
        for position, players in available_players.get("players_by_position", {}).items():
            sample_available[position] = players[:3]  # First 3 players per position
        
        sample_file = os.path.join(validation_dir, f"{timestamp}_available_players_sample.json")
        with open(sample_file, 'w') as f:
            json.dump(sample_available, f, indent=2)
        print(f"✅ Available players sample saved to: {sample_file}")
    
    # Transaction trends sample
    transaction_trends = comprehensive_data.get("transaction_trends", {})
    if transaction_trends:
        sample_file = os.path.join(validation_dir, f"{timestamp}_transaction_trends_sample.json")
        with open(sample_file, 'w') as f:
            json.dump(transaction_trends, f, indent=2)
        print(f"✅ Transaction trends sample saved to: {sample_file}")

if __name__ == "__main__":
    test_data_compilation()
