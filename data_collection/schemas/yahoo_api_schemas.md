# Yahoo Fantasy Sports API - Expected Response Schemas

## Overview

This document defines the expected response structures for Yahoo Fantasy Sports API endpoints used in our data collection system. Each schema ensures we extract **ALL** available data consistently.

## ⚠️ **CRITICAL: Yahoo API Response Format**

**Yahoo returns JSON that mimics XML structure** - this is crucial for parsing!

### **Response Format Characteristics:**
- ✅ **Format**: JSON (not XML)
- ⚠️ **Structure**: Nested arrays that mimic XML hierarchy
- 🔍 **Key Pattern**: Uses numbered keys (`"0"`, `"1"`, `"2"`) for array indexing
- 📋 **Data Storage**: Properties stored as **arrays of objects** rather than simple objects
- 🎯 **XML Artifacts**: Contains XML-style attributes like `"xml:lang"`, `"yahoo:uri"`

### **Critical Parsing Patterns:**

#### **1. List-of-Lists Structure:**
```json
"player": [
  [ // First array: player properties
    {"player_key": "461.p.32671"},
    {"name": {"full": "Joe Burrow"}},
    {"editorial_team_abbr": "Cin"}
  ],
  [ // Second array: position data
    {"selected_position": [
      {"coverage_type": "week", "week": "1"},
      {"position": "QB"}  // ← Actual starting position!
    ]}
  ]
]
```

#### **2. Numbered Key Navigation:**
```json
"users": {
  "0": {
    "user": [ // Array, not object!
      {"guid": "..."},
      {"games": {"0": {"game": [...]}}}
    ]
  }
}
```

#### **3. Selected Position Parsing:**
```json
// WRONG: Taking first item
"selected_position": [
  {"coverage_type": "week", "week": "1"}, // ← Not the position!
  {"position": "QB"} // ← This is the actual position!
]

// CORRECT: Search for object with 'position' key
for pos_item in selected_position:
    if 'position' in pos_item:
        actual_position = pos_item['position']
```

#### **4. Bye Week Data Extraction:**
```json
// CORRECT: Extract from bye_weeks object
"bye_weeks": {
  "week": "10"
}

// CORRECT: Store as simple field
player_info['bye_week'] = player_info['bye_weeks'].get('week', '')

// WRONG: Don't nest under bye_weeks in output
player.get('bye_weeks', {}).get('bye_week', 'N/A')  // ❌ This will fail!
```

## Authentication

- **Method**: OAuth 2.0 (Authorization Code Grant)
- **Tokens**: Access token (1 hour expiry) + Refresh token (auto-renewal)
- **Scopes**: `fspt-w` (Fantasy Sports read/write)

---

## 1. My Team Roster - `team/{team_key}/roster`

### Expected Response Structure:
```json
{
  "fantasy_content": {
    "team": [
      {
        "team_key": "string",
        "team_id": "string", 
        "name": "string",
        "is_owned_by_current_login": 1,
        "url": "string",
        "team_logo": "string",
        "waiver_priority": "number",
        "faab_balance": "string",
        "number_of_moves": "string",
        "number_of_trades": "string",
        "roster_adds": "object",
        "managers": [
          {
            "manager": {
              "manager_id": "string",
              "nickname": "string", 
              "guid": "string",
              "image_url": "string"
            }
          }
        ]
      },
      {
        "roster": {
          "0": {
            "players": {
              "0": {
                "player": [
                  {
                    "player_key": "string",
                    "player_id": "string", 
                    "name": {
                      "full": "string",
                      "first": "string", 
                      "last": "string",
                      "ascii_first": "string",
                      "ascii_last": "string"
                    },
                    "editorial_player_key": "string",
                    "editorial_team_key": "string",
                    "editorial_team_full_name": "string",
                    "editorial_team_abbr": "string",
                    "bye_weeks": {
                      "week": "string"
                    },
                    "uniform_number": "string", 
                    "display_position": "string",
                    "headshot": {
                      "url": "string",
                      "size": "string"
                    },
                    "image_url": "string",
                    "is_undroppable": "string",
                    "position_type": "string",
                    "primary_position": "string",
                    "eligible_positions": [
                      {
                        "position": "string"
                      }
                    ],
                    "has_player_notes": 1,
                    "player_notes_last_timestamp": "string",
                    "status": "string",
                    "status_full": "string",
                    "injury_note": "string"
                  },
                  {
                    "selected_position": [
                      {
                        "coverage_type": "string", 
                        "date": "string",
                        "position": "string"
                      }
                    ]
                  }
                ]
              }
            }
          }
        }
      }
    ]
  }
}
```

### Key Data Points:
- **Team Metadata**: team_key, name, waiver_priority, faab_balance
- **Player Details**: player_key, player_id, full name, NFL team
- **Positions**: selected_position (starter/bench), eligible_positions
- **Status**: injury_status, status_full, bye_weeks
- **Manager Info**: nickname, manager_id

