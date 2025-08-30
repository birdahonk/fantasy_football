# Fantasy Football Pre-MVP Application - Product Requirements Document

## Project Overview

**Product Name:** Fantasy Football AI General Manager  
**User:** Haven (single user, personal application)  
**Purpose:** AI-powered fantasy football analysis and optimization tool using Cursor AI Agent as the primary interface

## Core Concept

The Cursor AI Agent serves as Haven's Fantasy Football General Manager and Coach, using a collection of Python scripts and APIs to:
- Gather real-time fantasy football data
- Analyze roster performance and opportunities
- Provide strategic recommendations
- Generate organized analysis reports
- Optimize weekly lineups for maximum wins

## Technical Architecture (Ultra-Simple, Local-First)

### Core Components
1. **Cursor AI Agent** (Primary Interface)
   - Acts as Fantasy Football GM/Coach
   - Orchestrates script execution
   - Provides conversational analysis
   - Makes strategic recommendations

2. **Python Scripts** (Data Collection Tools)
   - Yahoo Fantasy API integration
   - External data source APIs
   - Data processing and analysis
   - Report generation

3. **Local File System** (Data Storage)
   - Organized weekly analysis directories
   - Timestamped output files
   - Historical data tracking
   - Configuration files

4. **External APIs** (Data Sources)
   - Yahoo Fantasy Sports API (primary)
   - OpenAI API (enhanced analysis)
   - Anthropic API (additional insights)
   - Free/freemium fantasy data APIs

## MVP Features

### Core Functionality
1. **Yahoo Fantasy API Integration**
   - Authenticate and connect to Yahoo Fantasy
   - Discover league and team information automatically
   - Fetch current roster and player data
   - Retrieve opponent information

2. **Data Analysis Scripts**
   - Roster health and performance analysis
   - Free agent evaluation and recommendations
   - Weekly matchup analysis and optimization
   - Post-game performance assessment

3. **AI-Enhanced Analysis**
   - OpenAI API integration for strategic insights
   - Anthropic API for additional analysis perspectives
   - Player projection accuracy tracking
   - Risk assessment and mitigation strategies

4. **Organized Output System**
   - Weekly subdirectories with timestamped files
   - Pre-game and post-game analysis reports
   - Structured markdown with tables, charts, and emojis
   - Historical performance tracking

## File Organization Structure

```
fantasy_football/
├── README.md
├── .env (API keys and configuration)
├── requirements.txt
├── scripts/
│   ├── yahoo_connect.py
│   ├── roster_analyzer.py
│   ├── free_agent_analyzer.py
│   ├── matchup_analyzer.py
│   ├── performance_tracker.py
│   └── utils.py
├── analysis/
│   ├── week_1/
│   │   ├── 20250115_090000_1-pregame_roster_analysis.md
│   │   ├── 20250115_090000_1-pregame_matchup_analysis.md
│   │   ├── 20250115_090000_1-pregame_free_agent_analysis.md
│   │   ├── 20250119_220000_2-postgame_performance_analysis.md
│   │   └── 20250119_220000_2-postgame_opponent_analysis.md
│   ├── week_2/
│   └── historical/
│       ├── player_performance_tracking.csv
│       ├── projection_accuracy.csv
│       └── weekly_results.csv
├── config/
│   ├── yahoo_config.json
│   └── api_config.json
└── logs/
    └── api_calls.log
```

## Script Specifications

### 1. yahoo_connect.py
**Purpose:** Establish and maintain Yahoo Fantasy API connection

**Functions:**
- `discover_league_info()` - Find league and team IDs automatically
- `get_current_roster()` - Fetch current roster with player details
- `get_opponent_roster(week)` - Get opponent information for specific week
- `get_player_news(player_id)` - Retrieve player status and news
- `get_available_players()` - Fetch free agent pool

**Output:** JSON data structures for use by other scripts

### 2. roster_analyzer.py
**Purpose:** Analyze current roster health and performance

**Functions:**
- `analyze_roster_health(roster_data)` - Identify injuries, byes, risks
- `assess_player_performance(player_data)` - Evaluate individual performance
- `identify_roster_gaps()` - Find positions needing improvement
- `generate_roster_report()` - Create comprehensive roster analysis

**Output:** Markdown report with tables, charts, and recommendations

### 3. free_agent_analyzer.py
**Purpose:** Evaluate available players and suggest transactions

