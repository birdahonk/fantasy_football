# Sleeper NFL API - Expected Response Schemas

## Overview

This document defines the expected response structures for Sleeper NFL API endpoints. The Sleeper API is completely free with no authentication required and provides comprehensive NFL player data and trending insights.

## ACTUAL PROCESSED DATA STRUCTURES

### **1. My Roster Data Structure**
**File**: `data_collection/outputs/sleeper/my_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_my_roster_raw_data.json`

```json
{
  "extraction_metadata": {
    "script": "sleeper_my_roster.py",
    "extraction_timestamp": "2025-09-08T16:59:11.123456",
    "execution_stats": {
      "start_time": "2025-09-08 16:59:10.123456",
      "api_calls": 0,
      "errors": 0,
      "players_processed": 15,
      "players_matched": 15,
      "players_unmatched": 0
    }
  },
  "season_context": {...},
  "matched_players": [
    {
      "yahoo_player": {
        "player_key": "461.p.32671",
        "player_id": "32671",
        "name": {"full": "Joe Burrow", "first": "Joe", "last": "Burrow"},
        "display_position": "QB",
        "editorial_team_abbr": "Cin",
        "bye_weeks": {"week": "10"},
        "bye_week": "10"
      },
      "sleeper_player": {
        "player_id": "string",
        "full_name": "Joe Burrow",
        "first_name": "Joe",
        "last_name": "Burrow",
        "position": "QB",
        "team": "CIN",
        "age": 27,
        "years_exp": 5,
        "height": "6'4\"",
        "weight": "215",
        "college": "LSU",
        "yahoo_id": "32671"
      },
      "mapping": {
        "match_type": "yahoo_id",
        "confidence": "high"
      }
    }
  ],
  "unmatched_players": []
}
```

### **2. Opponent Roster Data Structure**
**File**: `data_collection/outputs/sleeper/opponent_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_opponent_roster_raw_data.json`

```json
{
  "extraction_metadata": {
    "script": "sleeper_opponent_roster.py",
    "extraction_timestamp": "2025-09-08T17:21:15.713480",
    "opponent_name": "Kissyface",
    "opponent_team_key": "461.l.595012.t.5",
    "execution_stats": {
      "start_time": "2025-09-08 17:21:15.128964",
      "api_calls": 0,
      "errors": 0,
      "players_processed": 15,
      "players_matched": 15,
      "players_unmatched": 0
    }
  },
  "opponent_info": {
    "opponent_name": "Kissyface",
    "opponent_team_key": "461.l.595012.t.5",
    "total_players": 15,
    "matched_players": 15,
    "unmatched_players": 0
  },
  "matched_players": [
    {
      "yahoo_data": {
        "player_key": "461.p.31833",
        "player_id": "31833",
        "name": {"full": "Kyler Murray", "first": "Kyler", "last": "Murray"},
        "display_position": "QB",
        "editorial_team_abbr": "Ari",
        "bye_weeks": {"week": "8"},
        "bye_week": "8"
      },
      "sleeper_player": {
        "player_id": "string",
        "full_name": "Kyler Murray",
        "first_name": "Kyler",
        "last_name": "Murray",
        "position": "QB",
        "team": "ARI",
        "age": 27,
        "years_exp": 6,
        "yahoo_id": "31833"
      },
      "match_type": "yahoo_id"
    }
  ],
  "unmatched_players": []
}
```

### **3. Available Players Data Structure**
**File**: `data_collection/outputs/sleeper/available_players/YYYY/MM/DD/YYYYMMDD_HHMMSS_available_players_raw_data.json`

```json
{
  "extraction_metadata": {
    "script": "sleeper_available_players.py",
    "extraction_timestamp": "2025-09-08T16:59:26.123456",
    "execution_stats": {
      "start_time": "2025-09-08 16:59:25.123456",
      "api_calls": 0,
      "errors": 0,
      "players_processed": 110,
      "players_matched": 110,
      "players_unmatched": 0
    }
  },
  "season_context": {...},
  "matched_players": [
    {
      "yahoo_player": {
        "player_key": "461.p.12345",
        "player_id": "12345",
        "name": {"full": "Evan Engram", "first": "Evan", "last": "Engram"},
        "display_position": "TE",
        "editorial_team_abbr": "Den",
        "bye_weeks": {"week": "10"},
        "bye_week": "10"
      },
      "sleeper_player": {
        "player_id": "string",
        "full_name": "Evan Engram",
        "first_name": "Evan",
        "last_name": "Engram",
        "position": "TE",
        "team": "DEN",
        "age": 30,
        "years_exp": 8,
        "yahoo_id": "12345"
      },
      "mapping": {
        "match_method": "direct_yahoo_id|name_team_match|defense_team_match",
        "confidence": "high|medium|low"
      }
    }
  ],
  "unmatched_players": []
}
```

