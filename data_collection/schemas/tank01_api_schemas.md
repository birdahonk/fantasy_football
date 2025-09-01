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
      "timePosted": "string",
      "author": "string",
      "impact": "string"
    }
  ]
}
```

**Key Data Points**:
- **Player-Specific News**: When `playerID` is provided, returns news articles specifically about that player
- **Team-Specific News**: When `teamID` or `teamAbv` is provided, returns news articles about that team
- **Fantasy-Relevant News**: When `fantasyNews=true`, filters for fantasy-relevant content
- **Article Metadata**: title, link, author, impact assessment
- **Time Posted Information**: Recent news filtering available

**Examples**:
- `getNFLNews(playerID="3117251")` - News about Christian McCaffrey
- `getNFLNews(teamAbv="SF")` - News about San Francisco 49ers
- `getNFLNews(fantasyNews=true, maxItems=50)` - General fantasy news

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

**Purpose**: Extract comprehensive Tank01 data for all available players from Yahoo Fantasy.

**Planned Data Sources**:
1. Player database (getNFLPlayerList) - 1 call
2. Weekly projections (getNFLProjections) - 1 call
3. Fantasy news (getNFLNews) - 1 call
4. Depth charts (getNFLDepthCharts) - 1 call
5. Teams information (getNFLTeams) - 1 call

**Estimated API Calls**: 5 calls for 200+ players (0.025 calls per player)

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
- **Usage Tracking**: RapidAPI header-based tracking (authoritative source)
- **Optimization**: Batch calls where possible to minimize usage
- **Monitoring**: Real-time usage tracking with Pacific Time Zone display

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

## Implementation Notes

- All string values in responses are returned as strings, not numbers
- Team abbreviations may vary between endpoints
- Player matching requires multiple strategies due to name/team variations
- News endpoint provides general fantasy news, not player-specific news
- Game stats provide the most comprehensive individual player data
- Depth charts provide crucial context for player opportunities
- Team data provides important context for player value assessment