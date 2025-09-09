# API Data Schemas and Structure Guide

## Overview

This guide provides high-level structure guidance for working with API data in this fantasy football project. **ALWAYS reference the detailed schema files before creating new scripts or analyzing API output data.**

## 📁 Schema Files Location
- **Yahoo API**: `data_collection/schemas/yahoo_api_schemas.md`
- **Sleeper API**: `data_collection/schemas/sleeper_api_schemas.md`
- **Tank01 API**: `data_collection/schemas/tank01_api_schemas.md`
- **Comprehensive Data**: `data_collection/schemas/comprehensive_data_schemas.md`

## 🚨 Critical Data Structure Patterns

### **1. Yahoo API Data Structure**
**ALWAYS CHECK**: `data_collection/schemas/yahoo_api_schemas.md` for complete details

#### **Key Patterns:**
- **My Roster**: Complex nested structure - roster data at `team[1].roster` with players in numbered keys
- **Opponent Rosters**: `rosters` dictionary keyed by `team_key` (e.g., "461.l.595012.t.1") with `players` arrays
- **Team Matchups**: `matchups.week_1.matchups` array contains matchup objects
- **Available Players**: `available_players` array contains 1,095+ players (or `all_players`)
- **Transaction Trends**: `transactions` array contains transaction objects

#### **Critical Parsing Notes:**
- **My Roster**: Players are in `roster_raw.fantasy_content.team[1].roster.0.players` with complex nested structure
- **Opponent Rosters**: Players are already processed into simple arrays in `rosters[team_key].players`
- **Available Players**: Direct access to `available_players` array (1,095 players total)
- **Team Matchups**: Nested under `matchups.week_1.matchups` with team pairs

#### **Common Mistakes to Avoid:**
- ❌ **Don't assume** my roster has simple structure - it's deeply nested
- ❌ **Don't assume** `rosters` is an array - it's a dictionary keyed by team_key
- ❌ **Don't assume** `teams` contains player data - it only has team metadata
- ❌ **Don't assume** available players are in `players` - they're in `available_players`
- ✅ **Always check** the actual structure before accessing data
- ✅ **Use** complex parsing for my roster, simple access for opponent rosters

### **2. Sleeper API Data Structure**
**ALWAYS CHECK**: `data_collection/schemas/sleeper_api_schemas.md` for complete details

#### **Key Patterns:**
- **My Roster**: `matched_players` array with `yahoo_player`, `sleeper_player`, `mapping` objects
- **Opponent Roster**: `matched_players` array with `yahoo_data`, `sleeper_player`, `match_type` objects
- **Available Players**: `matched_players` array contains 110 enriched players (optimized subset)
- **Trending Players**: `trending_adds`, `trending_drops`, `raw_trending_adds`, `raw_trending_drops` arrays
- **Position Data**: Use `player['yahoo_player']['display_position']` for position filtering
- **Command Line**: Supports `--qb`, `--rb`, `--wr`, `--te`, `--k`, `--defense`, `--flex`, `--all`, `--dev` parameters

#### **Critical Structure Differences:**
- **My Roster**: Uses `yahoo_player` key for Yahoo data
- **Opponent Roster**: Uses `yahoo_data` key for Yahoo data (different structure!)
- **Available Players**: Uses `yahoo_player` key for Yahoo data
- **Trending Players**: Uses `raw_trending_adds`/`raw_trending_drops` for full player data

#### **Common Mistakes to Avoid:**
- ❌ **Don't assume** all scripts use same structure - opponent roster uses `yahoo_data` not `yahoo_player`
- ❌ **Don't assume** position is at top level - it's in `yahoo_player.display_position` or `yahoo_data.display_position`
- ❌ **Don't assume** all data is in arrays - check for dictionaries
- ❌ **Don't assume** available players has full 1,095 players - it's optimized to 110
- ✅ **Always check** the actual structure before accessing data
- ✅ **Use** correct key names based on script type (`yahoo_player` vs `yahoo_data`)

### **3. Tank01 API Data Structure**
**ALWAYS CHECK**: `data_collection/schemas/tank01_api_schemas.md` for complete details

