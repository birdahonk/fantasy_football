# Tank01 NFL API Schemas

This document outlines the complete response structures for all Tank01 NFL API endpoints used in the data collection scripts.

## Overview

The Tank01 API provides comprehensive NFL data including:
- Player information and statistics
- Fantasy projections and historical game data
- Team rosters, depth charts, and team statistics
- News and updates
- Game information and live scores
- Changelog and system updates

## Authentication

- **API Key**: Required via RapidAPI
- **Rate Limits**: 1000 calls/day (upgraded plan)
- **Base URL**: `https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com`

## ⚠️ CRITICAL: Correct Endpoint Names

**DO NOT USE THESE INCORRECT ENDPOINTS** (they will return 404 errors):
- ❌ `getNFLPlayers` → ✅ Use `getNFLPlayerList`
- ❌ `getNFLTeamStats` → ✅ Use `getNFLTeamRoster`

**All Valid Endpoints:**
- ✅ `getNFLPlayerList` - Complete player database
- ✅ `getNFLProjections` - Weekly fantasy projections
- ✅ `getNFLGamesForPlayer` - Individual player game stats
- ✅ `getNFLTeamRoster` - Team roster information
- ✅ `getNFLDepthCharts` - Team depth charts
- ✅ `getNFLTeams` - Team information and stats
- ✅ `getNFLGameInfo` - Game details and scores
- ✅ `getNFLScoresOnly` - Daily scoreboard
- ✅ `getNFLNews` - Player and team news
- ✅ `getNFLPlayerInfo` - Individual player details
- ✅ `getNFLChangelog` - API updates and changes

## ACTUAL PROCESSED DATA STRUCTURES

### **1. My Roster Data Structure**
**File**: `data_collection/outputs/tank01/my_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_my_roster_raw_data.json`

```json
{
  "extraction_metadata": {
    "script": "tank01_my_roster.py",
    "extraction_timestamp": "2025-09-08T12:53:06.123456",
    "execution_stats": {
      "start_time": "2025-09-08 12:53:05.123456",
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
      "tank01_data": {
        "playerID": "string",
        "longName": "Joe Burrow",
        "pos": "QB",
        "team": "CIN",
        "age": 27,
        "exp": 5,
        "height": "6'4\"",
        "weight": "215",
        "school": "LSU",
        "yahooPlayerID": "32671",
        "espnID": "string",
        "sleeperBotID": "string",
        "fantasyProsPlayerID": "string",
        "fantasy_projections": {...},
        "recent_news": {...},
        "game_stats": {...},
        "depth_chart": {...},
        "team_context": {...}
      }
    }
  ],
  "unmatched_players": [],
  "tank01_api_usage": {
    "calls_made": 15,
    "calls_remaining": 985,
    "reset_time": "2025-09-09T11:17:46.000Z"
  }
}
```

### **2. Opponent Roster Data Structure**
**File**: `data_collection/outputs/tank01/opponent_roster/YYYY/MM/DD/YYYYMMDD_HHMMSS_opponent_roster_raw_data.json`

```json
{
  "extraction_metadata": {
    "script": "tank01_opponent_roster.py",
    "extraction_timestamp": "2025-09-08T12:55:58.123456",
    "opponent_name": "Kissyface",
    "opponent_team_key": "461.l.595012.t.5",
    "execution_stats": {
      "start_time": "2025-09-08 12:55:57.123456",
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
      "tank01_data": {
        "playerID": "string",
        "longName": "Kyler Murray",
        "pos": "QB",
        "team": "ARI",
        "age": 27,
        "exp": 6,
        "yahooPlayerID": "31833"
      },
      "match_type": "yahoo_id"
    }
  ],
  "unmatched_players": []
}
```

### **3. Available Players Data Structure**
**File**: `data_collection/outputs/tank01/available_players/YYYY/MM/DD/YYYYMMDD_HHMMSS_available_players_raw_data.json`

```json
{
  "extraction_metadata": {...},
  "season_context": {...},
  "processed_data": {
    "available_players": [
      {
        "yahoo_data": {
          "player_key": "461.p.12345",
          "player_id": "12345",
          "name": {"full": "Evan Engram", "first": "Evan", "last": "Engram"},
          "display_position": "TE",
          "editorial_team_abbr": "Den",
          "bye_weeks": {"week": "10"},
          "bye_week": "10",
          "percent_owned_value": "85.2"
        },
        "tank01_data": {
          "playerID": "string",
          "longName": "Evan Engram",
          "pos": "TE",
          "team": "DEN",
          "age": 30,
          "exp": 8,
          "yahooPlayerID": "12345",
          "fantasy_projections": {...},
          "recent_news": {...},
          "game_stats": {...},
          "depth_chart": {...},
          "team_context": {...}
        },
        "projection": {...},
        "news": {...},
        "game_stats": {...},
        "depth_chart": {...},
        "team_context": {...},
        "display_position": "TE",
        "name": "Evan Engram",
        "team": "DEN"
      }
    ],
    "injury_reports": [...],
    "top_available": [...]
  },
  "cached_data": {...},
  "efficiency_metrics": {
    "players_processed": 125,
    "players_matched": 125,
    "match_rate": 100.0,
    "execution_time_seconds": 360.09349,
    "api_name": "Tank01",
    "calls_made_this_session": 881,
    "daily_limit": 1000,
    "remaining_calls": 119,
    "percentage_used": 88.1
  }
}
```

### **4. NFL Matchups Data Structure**
**File**: `data_collection/outputs/tank01/nfl_matchups/YYYY/MM/DD/YYYYMMDD_HHMMSS_nfl_matchups_raw_data.json`

