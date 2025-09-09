# Fantasy Football Data Collection System

## 🎯 Purpose

This directory contains **clean, focused data extraction scripts** for reliable fantasy football data collection. These scripts are designed to:

- Extract **ALL** data from API responses (no filtering or analysis)
- Output both clean markdown and raw JSON data
- Focus on one endpoint at a time for reliability
- Provide a solid data foundation for analysis scripts
- Maintain consistent structure and error handling

## 📁 Directory Structure

```
data_collection/
├── README.md                    # This guide
├── schemas/                     # API schema documents for validation
│   ├── yahoo_api_schemas.md     # Expected Yahoo API response structures
│   ├── sleeper_api_schemas.md   # Expected Sleeper API response structures
│   └── tank01_api_schemas.md    # Expected Tank01 API response structures
├── scripts/                     # Clean data extraction scripts
│   ├── yahoo/                   # Yahoo Fantasy API data extraction
│   ├── sleeper/                 # Sleeper NFL API data extraction
│   ├── tank01/                  # Tank01 NFL API data extraction
│   └── shared/                  # Shared utilities
├── outputs/                     # All script outputs organized by timestamp
│   ├── yahoo/                   # Yahoo API data outputs
│   ├── sleeper/                 # Sleeper API data outputs
│   └── tank01/                  # Tank01 API data outputs
├── tests/                       # Validation tests for each script
└── debug/                       # Debug outputs and logs
```

## 🎉 **AI ANALYST AGENT FULLY OPERATIONAL - STREAMLINED DATA PROCESSING!**

**Last Updated**: September 8, 2025 (11:15 PM PDT)  
**Status**: ✅ **AI ANALYST AGENT FULLY OPERATIONAL WITH STREAMLINED DATA PROCESSING & COMPREHENSIVE ANALYSIS**

### 📊 **COMPLETION SUMMARY**
- **Yahoo API Scripts**: 5/5 ✅ **COMPLETE** (my_roster, opponent_rosters, team_matchups, available_players, transaction_trends)
- **Sleeper API Scripts**: 4/4 ✅ **COMPLETE** (my_roster, available_players, opponent_roster, trending)
- **Tank01 API Scripts**: 5/5 ✅ **COMPLETE** (my_roster, available_players, opponent_roster, transaction_trends, nfl_matchups)
- **Total Scripts**: 14/14 ✅ **COMPLETE** with 100% player matching and enrichment across all APIs

### 🔧 **LATEST ENHANCEMENTS (September 8, 2025)**
- **AI Analyst Agent Integration**: ✅ **FULLY OPERATIONAL!** Complete AI agent with streamlined data processing
- **Token Usage Optimization**: ✅ **68% REDUCTION!** Streamlined from 515k to 162k tokens (37k+ headroom)
- **Comprehensive Analysis**: ✅ **COMPLETE!** Individual player analysis, opponent evaluation, specific recommendations
- **Breaking News Integration**: ✅ **REAL-TIME!** Live news integration (Tank Bigsby trade) in analysis
- **100% Player Enrichment Achievement**: Complete player matching and enrichment across all APIs
- **Multi-Position Player Handling**: Fixed comprehensive handling of multi-position players (WR,TE, RB,TE, WR,RB, QB,WR) with FLEX conversion
- **Comprehensive Data Processor Refinement**: Updated processor to handle YYYY/MM/DD directory structure and multi-position players
- **Data Collection Script Synchronization**: Synchronized multi-position handling logic across all data collection scripts
- **Validation System Enhancement**: Enhanced validation system with detailed debugging and 100% accuracy verification
- **Centralized API Usage Management**: New shared utility for consistent API usage tracking across all Tank01 scripts
- **Complete Reset Time Tracking**: Accurate limit reset time calculations with Pacific Time Zone support
- **Standardized Reporting**: Consistent API usage reporting format across all scripts
- **Enhanced Markdown Output**: All scripts now include complete API usage data with reset time in both top and bottom sections

### 🚀 Quick Start

### 1. Extract My Yahoo Team Roster
```bash
cd data_collection/scripts/yahoo
python3 my_roster.py
```
**Output:**
- `outputs/yahoo/my_roster/YYYYMMDD_HHMMSS_my_roster_clean.md`
- `outputs/yahoo/my_roster/YYYYMMDD_HHMMSS_my_roster_raw_data.json`

### 2. Extract Opponent Rosters
```bash
python3 opponent_rosters.py
```
**Output:**
- Clean markdown file with all opponent rosters
- Raw API response data