**Key Notes:**
- **Position Filtering**: Script applies position-based limits (default: QB:20, RB:20, WR:20, TE:20, K:20, DEF:10, FLEX:15)
- **Player Structure**: Each matched player contains both `yahoo_player` and `sleeper_player` data
- **Position Access**: Use `player['yahoo_player']['display_position']` for position filtering
- **Command Line Options**: Supports `--qb`, `--rb`, `--wr`, `--te`, `--k`, `--defense`, `--flex`, `--all`, `--dev` parameters

### **4. Trending Players Data Structure**
**File**: `data_collection/outputs/sleeper/trending/YYYY/MM/DD/YYYYMMDD_HHMMSS_trending_raw_data.json`

```json
{
  "extraction_metadata": {
    "source": "Sleeper API - Trending Players",
    "extraction_timestamp": "2025-09-08T16:59:43.945700",
    "lookback_period": "24 hours",
    "nfl_state": {
      "week": 1,
      "leg": 1,
      "season": "2025",
      "season_type": "regular",
      "league_season": "2025",
      "previous_season": "2024",
      "season_start_date": "2025-09-04",
      "display_week": 1,
      "league_create_season": "2025",
      "season_has_scores": true
    },
    "execution_stats": {
      "start_time": "2025-09-08 16:59:41.591454",
      "api_calls": 3,
      "errors": 0,
      "trending_adds_count": 25,
      "trending_drops_count": 25,
      "enriched_players": 50,
      "execution_time": 2.352834
    }
  },
  "season_context": {...},
  "trending_adds": [
    {
      "trend_type": "add",
      "trend_count": 1234,
      "player_id": "string",
      "player_details": {...},
      "trend_data": {...}
    }
  ],
  "trending_drops": [
    {
      "trend_type": "drop",
      "trend_count": 567,
      "player_id": "string",
      "player_details": {...},
      "trend_data": {...}
    }
  ],
  "raw_trending_adds": [
    {
      "player_id": "string",
      "full_name": "Quentin Johnston",
      "first_name": "Quentin",
      "last_name": "Johnston",
      "position": "WR",
      "team": "LAC",
      "age": 22,
      "years_exp": 2,
      "trending_count": 1234,
      "trending_type": "add",
      "yahoo_id": "string"
    }
  ],
  "raw_trending_drops": [
    {
      "player_id": "string",
      "full_name": "Marvin Mims",
      "first_name": "Marvin",
      "last_name": "Mims",
      "position": "WR",
      "team": "DEN",
      "age": 22,
      "years_exp": 2,
      "trending_count": 567,
      "trending_type": "drop",
      "yahoo_id": "string"
    }
  ]
}
```

**Key Notes:**
- **Trending Data**: Separate arrays for `trending_adds` and `trending_drops` (25 each)
- **Raw Data**: `raw_trending_adds` and `raw_trending_drops` contain full player details
- **Player Structure**: Raw data includes complete Sleeper player information
- **Trending Counts**: Shows how many times players were added/dropped in 24 hours

## API Details

- **Base URL**: `https://api.sleeper.app/v1/`
- **Authentication**: None required (completely free)
- **Rate Limits**: Reasonable usage (no strict limits documented)
- **Data Coverage**: 11,400+ NFL players with comprehensive metadata

## ⚠️ CRITICAL: Correct Endpoint Names

**DO NOT USE THESE INCORRECT ENDPOINTS** (they will return 404 errors):
- ❌ `players/nfl/news` → ✅ News data comes from player objects (`news_updated` field)

**All Valid Endpoints:**
- ✅ `state/nfl` - NFL season state and current week
- ✅ `players/nfl` - Complete player database
- ✅ `players/nfl/trending/add` - Trending adds
- ✅ `players/nfl/trending/drop` - Trending drops  
- ✅ `players/nfl/trending/waiver` - Trending waivers

**News Data Access:**
- News information is embedded in player objects via the `news_updated` field
- No separate news endpoint exists
- Use `players/nfl` and extract `news_updated` timestamp for each player

---

## 1. NFL Players Database - `players/nfl`

### Expected Response Structure:
```json
{
  "player_id": {
    "player_id": "string",
    "first_name": "string", 
    "last_name": "string",
    "full_name": "string",
    "position": "string",
    "team": "string",
    "age": "number",
    "birth_date": "string",
    "years_exp": "number",
    "height": "string",
    "weight": "string",
    "college": "string",
    "high_school": "string",
    "birth_city": "string",
    "birth_state": "string",
    "birth_country": "string",
    "status": "string",
    "injury_status": "string",
    "injury_body_part": "string", 
    "injury_start_date": "string",
    "injury_notes": "string",
    "fantasy_data_id": "number",
    "espn_id": "number",
    "yahoo_id": "number",
    "rotowire_id": "number",
    "sportradar_id": "string",
    "stats_id": "number",
    "gsis_id": "string",
    "depth_chart_position": "string",
    "depth_chart_order": "number",
    "practice_participation": "string",
    "practice_description": "string",
    "active": true,
    "sport": "nfl",
    "news_updated": "number"
  }
}
```