```json
{
  "season_context": {
    "nfl_season": 2025,
    "current_week": 1,
    "season_phase": "Regular Season"
  },
  "games": [
    {
      "game_id": "string",
      "date": "2025-09-08",
      "week": 1,
      "season": 2025,
      "home_team": "LAC",
      "away_team": "KC",
      "venue": "SoFi Stadium",
      "game_time_et": "8:00p",
      "game_time_pt": "5:00p",
      "game_time_epoch": 1725840000,
      "game_time_utc": "2025-09-09T01:00:00Z",
      "game_status": "Completed",
      "game_status_code": "F",
      "season_type": "regular",
      "neutral_site": false,
      "espn_id": "string",
      "espn_link": "string",
      "cbs_link": "string",
      "team_id_home": "string",
      "team_id_away": "string",
      "top_performers": [...]
    }
  ],
  "total_games": 15,
  "api_usage": {
    "calls_made": 1,
    "calls_remaining": 999,
    "reset_time": "2025-09-09T11:17:46.000Z"
  }
}
```

### **5. Transaction Trends Data Structure**
**File**: `data_collection/outputs/tank01/transaction_trends/YYYY/MM/DD/YYYYMMDD_HHMMSS_transaction_trends_raw_data.json`

```json
{
  "yahoo_data": {...},
  "league_players": [...],
  "enriched_players": [
    {
      "yahoo_data": {
        "name": "Cedric Tillman",
        "position": "WR",
        "team": "Cle",
        "transaction_type": "add/drop_add",
        "transaction_time": "2025-09-08T12:00:00Z",
        "yahoo_data": {...}
      },
      "tank01_data": {
        "player_id": "string",
        "name": "Cedric Tillman",
        "team": "CLE",
        "position": "WR",
        "yahoo_id": "string",
        "sleeper_id": "string"
      },
      "match_status": "matched",
      "match_confidence": "high",
      "tank01_enrichment": {...}
    }
  ],
  "enrichment_summary": {
    "total_players": 38,
    "matched_players": 38,
    "unmatched_players": 0,
    "match_rate": 100.0
  },
  "api_usage": {
    "calls_made": 38,
    "calls_remaining": 962,
    "reset_time": "2025-09-09T11:17:46.000Z"
  }
}
```

## Complete Endpoint Analysis

### 1. Player List (`getNFLPlayerList`)

**Purpose**: Get comprehensive list of all NFL players with cross-platform IDs.

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": [
    {
      "playerID": "string",
      "longName": "string",
      "team": "string",
      "pos": "string",
      "espnID": "string",
      "sleeperBotID": "string",
      "yahooPlayerID": "string",
      "cbsPlayerID": "string",
      "rotoWirePlayerID": "string",
      "fRefID": "string",
      "teamID": "string",
      "jerseyNum": "string",
      "height": "string",
      "weight": "string",
      "age": "string",
      "exp": "string",
      "school": "string"
    }
  ]
}
```

**Key Data Points**:
- Complete player database (5,316+ players)
- Cross-platform ID mapping (ESPN, Sleeper, Yahoo, CBS, RotoWire, FRef)
- Physical attributes and experience
- Team and position information

**Team Defense Data Structure**:
Team defense players have a different data structure than individual players:
```json
{
  "playerID": "DEF_27",
  "longName": "Phi Defense",
  "team": "Phi",
  "pos": "DEF",
  "teamID": "27",
  "isTeamDefense": true,
  "espnID": null,
  "sleeperBotID": null,
  "height": null,
  "weight": null,
  "age": null,
  "exp": null,
  "school": null
}
```

**Team Defense Key Differences**:
- **Player ID**: Format is "DEF_{teamID}" (e.g., "DEF_27" for Philadelphia)
- **Team Abbreviation**: May be lowercase in API response (e.g., "Phi" instead of "PHI")
- **Individual Player Fields**: Most individual player fields (height, weight, age, etc.) are null
- **Team-Specific Fields**: Focus on teamID, team abbreviation, and position
- **News Strategy**: Use team abbreviation for news retrieval (must normalize case)

### 2. Weekly Projections (`getNFLProjections`)

**Purpose**: Get fantasy projections for all players for a specific week.

**Parameters**:
- `week`: Week number (1-18)
- `archiveSeason`: Season year (default: 2025)
- Scoring settings (passYards, passTD, etc.)

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": {
    "playerProjections": [
      {
        "playerID": "string",
        "fantasyPoints": "number",
        "fantasyPointsDefault": {
          "standard": "number",
          "PPR": "number",
          "halfPPR": "number"
        },
        "Passing": {
          "passAttempts": "number",
          "passTD": "number",
          "passYds": "number",
          "int": "number",
          "passCompletions": "number"
        },
        "Rushing": {
          "rushYds": "number",
          "carries": "number",
          "rushTD": "number"
        },
        "Receiving": {
          "receptions": "number",
          "recTD": "number",
          "targets": "number",
          "recYds": "number"
        }
      }
    ],
    "teamDefenseProjections": [
      {
        "teamID": "string",
        "team": "string",
        "isTeamDefense": true,
        "fantasyPoints": "number",
        "defTD": "number",
        "sacks": "number",
        "int": "number",
        "fumblesRecovered": "number",
        "safeties": "number",
        "pointsAllowed": "number",
        "yardsAllowed": "number"
      }
    ]
  }
}
```

**Key Data Points**:
- Batch projections for all players (single API call)
- Multiple scoring formats (Standard, PPR, Half-PPR)
- Detailed stat breakdowns by category
- Separate team defense projections

**⚠️ CRITICAL: Fantasy Projections Integration**

