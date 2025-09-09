# Complete Fantasy Football Data Pipeline Walkthrough

## Executive Summary

This document provides a comprehensive walkthrough of the entire fantasy football data pipeline, from initial data collection through AI agent analysis. The pipeline consists of 14 data collection scripts, a comprehensive data processor, and an AI analyst agent, all working together to provide 100% accurate, enriched player data for fantasy football analysis.

### Process Overview
1. **Yahoo Data Collection** (7 scripts) - Collects base player data, rosters, and league information
2. **Sleeper Data Enrichment** (4 scripts) - Matches Yahoo players to Sleeper database for enhanced data
3. **Tank01 Data Enrichment** (3 scripts) - Matches Yahoo players to Tank01 database for projections
4. **Comprehensive Data Processing** - Combines all data sources into unified player profiles
5. **AI Agent Analysis** - Analyzes enriched data to provide fantasy recommendations

---

## Phase 1: Yahoo Fantasy Data Collection

### 1.1 League Information Collection

**Script**: `data_collection/scripts/yahoo/league_settings.py`
**Output**: `data_collection/outputs/yahoo/league_settings/YYYY/MM/DD/YYYYMMDD_HHMMSS_league_settings_raw_data.json`

**Purpose**: Establishes league context and configuration
**Data Structure**: Dictionary containing league metadata
```json
{
  "league_info": {
    "league_key": "461.l.595012",
    "league_name": "Fantasy League",
    "season": "2025"
  },
  "settings": {
    "scoring_type": "head",
    "roster_positions": {...},
    "stat_categories": {...}
  }
}
```

**Key Variables**:
- `league_key`: Used by all subsequent scripts to identify the league
- `roster_positions`: Defines valid positions for player categorization
- `scoring_type`: Determines how points are calculated

### 1.2 Season Context Collection

**Script**: `data_collection/scripts/yahoo/season_info.py`
**Output**: `data_collection/outputs/yahoo/season_info/YYYY/MM/DD/YYYYMMDD_HHMMSS_season_info_raw_data.json`

**Purpose**: Establishes current week and season timing
**Data Structure**: Dictionary with season metadata
```json
{
  "season_context": {
    "nfl_season": "2025",
    "current_week": 1,
    "season_phase": "Early Regular Season"
  }
}
```

**Key Variables**:
- `current_week`: Used for matchup analysis and weekly projections
- `nfl_season`: Ensures data consistency across all APIs

### 1.3 Team Matchup Collection

**Script**: `data_collection/scripts/yahoo/team_matchups.py`
**Output**: `data_collection/outputs/yahoo/team_matchups/YYYY/MM/DD/YYYYMMDD_HHMMSS_team_matchups_raw_data.json`

**Purpose**: Identifies current week opponents for each team
**Data Structure**: Dictionary containing team matchup information
```json
{
  "teams": [
    {
      "team_key": "461.l.595012.t.1",
      "name": "birdahonkers",
      "matchups": [
        {
          "week": 1,
          "opponent": "461.l.595012.t.5",
          "opponent_name": "Kissyface"
        }
      ]
    }
  ]
}
```

**Key Variables**:
- `team_key`: Used to identify specific teams in subsequent scripts
- `opponent`: Team key of the current week opponent
- `opponent_name`: Human-readable opponent name

### 1.4 My Roster Collection

**Script**: `data_collection/scripts/yahoo/my_roster.py`
**Output**: `data_collection/outputs/yahoo/my_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_my_roster_raw_data.json`

**Purpose**: Collects the user's current roster with player details
**Data Structure**: Dictionary containing roster information
```json
{
  "teams": [
    {
      "team_key": "461.l.595012.t.1",
      "name": "birdahonkers",
      "roster": {
        "players": [
          {
            "player_key": "461.p.12345",
            "player_id": "12345",
            "name": {
              "full": "Joe Burrow",
              "first": "Joe",
              "last": "Burrow"
            },
            "editorial_team_abbr": "Cin",
            "display_position": "QB",
            "selected_position": "QB"
          }
        ]
      }
    }
  ]
}
```

**Key Variables**:
- `player_key`: Unique identifier for each player (used for matching)
- `player_id`: Numeric player identifier
- `editorial_team_abbr`: Team abbreviation (e.g., "Cin", "SF", "Sea")
- `display_position`: Primary position (QB, RB, WR, TE, K, DEF)

### 1.5 Opponent Roster Collection

**Script**: `data_collection/scripts/yahoo/opponent_rosters.py`
**Output**: `data_collection/outputs/yahoo/opponent_rosters/YYYY/MM/DD/YYYYMMDD_HHMMSS_opponent_rosters_raw_data.json`

