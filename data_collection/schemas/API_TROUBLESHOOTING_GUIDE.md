# API Troubleshooting Guide

This guide helps prevent common API endpoint errors and provides quick reference for correct endpoint usage.

## 🚨 Common 404 Errors and Solutions

### Tank01 NFL API (RapidAPI)

**❌ INCORRECT ENDPOINTS (Will cause 404 errors):**
- `getNFLPlayers` → ✅ Use `getNFLPlayerList`
- `getNFLTeamStats` → ✅ Use `getNFLTeamRoster`

**✅ CORRECT ENDPOINTS:**
- `getNFLPlayerList` - Complete player database
- `getNFLProjections` - Weekly fantasy projections  
- `getNFLGamesForPlayer` - Individual player game stats
- `getNFLTeamRoster` - Team roster information
- `getNFLDepthCharts` - Team depth charts
- `getNFLTeams` - Team information and stats
- `getNFLGameInfo` - Game details and scores
- `getNFLScoresOnly` - Daily scoreboard
- `getNFLNews` - Player and team news
- `getNFLPlayerInfo` - Individual player details
- `getNFLChangelog` - API updates and changes

### Sleeper NFL API

**❌ INCORRECT ENDPOINTS (Will cause 404 errors):**
- `players/nfl/news` → ✅ News data comes from player objects (`news_updated` field)

**✅ CORRECT ENDPOINTS:**
- `state/nfl` - NFL season state and current week
- `players/nfl` - Complete player database
- `players/nfl/trending/add` - Trending adds
- `players/nfl/trending/drop` - Trending drops
- `players/nfl/trending/waiver` - Trending waivers

**News Data Access:**
- News information is embedded in player objects via the `news_updated` field
- No separate news endpoint exists
- Use `players/nfl` and extract `news_updated` timestamp for each player

### Yahoo Fantasy Sports API

**✅ CORRECT ENDPOINTS:**
- `users;use_login=1/games` - User's fantasy games
- `team/{team_key}` - Team information
- `league/{league_key}` - League information
- `league/{league_key}/settings` - League settings
- `league/{league_key}/players` - Available players
- `league/{league_key}/transactions` - League transactions

## 🔍 Quick Validation Checklist

Before creating new scripts, verify:

1. **Endpoint Name**: Check this guide for correct endpoint names
2. **Base URL**: Ensure you're using the correct base URL
3. **Authentication**: Verify required authentication (Yahoo OAuth, Tank01 API key)
4. **Parameters**: Check if endpoint requires specific parameters
5. **Rate Limits**: Be aware of API rate limits

## 📚 Reference Files

- **Tank01 API**: `tank01_api_schemas.md`
- **Sleeper API**: `sleeper_api_schemas.md`  
- **Yahoo API**: `yahoo_api_schemas.md`
- **Health Check**: `data_collection/scripts/api_health_check.py`

## 🛠️ Testing New Endpoints

Use the API health check script to validate endpoints:
```bash
cd data_collection/scripts
python api_health_check.py
```

This will test all endpoints and show which ones are working correctly.

## 📝 Best Practices

1. **Always reference this guide** when adding new API calls
2. **Test endpoints** with the health check script before implementing
3. **Use existing client classes** (`Tank01Client`, `SleeperClient`, `SimpleYahooAuth`)
4. **Check rate limits** before making bulk API calls
5. **Handle errors gracefully** with proper try/catch blocks

---

**Last Updated**: September 2, 2025
**Purpose**: Prevent 404 errors and ensure correct API endpoint usage