### Key Data Points:
- **Player Identity**: player_id, full_name, position, team
- **Physical Stats**: age, height, weight, years_exp
- **Injury Information**: injury_status, injury_body_part, injury_notes
- **Depth Chart**: depth_chart_position, depth_chart_order
- **Cross-Platform IDs**: yahoo_id, espn_id, fantasy_data_id
- **News Updates**: news_updated timestamp

---

## 2. Trending Players (Adds) - `players/nfl/trending/add?lookback_hours={hours}&limit={limit}`

### Expected Response Structure:
```json
[
  {
    "player_id": "string",
    "count": "number"
  }
]
```

### Enhanced Response (with player details):
```json
[
  {
    "player_id": "string",
    "count": "number",
    "trending_count": "number",
    "player_data": {
      "player_id": "string",
      "full_name": "string",
      "position": "string", 
      "team": "string",
      "injury_status": "string",
      "age": "number",
      "years_exp": "number"
    }
  }
]
```

### Key Data Points:
- **Trending Metrics**: count (trending activity), lookback period
- **Player Details**: Full player information from database
- **Market Intelligence**: Players being added rapidly

### ✅ **Validation Status**: COMPLETE - All data extracted successfully
- **Script**: `sleeper_trending.py`
- **Data Quality**: 25 trending adds with full player enrichment
- **Performance**: 1.69s execution, 3 API calls, 0 errors
- **Special Handling**: Defense names converted to team names in ALL CAPS (e.g., "ARIZONA", "NEW ENGLAND")

---

## 3. Trending Players (Drops) - `players/nfl/trending/drop?lookback_hours={hours}&limit={limit}`

### Expected Response Structure:
```json
[
  {
    "player_id": "string",
    "count": "number"  
  }
]
```

### Key Data Points:
- **Trending Metrics**: count (drop activity), lookback period  
- **Market Intelligence**: Players being dropped rapidly
- **Avoid Signals**: Players with injury/performance issues

### ✅ **Validation Status**: COMPLETE - All data extracted successfully
- **Script**: `sleeper_trending.py`
- **Data Quality**: 25 trending drops with full player enrichment
- **Performance**: 1.69s execution, 3 API calls, 0 errors
- **Special Handling**: Defense names converted to team names in ALL CAPS

---

## 4. NFL Season State - `state/nfl`

### Expected Response Structure:
```json
{
  "week": "number",
  "season_type": "string",
  "season": "string",
  "previous_season": "string", 
  "display_week": "number",
  "season_start_date": "string",
  "leg": "number"
}
```

### Key Data Points:
- **Current State**: week, season, season_type
- **Timing**: season_start_date, display_week
- **Context**: For aligning trending data with NFL schedule

---

## Player Roster Stats Integration

### For My Roster Players:
1. **Get Yahoo roster** (player names/IDs)
2. **Match to Sleeper database** using name matching algorithms
3. **Extract enhanced data**:
   - Real-time injury status (more current than Yahoo)
   - Depth chart position and order
   - Physical stats and experience
   - Cross-platform IDs for further integration

### ✅ **Enhanced My Roster Script**: COMPLETE - All data extracted successfully
- **Script**: `sleeper_my_roster.py`
- **Data Quality**: 15/15 players matched (100% success rate)
- **Performance**: 0.60s execution, 0 errors
- **Enhanced Fields Added**:
  - **Injury Tracking**: injury_status, injury_body_part, injury_notes, injury_start_date
  - **Practice Data**: practice_participation, practice_description
  - **Depth Chart**: depth_chart_position, depth_chart_order
  - **Physical Stats**: age, height, weight, years_exp, college, high_school
  - **Birthplace**: birth_city, birth_state, birth_country
  - **Cross-Platform IDs**: ESPN, RotoWire, Rotoworld, Sportradar, GSIS, Stats, FantasyData
  - **News Metadata**: news_updated (formatted timestamps), search_rank, hashtag
  - **Fantasy Positions**: Array of eligible fantasy positions per player