### 3. Extract Team Matchups
```bash
python3 matchups.py
```
**Output:**
- Weekly matchup data (current and previous week if available)
- Separate files for each week

## 📋 Available Data Extraction Scripts

### Yahoo Fantasy API Scripts
- **`my_roster.py`** - My team roster, metadata, player details
- **`opponent_rosters.py`** - All opponent team rosters in the league
- **`matchups.py`** - Weekly team matchups (current & previous week)
- **`players_list.py`** - Complete available player list with all sections
- **`transaction_trends.py`** - Transaction trends data

### Sleeper NFL API Scripts  
- **`my_roster_stats.py`** - Stats and data for my roster players
- **`players_list_stats.py`** - Stats and data for all available players

### Tank01 NFL API Scripts
- **`my_roster.py`** - Comprehensive Tank01 data for my roster players (projections, news, game stats, depth charts, team context)
- **`available_players.py`** - Comprehensive Tank01 data for available players with 100% matching success

## 🔧 Script Behavior

### Each Script Will:
1. **Extract ALL data** from the specific API endpoint
2. **Output clean markdown** with organized, readable data
3. **Save raw API response** unchanged for debugging/analysis
4. **Include player IDs** consistently across all outputs
5. **Use timestamp prefixes** for chronological organization
6. **Log execution details** for debugging and validation
7. **Validate against schemas** to ensure complete data extraction

### Output Format:
- **Clean Data**: `YYYYMMDD_HHMMSS_[script_name]_clean.md`
- **Raw Data**: `YYYYMMDD_HHMMSS_[script_name]_raw_data.json`
- **Logs**: Saved to `debug/logs/`

## 📊 Schema Validation

Each API endpoint has a documented schema that defines:
- Expected response structure
- Required data fields
- Data types and formats
- Validation rules

Scripts validate against these schemas to ensure:
- **Complete data extraction** (no missing fields)
- **Consistent data formats** across runs
- **Early detection** of API changes
- **Reliable data quality** for downstream analysis

## 🧪 Testing & Validation

### Test Categories:
- **Endpoint Tests** - Verify each script extracts expected data
- **Schema Tests** - Validate output matches expected structure
- **Integration Tests** - Test against live API endpoints
- **Regression Tests** - Ensure consistency across API changes

### Running Tests:
```bash
cd tests/
python3 test_yahoo_scripts.py    # Test Yahoo data extraction
python3 test_sleeper_scripts.py  # Test Sleeper data extraction
python3 test_tank01_scripts.py   # Test Tank01 data extraction
python3 test_schemas.py          # Schema validation tests
```

## 🔄 Usage Workflow

1. **Run data extraction scripts** weekly (or multiple times before games)
2. **Verify outputs** in the `outputs/` directory
3. **Check logs** in `debug/logs/` for any issues
4. **Use timestamped files** for analysis scripts to consume
5. **Run tests** to validate data quality and completeness

## 🎯 Design Principles

### Focus on Reliability
- One endpoint per script (no complex multi-API integration)
- Extract ALL data (no filtering or analysis)
- Consistent error handling and logging
- Schema validation for completeness

### Clean Separation
- Completely separate from existing analysis scripts
- No sophisticated matching or analysis logic
- Raw data preparation for other scripts to consume
- Simple, maintainable code structure

### Organized Output
- Timestamp-based file naming
- Consistent directory structure
- Both human-readable and machine-readable formats
- Debug information for troubleshooting

## ✅ **FIRST SCRIPT SUCCESS: my_roster.py**

**🎉 Working Perfectly!** Your first data extraction script is complete:

- **✅ Full Roster Extraction**: 15 players with complete data
- **✅ Starting Lineup Detection**: 9 starters + 6 bench correctly identified
- **✅ Yahoo JSON-XML Parsing**: Mastered complex nested structure  
- **✅ Clean Output**: Both markdown (2KB) and raw JSON (95KB)
- **✅ Performance**: 2 API calls, 0.39 seconds, 0 errors
- **✅ Your Data**: "birdahonkers" team (Joe Burrow, Christian McCaffrey, etc.)

**📁 Find Your Data:** `data_collection/outputs/yahoo/my_roster/`

## 🔮 Next Steps

With the proven foundation working:
1. **✅ Build Remaining Scripts**: Use the same proven parsing patterns
2. **Extract All API Data**: Complete the 9-script collection system
3. **Analysis Scripts Integration**: Consume this clean, reliable data
4. **AI Integration**: Feed clean data to analysis engines

---

**Success Formula**: Clean data extraction FIRST → sophisticated analysis SECOND! 🏈
