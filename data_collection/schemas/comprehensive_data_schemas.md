# Comprehensive Data Integration Schemas

## Overview

This document defines the complete data structures and integration patterns used in the Fantasy Football AI General Manager system. It covers the data flow from raw API responses through the `ComprehensiveDataProcessor` to the final optimized player profiles used by the AI agents.

## Data Flow Architecture

```
Raw API Data → Data Collection Scripts → ComprehensiveDataProcessor → AI Agents
     ↓                    ↓                        ↓                    ↓
Yahoo/Sleeper/Tank01 → JSON Output Files → Optimized Profiles → Analysis Reports
```

## 1. Data Collection Scripts Output Structure

### Yahoo Fantasy Sports API Scripts

**My Roster Script** (`yahoo/my_roster.py`):
```json
{
  "league_info": {
    "league_key": "string",
    "league_name": "string",
    "current_week": "number"
  },
  "team_info": {
    "team_key": "string", 
    "team_name": "string"
  },
  "season_context": {
    "current_week": "number",
    "nfl_season": "string",
    "league_info": {
      "league_name": "string"
    }
  },
  "roster_players": [
    {
      "player_key": "string",
      "player_id": "string",
      "name": {
        "full": "string",
        "first": "string",
        "last": "string"
      },
      "display_position": "string",
      "editorial_team_abbr": "string",
      "bye_week": "string",
      "status": "string",
      "percent_owned_value": "string"
    }
  ],
  "roster_raw": {
    "fantasy_content": {
      "team": [
        {
          "team_key": "string",
          "name": "string"
        },
        {
          "roster": {
            "0": {
              "players": {
                "0": {
                  "player": [
                    {
                      "player_key": "string",
                      "name": {"full": "string"}
                    },
                    {
                      "selected_position": [
                        {"coverage_type": "week", "week": "1"},
                        {"position": "QB"}
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
}
```

**Opponent Rosters Script** (`yahoo/opponent_rosters.py`):
```json
{
  "rosters": {
    "team_key_1": {
      "players": [player_data]
    },
    "team_key_2": {
      "players": [player_data]
    }
  },
  "teams": [
    {
      "team_key": "string",
      "name": "string"
    }
  ]
}
```

**Team Matchups Script** (`yahoo/team_matchups.py`):
```json
{
  "season_context": {
    "current_week": "number",
    "nfl_season": "string"
  },
  "league_info": {
    "team_key": "string"
  },
  "matchups": {
    "week_1": {
      "matchups": [
        {
          "teams": [
            {
              "team_key": "string",
              "name": "string"
            },
            {
              "team_key": "string", 
              "name": "string"
            }
          ]
        }
      ]
    }
  }
}
```

### Sleeper NFL API Scripts

**My Roster Script** (`sleeper/my_roster.py`):
```json
{
  "matched_players": [
    {
      "yahoo_player": {
        "player_key": "string",
        "name": {"full": "string"}
      },
      "sleeper_player": {
        "player_id": "string",
        "full_name": "string",
        "position": "string",
        "team": "string",
        "depth_chart_position": "string",
        "injury_status": "string",
        "years_exp": "number",
        "age": "number",
        "height": "string",
        "weight": "string",
        "college": "string",
        "player_ids": {
          "yahoo_id": "string",
          "espn_id": "string",
          "sportradar_id": "string"
        }
      }
    }
  ]
}
```

**Opponent Roster Script** (`sleeper/opponent_roster.py`):
```json
{
  "matched_players": [
    {
      "yahoo_player": {
        "player_key": "string",
        "name": {"full": "string"}
      },
      "sleeper_player": {
        "player_id": "string",
        "full_name": "string",
        "position": "string",
        "team": "string",
        "depth_chart_position": "string",
        "injury_status": "string"
      }
    }
  ]
}
```

### Tank01 NFL API Scripts

**My Roster Script** (`tank01/my_roster.py`):
```json
{
  "matched_players": [
    {
      "yahoo_player": {
        "player_key": "string",
        "name": {"full": "string"}
      },
      "tank01_data": {
        "playerID": "string",
        "longName": "string",
        "pos": "string",
        "team": "string",
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
            "passYds": "number"
          }
        },
        "recent_news": [
          {
            "title": "string",
            "link": "string",
            "date": "string"
          }
        ],
        "game_stats": {},
        "depth_chart": {},
        "team_context": {}
      }
    }
  ]
}
```