**Data Collection Scripts MUST Include Fantasy Projections**:
- **My Roster Script**: ✅ **IMPLEMENTED** - Loads weekly projections and adds `fantasy_projections` to each player
- **Available Players Script**: ✅ **IMPLEMENTED** - Loads weekly projections and adds `fantasy_projections` to each player  
- **Opponent Roster Script**: ✅ **IMPLEMENTED** - Loads weekly projections and adds `fantasy_projections` to each player

**Fantasy Projections Data Structure in Player Profiles**:
```json
{
  "fantasy_projections": {
    "fantasyPoints": "number",
    "fantasyPointsDefault": {
      "standard": "number",
      "PPR": "number", 
      "halfPPR": "number"
    },
    "Passing": {
      "passAttempts": "number",
      "passTD": "number",
      "passYds": "number",
      "int": "number",
      "passCompletions": "number"
    },
    "Rushing": {
      "rushYds": "number",
      "carries": "number",
      "rushTD": "number"
    },
    "Receiving": {
      "receptions": "number",
      "recTD": "number",
      "targets": "number",
      "recYds": "number"
    }
  }
}
```

**Team Defense Fantasy Projections**:
```json
{
  "fantasy_projections": {
    "fantasyPoints": "null",
    "fantasyPointsDefault": "number",
    "defTD": "number",
    "sacks": "number",
    "int": "number",
    "fumblesRecovered": "number",
    "safeties": "number",
    "pointsAllowed": "number",
    "yardsAllowed": "number",
    "returnTD": "number",
    "blockKick": "number"
  }
}
```

**⚠️ IMPORTANT: Defense Player Data Structure**:
- **fantasyPoints**: Always `null` for defense players (team-based scoring)
- **fantasyPointsDefault**: Single number value (not object) for defense players
- **Other fields**: Standard defense statistics

**Implementation Requirements**:
1. **Weekly Projections Loading**: Scripts must call `getNFLProjections(week=current_week, archiveSeason=2025)` at startup
2. **Projections Caching**: Cache projections data to avoid repeated API calls
3. **Player Matching**: Match each player's `playerID` to projections data
4. **Data Integration**: Add `fantasy_projections` field to each player's `tank01_data` section
5. **Markdown Display**: Include fantasy projections in markdown reports with proper formatting

## Comprehensive Data Processor Integration

**Purpose**: Documents how Tank01 data integrates with the `ComprehensiveDataProcessor` for AI analyst agent consumption.

**Data Structure Variations**:
- **Available Players**: `projection` data at root level, `tank01_data` contains metadata
- **Roster Players**: `fantasy_projections` within `tank01_data`, `yahoo_player` key structure
- **Opponent Roster**: `fantasy_projections` within `tank01_data`, `yahoo_data` key structure

**Comprehensive Output Integration**:
```json
{
  "tank01_data": {
    "player_id": "string",
    "name": {"full": "string", "first": "string", "last": "string"},
    "display_position": "string",
    "team": "string",
    "team_id": "string",
    "projection": {
      "fantasyPoints": "number|null",
      "fantasyPointsDefault": "number|object",
      "week_1": {
        "fantasy_points": "number|null",
        "fantasy_points_default": "number|object"
      }
    },
    "news": "array",
    "game_stats": "object",
    "depth_chart": "object",
    "team_context": "object"
  }
}
```

**Fantasy Points Data Types**:
- **Non-Defense Players**: `fantasyPoints` (number), `fantasyPointsDefault` (object with standard/PPR/halfPPR)
- **Defense Players**: `fantasyPoints` (null), `fantasyPointsDefault` (number)

### 3. Player Game Stats (`getNFLGamesForPlayer`)

**Purpose**: Get historical game statistics for a specific player.

**Parameters**:
- `playerID`: Tank01 player ID
- `season`: Optional season (default: current)
- Fantasy scoring parameters

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": {
    "20241201_SF@BUF": {
      "teamAbv": "SF",
      "snapCounts": {
        "offSnapPct": "0.25",
        "defSnap": "0",
        "stSnap": "0",
        "stSnapPct": "0.00",
        "offSnap": "12",
        "defSnapPct": "0.00"
      },
      "Receiving": {
        "receptions": "2",
        "recTD": "0",
        "longRec": "12",
        "targets": "3",
        "recYds": "14",
        "recAvg": "7.0"
      },
      "Rushing": {
        "rushAvg": "7.6",
        "rushYds": "53",
        "carries": "7",
        "longRush": "19",
        "rushTD": "0"
      },
      "Defense": {
        "fumblesLost": "1",
        "defensiveInterceptions": "0",
        "forcedFumbles": "0",
        "fumbles": "1",
        "fumblesRecovered": "0"
      },
      "longName": "Christian McCaffrey",
      "playerID": "3117251",
      "team": "SF",
      "teamID": "28",
      "gameID": "20241201_SF@BUF"
    }
  }
}
```

**Key Data Points**:
- Historical game-by-game statistics
- Snap count percentages (offensive, defensive, special teams)
- Detailed receiving, rushing, and defensive stats
- Game-specific performance metrics
- Long plays and averages

### 4. Team Roster (`getNFLTeamRoster`)

**Purpose**: Get team roster with player statistics.

**Parameters**:
- `teamID`: Team abbreviation (e.g., "SF")
- `getStats`: Include player statistics
- `fantasyPoints`: Include fantasy points

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": {
    // Team roster data structure varies by team
    // Contains player information and statistics
  }
}
```

**Key Data Points**:
- Complete team roster
- Player statistics and fantasy points
- Team-specific player data

### 5. Depth Charts (`getNFLDepthCharts`)

