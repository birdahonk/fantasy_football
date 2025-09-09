#!/usr/bin/env python3
"""
Analyze Player Data Fields

Analyzes the field structure across my_roster, opponent_roster, and available_players
to identify what fields are included and create a review file.
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def get_nested_keys(data, prefix="", max_depth=5, current_depth=0):
    """Recursively get all nested keys from a dictionary"""
    if current_depth >= max_depth:
        return []
    
    keys = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_key = f"{prefix}.{key}" if prefix else key
            keys.append(current_key)
            
            if isinstance(value, (dict, list)) and current_depth < max_depth - 1:
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    # If it's a list of dicts, analyze the first item
                    keys.extend(get_nested_keys(value[0], current_key, max_depth, current_depth + 1))
                elif isinstance(value, dict):
                    keys.extend(get_nested_keys(value, current_key, max_depth, current_depth + 1))
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        # If it's a list of dicts, analyze the first item
        keys.extend(get_nested_keys(data[0], prefix, max_depth, current_depth + 1))
    
    return keys

def analyze_player_sections(comprehensive_data):
    """Analyze player data structure across all sections"""
    
    print("Analyzing player data structure...")
    
    # Get player data from each section
    my_roster = comprehensive_data.get('my_roster', {}).get('players_by_position', {})
    opponent_roster = comprehensive_data.get('opponent_roster', {}).get('players_by_position', {})
    available_players = comprehensive_data.get('available_players', {}).get('players_by_position', {})
    
    # Collect all players from all sections
    all_players = []
    
    # My roster players
    for position_type, position_groups in my_roster.items():
        for position, players in position_groups.items():
            all_players.extend(players)
    
    # Opponent roster players
    for position_type, position_groups in opponent_roster.items():
        for position, players in position_groups.items():
            all_players.extend(players)
    
    # Available players
    for position, players in available_players.items():
        all_players.extend(players)
    
    print(f"Total players analyzed: {len(all_players)}")
    
    # Analyze field structure
    all_fields = set()
    field_examples = {}
    
    for i, player in enumerate(all_players[:5]):  # Analyze first 5 players
        player_fields = get_nested_keys(player)
        all_fields.update(player_fields)
        
        if i == 0:  # Use first player as example
            field_examples = player
    
    return sorted(list(all_fields)), field_examples

def create_review_file(fields, example_player, output_file):
    """Create a review file with fields and example"""
    
    print(f"Creating review file: {output_file}")
    
    content = f"""# Player Data Fields Analysis
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Field Structure
The following fields are present in player data across my_roster, opponent_roster, and available_players:

### Top-Level Fields
{chr(10).join(f"- {field}" for field in fields if '.' not in field)}

### Nested Fields
{chr(10).join(f"- {field}" for field in fields if '.' in field)}

## Example Player Data
The following is an actual example of a player from the comprehensive data:

```json
{json.dumps(example_player, indent=2)}
```

## Field Count Summary
- Total unique fields: {len(fields)}
- Top-level fields: {len([f for f in fields if '.' not in f])}
- Nested fields: {len([f for f in fields if '.' in f])}

## Recommendations for Streamlining
Consider removing or simplifying the following high-token fields:
- `tank01_data.news` (array of news items)
- `tank01_data.game_stats` (detailed game statistics)
- `tank01_data.depth_chart` (detailed depth chart info)
- `tank01_data.team_context` (team context data)
- `sleeper_data.player_ids` (extensive ID mapping)
- `tank01_data.player_ids` (extensive ID mapping)

Keep these essential fields for analysis:
- `name` (player name)
- `yahoo_data.display_position` (position)
- `yahoo_data.team` (team)
- `yahoo_data.bye_week` (bye week)
- `yahoo_data.injury_status` (injury status)
- `yahoo_data.percent_owned` (ownership percentage)
- `tank01_data.projection.fantasyPoints` (projected points)
- `tank01_data.projection.fantasyPointsDefault` (default projections)
- `sleeper_data.depth_chart_position` (depth chart position)
- `sleeper_data.years_exp` (experience)
- `sleeper_data.active` (active status)
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print("✅ Review file created successfully!")

def main():
    """Main function"""
    
    print("🔍 ANALYZING PLAYER DATA FIELDS")
    print("=" * 50)
    
    # Load comprehensive data
    validation_dir = os.path.join(project_root, "data_collection", "outputs", "validation_tests", "2025", "09", "08")
    json_files = [f for f in os.listdir(validation_dir) if f.endswith('.json') and 'comprehensive_data_processor' in f]
    latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(validation_dir, f)))
    
    with open(os.path.join(validation_dir, latest_file), 'r') as f:
        comprehensive_data = json.load(f)
    
    print(f"Loaded: {latest_file}")
    
    # Analyze fields
    fields, example_player = analyze_player_sections(comprehensive_data)
    
    # Create review file
    output_file = os.path.join(project_root, "player_fields_analysis.md")
    create_review_file(fields, example_player, output_file)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total unique fields: {len(fields)}")
    print(f"Top-level fields: {len([f for f in fields if '.' not in f])}")
    print(f"Nested fields: {len([f for f in fields if '.' in f])}")
    print(f"\nReview file saved to: {output_file}")

if __name__ == "__main__":
    main()
