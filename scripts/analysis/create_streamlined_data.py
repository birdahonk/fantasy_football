#!/usr/bin/env python3
"""
Create Streamlined Data for Analyst Agent

Creates a token-efficient version of the comprehensive data for use in analyst prompts.
"""

import os
import sys
import json
import tiktoken
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def calculate_tokens(text: str) -> int:
    """Calculate tokens using tiktoken"""
    encoding = tiktoken.get_encoding('cl100k_base')
    return len(encoding.encode(text))

def create_streamlined_player(player_data: dict) -> dict:
    """Create a streamlined version of a player for analyst consumption"""
    
    # Extract only essential data for analysis
    streamlined = {
        "name": player_data.get("name", "Unknown"),
        "position": player_data.get("yahoo_data", {}).get("display_position", "Unknown"),
        "team": player_data.get("yahoo_data", {}).get("team", "Unknown"),
        "bye_week": player_data.get("yahoo_data", {}).get("bye_week", "Unknown"),
        "injury_status": player_data.get("yahoo_data", {}).get("injury_status", "Healthy"),
        "percent_owned": player_data.get("yahoo_data", {}).get("percent_owned", "0"),
        "roster_position": player_data.get("roster_position", "Unknown")
    }
    
    # Add fantasy points data (most important for analysis)
    tank01_data = player_data.get("tank01_data", {})
    if tank01_data:
        projection = tank01_data.get("projection", {})
        if projection:
            streamlined["fantasy_points"] = projection.get("fantasyPoints")
            streamlined["fantasy_points_default"] = projection.get("fantasyPointsDefault")
    
    # Add key Sleeper data (minimal)
    sleeper_data = player_data.get("sleeper_data", {})
    if sleeper_data:
        streamlined["depth_chart_position"] = sleeper_data.get("depth_chart_position")
        streamlined["years_exp"] = sleeper_data.get("years_exp")
        streamlined["active"] = sleeper_data.get("active")
        streamlined["age"] = sleeper_data.get("age")
    
    # Add recent news (keep current quantity, simplified format)
    if tank01_data:
        news = tank01_data.get("news", [])
        if news:
            streamlined["recent_news"] = [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", "")
                }
                for item in news  # Keep all news items, just simplified format
            ]
        
        # Add basic injury info from Tank01
        injury = tank01_data.get("injury", {})
        if injury and injury.get("description"):
            streamlined["injury_details"] = {
                "description": injury.get("description", ""),
                "designation": injury.get("designation", "")
            }
    
    # Add deduplicated ID mappings (helpful for web research)
    player_ids = {}
    
    # Sleeper IDs
    if sleeper_data:
        sleeper_ids = sleeper_data.get("player_ids", {})
        if sleeper_ids:
            player_ids["sleeper_id"] = sleeper_ids.get("sleeper_id")
            player_ids["yahoo_id"] = sleeper_ids.get("yahoo_id")
            player_ids["espn_id"] = sleeper_ids.get("espn_id")
    
    # Tank01 IDs
    if tank01_data:
        tank01_ids = tank01_data.get("player_ids", {})
        if tank01_ids:
            player_ids["tank01_id"] = tank01_data.get("player_id")  # Main Tank01 ID
            player_ids["fantasypros_id"] = tank01_ids.get("fantasypros_id")
            player_ids["rotowire_id"] = tank01_ids.get("rotowire_id")
    
    # Yahoo IDs
    yahoo_data = player_data.get("yahoo_data", {})
    if yahoo_data:
        player_ids["yahoo_player_key"] = yahoo_data.get("player_key")
        player_ids["yahoo_player_id"] = yahoo_data.get("player_id")
    
    # Only add if we have IDs
    if any(player_ids.values()):
        streamlined["player_ids"] = {k: v for k, v in player_ids.items() if v is not None}
    
    return streamlined

def create_streamlined_data(comprehensive_data: dict) -> dict:
    """Create streamlined version of comprehensive data for analyst agent"""
    
    print("Creating streamlined data for analyst agent...")
    
    # Base structure
    streamlined = {
        "season_context": comprehensive_data.get("season_context", {}),
        "league_metadata": comprehensive_data.get("league_metadata", {}),
        "my_roster": {},
        "opponent_roster": {},
        "available_players": {},
        "nfl_matchups": comprehensive_data.get("nfl_matchups", {}),
        "data_files": comprehensive_data.get("data_files", {}),
        "processing_timestamp": comprehensive_data.get("processing_timestamp", "")
    }
    
    # Streamline my roster
    my_roster = comprehensive_data.get("my_roster", {})
    streamlined["my_roster"] = {
        "total_players": my_roster.get("total_players", 0),
        "starting_count": my_roster.get("starting_count", 0),
        "bench_count": my_roster.get("bench_count", 0),
        "team_name": my_roster.get("team_name", "Unknown"),
        "league_name": my_roster.get("league_name", "Unknown"),
        "players_by_position": {}
    }
    
    # Process my roster players
    my_players = my_roster.get("players_by_position", {})
    for position_type, position_groups in my_players.items():
        streamlined["my_roster"]["players_by_position"][position_type] = {}
        for position, players in position_groups.items():
            streamlined["my_roster"]["players_by_position"][position_type][position] = [
                create_streamlined_player(player) for player in players
            ]
    
    # Streamline opponent roster
    opponent_roster = comprehensive_data.get("opponent_roster", {})
    streamlined["opponent_roster"] = {
        "total_players": opponent_roster.get("total_players", 0),
        "starting_count": opponent_roster.get("starting_count", 0),
        "bench_count": opponent_roster.get("bench_count", 0),
        "opponent_name": opponent_roster.get("opponent_name", "Unknown"),
        "opponent_team_key": opponent_roster.get("opponent_team_key", "Unknown"),
        "players_by_position": {}
    }
    
    # Process opponent roster players
    opp_players = opponent_roster.get("players_by_position", {})
    for position_type, position_groups in opp_players.items():
        streamlined["opponent_roster"]["players_by_position"][position_type] = {}
        for position, players in position_groups.items():
            streamlined["opponent_roster"]["players_by_position"][position_type][position] = [
                create_streamlined_player(player) for player in players
            ]
    
    # Streamline available players (most important for token reduction)
    available_players = comprehensive_data.get("available_players", {})
    streamlined["available_players"] = {
        "total_players": available_players.get("total_players", 0),
        "players_by_position": {}
    }
    
    # Process available players
    avail_players = available_players.get("players_by_position", {})
    for position, players in avail_players.items():
        streamlined["available_players"]["players_by_position"][position] = [
            create_streamlined_player(player) for player in players
        ]
    
    return streamlined