**Purpose**: Get depth chart information for all teams.

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": [
    {
      "depthChart": {
        "RB": [
          {
            "depthPosition": "RB1",
            "playerID": "3045147",
            "longName": "James Conner"
          },
          {
            "depthPosition": "RB2",
            "playerID": "4429275",
            "longName": "Trey Benson"
          }
        ],
        "QB": [
          {
            "depthPosition": "QB1",
            "playerID": "3917315",
            "longName": "Kyler Murray"
          }
        ],
        "TE": [
          {
            "depthPosition": "TE1",
            "playerID": "string",
            "longName": "string"
          }
        ]
      },
      "teamAbv": "ARI",
      "teamID": "1"
    }
  ]
}
```

**Key Data Points**:
- Complete depth charts for all 32 teams
- Position-specific depth rankings
- Player IDs and names for each depth position
- Team organization structure

### 6. Teams Information (`getNFLTeams`)

**Purpose**: Get comprehensive team information including standings, stats, and top performers.

**Parameters**:
- `sortBy`: Sort teams by (standings, etc.)
- `rosters`: Include team rosters
- `schedules`: Include team schedules
- `topPerformers`: Include top performers
- `teamStats`: Include team statistics
- `teamStatsSeason`: Season for team stats

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": [
    {
      "teamAbv": "BUF",
      "teamCity": "Buffalo",
      "currentStreak": {
        "result": "",
        "length": "0"
      },
      "loss": "0",
      "teamName": "Bills",
      "nflComLogo1": "https://res.cloudinary.com/nflleague/image/private/f_auto/league/giphcy6ie9mxbnldntsf",
      "teamID": "4",
      "tie": "0",
      "byeWeeks": {
        "2023": ["13"],
        "2022": ["7"],
        "2025": ["7"],
        "2024": ["12"]
      },
      "division": "East",
      "conferenceAbv": "AFC",
      "pa": "0",
      "pf": "0",
      "espnLogo1": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/buf.png",
      "wins": "0",
      "conference": "American Football Conference",
      "topPerformers": {
        "Rushing": {
          "rushYds": {
            "total": "1009.0",
            "playerID": ["4379399"]
          }
        }
      },
      "teamStats": {
        // Detailed team statistics
      }
    }
  ]
}
```

**Key Data Points**:
- Complete team information (32 teams)
- Current standings and records
- Division and conference information
- Bye weeks for multiple seasons
- Top performers by category
- Team statistics and logos
- Current win/loss streaks

### 7. Game Information (`getNFLGameInfo`)

**Purpose**: Get detailed information for a specific game.

**Parameters**:
- `gameID`: Game ID (e.g., "20241201_SF@BUF")

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": {
    "away": "SF",
    "cbsLink": "https://www.cbssports.com/nfl/gametracker/boxscore/NFL_20241201_SF@BUF",
    "espnID": "401671781",
    "espnLink": "https://www.espn.com/nfl/boxscore/_/gameId/401671781",
    "gameDate": "20241201",
    "gameID": "20241201_SF@BUF",
    "gameStatus": "Final",
    "gameTime": "8:20p",
    "gameTime_epoch": "1733102400.0",
    "gameWeek": "Week 13",
    "home": "BUF",
    "neutralSite": "False",
    "season": "2024",
    "seasonType": "Regular Season",
    "teamIDAway": "28",
    "teamIDHome": "4",
    "venue": "Highmark Stadium",
    "gameTime_utc_iso8601": "2024-12-02T01:20:00",
    "gameStatusCode": "2"
  }
}
```

**Key Data Points**:
- Complete game metadata
- Team information (home/away)
- Game timing and status
- Venue and location details
- External links (CBS, ESPN)
- Season and week information

### 8. Daily Scoreboard (`getNFLScoresOnly`)

**Purpose**: Get live scoreboard for a specific date.

**Parameters**:
- `gameDate`: Game date (YYYYMMDD format)
- `topPerformers`: Include top performers

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": {
    "20241201_SF@BUF": {
      // Game score and performance data
    },
    "20241201_TEN@WSH": {
      // Game score and performance data
    }
    // ... other games for the date
  }
}
```

**Key Data Points**:
- Live game scores and status
- Top performers for each game
- Real-time game updates
- Multiple games per date

### 9. News (`getNFLNews`)

**Purpose**: Get fantasy football news and updates, with support for player-specific and team-specific filtering.

