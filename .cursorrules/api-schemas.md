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
- **My Roster**: `roster_players` array contains all player data
- **Opponent Rosters**: `rosters` dictionary keyed by `team_key` (e.g., "461.l.595012.t.1")
- **Team Matchups**: `matchups` array contains matchup objects
- **Available Players**: `available_players` array contains 1,095+ players
- **Transaction Trends**: `transactions` array contains transaction objects

#### **Common Mistakes to Avoid:**
- ❌ **Don't assume** `rosters` is an array - it's a dictionary keyed by team_key
- ❌ **Don't assume** `teams` contains player data - it only has team metadata
- ✅ **Always check** the actual structure before accessing data
- ✅ **Use** `roster_players` for my roster, `rosters[team_key].players` for opponent rosters

### **2. Sleeper API Data Structure**
**ALWAYS CHECK**: `data_collection/schemas/sleeper_api_schemas.md` for complete details

#### **Key Patterns:**
- **Available Players**: `matched_players` array contains enriched player data
- **Player Structure**: Each player has `yahoo_player`, `sleeper_player`, and `mapping` objects
- **Position Data**: Use `player['yahoo_player']['display_position']` for position filtering
- **Command Line**: Supports `--qb`, `--rb`, `--wr`, `--te`, `--k`, `--defense`, `--flex`, `--all`, `--dev` parameters

#### **Common Mistakes to Avoid:**
- ❌ **Don't assume** position is at top level - it's in `yahoo_player.display_position`
- ❌ **Don't assume** all data is in arrays - check for dictionaries
- ❌ **Don't assume** player data is nested - check top-level keys first
- ✅ **Always check** the actual structure before accessing data
- ✅ **Use** `player['yahoo_player']['display_position']` for position filtering

### **3. Tank01 API Data Structure**
**ALWAYS CHECK**: `data_collection/schemas/tank01_api_schemas.md` for complete details

#### **Key Patterns:**
- **Player Data**: Usually in `processed_data.available_players` array
- **Team Data**: Usually in `processed_data.teams` array
- **Raw Data**: Usually in `raw_data` object

#### **Common Mistakes to Avoid:**
- ❌ **Don't assume** data is at top level - check `processed_data` first
- ❌ **Don't assume** arrays are simple - check for nested structures
- ✅ **Always check** the actual structure before accessing data

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
# My Roster
players = data['roster_players']  # Array of player objects

# Opponent Rosters
rosters = data['rosters']  # Dictionary keyed by team_key
for team_key, roster in rosters.items():
    players = roster['players']  # Array of player objects

# Available Players
players = data['available_players']  # Array of 1,095+ player objects

# Team Matchups
matchups = data['matchups']  # Array of matchup objects
```

### **Sleeper API Data Access:**
```python
# Check schema file for exact structure
# Usually: data['players'] or data['matched_players']
```

### **Tank01 API Data Access:**
```python
# Check schema file for exact structure
# Usually: data['processed_data']['available_players']
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