### ✅ **Validation Status**: COMPLETE - All data extracted successfully
- **Script**: `my_roster.py` ✅ **WORKING PERFECTLY**
- **Data Quality**: 100% successful extraction (15 players, 9 starters + 6 bench)
- **Performance**: 2 API calls, 0.39s execution, 0 errors
- **Bye Weeks**: ✅ **CORRECTLY EXTRACTED** and displayed

---

## 2. Opponent Team Rosters - `league/{league_key}/teams` + `team/{team_key}/roster`

### League Teams Response:
```json
{
  "fantasy_content": {
    "league": [
      {
        "league_key": "string",
        "league_id": "string",
        "name": "string",
        "url": "string",
        "logo_url": "string",
        "draft_status": "string",
        "num_teams": "number",
        "edit_key": "string",
        "weekly_deadline": "string",
        "league_update_timestamp": "string",
        "scoring_type": "string",
        "league_type": "string",
        "renew": "string",
        "renewed": "string",
        "iris_group_chat_id": "string",
        "allow_add_to_dl_extra_pos": 0,
        "is_pro_league": "string",
        "is_cash_league": "string",
        "current_week": "string",
        "start_week": "string",
        "start_date": "string",
        "end_week": "string", 
        "end_date": "string",
        "game_code": "string",
        "season": "string"
      },
      {
        "teams": {
          "0": {
            "team": {
              "team_key": "string",
              "team_id": "string",
              "name": "string", 
              "is_owned_by_current_login": 0,
              "url": "string",
              "team_logo": "string",
              "waiver_priority": "number",
              "faab_balance": "string",
              "number_of_moves": "string",
              "number_of_trades": "string",
              "roster_adds": "object",
              "managers": "array"
            }
          }
        }
      }
    ]
  }
}
```

### Expected Data Points:
- **League Metadata**: league_key, name, num_teams, current_week
- **Team List**: All team_keys, names, managers
- **Individual Rosters**: Same structure as My Team Roster for each team

### ✅ **Validation Status**: COMPLETE - All data extracted successfully
- **Script**: `opponent_rosters.py` ✅ **WORKING PERFECTLY**
- **Data Quality**: 100% successful extraction (152 players across 10 teams)
- **Performance**: 12 API calls, 0 errors
- **Bye Weeks**: ✅ **CORRECTLY EXTRACTED** and displayed in all sections
- **Team Discovery**: ✅ **AUTOMATIC** - Finds all teams in league
- **Roster Parsing**: ✅ **COMPLETE** - All players with positions, status, metadata

---

## 3. Team Matchups - `league/{league_key}/scoreboard;week={week}`

### Expected Response Structure:
```json
{
  "fantasy_content": {
    "league": [
      {
        "league_key": "string",
        "league_id": "string",
        "name": "string",
        "current_week": "string",
        "start_week": "string",
        "end_week": "string"
      },
      {
        "scoreboard": {
          "0": {
            "matchups": {
              "0": {
                "matchup": {
                  "week": "string",
                  "week_start": "string",
                  "week_end": "string", 
                  "status": "string",
                  "is_playoffs": "string",
                  "is_consolation": "string",
                  "is_tied": 0,
                  "winner_team_key": "string",
                  "0": {
                    "teams": {
                      "0": {
                        "team": [
                          {
                            "team_key": "string",
                            "team_id": "string",
                            "name": "string",
                            "managers": "array"
                          },
                          {
                            "team_points": {
                              "coverage_type": "string",
                              "week": "string", 
                              "total": "string"
                            }
                          },
                          {
                            "team_projected_points": {
                              "coverage_type": "string",
                              "week": "string",
                              "total": "string"
                            }
                          }
                        ]
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    ]
  }
}
```

### Key Data Points:
- **Matchup Metadata**: week, week_start, week_end, status
- **Team Matchups**: team_key pairs, team names, managers
- **Scoring**: team_points, team_projected_points
- **Playoff Info**: is_playoffs, is_consolation, winner_team_key

### 🔄 **Validation Status**: PENDING - Script not yet created
- **Script**: `team_matchups.py` - **TO BE CREATED**
- **Priority**: Next script to implement
- **Expected Complexity**: Medium (similar to opponent rosters)

---

## 4. Available Players List - `league/{league_key}/players;position={pos};status=A;sort=OR;start={start};count={count}`