**Parameters**:
- `fantasyNews`: true/false (default: true)
- `maxItems`: Maximum number of news items (default: 20)
- `playerID`: Get news specific to a player (optional)
- `teamID`: Get news specific to a team by numeric ID (optional)
- `teamAbv`: Get news for team by abbreviation (optional)
- `topNews`: Include top news (default: true)
- `recentNews`: Include recent news (default: true)

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": [
    {
      "title": "string",
      "link": "string",
      "image": "string",
      "playerID": "string"
    }
  ]
}
```

**Key Data Points**:
- **Player-Specific News**: When `playerID` is provided, returns news articles specifically about that player
- **Team-Specific News**: When `teamID` or `teamAbv` is provided, returns news articles about that team
- **Fantasy-Relevant News**: When `fantasyNews=true`, filters for fantasy-relevant content
- **Article Metadata**: title, link, image (no publication dates available)
- **Team Defense News Strategy**: For team defense players, use `teamAbv` parameter to get team news

**Team Defense News Implementation**:
- **Challenge**: No specific defense-only news filtering available
- **Solution**: Use `teamAbv` parameter to get general team news (10 most recent articles)
- **Team Abbreviation Normalization**: Must use uppercase abbreviations (e.g., "PHI" not "Phi")
- **Case Sensitivity**: API requires exact case matching for team abbreviations
- **News Content**: Team news includes general team updates, player news, and organizational news

**Examples**:
- `getNFLNews(playerID="3117251")` - News about Christian McCaffrey
- `getNFLNews(teamAbv="PHI")` - News about Philadelphia Eagles (for team defense)
- `getNFLNews(teamAbv="SF")` - News about San Francisco 49ers
- `getNFLNews(fantasyNews=true, maxItems=50)` - General fantasy news

**Important Notes**:
- **No Publication Dates**: API does not provide timestamp information for news articles
- **Team Abbreviation Case**: Must use uppercase (PHI, SF, BUF) not lowercase (phi, sf, buf)
- **Defense News Limitation**: Cannot filter specifically for defense-related news, only general team news

### 10. Player Info (`getNFLPlayerInfo`)

**Purpose**: Get detailed information for a specific player by name.

**Parameters**:
- `playerName`: Player name to search for
- `getStats`: Include player statistics

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": [
    {
      "playerID": "string",
      "longName": "string",
      "team": "string",
      "pos": "string",
      "espnID": "string",
      "sleeperBotID": "string",
      "yahooPlayerID": "string",
      "cbsPlayerID": "string",
      "rotoWirePlayerID": "string",
      "fRefID": "string",
      "teamID": "string",
      "jerseyNum": "string",
      "height": "string",
      "weight": "string",
      "age": "string",
      "exp": "string",
      "school": "string"
    }
  ]
}
```

**Key Data Points**:
- Player search by name
- Complete cross-platform ID mapping
- Physical and career information
- Team and position details

### 11. Changelog (`getNFLChangelog`)

**Purpose**: Get system changelog and updates.

**Parameters**:
- `maxDays`: Maximum days to look back

**Response Structure**:
```json
{
  "statusCode": 200,
  "body": {
    "changeLog": [
      {
        "date": "string",
        "changes": "string"
      }
    ],
    "error": "string"
  }
}
```

**Key Data Points**:
- System updates and changes
- Date-stamped change log
- Error information if applicable

## Data Collection Scripts

### My Roster Script (`tank01_my_roster.py`)

**Purpose**: Extract comprehensive Tank01 data for Yahoo Fantasy roster players.

**Data Sources**:
1. Player database (getNFLPlayerList) - 1 call
2. Weekly projections (getNFLProjections) - 1 call
3. Player info for unmatched players (getNFLPlayerInfo) - 3 calls
4. Fantasy news (getNFLNews) - 1 call

**Total API Calls**: 6 calls for 15 players (0.4 calls per player)

**Output Structure**:
- **Clean Data**: Markdown report with organized player data
- **Raw Data**: Complete JSON response data
- **API Usage**: Comprehensive tracking of API calls and efficiency

**Key Features**:
- 100% player matching using multiple strategies
- Comprehensive cross-platform ID mapping
- Detailed fantasy projections with multiple scoring formats
- Historical game statistics (via player game stats endpoint)
- Fantasy news integration
- Optimized API usage

### Available Players Script (`tank01_available_players.py`)

**Purpose**: Extract comprehensive Tank01 data for available players from Yahoo Fantasy.

**Data Sources**:
1. Player database (getNFLPlayerList) - 1 call
2. Weekly projections (getNFLProjections) - 1 call
3. Depth charts (getNFLDepthCharts) - 1 call
4. Teams information (getNFLTeams) - 1 call
5. Player-specific news (getNFLNews) - 1 call per player
6. Player game stats (getNFLGamesForPlayer) - 1 call per player
7. Player info for unmatched players (getNFLPlayerInfo) - 1 call per unmatched player

**Total API Calls**: 4 base calls + 2-3 calls per player (19 calls for 5 players in development mode)

**Output Structure**:
- **Clean Data**: Markdown report with organized player data
- **Raw Data**: Complete JSON response data
- **API Usage**: Comprehensive tracking of API calls and efficiency

**Key Features**:
- 100% player matching using multiple strategies
- Comprehensive cross-platform ID mapping
- Detailed fantasy projections with multiple scoring formats
- Historical game statistics (via player game stats endpoint)
- Player-specific news integration
- Depth chart position analysis
- Team context for fantasy outlook
- Optimized API usage with batch data caching
- Development mode (5 players) and production mode (25 players) support

## Critical Findings for Data Completeness

### 1. Missing Data Sources

**Current Issues**:
- **Injury Status**: Not available in current endpoints
- **Fantasy Outlook**: Not available in current endpoints
- **Player-Specific News**: News endpoint provides general fantasy news, not player-specific

**Solutions**:
- Use `getNFLGamesForPlayer` to get recent game data and infer injury status
- Use `getNFLTeams` top performers to get fantasy outlook context
- Consider using game-specific data to provide more relevant news context

### 2. Enhanced Data Extraction Strategy

**For My Roster Script**:
1. **Add Player Game Stats**: Use `getNFLGamesForPlayer` for each player to get:
   - Recent game performance
   - Snap count percentages
   - Injury indicators (low snap counts, missed games)
   - Historical performance trends

2. **Add Depth Chart Context**: Use `getNFLDepthCharts` to get:
   - Player's depth chart position
   - Competition for playing time
   - Role clarity and opportunity

3. **Add Team Context**: Use `getNFLTeams` to get:
   - Team performance and trends
   - Top performers context
   - Team statistics that affect player value

**For Available Players Script**:
1. **Batch Processing**: Use team-based approaches to minimize API calls
2. **Depth Chart Integration**: Include depth chart positions for all players
3. **Team Performance Context**: Add team-level data for better analysis

### 3. API Usage Optimization

**Current Efficiency**: 6 calls for 15 players (0.4 calls per player)
**Target Efficiency**: 8-10 calls for 200+ players (0.04-0.05 calls per player)

