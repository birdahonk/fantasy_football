#!/usr/bin/env python3
"""
Validate Streamlined Data Structure

Comprehensive validation of the streamlined processor output to ensure
all essential data is present and correctly structured.
"""

import json
import os
from collections import defaultdict

def validate_streamlined_data(file_path):
    """Validate the streamlined data structure"""
    
    print("🔍 VALIDATING STREAMLINED DATA STRUCTURE")
    print("=" * 60)
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check top-level structure
        print("📋 TOP-LEVEL STRUCTURE")
        print("-" * 40)
        required_sections = ['season_context', 'league_metadata', 'my_roster', 
                           'opponent_roster', 'available_players', 'nfl_matchups', 
                           'data_sources', 'processing_timestamp']
        
        for section in required_sections:
            if section in data:
                print(f"✅ {section}: Present")
            else:
                print(f"❌ {section}: Missing")
        
        # Validate season context
        print(f"\n📅 SEASON CONTEXT VALIDATION")
        print("-" * 40)
        season_context = data.get('season_context', {})
        print(f"Current week: {season_context.get('current_week', 'Missing')}")
        print(f"NFL season: {season_context.get('nfl_season', 'Missing')}")
        print(f"Season phase: {season_context.get('season_phase', 'Missing')}")
        
        # Validate league metadata
        print(f"\n🏈 LEAGUE METADATA VALIDATION")
        print("-" * 40)
        league_metadata = data.get('league_metadata', {})
        print(f"League name: {league_metadata.get('league_name', 'Missing')}")
        print(f"Team name: {league_metadata.get('team_name', 'Missing')}")
        print(f"Team key: {league_metadata.get('team_key', 'Missing')}")
        
        # Validate my roster structure
        print(f"\n👥 MY ROSTER VALIDATION")
        print("-" * 40)
        my_roster = data.get('my_roster', {})
        players_by_position = my_roster.get('players_by_position', {})
        
        starting_lineup = players_by_position.get('starting_lineup', {})
        bench_players = players_by_position.get('bench_players', {})
        
        print(f"Starting lineup positions: {list(starting_lineup.keys())}")
        print(f"Bench players positions: {list(bench_players.keys())}")
        
        # Count players
        total_starting = sum(len(players) for players in starting_lineup.values() if isinstance(players, list))
        total_bench = sum(len(players) for players in bench_players.values() if isinstance(players, list))
        total_my_roster = total_starting + total_bench
        
        print(f"Total starting players: {total_starting}")
        print(f"Total bench players: {total_bench}")
        print(f"Total my roster players: {total_my_roster}")
        
        # Validate opponent roster structure
        print(f"\n⚔️ OPPONENT ROSTER VALIDATION")
        print("-" * 40)
        opponent_roster = data.get('opponent_roster', {})
        opp_players_by_position = opponent_roster.get('players_by_position', {})
        
        opp_starting_lineup = opp_players_by_position.get('starting_lineup', {})
        opp_bench_players = opp_players_by_position.get('bench_players', {})
        
        print(f"Opponent name: {opponent_roster.get('opponent_name', 'Missing')}")
        print(f"Opponent starting positions: {list(opp_starting_lineup.keys())}")
        print(f"Opponent bench positions: {list(opp_bench_players.keys())}")
        
        total_opp_starting = sum(len(players) for players in opp_starting_lineup.values() if isinstance(players, list))
        total_opp_bench = sum(len(players) for players in opp_bench_players.values() if isinstance(players, list))
        total_opp_roster = total_opp_starting + total_opp_bench
        
        print(f"Total opponent starting players: {total_opp_starting}")
        print(f"Total opponent bench players: {total_opp_bench}")
        print(f"Total opponent roster players: {total_opp_roster}")
        
        # Validate available players structure
        print(f"\n🆓 AVAILABLE PLAYERS VALIDATION")
        print("-" * 40)
        available_players = data.get('available_players', {})
        avail_players_by_position = available_players.get('players_by_position', {})
        
        print(f"Available player positions: {list(avail_players_by_position.keys())}")
        
        total_available = sum(len(players) for players in avail_players_by_position.values() if isinstance(players, list))
        print(f"Total available players: {total_available}")
        
        # Validate player data structure (using first player from my roster)
        print(f"\n🔍 PLAYER DATA STRUCTURE VALIDATION")
        print("-" * 40)
        
        sample_player = None
        if starting_lineup:
            first_position = list(starting_lineup.keys())[0]
            if starting_lineup[first_position] and len(starting_lineup[first_position]) > 0:
                sample_player = starting_lineup[first_position][0]
        
        if sample_player:
            print(f"Sample player: {sample_player.get('name', 'Unknown')}")
            print(f"Sample player position: {sample_player.get('position', 'Unknown')}")
            print(f"Sample player team: {sample_player.get('team', 'Unknown')}")
            
            # Check essential fields
            essential_fields = [
                'name', 'position', 'team', 'bye_week', 'injury_status', 
                'percent_owned', 'roster_position', 'fantasy_points', 
                'fantasy_points_default', 'depth_chart_position', 'years_exp', 
                'active', 'age', 'recent_news', 'player_ids'
            ]
            
            print(f"\nEssential fields present:")
            for field in essential_fields:
                if field in sample_player:
                    print(f"  ✅ {field}")
                else:
                    print(f"  ❌ {field}: Missing")
            
            # Check fantasy points structure
            print(f"\nFantasy points validation:")
            fantasy_points = sample_player.get('fantasy_points')
            fantasy_points_default = sample_player.get('fantasy_points_default')
            
            print(f"  fantasy_points: {fantasy_points} (type: {type(fantasy_points)})")
            print(f"  fantasy_points_default: {fantasy_points_default} (type: {type(fantasy_points_default)})")
            
            if isinstance(fantasy_points_default, dict):
                print(f"    Standard: {fantasy_points_default.get('standard', 'N/A')}")
                print(f"    PPR: {fantasy_points_default.get('PPR', 'N/A')}")
                print(f"    Half-PPR: {fantasy_points_default.get('halfPPR', 'N/A')}")
            
            # Check news structure
            recent_news = sample_player.get('recent_news', [])
            print(f"\nNews validation:")
            print(f"  Number of news items: {len(recent_news)}")
            if recent_news:
                first_news = recent_news[0]
                print(f"  First news item keys: {list(first_news.keys())}")
                print(f"  Has title: {'title' in first_news}")
                print(f"  Has link: {'link' in first_news}")
            
            # Check player IDs structure
            player_ids = sample_player.get('player_ids', {})
            print(f"\nPlayer IDs validation:")
            print(f"  Number of IDs: {len(player_ids)}")
            print(f"  ID types: {list(player_ids.keys())}")
        
        # Validate NFL matchups
        print(f"\n🏟️ NFL MATCHUPS VALIDATION")
        print("-" * 40)
        nfl_matchups = data.get('nfl_matchups', {})
        games = nfl_matchups.get('games', [])
        
        print(f"Number of games: {len(games)}")
        if games:
            first_game = games[0]
            print(f"First game: {first_game.get('away_team', 'Unknown')} @ {first_game.get('home_team', 'Unknown')}")
            print(f"Game date: {first_game.get('date', 'Unknown')}")
            print(f"Game time: {first_game.get('game_time_et', 'Unknown')}")
            print(f"Game week: {first_game.get('week', 'Unknown')}")
        
        # Check for any missing critical data
        print(f"\n⚠️ CRITICAL DATA CHECKS")
        print("-" * 40)
        
        issues = []
        
        # Check if we have players
        if total_my_roster == 0:
            issues.append("No players in my roster")
        if total_opp_roster == 0:
            issues.append("No players in opponent roster")
        if total_available == 0:
            issues.append("No available players")
        
        # Check if we have fantasy points
        if sample_player and not sample_player.get('fantasy_points'):
            issues.append("Sample player missing fantasy_points")
        if sample_player and not sample_player.get('fantasy_points_default'):
            issues.append("Sample player missing fantasy_points_default")
        
        # Check if we have news
        if sample_player and not sample_player.get('recent_news'):
            issues.append("Sample player missing recent_news")
        
        # Check if we have player IDs
        if sample_player and not sample_player.get('player_ids'):
            issues.append("Sample player missing player_ids")
        
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No critical issues found")
        
        # Summary
        print(f"\n📊 VALIDATION SUMMARY")
        print("-" * 40)
        print(f"My roster players: {total_my_roster}")
        print(f"Opponent roster players: {total_opp_roster}")
        print(f"Available players: {total_available}")
        print(f"NFL games: {len(games)}")
        print(f"Critical issues: {len(issues)}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error validating data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main validation function"""
    file_path = "/Users/haven/Library/CloudStorage/Dropbox/Personal Stuff/DEV/fantasy_football/data_collection/outputs/validation_tests/2025/09/08/20250908_224710_streamlined_processor_test.json"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return 1
    
    success = validate_streamlined_data(file_path)
    
    if success:
        print(f"\n🎉 SUCCESS: Streamlined data validation passed!")
    else:
        print(f"\n❌ FAILED: Streamlined data validation found issues")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
