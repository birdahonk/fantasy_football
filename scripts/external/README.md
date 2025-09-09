# External API Integrations

This directory contains clients for external APIs that enhance our Yahoo Fantasy Sports data with additional insights and capabilities.

## 🏈 Sleeper NFL API

### Overview
The Sleeper NFL API provides trending player data and comprehensive player metadata to enhance our fantasy football analysis.

- **Base URL**: `https://api.sleeper.app/v1/`
- **Authentication**: None required (completely free)
- **Data Coverage**: 11,400+ NFL players
- **Update Frequency**: Real-time trending data (24-hour windows)

### Key Features
- **Trending Players**: Most added/dropped players across thousands of leagues
- **Player Database**: Comprehensive metadata including age, experience, injury status
- **Real-time Injuries**: More current than Yahoo's injury data
- **Market Intelligence**: Understand what fantasy managers are doing

### Implementation

#### SleeperClient (`sleeper_client.py`)
Core API client for direct Sleeper API interactions.

```python
from external.sleeper_client import SleeperClient

client = SleeperClient()

# Get trending players with full details
hot_adds = client.get_trending_players_with_details("add", limit=25)
hot_drops = client.get_trending_players_with_details("drop", limit=25)

# Search for specific players
josh_allens = client.search_players_by_name("Josh Allen", position="QB")

# Get all players for a team
bills_players = client.get_players_by_team("BUF")
```

#### Key Methods
- `get_trending_players_with_details()` - Trending players with full metadata
- `search_players_by_name()` - Find players by name with position filtering
- `get_players_by_team()` - All players for specific NFL teams
- `get_players_by_position()` - Filter by position (QB, RB, WR, etc.)
- `get_nfl_players()` - Complete player database (11,400+ players)

### Data Quality
- **Player Matching**: 100% success rate matching with Yahoo players
- **Injury Accuracy**: Real-time injury status updates
- **Trending Reliability**: Based on actual waiver wire activity
- **Response Time**: ~0.3s average for trending data, ~0.6s for full player database

### Usage Examples

#### Basic Trending Analysis
```python
client = SleeperClient()

# Get most added players
trending_up = client.get_trending_players_with_details("add", limit=10)
for player in trending_up:
    name = player.get("full_name")
    position = player.get("position")
    team = player.get("team")
    adds = player.get("trending_count")
    injury = player.get("injury_status") or "Healthy"
    
    print(f"{name} ({position}, {team}): +{adds:,} adds - {injury}")
```

#### Player Research
```python
# Find all Josh Allens
allens = client.search_players_by_name("Josh Allen")
for player in allens:
    print(f"{player['full_name']} - {player['position']} - {player['team']}")

# Get Buffalo Bills roster
bills = client.get_players_by_team("BUF")
print(f"Buffalo Bills have {len(bills)} players in database")
```

### Integration with Yahoo Data
The Sleeper API is designed to complement Yahoo Fantasy data:

- **Enhanced Free Agents**: Add trending insights to Yahoo's available players
- **Injury Updates**: More current injury data than Yahoo provides
- **Market Intelligence**: Understand waiver wire trends
- **Player Enrichment**: Add age, experience, physical stats to Yahoo players

### Error Handling
The client includes comprehensive error handling:
- Network timeouts and connection errors
- JSON parsing errors
- API rate limiting (though none currently enforced)
- Graceful degradation when data is unavailable

### Logging
All API calls are logged with:
- Request URLs and parameters
- Response times and data sizes
- Error details for debugging
- Player match success/failure rates

## 🚀 Future External APIs

### Tank01 NFL API (In Development)
- **Purpose**: Fantasy point projections and news headlines
- **Cost**: 1000 calls/month free tier via RapidAPI
- **Status**: Account setup complete, implementation pending

### Additional Planned Integrations
- **FantasyData**: Advanced metrics and historical data
- **ESPN Unofficial**: News and injury updates
- **NFL.com**: Official injury reports and player status

## 📊 Performance Notes

### Caching Strategy
- Player database cached for session duration
- Trending data refreshed on each request (real-time nature)
- Failed requests cached briefly to avoid repeated failures

### Rate Limiting
- Sleeper: No strict limits, reasonable usage expected
- Tank01: 1000 calls/month, requires careful usage tracking
- Future APIs: Will implement appropriate rate limiting

### Error Recovery
- Automatic retry for transient network errors
- Graceful fallback when external APIs are unavailable
- Detailed logging for debugging integration issues

## 🔧 Development Guidelines

### Adding New External APIs
1. Create new client class in this directory
2. Follow the pattern established by `SleeperClient`
3. Include comprehensive error handling and logging
4. Add integration tests
5. Update this README with usage examples

### Testing External APIs
```python
# Test Sleeper client
python3 scripts/external/sleeper_client.py

# This will run comprehensive tests including:
# - Trending players retrieval
# - Player search functionality
# - Team roster retrieval
# - Error handling validation
```

### Best Practices
- Always handle API failures gracefully
- Cache expensive operations when appropriate
- Log all API interactions for debugging
- Provide fallback behavior when external data unavailable
- Document rate limits and usage costs