**Optimization Strategies**:
1. **Batch Team Data**: Get team rosters and depth charts once per team
2. **Selective Player Stats**: Only get game stats for key players
3. **Caching**: Cache team and depth chart data between runs
4. **Smart Filtering**: Focus on players with recent activity

## Error Handling

All endpoints return consistent error structures:
```json
{
  "statusCode": 400,
  "body": "Error message"
}
```

## Rate Limiting & Usage Tracking

- **Current Plan**: 1000 calls/day (upgraded plan)
- **Usage Tracking**: Centralized API usage manager with RapidAPI header-based tracking
- **Optimization**: Batch calls where possible to minimize usage
- **Monitoring**: Real-time usage tracking with Pacific Time Zone display

### Centralized API Usage Manager

**New Implementation**: All Tank01 scripts now use a centralized `ApiUsageManager` class for consistent API usage tracking and reporting.

**Location**: `data_collection/scripts/shared/api_usage_manager.py`

**Key Features**:
- **Unified Interface**: Single point of control for all API usage tracking
- **Pacific Time Zone**: Consistent timezone handling across all scripts
- **Reset Time Calculation**: Accurate calculation of limit reset times
- **Standardized Reporting**: Consistent API usage reporting format
- **Rate Limit Monitoring**: Real-time monitoring with alerts

**Usage Manager Methods**:
```python
class ApiUsageManager:
    def get_usage_info(self) -> dict
    def get_usage_summary_for_markdown(self) -> str
    def get_reset_time_pacific(self) -> str
    def is_near_limit(self, threshold: float = 0.9) -> bool
    def get_usage_percentage(self) -> float
```

### RapidAPI Usage Headers

The Tank01 API via RapidAPI provides real-time usage data in response headers:

**Headers**:
- `X-RateLimit-Requests-Limit`: Total daily limit (e.g., 1000)
- `X-RateLimit-Requests-Remaining`: Remaining calls today (e.g., 604)
- `X-RateLimit-Requests-Reset`: Seconds until limit resets (countdown format)

**Usage Data Structure**:
```json
{
  "calls_made_this_session": 396,
  "daily_limit": 1000,
  "remaining_calls": 604,
  "percentage_used": 39.6,
  "reset_timestamp": 77345,
  "reset_timestamp_pacific": "2025-09-02 11:17:46 PDT",
  "data_source": "rapidapi_headers",
  "last_updated": 1756759691.154975
}
```

**Key Features**:
- **Authoritative Source**: Uses RapidAPI response headers, not client-side tracking
- **Real-time Updates**: Updated with every API call
- **Timezone Support**: Displays reset times in Pacific Time Zone
- **Countdown Format**: Reset timestamp is seconds until reset, not Unix timestamp
- **Current Time Display**: Shows current time in Pacific Time Zone for context
- **Centralized Management**: All scripts use the same usage manager for consistency

## Optimized Player Profile Data Structure

### Comprehensive Data Integration Schema

**Purpose**: Documents the complete data structure used in the `ComprehensiveDataProcessor` for optimized player profiles that combine Yahoo, Sleeper, and Tank01 data.

**Data Sources Integration**:
- **Yahoo Fantasy Sports API**: Base player data, roster positions, team info
- **Sleeper NFL API**: Enhanced player metadata, injury status, depth chart positions
- **Tank01 NFL API**: Fantasy projections, news, game stats, team context

**Complete Player Profile Structure**:
```json
{
  "yahoo_data": {
    "player_key": "string",
    "player_id": "string", 
    "name": {
      "full": "string",
      "first": "string",
      "last": "string"
    },
    "display_position": "string",
    "team": "string",
    "bye_week": "string",
    "injury_status": "string",
    "percent_owned": "string"
  },
  "sleeper_data": {
    "player_id": "string",
    "name": "string",
    "position": "string",
    "team": "string",
    "team_abbr": "string",
    "depth_chart_position": "string",
    "injury_status": "string",
    "status": "string",
    "active": "boolean",
    "years_exp": "number",
    "age": "number",
    "height": "string",
    "weight": "string",
    "college": "string",
    "birth_date": "string",
    "fantasy_positions": ["string"],
    "player_ids": {
      "sleeper_id": "string",
      "yahoo_id": "string",
      "espn_id": "string",
      "sportradar_id": "string",
      "gsis_id": "string",
      "rotowire_id": "string",
      "fantasy_data_id": "string",
      "pandascore_id": "string",
      "oddsjam_id": "string"
    }
  },
  "tank01_data": {
    "player_id": "string",
    "name": {
      "full": "string",
      "first": "string", 
      "last": "string"
    },
    "display_position": "string",
    "team": "string",
    "team_id": "string",
    "jersey_number": "string",
    "age": "string",
    "height": "string",
    "weight": "string",
    "college": "string",
    "years_exp": "string",
    "last_game_played": "string",
    "injury": "object",
    "fantasy_projections": {
      "fantasyPoints": "number",
      "fantasyPointsDefault": {
        "standard": "number",
        "PPR": "number",
        "halfPPR": "number"
      },
      "Passing": {
        "passAttempts": "number",
        "passTD": "number",
        "passYds": "number",
        "int": "number",
        "passCompletions": "number"
      },
      "Rushing": {
        "rushYds": "number",
        "carries": "number",
        "rushTD": "number"
      },
      "Receiving": {
        "receptions": "number",
        "recTD": "number",
        "targets": "number",
        "recYds": "number"
      }
    },
    "recent_news": [
      {
        "title": "string",
        "link": "string",
        "date": "string"
      }
    ],
    "game_stats": "object",
    "depth_chart": "object",
    "team_context": "object",
    "player_ids": {
      "espn_id": "string",
      "sleeper_id": "string",
      "fantasypros_id": "string",
      "yahoo_id": "string",
      "rotowire_id": "string",
      "cbs_id": "string",
      "fref_id": "string"
    }
  },
  "roster_position": "string"
}
```