**Purpose**: Collects all opponent team rosters for analysis
**Data Structure**: Dictionary containing all team rosters
```json
{
  "teams": [
    {
      "team_key": "461.l.595012.t.5",
      "name": "Kissyface",
      "roster": {
        "players": [
          {
            "player_key": "461.p.67890",
            "player_id": "67890",
            "name": {
              "full": "Kyler Murray",
              "first": "Kyler",
              "last": "Murray"
            },
            "editorial_team_abbr": "Ari",
            "display_position": "QB"
          }
        ]
      }
    }
  ]
}
```

**Key Variables**:
- Same structure as my_roster but for all teams
- Used to identify current week opponent via team_matchups data

### 1.6 Available Players Collection

**Script**: `data_collection/scripts/yahoo/available_players.py`
**Output**: `data_collection/outputs/yahoo/available_players/YYYY/MM/DD/YYYYMMDD_HHMMSS_available_players_raw_data.json`

**Purpose**: Collects all available free agents
**Data Structure**: Dictionary containing available players
```json
{
  "players": [
    {
      "player_key": "461.p.11111",
      "player_id": "11111",
      "name": {
        "full": "Caleb Williams",
        "first": "Caleb",
        "last": "Williams"
      },
      "editorial_team_abbr": "Chi",
      "display_position": "QB"
    }
  ]
}
```

**Key Variables**:
- `players`: List of all available players (typically 1000+ players)
- Used for waiver wire analysis and free agent recommendations

### 1.7 Transaction Trends Collection

**Script**: `data_collection/scripts/yahoo/transaction_trends.py`
**Output**: `data_collection/outputs/yahoo/transaction_trends/YYYY/MM/DD/YYYYMMDD_HHMMSS_transaction_trends_raw_data.json`

**Purpose**: Collects recent add/drop trends for market analysis
**Data Structure**: Dictionary containing transaction data
```json
{
  "transactions": [
    {
      "player_key": "461.p.22222",
      "transaction_type": "add",
      "count": 15,
      "week": 1
    }
  ]
}
```

**Key Variables**:
- `transaction_type`: "add" or "drop"
- `count`: Number of transactions
- Used for identifying trending players

---

## Phase 2: Sleeper Data Enrichment

### 2.1 Sleeper My Roster Enrichment

**Script**: `data_collection/scripts/sleeper/my_roster.py`
**Dependencies**: Yahoo my_roster data
**Output**: `data_collection/outputs/sleeper/my_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_my_roster_raw_data.json`

**Purpose**: Enriches user's roster with Sleeper database information
**Data Structure**: Dictionary containing matched and unmatched players
```json
{
  "matched_players": [
    {
      "yahoo_data": {
        "player_key": "461.p.12345",
        "name": {"full": "Joe Burrow"},
        "editorial_team_abbr": "Cin",
        "display_position": "QB"
      },
      "sleeper_player": {
        "player_id": "6770",
        "full_name": "Joe Burrow",
        "position": "QB",
        "team": "CIN",
        "injury_status": null,
        "news_updated": "1757288429"
      }
    }
  ],
  "unmatched_players": []
}
```

**Key Matching Logic**:
1. **Yahoo ID Matching**: `yahoo_player.get('player_id')` → `sleeper_player.get('yahoo_id')`
2. **Name + Team Matching**: Fallback when Yahoo ID not available
3. **Team Normalization**: Uses `team_mapping.py` to normalize team abbreviations

**Critical Variables**:
- `yahoo_data`: Original Yahoo player information
- `sleeper_player`: Enhanced Sleeper database information
- `injury_status`: Real-time injury information
- `news_updated`: Timestamp of latest news

### 2.2 Sleeper Opponent Roster Enrichment

**Script**: `data_collection/scripts/sleeper/opponent_roster.py`
**Dependencies**: Yahoo opponent_rosters + team_matchups data
**Output**: `data_collection/outputs/sleeper/opponent_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_opponent_roster_raw_data.json`

**Purpose**: Enriches current week opponent's roster with Sleeper data
**Data Structure**: Same as my_roster but for opponent players
```json
{
  "opponent_info": {
    "opponent_name": "Kissyface",
    "opponent_team_key": "461.l.595012.t.5"
  },
  "matched_players": [...],
  "unmatched_players": []
}
```

**Key Process**:
1. **Opponent Identification**: Uses team_matchups to find current week opponent
2. **Player Matching**: Same logic as my_roster matching
3. **Team Key Mapping**: Maps opponent team_key to specific roster

### 2.3 Sleeper Available Players Enrichment

**Script**: `data_collection/scripts/sleeper/available_players.py`
**Dependencies**: Yahoo available_players data + player_limits configuration
**Output**: `data_collection/outputs/sleeper/available_players/YYYY/MM/DD/YYYYMMDD_HHMMSS_available_players_raw_data.json`