**Functions:**
- `analyze_free_agents(roster_data, free_agents)` - Compare available players to current roster
- `identify_upgrade_opportunities()` - Find players who improve team
- `suggest_add_drop_transactions()` - Recommend specific moves
- `generate_transaction_report()` - Create actionable recommendations

**Output:** Markdown report with transaction suggestions and rationale

### 4. matchup_analyzer.py
**Purpose:** Analyze weekly matchups and optimize lineups

**Functions:**
- `analyze_opponent_strength(opponent_data)` - Assess opponent's team
- `optimize_lineup(roster_data, opponent_data)` - Suggest optimal lineup
- `identify_matchup_advantages()` - Find favorable matchups
- `generate_matchup_report()` - Create weekly strategy guide

**Output:** Markdown report with lineup recommendations and strategy

### 5. performance_tracker.py
**Purpose:** Track and analyze post-game performance

**Functions:**
- `compare_projections_to_actual(projections, actual)` - Analyze accuracy
- `track_player_performance(player_id)` - Monitor individual trends
- `assess_team_performance(week)` - Evaluate overall team performance
- `generate_performance_report()` - Create post-game analysis

**Output:** Markdown report with performance insights and lessons learned

### 6. utils.py
**Purpose:** Common utility functions and helpers

**Functions:**
- `format_timestamp()` - Generate consistent timestamps
- `create_weekly_directory(week_number)` - Set up weekly analysis folders
- `save_markdown_report(content, filename)` - Save formatted reports
- `load_config()` - Load configuration files
- `log_api_call(endpoint, response_time)` - Track API usage

## API Integration Strategy

### Primary Data Sources
1. **Yahoo Fantasy Sports API**
   - Roster and player data
   - League standings and matchups
   - Player statistics and projections
   - Transaction history

2. **OpenAI API**
   - Strategic analysis and insights
   - Player comparison evaluations
   - Risk assessment and mitigation
   - Creative strategy recommendations

3. **Anthropic API**
   - Alternative analysis perspectives
   - Historical pattern recognition
   - Performance trend analysis
   - Backup analysis when OpenAI unavailable

### Additional Data Sources (Research Required)
1. **Player News and Updates**
   - ESPN API (free tier)
   - NFL.com RSS feeds
   - Player injury reports
   - Team depth chart changes

2. **Fantasy Analysis and Rankings**
   - FantasyPros API (freemium)
   - ESPN Fantasy API (unofficial)
   - Expert consensus rankings
   - Weekly projections

3. **Statistical Data**
   - NFL official statistics
   - Weather data for outdoor games
   - Vegas betting lines and totals
   - Historical performance data

## User Interaction Flow

### Primary Workflow
1. **Haven opens Cursor session** and requests analysis
2. **AI Agent determines** what information is needed
3. **AI Agent executes** appropriate scripts to gather data
4. **AI Agent analyzes** data and provides insights
5. **AI Agent generates** organized markdown reports
6. **AI Agent saves** reports to appropriate weekly directories
7. **AI Agent provides** conversational summary and recommendations

### Analysis Types and Triggers
1. **"Analyze my roster"** → Runs roster_analyzer.py
2. **"Check free agents"** → Runs free_agent_analyzer.py
3. **"Analyze this week's matchup"** → Runs matchup_analyzer.py
4. **"Review last week's performance"** → Runs performance_tracker.py
5. **"Full weekly analysis"** → Runs all scripts for comprehensive review

## Manual Setup Instructions for Haven

### 1. Yahoo Fantasy API Setup

1. **Create Yahoo Developer Account**
   - Go to https://developer.yahoo.com/apps/create/
   - Sign in with your Yahoo account
   - Click "Create an App"

2. **Configure Yahoo App**
   - Application Name: "Haven's Fantasy Football GM"
   - Description: "Personal fantasy football analysis tool"
   - Home Page URL: `https://tools.birdahonk.com/fantasy`
   - Redirect URI: `https://tools.birdahonk.com/fantasy/callback`
   - API Permissions: Select "Fantasy Sports" with "Read" access
   - Click "Create App"

3. **Save Credentials**
   - Copy "Consumer Key" (Client ID)
   - Copy "Consumer Secret" (Client Secret)
   - Store these securely for environment variables

4. **Create Callback File**
   - Create `callback.html` in your fantasy subdirectory
   - This file will handle OAuth redirects (script will provide content)

### 2. API Key Setup

1. **OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Sign in and click "Create new secret key"
   - Name: "Fantasy Football GM"
   - Copy and save the API key securely

