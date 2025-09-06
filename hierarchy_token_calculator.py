#!/usr/bin/env python3
"""
Calculate token usage for the user's hierarchy of needs
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_tools import AnalystTools
import tiktoken

def calculate_hierarchy_tokens():
    """Calculate token usage for the user's defined hierarchy"""
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    print("HIERARCHY OF NEEDS - TOKEN CALCULATION")
    print("=" * 50)
    
    # Load current data to get sample structures
    analysis_tools = AnalystTools()
    analysis_data = analysis_tools.analyze_recent_data()
    
    # 1. MY ROSTER (15 players) - Full data from all 3 APIs
    print("\n1. MY ROSTER (15 players)")
    print("-" * 30)
    
    # Get current roster data
    roster_analysis = analysis_data.get("roster_analysis", {})
    yahoo_roster = roster_analysis.get("yahoo", {})
    
    # Calculate tokens for full roster with all APIs
    roster_tokens = 0
    
    # Yahoo roster (current)
    if yahoo_roster:
        yahoo_json = json.dumps(yahoo_roster, indent=2)
        yahoo_tokens = len(encoding.encode(yahoo_json))
        roster_tokens += yahoo_tokens
        print(f"  Yahoo: {yahoo_tokens:,} tokens")
    
    # Estimate Sleeper roster (similar structure)
    sleeper_roster_tokens = yahoo_tokens * 0.8  # Sleeper typically has less metadata
    roster_tokens += sleeper_roster_tokens
    print(f"  Sleeper: {sleeper_roster_tokens:,.0f} tokens (estimated)")
    
    # Estimate Tank01 roster (richer data)
    tank01_roster_tokens = yahoo_tokens * 1.5  # Tank01 has more projections/stats
    roster_tokens += tank01_roster_tokens
    print(f"  Tank01: {tank01_roster_tokens:,.0f} tokens (estimated)")
    
    print(f"  TOTAL ROSTER: {roster_tokens:,.0f} tokens")
    
    # 2. TOP AVAILABLE PLAYERS (25 per position = 175 total)
    print("\n2. TOP AVAILABLE PLAYERS (25 per position = 175 total)")
    print("-" * 50)
    
    # Get current available players structure
    available_players = analysis_data.get("available_players", {})
    yahoo_available = available_players.get("yahoo", {})
    
    available_tokens = 0
    
    if yahoo_available and "top_players_by_position" in yahoo_available:
        # Calculate current tokens per player
        current_players = sum(len(players) for players in yahoo_available["top_players_by_position"].values() if isinstance(players, list))
        current_tokens = 0
        for position, players in yahoo_available["top_players_by_position"].items():
            if isinstance(players, list):
                position_json = json.dumps(players, indent=2)
                position_tokens = len(encoding.encode(position_json))
                current_tokens += position_tokens
        
        tokens_per_player = current_tokens / current_players if current_players > 0 else 0
        print(f"  Current: {current_players} players, {current_tokens:,} tokens")
        print(f"  Tokens per player: {tokens_per_player:.0f}")
        
        # Calculate for 25 per position (175 total)
        positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
        total_players_25 = len(positions) * 25  # 150 players
        total_players_25 += 25  # Multi-position players
        
        # Yahoo available players
        yahoo_25_tokens = total_players_25 * tokens_per_player
        available_tokens += yahoo_25_tokens
        print(f"  Yahoo (25 per position): {yahoo_25_tokens:,.0f} tokens")
        
        # Sleeper available players (similar structure)
        sleeper_25_tokens = yahoo_25_tokens * 0.8
        available_tokens += sleeper_25_tokens
        print(f"  Sleeper (25 per position): {sleeper_25_tokens:,.0f} tokens")
        
        # Tank01 available players (richer data)
        tank01_25_tokens = yahoo_25_tokens * 1.5
        available_tokens += tank01_25_tokens
        print(f"  Tank01 (25 per position): {tank01_25_tokens:,.0f} tokens")
    
    print(f"  TOTAL AVAILABLE: {available_tokens:,.0f} tokens")
    
    # 3. CURRENT WEEK OPPONENT
    print("\n3. CURRENT WEEK OPPONENT")
    print("-" * 30)
    
    # Get current opponent data
    league_context = analysis_data.get("league_context", {})
    opponents = league_context.get("opponents", {})
    opponent_analysis = opponents.get("opponent_analysis", {})
    
    opponent_tokens = 0
    
    if opponent_analysis:
        # Find current opponent (Kissyface - team 5)
        current_opponent = None
        for team_name, team_data in opponent_analysis.items():
            if isinstance(team_data, dict) and team_data.get("team_key") == "461.l.595012.t.5":
                current_opponent = team_data
                break
        
        if current_opponent:
            opponent_json = json.dumps(current_opponent, indent=2)
            opponent_tokens = len(encoding.encode(opponent_json))
            print(f"  Current opponent data: {opponent_tokens:,} tokens")
        else:
            # Estimate based on average team size
            avg_team_tokens = sum(len(encoding.encode(json.dumps(team_data, indent=2))) for team_data in opponent_analysis.values() if isinstance(team_data, dict)) / len(opponent_analysis)
            opponent_tokens = avg_team_tokens
            print(f"  Estimated opponent data: {opponent_tokens:,.0f} tokens")
    
    # Add Sleeper and Tank01 data for opponent
    sleeper_opponent_tokens = opponent_tokens * 0.8
    tank01_opponent_tokens = opponent_tokens * 1.5
    total_opponent_tokens = opponent_tokens + sleeper_opponent_tokens + tank01_opponent_tokens
    
    print(f"  Yahoo opponent: {opponent_tokens:,.0f} tokens")
    print(f"  Sleeper opponent: {sleeper_opponent_tokens:,.0f} tokens")
    print(f"  Tank01 opponent: {tank01_opponent_tokens:,.0f} tokens")
    print(f"  TOTAL OPPONENT: {total_opponent_tokens:,.0f} tokens")
    
    # 4. SEASON/WEEK CONTEXT
    print("\n4. SEASON/WEEK CONTEXT")
    print("-" * 25)
    
    season_context = analysis_data.get("season_context", {})
    season_json = json.dumps(season_context, indent=2)
    season_tokens = len(encoding.encode(season_json))
    print(f"  Season context: {season_tokens:,} tokens")
    
    # 5. ADDITIONAL CONTEXT (matchups, injuries, transactions)
    print("\n5. ADDITIONAL CONTEXT")
    print("-" * 20)
    
    # Matchup context
    matchups = league_context.get("matchups", {})
    matchup_analysis = matchups.get("matchup_analysis", {})
    matchup_json = json.dumps(matchup_analysis, indent=2)
    matchup_tokens = len(encoding.encode(matchup_json))
    print(f"  Matchup context: {matchup_tokens:,} tokens")
    
    # Transaction trends
    transactions = league_context.get("transactions", {})
    transaction_analysis = transactions.get("trending_analysis", {})
    transaction_json = json.dumps(transaction_analysis, indent=2)
    transaction_tokens = len(encoding.encode(transaction_json))
    print(f"  Transaction trends: {transaction_tokens:,} tokens")
    
    # TOTAL CALCULATION
    print("\n" + "=" * 50)
    print("TOTAL TOKEN CALCULATION")
    print("=" * 50)
    
    total_tokens = (
        roster_tokens + 
        available_tokens + 
        total_opponent_tokens + 
        season_tokens + 
        matchup_tokens + 
        transaction_tokens
    )
    
    print(f"1. My Roster: {roster_tokens:,.0f} tokens")
    print(f"2. Available Players: {available_tokens:,.0f} tokens")
    print(f"3. Current Opponent: {total_opponent_tokens:,.0f} tokens")
    print(f"4. Season Context: {season_tokens:,} tokens")
    print(f"5. Matchup Context: {matchup_tokens:,} tokens")
    print(f"6. Transaction Trends: {transaction_tokens:,} tokens")
    print("-" * 30)
    print(f"TOTAL: {total_tokens:,.0f} tokens")
    print(f"Token Limit: 200,000")
    print(f"Status: {'✅ Within Limit' if total_tokens <= 200000 else '❌ Over Limit'}")
    print(f"Buffer: {200000 - total_tokens:,.0f} tokens")
    
    # Scaling recommendations
    print("\n" + "=" * 50)
    print("SCALING RECOMMENDATIONS")
    print("=" * 50)
    
    if total_tokens > 200000:
        excess = total_tokens - 200000
        print(f"Over limit by {excess:,.0f} tokens")
        
        # Calculate scaling factors
        scale_20 = (200000 - (roster_tokens + total_opponent_tokens + season_tokens + matchup_tokens + transaction_tokens)) / available_tokens
        scale_15 = (200000 - (roster_tokens + total_opponent_tokens + season_tokens + matchup_tokens + transaction_tokens)) / (available_tokens * 0.6)
        scale_10 = (200000 - (roster_tokens + total_opponent_tokens + season_tokens + matchup_tokens + transaction_tokens)) / (available_tokens * 0.4)
        
        print(f"Scale to 20 per position: {scale_20:.1f}x available players")
        print(f"Scale to 15 per position: {scale_15:.1f}x available players")
        print(f"Scale to 10 per position: {scale_10:.1f}x available players")

if __name__ == "__main__":
    calculate_hierarchy_tokens()