**Purpose**: Enriches available players with Sleeper data (limited by position)
**Data Structure**: Same as my_roster but for available players
```json
{
  "extraction_metadata": {
    "player_limits": {"QB": 20, "RB": 20, "WR": 20, "TE": 20, "K": 20, "DEF": 10}
  },
  "matched_players": [...],
  "unmatched_players": []
}
```

**Key Process**:
1. **Position Filtering**: Uses `config/player_limits.py` to limit players per position
2. **Player Matching**: Same logic as roster matching
3. **Optimization**: Reduces from 1000+ to ~120 players for token efficiency

### 2.4 Sleeper Trending Data Collection

**Script**: `data_collection/scripts/sleeper/trending.py`
**Dependencies**: None (independent API call)
**Output**: `data_collection/outputs/sleeper/trending/YYYY/MM/DD/YYYYMMDD_HHMMSS_trending_raw_data.json`

**Purpose**: Collects trending add/drop data from Sleeper
**Data Structure**: Dictionary containing trending information
```json
{
  "trending_adds": [
    {
      "player_id": "12345",
      "count": 25,
      "player_data": {
        "full_name": "Caleb Williams",
        "position": "QB",
        "team": "CHI"
      }
    }
  ],
  "trending_drops": [...]
}
```

**Key Variables**:
- `trending_adds`: Players being added most frequently
- `trending_drops`: Players being dropped most frequently
- `count`: Number of transactions in last 24 hours

---

## Phase 3: Tank01 Data Enrichment

### 3.1 Tank01 My Roster Enrichment

**Script**: `data_collection/scripts/tank01/my_roster.py`
**Dependencies**: Yahoo my_roster data
**Output**: `data_collection/outputs/tank01/my_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_my_roster_raw_data.json`

**Purpose**: Enriches user's roster with Tank01 projections and stats
**Data Structure**: Dictionary containing matched players with projections
```json
{
  "matched_players": [
    {
      "yahoo_data": {
        "player_key": "461.p.12345",
        "name": {"full": "Joe Burrow"},
        "editorial_team_abbr": "Cin",
        "display_position": "QB"
      },
      "tank01_player": {
        "player_id": "12345",
        "name": "Joe Burrow",
        "position": "QB",
        "team": "CIN",
        "projected_points": 26.72,
        "stats": {...}
      }
    }
  ],
  "unmatched_players": []
}
```

**Key Variables**:
- `projected_points`: Weekly fantasy projections
- `stats`: Historical performance data
- `team`: Tank01 team abbreviation (normalized via team_mapping)

### 3.2 Tank01 Opponent Roster Enrichment

**Script**: `data_collection/scripts/tank01/opponent_roster.py`
**Dependencies**: Yahoo opponent_rosters + team_matchups data
**Output**: `data_collection/outputs/tank01/opponent_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_opponent_roster_raw_data.json`

**Purpose**: Enriches opponent roster with Tank01 projections
**Data Structure**: Same as my_roster but for opponent players

### 3.3 Tank01 Available Players Enrichment

**Script**: `data_collection/scripts/tank01/available_players.py`
**Dependencies**: Yahoo available_players data + player_limits configuration
**Output**: `data_collection/outputs/tank01/available_players/YYYY/MM/DD/YYYYMMDD_HHMMSS_available_players_raw_data.json`

**Purpose**: Enriches available players with Tank01 projections
**Data Structure**: Same as my_roster but for available players

---

## Phase 4: Comprehensive Data Processing

### 4.1 Data Aggregation and Matching

**Script**: `ai_agents/comprehensive_data_processor.py`
**Dependencies**: All 14 data collection script outputs
**Output**: `data_collection/outputs/validation_tests/YYYY/MM/DD/YYYYMMDD_HHMMSS_comprehensive_data.json`

**Purpose**: Combines all data sources into unified player profiles
**Data Structure**: Dictionary containing all enriched data
```json
{
  "my_roster": {
    "total_players": 15,
    "players_by_position": {
      "starting_lineup": {
        "QB": [
          {
            "player_key": "461.p.12345",
            "name": "Joe Burrow",
            "position": "QB",
            "team": "CIN",
            "tank01_data": {
              "projected_points": 26.72,
              "stats": {...}
            },
            "sleeper_data": {
              "injury_status": null,
              "news_updated": "1757288429"
            }
          }
        ]
      },
      "bench_players": {...}
    }
  },
  "opponent_roster": {...},
  "available_players": {...},
  "league_metadata": {...}
}
```

**Key Process**:
1. **Data Loading**: Loads all raw data files using YYYY/MM/DD directory structure
2. **Player Matching**: Matches players across all APIs using player_key and name+team
3. **Data Enrichment**: Combines Yahoo, Sleeper, and Tank01 data for each player
4. **Position Categorization**: Organizes players by position and lineup status