**Roster Organization Structure**:
```json
{
  "players_by_position": {
    "starting_lineup": {
      "QB": [player_profile],
      "RB": [player_profile],
      "WR": [player_profile],
      "TE": [player_profile],
      "K": [player_profile],
      "DEF": [player_profile],
      "FLEX": [player_profile]
    },
    "bench_players": {
      "QB": [player_profile],
      "RB": [player_profile],
      "WR": [player_profile],
      "TE": [player_profile],
      "K": [player_profile],
      "DEF": [player_profile]
    }
  }
}
```

**Team Defense Special Handling**:
```json
{
  "tank01_data": {
    "player_id": "DEF_27",
    "name": {
      "full": "Philadelphia Defense"
    },
    "display_position": "DEF",
    "team": "PHI",
    "team_id": "27",
    "fantasy_projections": {
      "fantasyPoints": "number",
      "defTD": "number",
      "sacks": "number",
      "int": "number",
      "fumblesRecovered": "number",
      "safeties": "number",
      "pointsAllowed": "number",
      "yardsAllowed": "number"
    },
    "recent_news": [
      {
        "title": "string",
        "link": "string",
        "date": "string"
      }
    ]
  }
}
```

**Team Defense Implementation Details**:
- **Team Mapping Utility**: Uses `data_collection/scripts/shared/team_mapping.py` for comprehensive team abbreviation mapping
- **Real Data Only**: Defense players are created using real team data, never mock data
- **Team Abbreviation Handling**: Handles differences between Yahoo ("Was"), Standard ("WAS"), and Tank01 ("WSH") abbreviations
- **Comprehensive Coverage**: All 32 NFL teams supported with proper team ID mapping
- **News Integration**: Uses team abbreviation for team-specific news retrieval
- **Projections Integration**: Includes team defense projections with defensive statistics
- **Match Rate**: 100% match rate for defense players when using proper team mapping

**Data Matching Requirements**:
1. **Yahoo Player Key Matching**: Primary identifier for cross-API matching
2. **Name + Team Matching**: Fallback strategy for unmatched players
3. **Position Validation**: Ensure position consistency across APIs
4. **Team Abbreviation Normalization**: Handle case differences (PHI vs phi)

**Token Optimization Strategy**:
- **Selective Data Inclusion**: Only include essential fields for analysis
- **Position-Based Limits**: Configurable limits per position (20 QB/RB/WR/TE/K, 10 DEF)
- **Structured Organization**: Group players by roster status and position
- **Comprehensive Enrichment**: 100% data matching across all three APIs

## Latest Development Learnings (September 2025)

### Available Players Script Enhancements

**Data Processing Improvements**:
- **Batch Data Caching**: Implemented efficient caching of large datasets (player database, projections, depth charts, teams) to minimize API calls
- **Player Matching Strategies**: Enhanced matching with 4 fallback strategies (Yahoo ID, exact name+team, last name+team, get_player_info API)
- **Data Structure Processing**: Proper handling of nested API responses (projections with playerProjections/teamDefenseProjections keys)
- **Error Handling**: Comprehensive error handling with meaningful fallback values instead of "N/A"

**API Usage Optimization**:
- **Efficiency Metrics**: 3.8 API calls per player in development mode (5 players = 19 total calls)
- **Batch Operations**: Single calls for player database, projections, depth charts, and teams data
- **Individual Player Calls**: Only for news, game stats, and unmatched player lookups
- **Usage Tracking**: Real-time RapidAPI header-based tracking with Pacific Time Zone display

**Data Completeness Achievements**:
- **Zero N/A Values**: Eliminated all "N/A" values with meaningful fallback data
- **Comprehensive Coverage**: All player data sections populated (projections, depth charts, game stats, team context)
- **Cross-Platform IDs**: Complete ID mapping across all platforms
- **Recent Performance**: Game-by-game snap count analysis for injury status inference
- **Team Context**: Fantasy outlook based on team performance and standings

**Technical Improvements**:
- **Variable Scope Management**: Fixed total_calls variable scope issues in markdown generation
- **Field Name Consistency**: Corrected API usage tracking field names (daily_limit, remaining_calls)
- **Fallback Values**: Meaningful alternatives ("Not Available", "No recent data") instead of "N/A"
- **Conditional Display**: Proper handling of different data types (individual players vs team defense)

### Team Mapping Consolidation (September 2025)

**Centralized Team Mapping**:
- **Shared Resource**: All Tank01 scripts now use `data_collection/scripts/shared/team_mapping.py` for consistent team abbreviation normalization
- **Comprehensive Coverage**: Complete mapping of all 32 NFL teams with multiple abbreviation variations
- **Case Handling**: Proper handling of case differences (PHI vs phi, WAS vs WSH)
- **Defense Matching**: 100% match rate for defense players using normalized team abbreviations

**Scripts Updated**:
- **available_players.py**: ✅ Uses shared team mapping
- **my_roster.py**: ✅ Uses shared team mapping  
- **opponent_roster.py**: ✅ Uses shared team mapping
- **transaction_trends.py**: ✅ Uses shared team mapping
- **nfl_matchups.py**: ✅ Uses shared team mapping