### ✅ **Available Players Script**: COMPLETE - All data extracted successfully
- **Script**: `sleeper_available_players.py`
- **Data Quality**: 1,095/1,095 players matched (100% success rate)
- **Performance**: 3.84s execution, 0 errors
- **Data Source**: Latest Yahoo available_players.py output
- **Output Structure**:
  - **Summary Table**: First 100 players with comprehensive Sleeper data
  - **Position Breakdown**: Count statistics by position (QB: 132, RB: 220, TE: 228, etc.)
  - **Detailed Sections**: Top 10 players per position with full Sleeper information
  - **Defense Names**: Team names in ALL CAPS (e.g., "ARIZONA", "NEW ENGLAND")
- **Enhanced Fields**: Same comprehensive data as my_roster script for all available players

### ✅ **Opponent Roster Script**: COMPLETE - All data extracted successfully
- **Script**: `sleeper_opponent_roster.py`
- **Data Quality**: 15/15 players matched (100% success rate)
- **Performance**: 0.60s execution, 0 errors
- **Data Source**: Latest Yahoo opponent_rosters.py output
- **Current Week Opponent**: Automatically identifies current week opponent from Yahoo team matchups
- **Output Structure**:
  - **Matched Players**: Array of opponent players with Sleeper enrichment
  - **Yahoo Player Data**: Original Yahoo player information
  - **Sleeper Player Data**: Enhanced Sleeper metadata and injury status
  - **Team Context**: Opponent team name and identification
- **Enhanced Fields**: Same comprehensive data as my_roster script for opponent players

### For Available Players:
1. **Get Yahoo free agents list**
2. **Match to Sleeper database**
3. **Add trending intelligence**:
   - Current add/drop trends
   - Injury status updates
   - Market activity insights
4. **Enhance recommendations** with market intelligence

---

## Data Enrichment Patterns

### Player Matching Algorithm:
```python
def match_player(yahoo_name, yahoo_team, sleeper_players):
    # 1. Exact name match
    # 2. Last name + team match  
    # 3. First + last initial match
    # 4. Sound-alike matching
    # Success rate: ~87% based on testing
```

### Cross-Reference Fields:
- **yahoo_id**: Direct Yahoo Fantasy player ID mapping
- **team**: NFL team abbreviation matching
- **position**: Position consistency validation
- **injury_status**: Real-time injury updates

## Team Defense Data

Team defense players in Sleeper have a special structure:

```json
{
  "player_id": "DEF_WSH",
  "first_name": "Washington",
  "last_name": "Commanders",
  "full_name": "Washington Commanders",
  "position": "DEF",
  "team": "WAS",
  "age": null,
  "birth_date": null,
  "years_exp": null,
  "height": null,
  "weight": null,
  "college": null,
  "status": "Active",
  "injury_status": null,
  "active": true,
  "sport": "nfl"
}
```

**Key Defense Player Fields**:
- **Name**: Full team name (e.g., "Washington Commanders", "Philadelphia Eagles")
- **Position**: Always "DEF"
- **Team**: Team abbreviation (e.g., "WAS", "PHI", "LAR")
- **Player ID**: Format "DEF_{TEAM_ABBR}" (e.g., "DEF_WSH", "DEF_PHI")
- **No Individual Stats**: Most individual player fields are null for defense

**Defense Player Identification Patterns**:
- **Sleeper Team Abbreviations**: Uses uppercase (e.g., "WAS", "PHI", "LAR", "CIN", "JAX")
- **Team Name Mapping**: Full team names in `full_name` field
- **Cross-API Matching**: Requires team abbreviation normalization for matching with Yahoo and Tank01
- **Special Handling**: Defense names converted to team names in ALL CAPS for display

---

## Validation Rules

### Required Fields:
- **player_id**: Must be present for all players
- **full_name**: Must be extractable for matching
- **position**: Must be valid NFL position
- **team**: Must be valid NFL team abbreviation (or null for free agents)

### Data Quality Checks:
- **Trending Data**: count > 0 for meaningful trends
- **Injury Data**: injury_status should be null or valid status
- **Depth Chart**: depth_chart_order should be numeric (1-99)
- **Cross-Platform IDs**: Should be numeric where present

### Enhancement Success Metrics:
- **Match Rate**: Target 85%+ player matching success
- **Injury Currency**: Sleeper injury data should be within 24 hours
- **Trending Relevance**: Focus on lookback_hours=24 for current trends

---

## Error Handling

### API Failures:
- Network timeouts (5-10 second timeout)
- JSON parsing errors (malformed responses)
- Rate limiting (though none currently enforced)

### Data Quality Issues:
- Missing player data (graceful degradation)
- Name matching failures (log for manual review)
- Team/position mismatches (flag for validation)

### Graceful Degradation:
- Continue processing if individual players fail
- Log match failures for improvement
- Provide partial data rather than complete failure

---

**Note**: The Sleeper API is exceptionally reliable and free. Use it extensively for player enhancement and market intelligence. The 87% matching rate with Yahoo players is excellent for this type of cross-platform integration.
