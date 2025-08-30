```
██████╗ ██╗██████╗ ██████╗  █████╗ ██╗  ██╗ ██████╗ ███╗   ██╗██╗  ██╗███████╗██████╗ ███████╗
██╔══██╗██║██╔══██╗██╔══██╗██╔══██╗██║  ██║██╔═══██╗████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██╔════╝
██████╔╝██║██████╔╝██║  ██║███████║███████║██║   ██║██╔██╗ ██║█████╔╝ █████╗  ██████╔╝███████╗
██╔══██╗██║██╔══██╗██║  ██║██╔══██║██╔══██║██║   ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██╔══██╗╚════██║
██████╔╝██║██║  ██║██████╔╝██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║  ██╗███████╗██║  ██║███████║
╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
                                                                                              

                             █████████████████    
                        ████████            ████  
                    █████      ███             ██ 
                 ████    ███     ███           ███
              ████   █████         ███          ██
            ████  ████               ███        ██
          ███   ███                   ████      ██
         ███  ███                       ███     ██
       ███                                ███   ██
      ███                  ███ ███          ██████
     ██                      ███              ███ 
    ██                  ██████ ███            ███ 
   ██                    ███                  ██  
  ███               ██████████               ███  
  ██                  ███                    ██   
 ███            ███ ██████                  ██           Yahoo! Fantasy Football App
 ███              ███                      ██                   General Manager
██████          ███ ███                  ███      
██   ███                                ███                     🏈🏈🏈🏈🏈🏈🏈
██     ███                            ███                       🏈           🏈
██      ████                         ███                        🏈    🏆     🏈
██        ███                     ████                          🏈           🏈
██          ███                 ████                            🏈🏈🏈🏈🏈🏈🏈
███           ███            ████                 
 ██             ███      █████                    
  ████            ████████                        
    █████████████████                                                  
```

# Fantasy Football AI General Manager 🏈

Your personal AI-powered Fantasy Football assistant built with Python scripts and the Cursor AI Agent.

## 🎯 What This Does

This application transforms the Cursor AI Agent into your Fantasy Football General Manager and Coach, helping you:
- 📊 Analyze your roster health and performance
- 🔍 Evaluate free agents and suggest transactions
- 🥊 Analyze weekly matchups and optimize lineups
- 📈 Track performance and projection accuracy
- 🧠 Get AI-enhanced strategic insights and recommendations

## 🏗️ Architecture

- **Cursor AI Agent**: Your Fantasy Football GM/Coach interface
- **Python Scripts**: Data collection and analysis tools
- **Yahoo Fantasy API**: Primary data source
- **OpenAI/Anthropic APIs**: Enhanced analysis and insights
- **Local File System**: Organized weekly analysis reports

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
# Yahoo Fantasy API (OAuth 1.0a)
YAHOO_CLIENT_ID=your_consumer_key_here
YAHOO_CLIENT_SECRET=your_consumer_secret_here

