#!/usr/bin/env python3
"""
Token Usage Analysis Script
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

def analyze_comprehensive_data():
    """Analyze token usage for comprehensive data"""
    
    print("=== COMPREHENSIVE DATA TOKEN ANALYSIS ===")
    
    # Load latest comprehensive data
    validation_dir = os.path.join(project_root, "data_collection", "outputs", "validation_tests", "2025", "09", "08")
    json_files = [f for f in os.listdir(validation_dir) if f.endswith('.json') and 'comprehensive_data_processor' in f]
    latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(validation_dir, f)))
    
    with open(os.path.join(validation_dir, latest_file), 'r') as f:
        data = json.load(f)
    
    # Calculate total tokens
    total_json = json.dumps(data, indent=2)
    total_tokens = calculate_tokens(total_json)
    
    print(f"Total tokens: {total_tokens:,}")
    print()
    
    # Analyze sections
    sections = {
        'my_roster': data.get('my_roster', {}),
        'opponent_roster': data.get('opponent_roster', {}),
        'available_players': data.get('available_players', {}),
        'nfl_matchups': data.get('nfl_matchups', {}),
        'season_context': data.get('season_context', {}),
        'league_metadata': data.get('league_metadata', {})
    }
    
    for name, section in sections.items():
        section_json = json.dumps(section, indent=2)
        section_tokens = calculate_tokens(section_json)
        percentage = (section_tokens / total_tokens) * 100
        print(f"{name:20s}: {section_tokens:8,} tokens ({percentage:5.1f}%)")
    
    return data, total_tokens

def analyze_prompt_tokens(data):
    """Analyze prompt token usage"""
    
    print("\n=== PROMPT TOKEN ANALYSIS ===")
    
    # Build prompt sections
    my_roster_json = json.dumps(data.get('my_roster', {}).get('players_by_position', {}), indent=2)
    opponent_json = json.dumps(data.get('opponent_roster', {}).get('players_by_position', {}), indent=2)
    available_json = json.dumps(data.get('available_players', {}).get('players_by_position', {}), indent=2)
    nfl_json = json.dumps(data.get('nfl_matchups', {}), indent=2)
    
    # Calculate section tokens
    my_tokens = calculate_tokens(my_roster_json)
    opponent_tokens = calculate_tokens(opponent_json)
    available_tokens = calculate_tokens(available_json)
    nfl_tokens = calculate_tokens(nfl_json)
    
    print(f"My roster: {my_tokens:,} tokens")
    print(f"Opponent roster: {opponent_tokens:,} tokens")
    print(f"Available players: {available_tokens:,} tokens")
    print(f"NFL matchups: {nfl_tokens:,} tokens")
    
    # Estimate full prompt (rough)
    prompt_estimate = my_tokens + opponent_tokens + available_tokens + nfl_tokens + 5000  # +5k for instructions
    print(f"\nEstimated full prompt: {prompt_estimate:,} tokens")
    
    return {
        'my_roster': my_tokens,
        'opponent': opponent_tokens,
        'available': available_tokens,
        'nfl': nfl_tokens,
        'total': prompt_estimate
    }

def main():
    print("🔍 TOKEN USAGE ANALYSIS")
    print("=" * 50)
    
    data, comp_tokens = analyze_comprehensive_data()
    prompt_analysis = analyze_prompt_tokens(data)
    
    print(f"\n=== SUMMARY ===")
    print(f"Comprehensive data: {comp_tokens:,} tokens")
    print(f"Estimated prompt: {prompt_analysis['total']:,} tokens")
    print(f"Token limit: 200,000")
    
    if prompt_analysis['total'] > 200000:
        excess = prompt_analysis['total'] - 200000
        print(f"❌ OVER LIMIT by {excess:,} tokens")
        print(f"\nBiggest contributors:")
        print(f"  Available players: {prompt_analysis['available']:,} tokens")
        print(f"  My roster: {prompt_analysis['my_roster']:,} tokens")
        print(f"  Opponent: {prompt_analysis['opponent']:,} tokens")
        print(f"  NFL matchups: {prompt_analysis['nfl']:,} tokens")
    else:
        remaining = 200000 - prompt_analysis['total']
        print(f"✅ Within limit! {remaining:,} tokens remaining")

if __name__ == "__main__":
    main()