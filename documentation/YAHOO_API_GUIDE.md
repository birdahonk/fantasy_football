# Yahoo Fantasy Sports API - Complete Implementation Guide

**⚠️ NOTE: This document has been superseded by the comprehensive guide.**  
**See: [YAHOO_API_COMPLETE_GUIDE.md](./YAHOO_API_COMPLETE_GUIDE.md) for complete documentation with all endpoints and capabilities.**

## 🎯 Overview

This guide documents the complete implementation of Yahoo Fantasy Sports API integration, including authentication, data retrieval, and parsing strategies based on real-world testing and debugging.

## 🔐 Authentication: OAuth 2.0 (WORKING)

### Current Implementation Status: ✅ **FULLY WORKING**

**Key Files:**
- `scripts/oauth/oauth2_client.py` - Main OAuth 2.0 client
- `scripts/oauth/get_oauth2_url.py` - Authorization URL generator
- `scripts/oauth/exchange_oauth2_code.py` - Token exchange handler

### Critical Implementation Details

#### 1. **Content-Type Headers**
```python
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',  # CRITICAL!
    'User-Agent': 'FantasyFootballApp/1.0'
}
```
**❌ WRONG:** `'Content-Type': 'application/xaml+xml, application/xml, text/xml, */*'`
**✅ CORRECT:** `'Content-Type': 'application/x-www-form-urlencoded'`

#### 2. **Token Storage Path**
```python
# Use absolute paths to avoid issues when running from different directories
script_dir = os.path.dirname(os.path.abspath(__file__))
self.tokens_file = os.path.join(script_dir, "..", "config", "yahoo_oauth2_tokens.json")
```

#### 3. **Scopes**
```python
YAHOO_SCOPES=fspt-w  # Fantasy Sports read/write - WORKING!
```

## 📊 Data Retrieval Patterns

### User Team Discovery

**Endpoint:** `users;use_login=1/games;game_keys=nfl/teams`

**Key Insights:**
- Use `use_login=1` to get user-specific data
- The `game_keys=nfl` filters to NFL fantasy football
- Response includes team key, league key, and team details

### Roster Retrieval

**Endpoint:** `team/{team_key}/roster`

**Example:** `team/461.l.595012.t.3/roster`

## 🔍 JSON Response Parsing - Critical Patterns

### 1. **Response Wrapper Structure**
All API responses from `oauth2_client.make_request()` return:
```python
{
    'status': 'success',
    'data': '...',  # Raw JSON string
    'parsed': {...}  # Parsed JSON object
}
```

**Always extract the `parsed` field:**
```python
response = self.oauth_client.make_request(endpoint)
if response and response.get('status') == 'success':
    parsed_data = response.get('parsed', {})
```

### 2. **Yahoo's Nested Structure Pattern**
Yahoo API responses follow a consistent but complex nesting pattern:

```python
{
    "fantasy_content": {
        "users": {
            "0": {  # Numeric keys for data objects
                "user": [  # Often arrays containing objects
                    {...},  # Metadata object
                    {
                        "games": {
                            "0": {  # Numeric key again
                                "game": [
                                    {...},  # Game metadata
                                    {
                                        "teams": {
                                            "0": {  # Team data
                                                "team": [
                                                    [  # Nested array structure
                                                        {"team_key": "..."},
                                                        {"name": {"full": "..."}},
                                                        {"is_owned_by_current_login": 1}
                                                    ]
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
            "count": 1  # Metadata - skip these keys
        }
    }
}
```

### 3. **Key Filtering Strategy**
```python
# Skip non-numeric keys (metadata) but ALLOW '0' (primary data)
for key, value in data.items():
    if not key.isdigit():
        logger.info(f"Skipping key: {key} (non-numeric)")
        continue
    # Process numeric keys including '0'
```

### 4. **List vs Dict Handling**
Many objects can be either lists or dictionaries:
```python
# Handle both cases
if isinstance(team, list):
    # Find the team object in the list
    for team_item in team:
        if isinstance(team_item, dict) and 'roster' in team_item:
            team = team_item
            break
```

## 🏈 Roster Data Structure

### Player Information Extraction
```python
# Players are nested in arrays within arrays
"roster": {
    "0": {  # Player index
        "player": [  # Array of player info objects
            {"player_key": "461.p.31007"},
            {"name": [{"full": "Joe Burrow"}]},
            {"display_position": "QB"},
            {"editorial_team_abbr": "Cin"},
            {"status": ""},
            {"selected_position": [{"position": "QB"}]}
        ]
    }
}
```

