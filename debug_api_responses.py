#!/usr/bin/env python3
"""
Debug script to capture and analyze complete API responses from all three APIs.
This will help us understand ALL the data fields available.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.core.external_api_manager import ExternalAPIManager

def save_debug_data(data, filename):
    """Save debug data to file."""
    debug_dir = Path("debug_api_data")
    debug_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = debug_dir / f"{timestamp}_{filename}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"📄 Saved debug data to: {filepath}")
    return filepath

def analyze_yahoo_roster_structure():
    """Analyze complete Yahoo roster response structure."""
    print("🔍 ANALYZING YAHOO ROSTER STRUCTURE")
    print("=" * 50)
    
    api_manager = ExternalAPIManager()
    yahoo_client = api_manager.yahoo_client
    
    # Get our team key
    teams_response = yahoo_client.oauth_client.make_request("users;use_login=1/games;game_keys=nfl/teams")
    if not teams_response or teams_response.get('status') != 'success':
        print("❌ Failed to get user teams")
        return
    
    parsed_data = teams_response.get('parsed', {})
    teams = yahoo_client._parse_user_teams_response(parsed_data)
    our_team_key = teams[0].get('team_key')
    
    # Get our team roster - RAW RESPONSE
    roster_response = yahoo_client.oauth_client.make_request(f"team/{our_team_key}/roster")
    
    # Save the complete raw response
    save_debug_data(roster_response, "yahoo_roster_complete")
    
    # Analyze the structure
    parsed = roster_response.get('parsed', {})
    
    print(f"📊 Yahoo Roster Response Structure:")
    print(f"   - Status: {roster_response.get('status')}")
    print(f"   - Top-level keys: {list(roster_response.keys())}")
    
    if 'parsed' in roster_response:
        fantasy_content = parsed.get('fantasy_content', {})
        print(f"   - fantasy_content keys: {list(fantasy_content.keys())}")
        
        if 'team' in fantasy_content:
            team = fantasy_content['team']
            print(f"   - team keys: {list(team.keys())}")
            
            if 'roster' in team:
                roster = team['roster']
                print(f"   - roster keys: {list(roster.keys())}")
                
                if '0' in roster:
                    roster_data = roster['0']
                    print(f"   - roster[0] keys: {list(roster_data.keys())}")
                    
                    if 'players' in roster_data:
                        players = roster_data['players']
                        print(f"   - players keys: {list(players.keys())}")
                        
                        # Analyze first player structure
                        for player_key in players.keys():
                            if player_key.isdigit():
                                player_data = players[player_key]
                                print(f"\n🎯 FIRST PLAYER ({player_key}) STRUCTURE:")
                                print(f"   - Player data keys: {list(player_data.keys())}")
                                
                                if 'player' in player_data:
                                    player_info = player_data['player']
                                    print(f"   - Player info type: {type(player_info)}")
                                    
                                    if isinstance(player_info, list):
                                        print(f"   - Player info list length: {len(player_info)}")
                                        for i, item in enumerate(player_info):
                                            print(f"   - Item {i} type: {type(item)}")
                                            if isinstance(item, dict):
                                                print(f"   - Item {i} keys: {list(item.keys())}")
                                            elif isinstance(item, list):
                                                print(f"   - Item {i} list length: {len(item)}")
                                                if len(item) > 0:
                                                    print(f"   - Item {i}[0] type: {type(item[0])}")
                                                    if isinstance(item[0], dict):
                                                        print(f"   - Item {i}[0] keys: {list(item[0].keys())}")
                                
                                # Save first player's complete data
                                save_debug_data(player_data, f"yahoo_first_player_{player_key}")
                                break
    
    return roster_response

def analyze_sleeper_trending_structure():
    """Analyze complete Sleeper trending response structure."""
    print("\n🔍 ANALYZING SLEEPER TRENDING STRUCTURE")  
    print("=" * 50)
    
    api_manager = ExternalAPIManager()
    sleeper_client = api_manager.sleeper_client
    
    # Get trending add players - RAW RESPONSE
    print("📈 Fetching trending ADD players...")
    trending_add = sleeper_client.get_trending_players('add', lookback_hours=24, limit=10)
    save_debug_data(trending_add, "sleeper_trending_add")
    
    print("📉 Fetching trending DROP players...")
    trending_drop = sleeper_client.get_trending_players('drop', lookback_hours=24, limit=10)
    save_debug_data(trending_drop, "sleeper_trending_drop")
    
    print("👥 Fetching ALL NFL players...")
    all_players = sleeper_client.get_nfl_players()
    
    # Save a subset of all players (first 100) to analyze structure
    if all_players:
        sample_players = dict(list(all_players.items())[:100])
        save_debug_data(sample_players, "sleeper_all_players_sample")
        
        # Analyze first player structure
        first_player_id = list(all_players.keys())[0]
        first_player = all_players[first_player_id]
        
        print(f"\n🎯 FIRST SLEEPER PLAYER ({first_player_id}) STRUCTURE:")
        print(f"   - Player data keys: {list(first_player.keys())}")
        print(f"   - Player data sample:")
        for key, value in first_player.items():
            print(f"     - {key}: {value} ({type(value)})")
        
        save_debug_data(first_player, f"sleeper_first_player_{first_player_id}")
    
    return trending_add, trending_drop, all_players

def analyze_tank01_structure():
    """Analyze complete Tank01 API response structures."""
    print("\n🔍 ANALYZING TANK01 API STRUCTURE")
    print("=" * 50)
    
    api_manager = ExternalAPIManager()
    tank01_client = api_manager.tank01_client
    
    # Get player list - RAW RESPONSE
    print("👥 Fetching Tank01 player list...")
    player_list = tank01_client.get_player_list()
    save_debug_data(player_list, "tank01_player_list_complete")
    
    if player_list and 'body' in player_list:
        players = player_list['body']
        if isinstance(players, list) and len(players) > 0:
            first_player = players[0]
            
            print(f"\n🎯 FIRST TANK01 PLAYER STRUCTURE:")
            print(f"   - Player data keys: {list(first_player.keys())}")
            print(f"   - Player data sample:")
            for key, value in first_player.items():
                print(f"     - {key}: {value} ({type(value)})")
            
            save_debug_data(first_player, "tank01_first_player")
    
    # Get fantasy projections for a known player (Joe Burrow)
    print("📊 Fetching Tank01 fantasy projections for Joe Burrow...")
    joe_burrow_projections = tank01_client.get_fantasy_projections(
        player_id='3915511',  # Joe Burrow's Tank01 ID
        scoring_settings={
            'fantasyPoints': 'true',
            'passYards': 0.04,
            'passTD': 4,
            'passInterceptions': -2,
            'rushYards': 0.1,
            'rushTD': 6,
            'receivingYards': 0.1,
            'receivingTD': 6,
            'pointsPerReception': 1,
            'fumbles': -2,
            'fgMade': 3,
            'fgMissed': -1,
            'xpMade': 1,
            'xpMissed': -1
        }
    )
    save_debug_data(joe_burrow_projections, "tank01_joe_burrow_projections")
    
    if joe_burrow_projections and 'body' in joe_burrow_projections:
        proj_data = joe_burrow_projections['body']
        if isinstance(proj_data, dict):
            first_game_key = list(proj_data.keys())[0]
            first_game_data = proj_data[first_game_key]
            
            print(f"\n🎯 FIRST TANK01 GAME DATA STRUCTURE:")
            print(f"   - Game key: {first_game_key}")
            print(f"   - Game data keys: {list(first_game_data.keys())}")
            print(f"   - Game data sample:")
            for key, value in first_game_data.items():
                if isinstance(value, dict):
                    print(f"     - {key}: {dict} with keys {list(value.keys())}")
                else:
                    print(f"     - {key}: {value} ({type(value)})")
            
            save_debug_data(first_game_data, "tank01_first_game_data")
    
    # Get NFL news
    print("📰 Fetching Tank01 NFL news...")
    news = tank01_client.get_nfl_news(fantasy_news=True, max_items=10)
    save_debug_data(news, "tank01_news_complete")
    
    return player_list, joe_burrow_projections, news

def main():
    """Main analysis function."""
    print("🔍 COMPREHENSIVE API RESPONSE ANALYSIS")
    print("=" * 60)
    print("This script will capture and analyze ALL data from the three APIs")
    print("to understand the complete structure for enhanced parsing.")
    print("")
    
    try:
        # Analyze all three APIs
        yahoo_data = analyze_yahoo_roster_structure()
        sleeper_data = analyze_sleeper_trending_structure()  
        tank01_data = analyze_tank01_structure()
        
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"📁 All debug data saved to: debug_api_data/")
        print(f"📋 Review the JSON files to understand complete API structures")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