### Expected Response Structure:
```json
{
  "fantasy_content": {
    "league": [
      {
        "league_key": "string",
        "league_id": "string",
        "name": "string"
      },
      {
        "players": {
          "0": {
            "player": [
              {
                "player_key": "string",
                "player_id": "string",
                "name": {
                  "full": "string",
                  "first": "string",
                  "last": "string",
                  "ascii_first": "string", 
                  "ascii_last": "string"
                },
                "editorial_player_key": "string",
                "editorial_team_key": "string", 
                "editorial_team_full_name": "string",
                "editorial_team_abbr": "string",
                "bye_weeks": {
                  "week": "string"
                },
                "uniform_number": "string",
                "display_position": "string", 
                "headshot": {
                  "url": "string",
                  "size": "string"
                },
                "image_url": "string",
                "is_undroppable": "string",
                "position_type": "string",
                "primary_position": "string",
                "eligible_positions": "array",
                "has_player_notes": 1,
                "player_notes_last_timestamp": "string",
                "status": "string",
                "status_full": "string", 
                "injury_note": "string",
                "percent_owned": {
                  "coverage_type": "string",
                  "week": "string",
                  "value": "string"
                }
              }
            ]
          },
          "count": "number",
          "start": "number", 
          "total": "number"
        }
      }
    ]
  }
}
```

### Special Sections to Extract:
- **Available Players**: Standard player list with availability
- **Injury Reports**: Players with injury_note, status details  
- **Who's Hot**: Trending or high percent_owned players
- **Top Available Players**: Sorted by Yahoo Overall Rank (OR)

### Key Data Points:
- **Player Info**: player_key, player_id, full name, NFL team
- **Availability**: status, percent_owned
- **Health**: injury_note, status_full
- **Pagination**: count, start, total (for complete dataset)

### 🔄 **Validation Status**: PENDING - Script not yet created
- **Script**: `available_players.py` - **TO BE CREATED**
- **Priority**: High (essential for free agent analysis)
- **Expected Complexity**: High (pagination, multiple sections)

---

## 5. Transaction Trends - `league/{league_key}/transactions`

### Expected Response Structure:
```json
{
  "fantasy_content": {
    "league": [
      {
        "league_key": "string",
        "league_id": "string",
        "name": "string"
      },
      {
        "transactions": {
          "0": {
            "transaction": {
              "transaction_key": "string",
              "transaction_id": "string",
              "type": "string",
              "status": "string",
              "timestamp": "string",
              "trader_team_key": "string",
              "tradee_team_key": "string",
              "players": {
                "0": {
                  "player": [
                    {
                      "player_key": "string",
                      "player_id": "string", 
                      "name": "object",
                      "editorial_team_abbr": "string",
                      "display_position": "string"
                    },
                    {
                      "transaction_data": [
                        {
                          "type": "string",
                          "source_type": "string",
                          "destination_type": "string"
                        }
                      ]
                    }
                  ]
                }
              }
            }
          },
          "count": "number",
          "start": "number", 
          "total": "number"
        }
      }
    ]
  }
}
```

### Key Data Points:
- **Transaction Metadata**: transaction_key, type, status, timestamp
- **Teams**: trader_team_key, tradee_team_key  
- **Players**: player_key, player_id, name, team, position
- **Transaction Details**: type, source_type, destination_type
- **Trends**: Frequency of adds/drops by player

### 🔄 **Validation Status**: PENDING - Script not yet created
- **Script**: `transaction_trends.py` - **TO BE CREATED**
- **Priority**: Medium (useful for market intelligence)
- **Expected Complexity**: Medium (similar to opponent rosters)

---

## Validation Rules

### Required Fields:
- **Player Identification**: player_key AND player_id must be present
- **Names**: full name must be extractable
- **Teams**: editorial_team_abbr for NFL team
- **Positions**: display_position or primary_position

### Data Completeness:
- No null/undefined critical fields
- Consistent player_key format (nfl.p.{player_id})
- Valid team_key format ({game_id}.l.{league_id}.t.{team_id})

### Error Handling:
- Missing optional fields should be handled gracefully
- API rate limits and timeouts should be retried
- Authentication token refresh should be automatic

### ✅ **Proven Parsing Patterns**:
- **List-of-Lists Navigation**: Successfully implemented in `my_roster.py` and `opponent_rosters.py`
- **Numbered Key Access**: Working perfectly for team and player data
- **Bye Week Extraction**: ✅ **FIXED** - Correctly extracts from `bye_weeks.week` and stores as `bye_week`
- **Position Parsing**: ✅ **WORKING** - Correctly identifies starting positions vs bench

---

**Note**: This schema represents the expected "perfect" response. Scripts should extract ALL available data from the actual response and validate against this schema to identify any missing or changed fields.

## 🎯 **Current Implementation Status**:
- ✅ **My Team Roster**: COMPLETE - `my_roster.py` working perfectly
- ✅ **Opponent Rosters**: COMPLETE - `opponent_rosters.py` working perfectly  
- 🔄 **Team Matchups**: PENDING - Next priority
- 🔄 **Available Players**: PENDING - High priority
- 🔄 **Transaction Trends**: PENDING - Medium priority