def main():
    """Main function to create and analyze streamlined data"""
    
    print("🔧 CREATING STREAMLINED DATA FOR ANALYST AGENT")
    print("=" * 60)
    
    # Load comprehensive data
    validation_dir = os.path.join(project_root, "data_collection", "outputs", "validation_tests", "2025", "09", "08")
    json_files = [f for f in os.listdir(validation_dir) if f.endswith('.json') and 'comprehensive_data_processor' in f]
    latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(validation_dir, f)))
    
    with open(os.path.join(validation_dir, latest_file), 'r') as f:
        comprehensive_data = json.load(f)
    
    print(f"Loaded: {latest_file}")
    
    # Create streamlined version
    streamlined_data = create_streamlined_data(comprehensive_data)
    
    # Calculate token usage
    comprehensive_json = json.dumps(comprehensive_data, indent=2)
    streamlined_json = json.dumps(streamlined_data, indent=2)
    
    comprehensive_tokens = calculate_tokens(comprehensive_json)
    streamlined_tokens = calculate_tokens(streamlined_json)
    
    print(f"\n=== TOKEN COMPARISON ===")
    print(f"Comprehensive data: {comprehensive_tokens:,} tokens")
    print(f"Streamlined data: {streamlined_tokens:,} tokens")
    print(f"Reduction: {comprehensive_tokens - streamlined_tokens:,} tokens ({(1 - streamlined_tokens/comprehensive_tokens)*100:.1f}%)")
    
    # Analyze sections
    print(f"\n=== SECTION BREAKDOWN ===")
    sections = ['my_roster', 'opponent_roster', 'available_players', 'nfl_matchups']
    
    for section in sections:
        comp_section = json.dumps(comprehensive_data.get(section, {}), indent=2)
        stream_section = json.dumps(streamlined_data.get(section, {}), indent=2)
        
        comp_tokens = calculate_tokens(comp_section)
        stream_tokens = calculate_tokens(stream_section)
        
        print(f"{section:20s}: {comp_tokens:8,} → {stream_tokens:8,} tokens ({(1-stream_tokens/comp_tokens)*100:.1f}% reduction)")
    
    # Check if within limit
    print(f"\n=== LIMIT CHECK ===")
    if streamlined_tokens <= 200000:
        remaining = 200000 - streamlined_tokens
        print(f"✅ Within limit! {remaining:,} tokens remaining")
    else:
        excess = streamlined_tokens - 200000
        print(f"❌ Still over limit by {excess:,} tokens")
    
    # Save streamlined data
    output_file = os.path.join(validation_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_streamlined_data.json")
    with open(output_file, 'w') as f:
        json.dump(streamlined_data, f, indent=2)
    
    print(f"\n✅ Streamlined data saved to: {output_file}")
    
    # Show sample streamlined player
    print(f"\n=== SAMPLE STREAMLINED PLAYER ===")
    if streamlined_data.get("available_players", {}).get("players_by_position", {}):
        first_position = list(streamlined_data["available_players"]["players_by_position"].keys())[0]
        sample_player = streamlined_data["available_players"]["players_by_position"][first_position][0]
        print(json.dumps(sample_player, indent=2))
    
    print(f"\n=== REMOVED DATA SUMMARY ===")
    print("Removed massive data dumps:")
    print("- tank01_data.game_stats.recent_games (detailed play-by-play stats)")
    print("- tank01_data.team_context (extensive team performance data)")
    print("- tank01_data.depth_chart (detailed depth chart info)")
    print("- Physical stats (height, weight, college, birth_date)")
    print("- Redundant name variations")
    print("- Jersey numbers, team IDs, etc.")
    print()
    print("Kept essential data:")
    print("- Basic player info (name, position, team, bye, injury, ownership)")
    print("- Fantasy points projections (most critical)")
    print("- Key Sleeper data (depth chart position, experience, active status)")
    print("- All news items (simplified format)")
    print("- Deduplicated ID mappings (for web research)")
    print("- Basic injury details")

if __name__ == "__main__":
    main()