2. **Anthropic API Key**
   - Go to https://console.anthropic.com/
   - Sign in and go to "API Keys"
   - Click "Create Key"
   - Name: "Fantasy Football GM"
   - Copy and save the API key securely

### 3. Local Environment Setup

1. **Create .env file** in project root:
```bash
# Yahoo Fantasy API
YAHOO_CLIENT_ID=your_consumer_key_here
YAHOO_CLIENT_SECRET=your_consumer_secret_here
YAHOO_REDIRECT_URI=https://tools.birdahonk.com/fantasy/callback

# AI APIs
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# App Configuration
LOG_LEVEL=INFO
DATA_DIR=./analysis
```

2. **Install Python Dependencies**
   - Python 3.8+ required
   - Run `pip install -r requirements.txt`

## Development Approach for Claude Code

### Phase 1: Core Infrastructure
1. **Project Setup**
   - Initialize git repository
   - Create directory structure
   - Set up environment configuration
   - Install required dependencies

2. **Yahoo API Integration**
   - Implement OAuth 2.0 flow
   - Create connection and discovery scripts
   - Test with live Yahoo Fantasy data
   - Handle authentication and token refresh

3. **Basic Script Framework**
   - Create utility functions
   - Implement data fetching scripts
   - Set up file organization system
   - Test basic functionality

### Phase 2: Analysis Scripts
1. **Roster Analysis**
   - Implement roster health assessment
   - Create player performance evaluation
   - Generate formatted reports
   - Test with live data

2. **Free Agent Analysis**
   - Implement player comparison logic
   - Create transaction recommendations
   - Generate upgrade opportunity reports
   - Test recommendation accuracy

3. **Matchup Analysis**
   - Implement opponent strength assessment
   - Create lineup optimization logic
   - Generate weekly strategy reports
   - Test optimization suggestions

### Phase 3: AI Enhancement
1. **OpenAI Integration**
   - Implement strategic analysis prompts
   - Create enhanced recommendation system
   - Test AI-generated insights
   - Optimize prompt engineering

2. **Anthropic Integration**
   - Implement alternative analysis perspectives
   - Create backup analysis system
   - Test Claude-generated insights
   - Compare with OpenAI results

### Phase 4: Performance Tracking
1. **Historical Data Collection**
   - Implement weekly performance tracking
   - Create projection accuracy analysis
   - Generate trend analysis reports
   - Test data persistence

2. **Advanced Analytics**
   - Implement pattern recognition
   - Create predictive modeling
   - Generate strategic insights
   - Test analysis accuracy

## Success Metrics

### MVP Success Criteria
- Successfully connects to Yahoo Fantasy API
- Discovers league and team information automatically
- Generates readable analysis reports in organized directories
- AI Agent can execute scripts and provide insights
- Basic roster and matchup analysis working

### Full Application Success
- All analysis scripts working reliably
- AI-enhanced insights providing actionable recommendations
- Historical performance tracking and trend analysis
- Organized file system with comprehensive weekly analysis
- AI Agent serving as effective Fantasy Football GM

## Risk Mitigation

### Technical Risks
- **Yahoo API Rate Limits:** Implement request throttling and caching
- **API Authentication:** Robust token refresh and error handling
- **Data Consistency:** Validate data before analysis and reporting
- **AI API Costs:** Monitor usage and implement budget controls

### Operational Risks
- **Script Failures:** Comprehensive error handling and logging
- **Data Loss:** Regular backups of analysis files
- **API Changes:** Version monitoring and update procedures
- **File Organization:** Automated directory creation and validation

## Cost Structure

### Monthly Operating Costs
- **OpenAI API:** ~$5-15/month (estimated usage)
- **Anthropic API:** ~$5-10/month (estimated usage)
- **Total:** $10-25/month

### One-Time Setup
- Domain subdomain: Already owned
- Web hosting: Already available
- Development time: Self-funded

## Conclusion

This pre-MVP application provides a solid foundation for AI-powered fantasy football analysis while maintaining simplicity and local control. The Cursor AI Agent serves as your personal Fantasy Football General Manager, using organized scripts and APIs to gather data and generate insights.

The file organization system ensures all analysis is properly tracked and easily accessible, while the script-based architecture allows for incremental development and testing. By starting with core functionality and building up to AI-enhanced analysis, you'll have a powerful tool for optimizing your fantasy football team throughout the season.

The step-by-step setup instructions ensure all external services are properly configured, while the development approach guides systematic implementation of each component. This foundation can later be expanded to include automated scheduling and more advanced features as your needs evolve.