### Position Mapping
- **Starting Positions:** QB, WR, WR, RB, RB, TE, W/R/T, K, DEF
- **Bench Positions:** BN (Bench)
- **IR Positions:** IR (Injured Reserve)

## 🔧 Error Handling Patterns

### 1. **API Response Validation**
```python
if not response:
    logger.error("Failed to get API response")
    return []

if response.get('status') != 'success':
    logger.error(f"API request failed: {response}")
    return []

parsed_data = response.get('parsed')
if not parsed_data:
    logger.error("No parsed data in response")
    return []
```

### 2. **Nested Data Validation**
```python
# Always check types before accessing
if isinstance(user_obj, list):
    for user_item in user_obj:
        if isinstance(user_item, dict) and 'games' in user_item:
            # Safe to proceed
```

### 3. **Graceful Degradation**
```python
try:
    # Complex parsing logic
    return parsed_data
except Exception as e:
    logger.error(f"Error parsing response: {e}")
    return []  # Return empty list, not None
```

## 📈 Performance Insights

### Response Times (OAuth 2.0)
- **Authentication:** ~0.5s
- **Team Discovery:** ~0.15s
- **Roster Retrieval:** ~0.15s
- **League Metadata:** ~0.15s

### Rate Limiting
- **OAuth 2.0:** No rate limiting issues observed
- **OAuth 1.0a:** Severe rate limiting (429 errors)

## 🎯 Working Endpoints

### User Data
- `users;use_login=1/profile` - User profile information
- `users;use_login=1/games` - All user's fantasy games
- `users;use_login=1/games;game_keys=nfl` - NFL fantasy games only
- `users;use_login=1/games;game_keys=nfl/teams` - User's NFL fantasy teams

### Team Data
- `team/{team_key}` - Team information
- `team/{team_key}/roster` - Team roster with players
- `team/{team_key}/matchups` - Team's matchup schedule

### League Data
- `league/{league_key}` - League information
- `league/{league_key}/standings` - League standings
- `league/{league_key}/teams` - All teams in league

## 🚨 Common Pitfalls & Solutions

### 1. **"'int' object has no attribute 'get'"**
**Cause:** Trying to call `.get()` on numeric keys or count fields
**Solution:** Filter keys with `if key.isdigit()` but allow '0'

### 2. **"'list' object has no attribute 'get'"**
**Cause:** Expecting dict but got list
**Solution:** Check type and handle both cases

### 3. **"No data found"**
**Cause:** Incorrect parsing of nested structure
**Solution:** Add extensive logging to trace data structure

### 4. **Token refresh failures**
**Cause:** Wrong Content-Type header
**Solution:** Use `application/x-www-form-urlencoded`

## 🔍 Debugging Strategies

### 1. **Response Structure Logging**
```python
logger.info(f"Response structure: {json.dumps(response, indent=2)}")
```

### 2. **Type Checking at Each Level**
```python
logger.info(f"Processing key: {key}, data type: {type(data)}")
```

### 3. **Save Raw Responses**
```python
# Save for offline analysis
with open('debug_response.json', 'w') as f:
    json.dump(response, f, indent=2)
```

## 🎉 Success Metrics

### Current Working Implementation
- ✅ **OAuth 2.0 Authentication:** 100% success rate
- ✅ **Team Discovery:** Successfully finds user's teams
- ✅ **Roster Retrieval:** Complete roster with 15 players
- ✅ **League Metadata:** Full league information including name
- ✅ **Player Parsing:** All player details (name, position, team, status)

### Example Successful Roster Retrieval
```
Team: birdahonkers (461.l.595012.t.3)
League: Greg Mulligan Memorial League
Players: 15 total
- Starting: QB, 2 WR, 2 RB, TE, FLEX, K, DEF
- Bench: 6 players
- All player details successfully parsed
```

## 📚 References

- [Yahoo Fantasy Sports API Documentation](https://developer.yahoo.com/fantasysports/guide/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- Working implementation: `scripts/core/roster_retriever.py`

---

**Last Updated:** January 2025  
**Status:** ✅ Fully Working Implementation  
**Next Steps:** Build analysis and recommendation engine