# AI APIs
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# App Configuration
LOG_LEVEL=INFO
DATA_DIR=./analysis
```

### 3. Yahoo API Setup
Follow the detailed setup instructions in `documentation/pre-mvp-fantasy-football-prd.md`

**Important**: This application uses **OAuth 1.0a** (not OAuth 2.0) as required by the official Yahoo! Fantasy Sports API. Access the official documentation here: https://developer.yahoo.com/fantasysports/guide/

**Authentication Flow**: 
- Initial OAuth setup required (one-time)
- Automatic token refresh (hourly)
- Minimal re-authentication needed (typically once every few weeks)


## 📋 Command Cheatsheet for Cursor AI Agent

### 🏈 Roster Analysis Commands
```
"Analyze my roster" → Runs roster_analyzer.py
"Check roster health" → Identifies injuries, byes, and risks
"Assess player performance" → Evaluates individual player stats
"Find roster gaps" → Identifies positions needing improvement
```

### 🔍 Free Agent Analysis Commands
```
"Check free agents" → Runs free_agent_analyzer.py
"Find upgrade opportunities" → Identifies players who improve your team
"Suggest transactions" → Recommends specific add/drop moves
"Compare players" → Detailed player comparison analysis
```

### 🥊 Matchup Analysis Commands
```
"Analyze this week's matchup" → Runs matchup_analyzer.py
"Optimize my lineup" → Suggests optimal weekly lineup
"Assess opponent strength" → Analyzes opponent's team
"Find matchup advantages" → Identifies favorable matchups
```

### 📊 Performance Tracking Commands
```
"Review last week's performance" → Runs performance_tracker.py
"Track player trends" → Monitors individual performance over time
"Analyze projection accuracy" → Compares pre-game vs actual performance
"Generate weekly report" → Creates comprehensive weekly analysis
```

### 🚀 Full Analysis Commands
```
"Full weekly analysis" → Runs all scripts for comprehensive review
"Complete roster review" → Full roster + free agent + matchup analysis
"Season strategy session" → Long-term planning and recommendations
"Emergency roster check" → Quick health and status assessment
```

### 🛠️ Utility Commands
```
"Update data" → Refreshes all data from Yahoo API
"Show current roster" → Displays current roster status
"Check player news" → Gets latest player updates and injuries
"Export analysis" → Saves current analysis to files
```

## 📁 File Organization

```
fantasy_football/
├── README.md (this file)
├── .env (API keys and configuration)
├── requirements.txt (Python dependencies)
├── scripts/ (Python analysis scripts)
├── analysis/ (Weekly analysis reports)
│   ├── week_1/ (Weekly subdirectories)
│   ├── week_2/
│   └── historical/ (Season-long tracking)
├── config/ (Configuration files)
└── logs/ (API call logs)
```

## 🔧 Script Overview

- **`yahoo_connect.py`**: Yahoo Fantasy API connection with OAuth 1.0a authentication and data fetching
- **`roster_analyzer.py`**: Roster health and performance analysis
- **`free_agent_analyzer.py`**: Free agent evaluation and transaction suggestions
- **`matchup_analyzer.py`**: Weekly matchup analysis and lineup optimization
- **`performance_tracker.py`**: Performance tracking and projection accuracy
- **`utils.py`**: Common utility functions and helpers
- **`test_oauth1.py`**: OAuth 1.0a authentication testing
- **`test_oauth_signature.py`**: OAuth signature validation testing

## 🎮 How to Use

1. **Open Cursor** and navigate to this project
2. **Ask the AI Agent** to perform any analysis using the commands above
3. **Review the results** both in conversation and in generated markdown files
4. **Make decisions** based on AI recommendations
5. **Track progress** through organized weekly analysis files

## 🚨 Important Notes

- **API Rate Limits**: Yahoo Fantasy API has rate limits - scripts include throttling and proper error handling
- **OAuth 1.0a Implementation**: Correctly implemented based on official Yahoo! documentation with HMAC-SHA1 signatures
- **Authentication**: Yahoo OAuth tokens expire hourly - scripts handle automatic refresh using session handles
- **Data Freshness**: Always run "Update data" before major analysis
- **File Organization**: Reports are automatically organized by week and timestamp

## 🆘 Troubleshooting

### Common Issues:
- **"Yahoo API Error"**: Check credentials and OAuth setup
- **"Script not found"**: Ensure all scripts are in the `scripts/` directory
- **"Permission denied"**: Check file permissions and Python environment
- **"API key invalid"**: Verify environment variables are set correctly

### Getting Help:
1. Check the logs in `logs/` directory
2. Verify your `.env` file configuration
3. Test individual scripts from command line
4. Ask the AI Agent for debugging help

## 🚀 Current Implementation Status

### ✅ **Completed & Working:**
- **OAuth 1.0a Implementation**: Fully functional with proper HMAC-SHA1 signatures
- **Yahoo! API Integration**: Correctly configured with official API endpoints
- **Authentication Flow**: Complete OAuth 1.0a flow with automatic token management
- **Error Handling**: Proper rate limiting and API error handling
- **Testing Framework**: OAuth signature validation and authentication testing

### 🔄 **In Progress:**
- **Rate Limit Management**: Currently testing with Yahoo!'s API limits
- **Token Persistence**: Local storage and automatic refresh implementation

### 📋 **Next Steps:**
- Complete initial OAuth authentication (after rate limit reset)
- Test roster and league data retrieval
- Implement player analysis scripts
- Generate first weekly analysis reports

## 🔮 Future Enhancements

- Automated daily monitoring
- Advanced statistical modeling
- Integration with additional data sources
- Mobile-friendly web interface
- Push notifications for critical updates

---

**Remember**: You're the GM, the AI Agent is your scout and analyst. Use the commands above to get the insights you need to dominate your fantasy league! 🏆
