#!/usr/bin/env python3
"""
Yahoo Roster Position Debug Script

This script examines the exact structure of Yahoo roster API responses
to understand where starting positions are stored and how to parse them correctly.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.core.external_api_manager import ExternalAPIManager

def debug_yahoo_roster_positions():
    """Debug Yahoo roster position parsing."""
    print("🔍 YAHOO ROSTER POSITION DEBUG")
    print("=" * 50)
    
    try:
        # Initialize API manager
        api_manager = ExternalAPIManager()
        yahoo_client = api_manager.yahoo_client
        
        # Get our team key
        print("📊 Getting team information...")
        teams_response = yahoo_client.oauth_client.make_request("users;use_login=1/games;game_keys=nfl/teams")
        
        if not teams_response or teams_response.get('status') != 'success':
            print("❌ Failed to get user teams")
            return
        
        parsed_data = teams_response.get('parsed', {})
        teams = yahoo_client._parse_user_teams_response(parsed_data)
        
        if not teams:
            print("❌ No teams found")
            return
        
        our_team_key = teams[0].get('team_key')
        print(f"✅ Our team key: {our_team_key}")
        
        # Get roster data
        print(f"\n📊 Getting roster data for team {our_team_key}...")
        roster_response = yahoo_client.oauth_client.make_request(f"team/{our_team_key}/roster")
        
        if not roster_response or roster_response.get('status') != 'success':
            print("❌ Failed to get roster data")
            return
        
        # Save raw response for analysis
        debug_dir = Path("analysis/debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        raw_file = debug_dir / "yahoo_roster_raw_response.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(roster_response, f, indent=2, default=str)
        
        print(f"✅ Raw roster response saved to: {raw_file}")
        
        # Analyze the structure
        print("\n🔍 ANALYZING ROSTER STRUCTURE:")
        print("-" * 40)
        
        parsed_roster = roster_response.get('parsed', {})
        print(f"📋 Top-level keys: {list(parsed_roster.keys())}")
        
        if 'fantasy_content' in parsed_roster:
            fantasy_content = parsed_roster['fantasy_content']
            print(f"📋 fantasy_content keys: {list(fantasy_content.keys())}")
            
            if 'team' in fantasy_content:
                team_data = fantasy_content['team']
                print(f"📋 team data type: {type(team_data)}")
                
                if isinstance(team_data, list):
                    print(f"📋 team array length: {len(team_data)}")
                    for i, item in enumerate(team_data):
                        print(f"   Item {i}: {type(item)} - keys: {list(item.keys()) if isinstance(item, dict) else 'N/A'}")
                        
                        if isinstance(item, dict) and 'roster' in item:
                            roster_data = item['roster']
                            print(f"     roster type: {type(roster_data)}")
                            print(f"     roster keys: {list(roster_data.keys()) if isinstance(roster_data, dict) else 'N/A'}")
                            
                            if isinstance(roster_data, dict) and '0' in roster_data:
                                roster_zero = roster_data['0']
                                print(f"     roster['0'] keys: {list(roster_zero.keys()) if isinstance(roster_zero, dict) else 'N/A'}")
                                
                                if 'players' in roster_zero:
                                    players = roster_zero['players']
                                    print(f"     players type: {type(players)}")
                                    print(f"     players keys: {list(players.keys()) if isinstance(players, dict) else 'N/A'}")
                                    
                                    # Examine first few players in detail
                                    player_keys = [k for k in players.keys() if k.isdigit()]
                                    print(f"     Found {len(player_keys)} players")
                                    
                                    for i, player_key in enumerate(player_keys[:3]):  # First 3 players
                                        print(f"\n     🏈 PLAYER {i+1} (key: {player_key}):")
                                        player_data = players[player_key]
                                        print(f"       player_data keys: {list(player_data.keys()) if isinstance(player_data, dict) else 'N/A'}")
                                        
                                        if 'player' in player_data:
                                            player_info = player_data['player']
                                            print(f"       player info type: {type(player_info)}")
                                            print(f"       player info length: {len(player_info) if isinstance(player_info, list) else 'N/A'}")
                                            
                                            if isinstance(player_info, list):
                                                for j, info_item in enumerate(player_info):
                                                    print(f"         Info item {j}: {type(info_item)}")
                                                    
                                                    if isinstance(info_item, list):
                                                        print(f"           Nested list length: {len(info_item)}")
                                                        for k, nested_item in enumerate(info_item[:5]):  # First 5 items
                                                            if isinstance(nested_item, dict):
                                                                print(f"             Item {k}: {list(nested_item.keys())}")
                                                                # Look for name and position info
                                                                if 'name' in nested_item:
                                                                    name_data = nested_item['name']
                                                                    if isinstance(name_data, dict) and 'full' in name_data:
                                                                        print(f"               NAME: {name_data['full']}")
                                                    elif isinstance(info_item, dict):
                                                        print(f"         Dict item {j}: {list(info_item.keys())}")
                                                        
                                                        # Look for position information
                                                        if 'selected_position' in info_item:
                                                            print(f"           🎯 FOUND selected_position: {info_item['selected_position']}")
                                                        if 'position' in info_item:
                                                            print(f"           📍 FOUND position: {info_item['position']}")
                                                        
                                                        # Look for other position-related keys
                                                        position_keys = [k for k in info_item.keys() if 'pos' in k.lower()]
                                                        if position_keys:
                                                            print(f"           🔍 Position-related keys: {position_keys}")
                                                            for pk in position_keys:
                                                                print(f"             {pk}: {info_item[pk]}")
        
        print(f"\n✅ Debug analysis complete!")
        print(f"📄 Full response saved to: {raw_file}")
        
    except Exception as e:
        print(f"❌ Error debugging roster positions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_yahoo_roster_positions()
