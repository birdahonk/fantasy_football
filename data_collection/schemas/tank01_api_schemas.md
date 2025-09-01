# Tank01 NFL API - Expected Response Schemas

## Overview

This document defines the expected response structures for Tank01 NFL API endpoints via RapidAPI. This API provides comprehensive NFL data including fantasy projections, news, and advanced statistics.

## API Details

- **Provider**: Tank01 NFL via RapidAPI  
- **Base URL**: `https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com`
- **Authentication**: RapidAPI key required
- **Rate Limits**: 1000 calls/month (free tier)
- **Headers**: `X-RapidAPI-Key`, `X-RapidAPI-Host`

---

## 1. NFL Player List - `getNFLPlayerList`

### Expected Response Structure:
```json
{
  "statusCode": 200,
  "body": [
    {
      "playerID": "string",
      "longName": "string",
      "team": "string", 
      "teamID": "string",
      "pos": "string",
      "jerseyNum": "string",
      "height": "string",
      "weight": "string",
      "age": "string",
      "exp": "string",
      "school": "string",
      "playerImage": "string",
      "espnName": "string",
      "espnID": "string",
      "yahooName": "string",
      "yahooID": "string",
      "sleeperbotID": "string",
      "injuryStatus": "string",
      "fantasyOutlook": "string",
      "lastGamePlayed": "string"
    }
  ]
}
```

### Key Data Points:
- **Player Identity**: playerID, longName, pos, team
- **Physical Stats**: height, weight, age, exp, school
- **Cross-Platform IDs**: espnID, yahooID, sleeperbotID  
- **Status**: injuryStatus, fantasyOutlook
- **Images**: playerImage for UI integration

---

## 2. Fantasy Projections - `getNFLGamesForPlayer?playerID={id}`

### Expected Response Structure:
```json
{
  "statusCode": 200,
  "body": {
    "playerID": "string",
    "longName": "string",
    "team": "string",
    "pos": "string",
    "fantasyPoints": [
      {
        "gameID": "string",
        "season": "string",
        "week": "string",
        "gameDate": "string",
        "teamABV": "string",
        "opponent": "string",
        "homeOrAway": "string",
        "fantasyPointsDefault": [
          {
            "position": "string",
            "fpts": "number"
          }
        ],
        "fantasyPointsPPR": [
          {
            "position": "string", 
            "fpts": "number"
          }
        ],
        "fantasyPointsHalfPPR": [
          {
            "position": "string",
            "fpts": "number"
          }
        ],
        "playerStats": {
          "passing": {
            "passYds": "number",
            "passTD": "number",
            "passInt": "number",
            "passCmp": "number",
            "passAtt": "number"
          },
          "rushing": {
            "rushYds": "number",
            "rushTD": "number", 
            "rushAtt": "number",
            "longRush": "number"
          },
          "receiving": {
            "targets": "number",
            "receptions": "number",
            "recYds": "number",
            "recTD": "number",
            "longRec": "number"
          },
          "kicking": {
            "fgMade": "number",
            "fgAtt": "number",
            "xpMade": "number",
            "xpAtt": "number"
          },
          "defense": {
            "totalTackles": "number",
            "sacks": "number",
            "defInt": "number",
            "fumRecovered": "number"
          }
        }
      }
    ]
  }
}
```

### Key Data Points:
- **Game Context**: gameID, week, gameDate, opponent
- **Fantasy Scoring**: Default, PPR, Half-PPR variants
- **Detailed Stats**: Position-specific statistics
- **Historical Data**: Season-long game-by-game performance

---

## 3. Weekly Projections - `getNFLProjections?week={week}&archiveSeason={season}`

### Expected Response Structure:
```json
{
  "statusCode": 200,
  "body": [
    {
      "playerID": "string",
      "longName": "string",
      "team": "string",
      "pos": "string",
      "projections": {
        "week": "string",
        "season": "string",
        "fantasyPointsDefault": "number",
        "fantasyPointsPPR": "number", 
        "fantasyPointsHalfPPR": "number",
        "projectedStats": {
          "passing": {
            "passYds": "number",
            "passTD": "number", 
            "passInt": "number"
          },
          "rushing": {
            "rushYds": "number",
            "rushTD": "number",
            "rushAtt": "number"
          },
          "receiving": {
            "targets": "number",
            "receptions": "number", 
            "recYds": "number",
            "recTD": "number"
          }
        }
      }
    }
  ]
}
```

### Key Data Points:
- **Weekly Focus**: Specific week projections
- **All Players**: Complete NFL player projections
- **Scoring Formats**: Multiple fantasy scoring systems
- **Statistical Breakdown**: Position-specific projected stats

---

## 4. NFL News - `getNFLNews?fantasyNews=true&maxItems={limit}`

### Expected Response Structure:
```json
{
  "statusCode": 200,
  "body": [
    {
      "id": "string",
      "title": "string",
      "url": "string", 
      "timePosted": "string",
      "author": "string",
      "playerID": "string",
      "playerName": "string",
      "team": "string",
      "fantasyAnalysis": "string",
      "impactRating": "string",
      "newsType": "string",
      "body": "string"
    }
  ]
}
```