#### **Key Patterns:**
- **My Roster**: `matched_players` array with `yahoo_player`, `tank01_data` objects
- **Opponent Roster**: `matched_players` array with `yahoo_data`, `tank01_data`, `match_type` objects
- **Available Players**: `processed_data.available_players` array contains 125 enriched players (optimized subset)
- **NFL Matchups**: `games` array with complete game information
- **Transaction Trends**: `enriched_players` array with `yahoo_data`, `tank01_data`, `match_status` objects
- **Position Data**: Use `player['yahoo_player']['display_position']` or `player['yahoo_data']['display_position']` for position filtering
- **Command Line**: Supports `--qb`, `--rb`, `--wr`, `--te`, `--k`, `--defense`, `--flex`, `--all`, `--dev` parameters
- **Team Mapping**: Uses shared `team_mapping.py` for consistent team abbreviation normalization
- **Defense Players**: Special handling for team defense with `DEF_{teamID}` format

#### **Critical Structure Differences:**
- **My Roster**: Uses `yahoo_player` key for Yahoo data
- **Opponent Roster**: Uses `yahoo_data` key for Yahoo data (different structure!)
- **Available Players**: Uses `yahoo_data` key for Yahoo data, nested under `processed_data.available_players`
- **Transaction Trends**: Uses `yahoo_data` key for Yahoo data, different structure than other scripts
- **NFL Matchups**: Direct `games` array with game information

#### **Common Mistakes to Avoid:**
- ❌ **Don't assume** all scripts use same structure - different scripts use different Yahoo data keys
- ❌ **Don't assume** position is at top level - it's in `yahoo_player.display_position` or `yahoo_data.display_position`
- ❌ **Don't assume** all data is in arrays - check for dictionaries
- ❌ **Don't assume** available players has full 1,095 players - it's optimized to 125
- ❌ **Don't assume** team abbreviations are consistent - use `normalize_team_abbreviation()`
- ❌ **Don't assume** defense players are individual players - they're team-based
- ✅ **Always check** the actual structure before accessing data
- ✅ **Use** correct key names based on script type (`yahoo_player` vs `yahoo_data`)
- ✅ **Use** shared team mapping for consistent team abbreviation handling

## 🔧 Script Creation Guidelines

### **Before Creating Any New Script:**
1. **Read the relevant schema file** for the API you're working with
2. **Check existing scripts** in `data_collection/scripts/{api_name}/` for patterns
3. **Understand the data structure** before writing any code
4. **Test with small data samples** before processing large datasets

### **Before Analyzing API Output Data:**
1. **Read the relevant schema file** to understand expected structure
2. **Check the actual data structure** using `print(list(data.keys()))`
3. **Verify assumptions** about arrays vs dictionaries
4. **Use the schema as a reference** for field names and nesting

## 📊 Data Access Patterns

### **Yahoo API Data Access:**
```python
# My Roster - COMPLEX NESTED STRUCTURE
roster_raw = data.get('roster_raw', {})
fantasy_content = roster_raw.get('fantasy_content', {})
team_data = fantasy_content.get('team', [])
if team_data and len(team_data) > 1:
    roster_data = team_data[1]  # Roster data is at index 1
    if isinstance(roster_data, dict) and 'roster' in roster_data:
        roster = roster_data['roster']
        # Extract players from numbered keys (0, 1, 2, etc.)
        for key, value in roster.items():
            if key.isdigit() and isinstance(value, dict) and 'players' in value:
                players_data = value['players']
                # Process players...

# Opponent Rosters - SIMPLE STRUCTURE
rosters = data['rosters']  # Dictionary keyed by team_key
for team_key, roster in rosters.items():
    players = roster['players']  # Array of player objects (15-16 per team)

# Available Players - DIRECT ACCESS
players = data['available_players']  # Array of 1,095+ player objects
# OR
players = data['all_players']  # Alternative player list

# Team Matchups - NESTED STRUCTURE
matchups = data['matchups']['week_1']['matchups']  # Array of matchup objects
```

