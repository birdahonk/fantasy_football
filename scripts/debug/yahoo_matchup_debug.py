#!/usr/bin/env python3
"""
Yahoo Matchup API Debug Script

This script examines the exact structure of Yahoo matchup API responses
to understand how to properly parse Week 1 opponent data.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.core.external_api_manager import ExternalAPIManager

def debug_yahoo_matchup_api():
    """Debug Yahoo matchup API response structure."""
    print("🔍 YAHOO MATCHUP API DEBUG")
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
        
        # Get matchup data
        print(f"\n📊 Getting matchup data for team {our_team_key}...")
        matchup_response = yahoo_client.oauth_client.make_request(f"team/{our_team_key}/matchups")
        
        if not matchup_response or matchup_response.get('status') != 'success':
            print("❌ Failed to get matchup data")
            return
        
        # Save raw response for analysis
        debug_dir = Path("analysis/debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        raw_file = debug_dir / "yahoo_matchup_raw_response.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(matchup_response, f, indent=2, default=str)
        
        print(f"✅ Raw matchup response saved to: {raw_file}")
        
        # Analyze the structure
        print("\n🔍 ANALYZING RESPONSE STRUCTURE:")
        print("-" * 40)
        
        parsed_matchup = matchup_response.get('parsed', {})
        print(f"📋 Top-level keys: {list(parsed_matchup.keys())}")
        
        if 'fantasy_content' in parsed_matchup:
            fantasy_content = parsed_matchup['fantasy_content']
            print(f"📋 fantasy_content keys: {list(fantasy_content.keys())}")
            
            if 'team' in fantasy_content:
                team_data = fantasy_content['team']
                print(f"📋 team data type: {type(team_data)}")
                
                if isinstance(team_data, list):
                    print(f"📋 team array length: {len(team_data)}")
                    for i, item in enumerate(team_data):
                        print(f"   Item {i}: {type(item)} - keys: {list(item.keys()) if isinstance(item, dict) else 'N/A'}")
                        
                        if isinstance(item, dict) and 'matchups' in item:
                            matchups = item['matchups']
                            print(f"     matchups type: {type(matchups)}")
                            print(f"     matchups keys: {list(matchups.keys()) if isinstance(matchups, dict) else 'N/A'}")
                            
                            # Look for actual matchup data
                            for key, value in matchups.items():
                                if key.isdigit():
                                    print(f"     Matchup {key}: {type(value)} - keys: {list(value.keys()) if isinstance(value, dict) else 'N/A'}")
                                    
                                    if isinstance(value, dict) and 'matchup' in value:
                                        matchup = value['matchup']
                                        print(f"       matchup data: {type(matchup)} - keys: {list(matchup.keys()) if isinstance(matchup, dict) else 'N/A'}")
                                        
                                        if isinstance(matchup, dict):
                                            week = matchup.get('week')
                                            print(f"       Week: {week}")
                                            
                                            if 'teams' in matchup:
                                                teams_in_matchup = matchup['teams']
                                                print(f"       teams type: {type(teams_in_matchup)}")
                                                print(f"       teams keys: {list(teams_in_matchup.keys()) if isinstance(teams_in_matchup, dict) else 'N/A'}")
                                                
                                                # Examine each team in the matchup
                                                for team_key, team_info in teams_in_matchup.items():
                                                    if team_key.isdigit():
                                                        print(f"         Team {team_key}: {type(team_info)}")
                                                        if isinstance(team_info, dict) and 'team' in team_info:
                                                            team_details = team_info['team']
                                                            team_key_val = team_details.get('team_key')
                                                            team_name = team_details.get('name')
                                                            print(f"           Team Key: {team_key_val}")
                                                            print(f"           Team Name: {team_name}")
                                                            print(f"           Is our team: {team_key_val == our_team_key}")
        
        print(f"\n✅ Debug analysis complete!")
        print(f"📄 Full response saved to: {raw_file}")
        
        # Try to find Week 1 matchup with improved logic
        print(f"\n🎯 ATTEMPTING TO FIND WEEK 1 OPPONENT...")
        week1_opponent = find_week1_opponent_improved(parsed_matchup, our_team_key)
        
        if week1_opponent:
            print(f"✅ FOUND Week 1 opponent!")
            print(f"   Team Key: {week1_opponent.get('team_key')}")
            print(f"   Team Name: {week1_opponent.get('name')}")
            print(f"   Manager: {week1_opponent.get('manager')}")
        else:
            print(f"❌ Could not find Week 1 opponent")
        
    except Exception as e:
        print(f"❌ Error debugging matchup API: {e}")
        import traceback
        traceback.print_exc()

def find_week1_opponent_improved(matchup_data: dict, our_team_key: str) -> dict:
    """Improved logic to find Week 1 opponent."""
    try:
        fantasy_content = matchup_data.get('fantasy_content', {})
        team_data = fantasy_content.get('team', [])
        
        if isinstance(team_data, list):
            for item in team_data:
                if isinstance(item, dict) and 'matchups' in item:
                    matchups = item.get('matchups', {})
                    
                    # Look through all matchups
                    for matchup_key, matchup_info in matchups.items():
                        if matchup_key.isdigit():
                            matchup = matchup_info.get('matchup', {})
                            
                            # Check if this is Week 1
                            week = matchup.get('week')
                            if str(week) == '1':
                                print(f"   Found Week 1 matchup!")
                                
                                # Find the opponent team in this matchup
                                teams = matchup.get('teams', {})
                                for team_key, team_info in teams.items():
                                    if team_key.isdigit():
                                        team = team_info.get('team', {})
                                        team_key_val = team.get('team_key')
                                        
                                        # If this isn't our team, it's the opponent
                                        if team_key_val and team_key_val != our_team_key:
                                            # Extract manager info
                                            managers = team.get('managers', {})
                                            manager_name = 'Unknown Manager'
                                            
                                            if isinstance(managers, dict):
                                                if 'manager' in managers:
                                                    manager_info = managers['manager']
                                                    if isinstance(manager_info, dict):
                                                        manager_name = manager_info.get('nickname', 'Unknown Manager')
                                                    elif isinstance(manager_info, list) and len(manager_info) > 0:
                                                        manager_name = manager_info[0].get('nickname', 'Unknown Manager')
                                            
                                            return {
                                                'team_key': team_key_val,
                                                'name': team.get('name', 'Unknown Team'),
                                                'manager': manager_name
                                            }
        
        return None
        
    except Exception as e:
        print(f"Error in improved opponent finder: {e}")
        return None

if __name__ == "__main__":
    debug_yahoo_matchup_api()