### Key Data Points:
- **Article Metadata**: id, title, url, timePosted, author
- **Player Context**: playerID, playerName, team
- **Fantasy Impact**: fantasyAnalysis, impactRating
- **Content**: body, newsType for categorization

---

## 5. Depth Charts - `getNFLDepthCharts?teamAbv={team}`

### Expected Response Structure:
```json
{
  "statusCode": 200,
  "body": [
    {
      "teamAbv": "string",
      "teamName": "string",
      "depthChart": {
        "QB": [
          {
            "playerID": "string", 
            "longName": "string",
            "depth": 1,
            "position": "QB"
          }
        ],
        "RB": [
          {
            "playerID": "string",
            "longName": "string", 
            "depth": 1,
            "position": "RB"
          }
        ],
        "WR": [
          {
            "playerID": "string",
            "longName": "string",
            "depth": 1,
            "position": "WR"
          }
        ],
        "TE": [
          {
            "playerID": "string", 
            "longName": "string",
            "depth": 1,
            "position": "TE"
          }
        ],
        "K": [
          {
            "playerID": "string",
            "longName": "string",
            "depth": 1,
            "position": "K"
          }
        ],
        "DEF": [
          {
            "playerID": "string",
            "longName": "string", 
            "depth": 1,
            "position": "DEF"
          }
        ]
      }
    }
  ]
}
```

### Key Data Points:
- **Team Organization**: teamAbv, teamName
- **Position Groups**: QB, RB, WR, TE, K, DEF
- **Depth Order**: depth ranking (1 = starter, 2+ = backups)
- **Usage Intelligence**: Understand player opportunities

---

## 6. Team Rosters - `getNFLTeamRoster?teamAbv={team}&getStats=true`

### Expected Response Structure:
```json
{
  "statusCode": 200,
  "body": {
    "teamAbv": "string",
    "teamName": "string", 
    "roster": [
      {
        "playerID": "string",
        "longName": "string",
        "pos": "string",
        "jerseyNum": "string",
        "height": "string", 
        "weight": "string",
        "age": "string",
        "exp": "string",
        "school": "string",
        "stats": {
          "2025": {
            "passing": "object",
            "rushing": "object",
            "receiving": "object",
            "kicking": "object",
            "defense": "object"
          }
        }
      }
    ]
  }
}
```

### Key Data Points:
- **Team Context**: teamAbv, teamName
- **Player Details**: Full roster with physical stats
- **Performance Stats**: Current season statistics
- **Team Analysis**: Complete team composition

---

## Player Roster Stats Integration

### For My Roster Players:
1. **Get Yahoo roster** (player names/teams)
2. **Match to Tank01 database** using name/team matching
3. **Extract fantasy data**:
   - Weekly fantasy projections (multiple scoring formats)
   - Historical performance trends
   - News and injury analysis
   - Depth chart positioning

### For Available Players:
1. **Get Yahoo free agents list**
2. **Match to Tank01 database**
3. **Add projection intelligence**:
   - Weekly fantasy projections
   - Recent news and updates
   - Opportunity analysis via depth charts
   - Historical performance patterns

---

## Player Matching Algorithm

### Tank01 Matching Strategy:
```python
def match_tank01_player(yahoo_name, yahoo_team, tank01_players):
    # 1. Direct yahooID match (when available)
    # 2. longName exact match + team
    # 3. Last name + team match
    # 4. Name similarity + position match
    # Success rate: ~93% based on testing
```

### Cross-Reference Fields:
- **yahooID**: Direct Yahoo Fantasy player ID
- **espnID**: ESPN player ID for additional validation
- **sleeperbotID**: Sleeper player ID for cross-platform integration
- **team**: NFL team abbreviation matching

---

## Rate Limiting & Usage

### Monthly Quota Management:
- **Free Tier**: 1000 calls/month
- **Usage Tracking**: Monitor API calls per session
- **Priority Endpoints**: Focus on projections and news
- **Caching Strategy**: Cache player list and depth charts

### Efficient Usage Patterns:
- **Batch Requests**: Get weekly projections for all players at once
- **Strategic Timing**: Update projections weekly, news daily
- **Error Recovery**: Graceful degradation when quota exceeded

---

## Validation Rules

### Required Fields:
- **playerID**: Must be present and consistent
- **longName**: Must be extractable for matching
- **team**: Must be valid NFL team abbreviation
- **pos**: Must be valid NFL position

### Data Quality Checks:
- **Fantasy Points**: Must be numeric and reasonable (0-50 range)
- **projectedStats**: Individual stats should sum to reasonable totals
- **News Currency**: timePosted should be recent for relevance
- **Depth Chart**: depth should be 1-10 range

### Error Handling:
- **Quota Exceeded**: Graceful degradation with cached data
- **Player Not Found**: Log missing players for investigation  
- **Malformed Data**: Skip individual players, continue processing
- **Network Timeouts**: Retry with exponential backoff

---

**Note**: Tank01 API provides the most comprehensive fantasy projections available. Use strategically within rate limits. The 93% player matching rate makes it highly valuable for enhancing Yahoo roster data with projections and news.