### **Sleeper API Data Access:**
```python
# My Roster - STANDARD STRUCTURE
matched_players = data['matched_players']  # Array of player objects
for player in matched_players:
    yahoo_data = player['yahoo_player']  # Yahoo player data
    sleeper_data = player['sleeper_player']  # Sleeper player data
    position = yahoo_data['display_position']
    team = yahoo_data['editorial_team_abbr']

# Opponent Roster - DIFFERENT STRUCTURE
matched_players = data['matched_players']  # Array of player objects
for player in matched_players:
    yahoo_data = player['yahoo_data']  # Note: 'yahoo_data' not 'yahoo_player'
    sleeper_data = player['sleeper_player']  # Sleeper player data
    position = yahoo_data['display_position']
    team = yahoo_data['editorial_team_abbr']

# Available Players - STANDARD STRUCTURE (110 players)
matched_players = data['matched_players']  # Array of 110 player objects
for player in matched_players:
    yahoo_data = player['yahoo_player']  # Yahoo player data
    sleeper_data = player['sleeper_player']  # Sleeper player data
    position = yahoo_data['display_position']

# Trending Players - MULTIPLE ARRAYS
trending_adds = data['trending_adds']  # Array of trending add objects
trending_drops = data['trending_drops']  # Array of trending drop objects
raw_adds = data['raw_trending_adds']  # Array of full player data for adds
raw_drops = data['raw_trending_drops']  # Array of full player data for drops
```

### **Tank01 API Data Access:**
```python
# My Roster - STANDARD STRUCTURE
matched_players = data['matched_players']  # Array of player objects
for player in matched_players:
    yahoo_data = player['yahoo_player']  # Yahoo player data
    tank01_data = player['tank01_data']  # Tank01 player data
    position = yahoo_data['display_position']
    team = yahoo_data['editorial_team_abbr']

# Opponent Roster - DIFFERENT STRUCTURE
matched_players = data['matched_players']  # Array of player objects
for player in matched_players:
    yahoo_data = player['yahoo_data']  # Note: 'yahoo_data' not 'yahoo_player'
    tank01_data = player['tank01_data']  # Tank01 player data
    position = yahoo_data['display_position']
    team = yahoo_data['editorial_team_abbr']

# Available Players - NESTED STRUCTURE (125 players)
processed_data = data['processed_data']
available_players = processed_data['available_players']  # Array of 125 player objects
for player in available_players:
    yahoo_data = player['yahoo_data']  # Yahoo player data
    tank01_data = player['tank01_data']  # Tank01 player data
    position = yahoo_data['display_position']
    team = yahoo_data['editorial_team_abbr']

# NFL Matchups - DIRECT STRUCTURE
games = data['games']  # Array of game objects
for game in games:
    home_team = game['home_team']
    away_team = game['away_team']
    game_time = game['game_time_et']
    week = game['week']

# Transaction Trends - ENRICHED STRUCTURE
enriched_players = data['enriched_players']  # Array of enriched transaction players
for player in enriched_players:
    yahoo_data = player['yahoo_data']  # Yahoo player data
    tank01_data = player['tank01_data']  # Tank01 player data
    match_status = player['match_status']
    match_confidence = player['match_confidence']
```

## ⚠️ Common Pitfalls

1. **Dictionary vs Array Confusion**: Always check the actual data type
2. **Nested Data Access**: Don't assume data is at the top level
3. **Key Naming**: Field names may differ between APIs
4. **Data Structure Changes**: APIs may change structure over time
5. **Missing Fields**: Always handle missing fields gracefully

## 🎯 Best Practices

1. **Always reference schema files** before writing code
2. **Test data access** with small samples first
3. **Handle missing data** gracefully with `.get()` methods
4. **Log data structure** when debugging
5. **Update schema files** when data structures change

## 📝 Quick Reference

- **Yahoo**: `data_collection/schemas/yahoo_api_schemas.md`
- **Sleeper**: `data_collection/schemas/sleeper_api_schemas.md`
- **Tank01**: `data_collection/schemas/tank01_api_schemas.md`
- **Comprehensive**: `data_collection/schemas/comprehensive_data_schemas.md`

**Remember**: The schema files contain the complete, detailed information. This guide is just a high-level overview to prevent common mistakes.
