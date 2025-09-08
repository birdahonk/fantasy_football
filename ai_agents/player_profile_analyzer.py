#!/usr/bin/env python3
"""
Analyze and create comprehensive player profiles with optimized data selection
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import tiktoken

def create_optimized_player_profile():
    """Create an optimized player profile structure based on user requirements"""
    
    # Sample player profile structure
    player_profile = {
        "yahoo_data": {
            # Essential Yahoo data (pruned from current 30+ fields)
            "player_key": "461.p.40901",
            "player_id": "40901", 
            "name": {
                "full": "Rome Odunze",
                "first": "Rome",
                "last": "Odunze"
            },
            "display_position": "WR",
            "primary_position": "WR",
            "eligible_positions": ["WR", "W/R/T"],
            "team": {
                "name": "Chicago Bears",
                "abbr": "Chi",
                "key": "nfl.t.3"
            },
            "bye_week": "5",
            "uniform_number": "15",
            "injury_status": "Healthy",  # Derived from status fields
            "is_undroppable": False,
            "percent_owned": "45.2"
        },
        
        "sleeper_data": {
            # Essential Sleeper data only
            "player_id": "12345",
            "name": {
                "full": "Rome Odunze",
                "first": "Rome", 
                "last": "Odunze"
            },
            "position": "WR",
            "team": "CHI",
            "depth_chart_position": 1,  # Key field for analysis
            "status": "Active",
            "injury_status": "Healthy",
            "player_ids": {
                "sleeper_id": "12345",
                "yahoo_id": "40901",
                "espn_id": "67890",
                "sportradar_id": "SR12345",
                "gsis_id": "GSIS12345",
                "pff_id": "PFF12345",
                "fantasypros_id": "FP12345"
            }
        },
        
        "tank01_data": {
            # Essential Tank01 data
            "player_id": "tank01_12345",
            "name": {
                "full": "Rome Odunze",
                "first": "Rome",
                "last": "Odunze"
            },
            "display_position": "WR",
            "primary_position": "WR", 
            "eligible_positions": ["WR", "W/R/T"],
            "bye_week": 5,
            "team": "CHI",
            "injury_status": "Healthy",
            "depth_chart": {
                "position": 1,
                "depth": "WR1"
            },
            "projection": {
                "week_1": {
                    "passing_yards": 0,
                    "passing_tds": 0,
                    "rushing_yards": 0,
                    "rushing_tds": 0,
                    "receiving_yards": 85,
                    "receiving_tds": 0.5,
                    "receptions": 6.2,
                    "fumbles": 0.1,
                    "interceptions": 0,
                    "fantasy_points": 12.8,
                    "projected_points": 12.8
                }
            },
            "news": [
                {
                    "headline": "Rome Odunze expected to start Week 1",
                    "summary": "Rookie WR Rome Odunze is expected to start for the Bears in Week 1...",
                    "url": "https://example.com/news1",
                    "published": "2025-09-04T10:00:00Z"
                }
            ],
            "game_stats": {
                "season_2024": {
                    "games_played": 12,
                    "receiving_yards": 1024,
                    "receiving_tds": 8,
                    "receptions": 67
                }
            },
            "transaction_trends": {
                "adds_this_week": 45,
                "drops_this_week": 12,
                "net_adds": 33,
                "ownership_change": "+2.3%"
            }
        }
    }
    
    return player_profile

def create_defense_profile():
    """Create an optimized defense profile structure"""
    
    defense_profile = {
        "yahoo_data": {
            "player_key": "461.p.100003",
            "player_id": "100003",
            "name": {
                "full": "Chicago",
                "first": "Chicago",
                "last": ""
            },
            "display_position": "DEF",
            "primary_position": "DEF",
            "eligible_positions": ["DEF"],
            "team": {
                "name": "Chicago Bears",
                "abbr": "Chi", 
                "key": "nfl.t.3"
            },
            "bye_week": "5",
            "is_undroppable": False,
            "percent_owned": "78.5"
        },
        
        "sleeper_data": {
            "player_id": "DEF_CHI",
            "name": {
                "full": "Chicago Bears Defense",
                "first": "Chicago",
                "last": "Bears"
            },
            "position": "DEF",
            "team": "CHI",
            "depth_chart_position": 1,
            "status": "Active",
            "player_ids": {
                "sleeper_id": "DEF_CHI",
                "yahoo_id": "100003",
                "espn_id": "DEF_CHI_ESPN"
            }
        },
        
        "tank01_data": {
            "player_id": "tank01_def_chi",
            "name": {
                "full": "Chicago Bears Defense",
                "first": "Chicago", 
                "last": "Bears"
            },
            "display_position": "DEF",
            "primary_position": "DEF",
            "eligible_positions": ["DEF"],
            "bye_week": 5,
            "team": "CHI",
            "projection": {
                "week_1": {
                    "points_allowed": 21.5,
                    "sacks": 2.8,
                    "interceptions": 1.2,
                    "fumble_recoveries": 0.8,
                    "defensive_tds": 0.1,
                    "safety": 0.05,
                    "fantasy_points": 8.2,
                    "projected_points": 8.2
                }
            },
            "news": [
                {
                    "headline": "Bears defense looks strong heading into Week 1",
                    "summary": "Chicago's defense has been impressive in preseason...",
                    "url": "https://example.com/defense_news",
                    "published": "2025-09-04T14:00:00Z"
                }
            ],
            "game_stats": {
                "season_2024": {
                    "games_played": 17,
                    "points_allowed_per_game": 22.1,
                    "sacks": 45,
                    "interceptions": 18,
                    "fumble_recoveries": 12
                }
            }
        }
    }
    
    return defense_profile

def calculate_token_usage():
    """Calculate token usage for optimized player profiles"""
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("OPTIMIZED PLAYER PROFILE TOKEN ANALYSIS")
    print("=" * 50)
    
    # Create sample profiles
    player_profile = create_optimized_player_profile()
    defense_profile = create_defense_profile()
    
    # Calculate tokens for each profile
    player_json = json.dumps(player_profile, indent=2)
    player_tokens = len(encoding.encode(player_json))
    
    defense_json = json.dumps(defense_profile, indent=2)
    defense_tokens = len(encoding.encode(defense_json))
    
    print(f"Optimized Player Profile: {player_tokens:,} tokens")
    print(f"Optimized Defense Profile: {defense_tokens:,} tokens")
    print(f"Average per player: {(player_tokens + defense_tokens) / 2:,.0f} tokens")
    
    # Calculate for different scenarios
    print(f"\nTOKEN CALCULATIONS FOR DIFFERENT SCENARIOS")
    print("-" * 45)
    
    scenarios = [
        ("My Roster (15 players)", 15, player_tokens),
        ("Current Opponent (15 players)", 15, player_tokens), 
        ("Available Players - Top 5 per position (30 players)", 30, player_tokens),
        ("Available Players - Top 10 per position (60 players)", 60, player_tokens),
        ("Available Players - Top 15 per position (90 players)", 90, player_tokens),
        ("Available Players - Top 20 per position (120 players)", 120, player_tokens),
        ("Available Players - Top 25 per position (150 players)", 150, player_tokens)
    ]
    
    for scenario_name, player_count, tokens_per_player in scenarios:
        total_tokens = player_count * tokens_per_player
        print(f"{scenario_name}: {total_tokens:,} tokens")
    
    # Calculate total system tokens
    print(f"\nTOTAL SYSTEM TOKEN CALCULATION")
    print("-" * 35)
    
    # Your hierarchy of needs
    my_roster_tokens = 15 * player_tokens
    opponent_tokens = 15 * player_tokens
    available_25_per_pos = 150 * player_tokens  # 25 per position × 6 positions
    season_context_tokens = 200  # Season/week context
    matchup_context_tokens = 1000  # Current week matchups
    transaction_trends_tokens = 2000  # League transaction trends
    
    total_system_tokens = (
        my_roster_tokens + 
        opponent_tokens + 
        available_25_per_pos + 
        season_context_tokens + 
        matchup_context_tokens + 
        transaction_trends_tokens
    )
    
    print(f"My Roster (15 players): {my_roster_tokens:,} tokens")
    print(f"Current Opponent (15 players): {opponent_tokens:,} tokens") 
    print(f"Available Players (25 per position): {available_25_per_pos:,} tokens")
    print(f"Season Context: {season_context_tokens:,} tokens")
    print(f"Matchup Context: {matchup_context_tokens:,} tokens")
    print(f"Transaction Trends: {transaction_trends_tokens:,} tokens")
    print("-" * 35)
    print(f"TOTAL SYSTEM: {total_system_tokens:,} tokens")
    print(f"Token Limit: 200,000")
    print(f"Status: {'✅ Within Limit' if total_system_tokens <= 200000 else '❌ Over Limit'}")
    print(f"Buffer: {200000 - total_system_tokens:+,} tokens")
    
    # Scaling recommendations
    if total_system_tokens > 200000:
        excess = total_system_tokens - 200000
        print(f"\nSCALING RECOMMENDATIONS")
        print("-" * 25)
        print(f"Over limit by {excess:,} tokens")
        
        # Calculate how many available players we can fit
        available_budget = 200000 - (my_roster_tokens + opponent_tokens + season_context_tokens + matchup_context_tokens + transaction_trends_tokens)
        max_available_players = available_budget // player_tokens
        
        print(f"Available token budget for players: {available_budget:,} tokens")
        print(f"Maximum available players: {max_available_players} players")
        print(f"Maximum per position: {max_available_players // 6} players per position")

def analyze_current_data_structure():
    """Analyze current data structure to see what we're actually getting"""
    
    print(f"\nCURRENT DATA STRUCTURE ANALYSIS")
    print("-" * 35)
    
    # Check Yahoo player data
    try:
        with open("data_collection/outputs/yahoo/available_players/20250905_140659_available_players_raw_data.json", 'r') as f:
            yahoo_data = json.load(f)
        
        if "available_players" in yahoo_data and yahoo_data["available_players"]:
            sample_yahoo = yahoo_data["available_players"][0]
            print(f"Yahoo player fields: {len(sample_yahoo.keys())} fields")
            print(f"Yahoo sample fields: {list(sample_yahoo.keys())[:10]}...")
            
    except Exception as e:
        print(f"Could not analyze Yahoo data: {e}")
    
    # Check Sleeper player data
    try:
        with open("data_collection/outputs/sleeper/available_players/20250905_140711_available_players_raw_data.json", 'r') as f:
            sleeper_data = json.load(f)
        
        if "available_players" in sleeper_data and sleeper_data["available_players"]:
            sample_sleeper = sleeper_data["available_players"][0]
            print(f"Sleeper player fields: {len(sample_sleeper.keys())} fields")
            print(f"Sleeper sample fields: {list(sample_sleeper.keys())[:10]}...")
            
    except Exception as e:
        print(f"Could not analyze Sleeper data: {e}")
    
    # Check Tank01 player data
    try:
        with open("data_collection/outputs/tank01/available_players/20250905_140853_available_players_raw_data.json", 'r') as f:
            tank01_data = json.load(f)
        
        if "available_players" in tank01_data and tank01_data["available_players"]:
            sample_tank01 = tank01_data["available_players"][0]
            print(f"Tank01 player fields: {len(sample_tank01.keys())} fields")
            print(f"Tank01 sample fields: {list(sample_tank01.keys())[:10]}...")
            
    except Exception as e:
        print(f"Could not analyze Tank01 data: {e}")

if __name__ == "__main__":
    calculate_token_usage()
    analyze_current_data_structure()
