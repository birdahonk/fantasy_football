#!/usr/bin/env python3
"""
Analyze just Sleeper API data structure.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.external.sleeper_client import SleeperClient

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

def main():
    """Analyze Sleeper trending data."""
    print("🔍 ANALYZING SLEEPER TRENDING DATA")
    print("=" * 50)
    
    sleeper_client = SleeperClient()
    
    # Get trending add players with details
    print("📈 Fetching trending ADD players with details...")
    trending_add_details = sleeper_client.get_trending_players_with_details('add', lookback_hours=24, limit=10)
    save_debug_data(trending_add_details, "sleeper_trending_add_details")
    
    if trending_add_details and len(trending_add_details) > 0:
        first_player = trending_add_details[0]
        print(f"\n🎯 FIRST TRENDING ADD PLAYER STRUCTURE:")
        print(f"   - Player data keys: {list(first_player.keys())}")
        print(f"   - Player data sample:")
        for key, value in first_player.items():
            if isinstance(value, dict):
                print(f"     - {key}: {dict} with keys {list(value.keys())}")
            elif isinstance(value, list):
                print(f"     - {key}: {list} with {len(value)} items")
            else:
                print(f"     - {key}: {value} ({type(value)})")
    
    # Get trending drop players with details  
    print("\n📉 Fetching trending DROP players with details...")
    trending_drop_details = sleeper_client.get_trending_players_with_details('drop', lookback_hours=24, limit=10)
    save_debug_data(trending_drop_details, "sleeper_trending_drop_details")
    
    print("\n✅ Sleeper analysis complete!")

if __name__ == "__main__":
    main()