**Available Players Script** (`tank01/available_players.py`):
```json
{
  "processed_data": {
    "available_players": [
      {
        "yahoo_data": {
          "player_key": "string",
          "name": {"full": "string"}
        },
        "tank01_data": {
          "playerID": "string",
          "longName": "string",
          "pos": "string",
          "team": "string"
        },
        "projection": {
          "fantasyPoints": "number",
          "fantasyPointsDefault": {
            "standard": "number",
            "PPR": "number",
            "halfPPR": "number"
          }
        },
        "news": [
          {
            "title": "string",
            "link": "string",
            "date": "string"
          }
        ],
        "game_stats": {},
        "depth_chart": {}
      }
    ]
  }
}
```

## 2. ComprehensiveDataProcessor Integration

### Input Data Sources

The `ComprehensiveDataProcessor` loads data from the following sources:

1. **Yahoo Data**:
   - `yahoo/my_roster/*_raw_data.json` - My roster with league/team metadata
   - `yahoo/opponent_rosters/*_raw_data.json` - All opponent rosters
   - `yahoo/team_matchups/*_raw_data.json` - Current week matchups
   - `yahoo/available_players/*_raw_data.json` - Available free agents
   - `yahoo/transaction_trends/*_raw_data.json` - League transaction trends

2. **Sleeper Data**:
   - `sleeper/my_roster/*_raw_data.json` - My roster enrichment
   - `sleeper/opponent_roster/*_raw_data.json` - Opponent roster enrichment
   - `sleeper/available_players/*_raw_data.json` - Available players enrichment

3. **Tank01 Data**:
   - `tank01/my_roster/*_raw_data.json` - My roster enrichment with projections
   - `tank01/opponent_roster/*_raw_data.json` - Opponent roster enrichment with projections
   - `tank01/available_players/*_raw_data.json` - Available players enrichment with projections

### Output Data Structure

**Complete Comprehensive Data**:
```json
{
  "season_context": {
    "current_week": "number",
    "nfl_season": "string",
    "league_info": {
      "league_name": "string"
    }
  },
  "league_metadata": {
    "league_name": "string",
    "team_name": "string",
    "team_key": "string",
    "league_key": "string",
    "current_week": "number",
    "nfl_season": "string"
  },
  "my_roster": {
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
    },
    "starting_lineup": {},
    "bench_players": {},
    "total_players": "number",
    "starting_count": "number",
    "bench_count": "number",
    "team_name": "string",
    "league_name": "string",
    "data_sources": ["yahoo", "sleeper", "tank01"]
  },
  "opponent_roster": {
    "players_by_position": {
      "starting_lineup": {},
      "bench_players": {}
    },
    "starting_lineup": {},
    "bench_players": {},
    "total_players": "number",
    "starting_count": "number",
    "bench_count": "number",
    "opponent_name": "string",
    "opponent_team_key": "string",
    "data_sources": ["yahoo", "sleeper", "tank01"]
  },
  "available_players": {
    "players_by_position": {
      "QB": [player_profile],
      "RB": [player_profile],
      "WR": [player_profile],
      "TE": [player_profile],
      "K": [player_profile],
      "DEF": [player_profile]
    },
    "total_players": "number",
    "data_sources": ["yahoo", "sleeper", "tank01"]
  },
  "transaction_trends": {},
  "total_tokens": "number",
  "data_files": {
    "yahoo_roster": "string",
    "sleeper_roster": "string",
    "tank01_roster": "string",
    "yahoo_opponents": "string",
    "yahoo_available": "string",
    "sleeper_available": "string",
    "tank01_available": "string",
    "yahoo_transactions": "string"
  },
  "processing_timestamp": "string"
}
```

## 3. Optimized Player Profile Structure

### Complete Player Profile

Each player in the system has a comprehensive profile that combines data from all three APIs:

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