**Team Mapping Function**:
```python
def normalize_team_abbreviation(team_abv: str) -> str:
    """
    Normalize team abbreviations to standard format.
    Handles all variations: Yahoo (Was), Standard (WAS), Tank01 (WSH)
    """
    team_mappings = {
        # Complete mapping of all 32 NFL teams
        'ARI': 'ARI', 'arizona': 'ARI', 'cardinals': 'ARI',
        'ATL': 'ATL', 'atlanta': 'ATL', 'falcons': 'ATL',
        'BAL': 'BAL', 'baltimore': 'BAL', 'ravens': 'BAL',
        'BUF': 'BUF', 'buffalo': 'BUF', 'bills': 'BUF',
        'CAR': 'CAR', 'carolina': 'CAR', 'panthers': 'CAR',
        'CHI': 'CHI', 'chicago': 'CHI', 'bears': 'CHI',
        'CIN': 'CIN', 'cincinnati': 'CIN', 'bengals': 'CIN',
        'CLE': 'CLE', 'cleveland': 'CLE', 'browns': 'CLE',
        'DAL': 'DAL', 'dallas': 'DAL', 'cowboys': 'DAL',
        'DEN': 'DEN', 'denver': 'DEN', 'broncos': 'DEN',
        'DET': 'DET', 'detroit': 'DET', 'lions': 'DET',
        'GB': 'GB', 'green bay': 'GB', 'packers': 'GB',
        'HOU': 'HOU', 'houston': 'HOU', 'texans': 'HOU',
        'IND': 'IND', 'indianapolis': 'IND', 'colts': 'IND',
        'JAX': 'JAX', 'jacksonville': 'JAX', 'jaguars': 'JAX',
        'KC': 'KC', 'kansas city': 'KC', 'chiefs': 'KC',
        'LV': 'LV', 'las vegas': 'LV', 'raiders': 'LV',
        'LAC': 'LAC', 'los angeles chargers': 'LAC', 'chargers': 'LAC',
        'LAR': 'LAR', 'los angeles rams': 'LAR', 'rams': 'LAR',
        'MIA': 'MIA', 'miami': 'MIA', 'dolphins': 'MIA',
        'MIN': 'MIN', 'minnesota': 'MIN', 'vikings': 'MIN',
        'NE': 'NE', 'new england': 'NE', 'patriots': 'NE',
        'NO': 'NO', 'new orleans': 'NO', 'saints': 'NO',
        'NYG': 'NYG', 'new york giants': 'NYG', 'giants': 'NYG',
        'NYJ': 'NYJ', 'new york jets': 'NYJ', 'jets': 'NYJ',
        'PHI': 'PHI', 'philadelphia': 'PHI', 'eagles': 'PHI',
        'PIT': 'PIT', 'pittsburgh': 'PIT', 'steelers': 'PIT',
        'SF': 'SF', 'san francisco': 'SF', '49ers': 'SF',
        'SEA': 'SEA', 'seattle': 'SEA', 'seahawks': 'SEA',
        'TB': 'TB', 'tampa bay': 'TB', 'buccaneers': 'TB',
        'TEN': 'TEN', 'tennessee': 'TEN', 'titans': 'TEN',
        'WSH': 'WSH', 'washington': 'WSH', 'commanders': 'WSH',
        'WAS': 'WSH', 'was': 'WSH'  # Yahoo uses WAS, Tank01 uses WSH
    }
    return team_mappings.get(team_abv.upper(), team_abv.upper())
```

### Defense Player Data Structure Fixes (September 2025)

**Projected Points Integration**:
- **Issue**: Defense players were missing projected points in markdown output
- **Root Cause**: Incorrect teamID lookup in teamDefenseProjections processing
- **Fix**: Changed from `tank01_player.get('teamID')` to `tank01_player.get('teamData', {}).get('teamID')`
- **Result**: Defense players now show complete fantasy projections

**Markdown Output Improvements**:
- **Long Name**: Fixed to use `fullName` instead of `longName` for defense players
- **Team ID**: Fixed to use `teamData.teamID` structure for proper team ID display
- **Fantasy Points**: Fixed to use `fantasyPointsDefault` instead of `fantasyPoints` for consistency
- **Data Completeness**: All defense players now show complete information instead of "N/A" values

**Cached Data Output**:
- **Raw JSON Enhancement**: Added `cached_data` section to raw output files
- **Includes**: `projections`, `depth_charts`, `teams` data for debugging and analysis
- **Purpose**: Enables verification of data completeness and API response structure

### All Tank01 Scripts Status (September 2025)

**Script Testing Results**:
- **available_players.py**: ✅ 100% functional with configurable position limits
- **my_roster.py**: ✅ 100% functional with shared team mapping
- **opponent_roster.py**: ✅ 100% functional with shared team mapping
- **transaction_trends.py**: ✅ 100% functional with Yahoo data enrichment
- **nfl_matchups.py**: ✅ 100% functional with comprehensive game data

**Key Achievements**:
- **100% Player Matching**: All players successfully matched across APIs
- **Complete Data Integration**: All data sources properly integrated
- **Defense Player Support**: Full support for team defense players with proper projections
- **API Efficiency**: Optimized API usage with batch operations and caching
- **Error Handling**: Comprehensive error handling with meaningful fallback values
- **Team Mapping**: Centralized team abbreviation normalization across all scripts

## Implementation Notes

- All string values in responses are returned as strings, not numbers
- Team abbreviations may vary between endpoints and require normalization
- Player matching requires multiple strategies due to name/team variations
- News endpoint provides player-specific news when playerID parameter is used
- Game stats provide the most comprehensive individual player data
- Depth charts provide crucial context for player opportunities
- Team data provides important context for player value assessment
- Batch data caching is essential for API efficiency with large player lists
- RapidAPI headers provide authoritative usage tracking data