**Critical Methods**:
- `_find_latest_file()`: Locates most recent data files
- `_find_matching_player()`: Matches players across APIs
- `_load_yahoo_roster()`: Loads Yahoo roster data
- `_load_sleeper_roster()`: Loads Sleeper enrichment data
- `_load_tank01_roster()`: Loads Tank01 projection data

---

## Phase 5: AI Agent Analysis

### 5.1 Data Preparation for AI Agent

**Script**: `ai_agents/analyst_agent.py`
**Dependencies**: Comprehensive data processor output
**Input**: Enriched player data from comprehensive_data_processor.py

**Purpose**: Prepares data for AI analysis and generates recommendations
**Data Structure**: Optimized player profiles for token efficiency
```json
{
  "optimized_player_profiles": [
    {
      "name": "Joe Burrow",
      "position": "QB",
      "team": "CIN",
      "projected_points": 26.72,
      "injury_status": null,
      "matchup": "vs. NE",
      "recommendation": "Start"
    }
  ]
}
```

**Key Process**:
1. **Data Optimization**: Reduces token usage by including only essential data
2. **Context Building**: Creates matchup context and league information
3. **Prompt Generation**: Builds comprehensive analysis prompts

### 5.2 AI Analysis and Recommendations

**Script**: `ai_agents/analyst_agent.py`
**Dependencies**: Optimized player profiles
**Output**: Analysis reports and recommendations

**Purpose**: Provides fantasy football analysis and recommendations
**Data Structure**: Analysis results with recommendations
```json
{
  "analysis_summary": {
    "my_roster_strength": "Strong",
    "opponent_roster_strength": "Moderate",
    "key_matchups": [...],
    "recommendations": [...]
  },
  "player_recommendations": [
    {
      "player": "Joe Burrow",
      "action": "Start",
      "reasoning": "High projection vs. weak defense"
    }
  ]
}
```

---

## Data Flow Dependencies

### Critical Data Dependencies:
1. **Yahoo Data** → **Sleeper/Tank01 Enrichment**
   - `player_key` and `player_id` used for matching
   - `editorial_team_abbr` used for team matching
   - `display_position` used for position validation

2. **Team Matchups** → **Opponent Roster Processing**
   - `opponent_team_key` used to identify current week opponent
   - `opponent_name` used for human-readable identification

3. **Player Limits** → **Available Players Filtering**
   - `DEFAULT_PLAYER_LIMITS` used to reduce token usage
   - Position-based filtering (QB: 20, RB: 20, etc.)

### Team Mapping Requirements:
- **Yahoo**: `editorial_team_abbr` (e.g., "Cin", "SF", "Sea")
- **Sleeper**: `team` (e.g., "CIN", "SF", "SEA")
- **Tank01**: `team` (e.g., "CIN", "SF", "SEA")
- **Normalization**: All converted to standard format via `team_mapping.py`

### Data Structure Requirements:
- **Yahoo**: Dictionary with `teams` array containing `roster.players`
- **Sleeper**: Dictionary with `matched_players` array containing `yahoo_data` and `sleeper_player`
- **Tank01**: Dictionary with `matched_players` array containing `yahoo_data` and `tank01_player`
- **Comprehensive**: Dictionary with `players_by_position` containing enriched player objects

---

## Validation and Quality Assurance

### Validation Scripts:
1. **Script Health Check**: `data_collection/scripts/validation/script_health_check.py`
   - Validates all 14 scripts run successfully
   - Checks for output file creation
   - Reports script execution status

2. **Comprehensive Data Validator**: `data_collection/scripts/validation/comprehensive_data_validator.py`
   - Validates 100% player matching
   - Checks for missing enrichment data
   - Ensures data completeness

3. **Master Validator**: `validate_all_data.py`
   - Runs all validation scripts
   - Provides overall system health status
   - Exits with error code if validation fails

### Success Criteria:
- ✅ All 14 data collection scripts pass health check
- ✅ 0 unmatched players in Sleeper/Tank01 outputs
- ✅ 100% enrichment rate for all player data
- ✅ All team abbreviations properly normalized
- ✅ No missing or null enrichment data

---

## Error Handling and Recovery

### Common Failure Points:
1. **Team Mapping Failures**: Incorrect team abbreviation handling
2. **Player Matching Failures**: Missing or incorrect player identifiers
3. **API Rate Limiting**: Excessive API calls causing failures
4. **Data Structure Changes**: API response format changes

### Recovery Strategies:
1. **Team Mapping**: Always use `team_mapping.py` for normalization
2. **Player Matching**: Implement fallback matching strategies
3. **API Management**: Use `ApiUsageManager` for rate limiting
4. **Data Validation**: Run validation scripts after each change

---

This pipeline ensures 100% accuracy and completeness of fantasy football data, providing the AI agent with comprehensive, enriched player information for optimal analysis and recommendations.