### Team Defense Special Handling

Team defense players have a different structure in Tank01 data:

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

## 4. Data Matching and Integration Patterns

### Player Matching Strategy

1. **Primary Matching**: Yahoo `player_key` as the unique identifier
2. **Fallback Matching**: Name + team combination
3. **Position Validation**: Ensure position consistency across APIs
4. **Team Normalization**: Handle case differences (PHI vs phi)

### Data Enrichment Process

1. **Load Base Data**: Yahoo player data as foundation
2. **Match Sleeper Data**: Find corresponding Sleeper player
3. **Match Tank01 Data**: Find corresponding Tank01 player
4. **Create Enriched Profile**: Combine all three data sources
5. **Organize by Position**: Group by roster status and position

### Error Handling and Fallbacks

- **Missing Data**: Graceful degradation with null values
- **API Failures**: Continue processing with available data
- **Matching Failures**: Log for manual review
- **Data Validation**: Ensure critical fields are present

## 5. Token Optimization Strategy

### Position-Based Limits

```json
{
  "QB": 20,
  "RB": 20,
  "WR": 20,
  "TE": 20,
  "K": 20,
  "DEF": 10,
  "FLEX": 15
}
```

### Data Selection Criteria

- **Essential Fields Only**: Remove unnecessary metadata
- **Structured Organization**: Group by position and roster status
- **Comprehensive Enrichment**: 100% data matching across APIs
- **Efficient Storage**: Optimize JSON structure for analysis

## 6. AI Agent Integration

### Input Data Format

The AI agents receive the complete comprehensive data structure with:

- **Season Context**: Current week, NFL season, league info
- **My Roster**: Starting lineup and bench players with full enrichment
- **Opponent Roster**: Current week opponent with full enrichment
- **Available Players**: Free agents with full enrichment
- **Transaction Trends**: League activity data

### Analysis Requirements

- **Player Analysis**: Individual player summaries with projections
- **Matchup Analysis**: Head-to-head comparison with opponent
- **Recommendations**: Lineup changes and waiver wire pickups
- **News Integration**: Recent news and injury updates

## 7. File Organization and Naming

### Output File Structure

```
data_collection/outputs/
├── yahoo/
│   ├── my_roster/
│   ├── opponent_rosters/
│   ├── team_matchups/
│   ├── available_players/
│   └── transaction_trends/
├── sleeper/
│   ├── my_roster/
│   ├── opponent_roster/
│   └── available_players/
├── tank01/
│   ├── my_roster/
│   ├── opponent_roster/
│   └── available_players/
└── analyst_reports/
    ├── optimized_player_data.json
    ├── optimized_player_data.md
    └── analysis_report.md
```

### File Naming Convention

- **Format**: `YYYYMMDD_HHMMSS_{script_name}_{type}.{extension}`
- **Types**: `raw_data.json`, `clean_data.json`, `clean.md`
- **Examples**:
  - `20250906_151853_opponent_roster_raw_data.json`
  - `20250906_151853_opponent_roster_clean.md`

## 8. Validation and Quality Assurance

### Data Completeness Checks

- **Player Matching**: Verify 100% match rate across APIs
- **Field Validation**: Ensure critical fields are present
- **Data Consistency**: Validate position and team information
- **Token Limits**: Verify within configured limits

### Error Reporting

- **Missing Data**: Log unmatched players
- **API Failures**: Track and report errors
- **Data Quality**: Flag inconsistencies
- **Performance**: Monitor processing times

## 9. Future Enhancements

### Planned Additions

- **Transaction Trends**: Sleeper and Tank01 transaction data
- **NFL Matchups**: Current week team matchups
- **Injury Updates**: Real-time injury status
- **Weather Data**: Game weather conditions

### Scalability Considerations

- **API Rate Limits**: Monitor and optimize usage
- **Data Caching**: Implement intelligent caching
- **Batch Processing**: Optimize for large datasets
- **Error Recovery**: Robust error handling and retry logic

---

**Note**: This schema represents the complete data integration system. All data collection scripts and the `ComprehensiveDataProcessor` must adhere to these structures to ensure consistent data flow and AI agent compatibility.
