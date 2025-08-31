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
# Yahoo Fantasy API (OAuth 2.0)
YAHOO_CLIENT_ID=your_client_id_here
YAHOO_CLIENT_SECRET=your_client_secret_here
YAHOO_REDIRECT_URI=https://tools.birdahonk.com/fantasy/oauth/callback
YAHOO_SCOPES=fspt-w

# AI APIs
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# App Configuration
LOG_LEVEL=INFO
DATA_DIR=./analysis
```

### 3. Yahoo API Setup
Follow the detailed setup instructions in `documentation/pre-mvp-fantasy-football-prd.md`

**Important**: This application now uses **OAuth 2.0** (successfully implemented) for the Yahoo! Fantasy Sports API. See [OAuth 2.0 Implementation Guide](documentation/OAUTH_2_0_IMPLEMENTATION.md) for details.

**Authentication Flow**: 
- OAuth 2.0 setup (one-time, ~2 minutes)
- Automatic token refresh (hourly)
- No rate limiting issues
- Fast API response times (0.15s average)


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
├── README.md                    # Main project documentation
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (OAuth 2.0)
├── .gitignore                   # Git ignore rules
├── documentation/               # Comprehensive documentation
│   ├── OAUTH_2_0_IMPLEMENTATION.md  # OAuth 2.0 guide
│   ├── pre-mvp-fantasy-football-prd.md
│   └── context/
├── scripts/                     # All Python scripts (organized)
│   ├── oauth/                  # OAuth 2.0 authentication
│   ├── core/                   # Core application logic
│   ├── testing/                # Testing and development
│   ├── config/                 # Configuration and tokens
│   ├── logs/                   # API call logs
│   ├── analysis/               # Analysis output
│   └── README.md               # Scripts directory guide
├── web_app/                     # Flask web application (feature branch)
└── webserver_deploy/            # Server deployment files
```

## 🔧 Script Overview

### **OAuth 2.0 Authentication (Current)**
- **`scripts/oauth/oauth2_client.py`**: Main OAuth 2.0 client for Yahoo Fantasy Sports API
- **`scripts/oauth/exchange_oauth2_code.py`**: Exchange authorization codes for access tokens
- **`scripts/oauth/get_oauth2_url.py`**: Generate fresh OAuth 2.0 authorization URLs

### **Core Analysis Scripts**
- **`scripts/core/roster_analyzer.py`**: Roster health and performance analysis
- **`scripts/core/free_agent_analyzer.py`**: Free agent evaluation and transaction suggestions
- **`scripts/core/matchup_analyzer.py`**: Weekly matchup analysis and lineup optimization
- **`scripts/core/performance_tracker.py`**: Performance tracking and projection accuracy
- **`scripts/core/utils.py`**: Common utility functions and helpers

### **Legacy OAuth 1.0a (Reference Only)**
- **`scripts/core/yahoo_connect.py`**: Legacy OAuth 1.0a implementation (kept for reference)
- **`scripts/testing/single_oauth_test.py`**: OAuth 1.0a testing (legacy)
- **`scripts/testing/safe_api_test.py`**: Safe API connectivity test

### **Testing and Development**
- **`scripts/testing/test_oauth2.py`**: Test OAuth 2.0 authentication flow
- **`scripts/testing/test_fantasy_api.py`**: Test Yahoo Fantasy Sports API calls

## 🎮 How to Use

1. **Open Cursor** and navigate to this project
2. **Ask the AI Agent** to perform any analysis using the commands above
3. **Review the results** both in conversation and in generated markdown files
4. **Make decisions** based on AI recommendations
5. **Track progress** through organized weekly analysis files

## 🚨 Important Notes

- **OAuth 2.0 Implementation**: ✅ **WORKING PERFECTLY!** Yahoo Fantasy Sports API access achieved
- **No Rate Limiting**: OAuth 2.0 bypasses all previous OAuth 1.0a rate limiting issues
- **Authentication**: OAuth 2.0 tokens expire hourly - scripts handle automatic refresh
- **Data Freshness**: Always run "Update data" before major analysis
- **File Organization**: Reports are automatically organized by week and timestamp
- **Legacy OAuth 1.0a**: Kept for reference but no longer used

## 🆘 Troubleshooting

### Common Issues:
- **"Yahoo API Error"**: Check credentials and OAuth setup
- **"Script not found"**: Ensure all scripts are in the `scripts/` directory
- **"Permission denied"**: Check file permissions and Python environment
- **"API key invalid"**: Verify environment variables are set correctly

### Getting Help:
1. Check the logs in `scripts/logs/` directory
2. Verify your `.env` file configuration
3. Test individual scripts from command line
4. Ask the AI Agent for debugging help

## 🚀 Current Implementation Status

### ✅ **Completed & Working:**
- **OAuth 2.0 Implementation**: ✅ **BREAKTHROUGH ACHIEVED!** Working perfectly
- **Yahoo! API Integration**: ✅ Successfully authenticated and retrieving data
- **Authentication Flow**: ✅ OAuth 2.0 flow complete with access/refresh tokens
- **API Access**: ✅ Fantasy Sports API calls working (0.15s response time)
- **Token Management**: ✅ Automatic refresh and local storage
- **No Rate Limiting**: ✅ OAuth 2.0 bypasses all previous issues

### 🔄 **Ready for Development:**
- **Core Functionality**: Ready to implement roster analysis, player evaluation
- **Data Retrieval**: Ready to build team data, player stats, matchups
- **AI Integration**: Ready to integrate OpenAI/Anthropic APIs
- **Web App**: Ready to merge Flask web application

### 📋 **Next Steps:**
- Build core Fantasy Football analysis scripts
- Implement roster retrieval and analysis
- Create player evaluation and recommendation system
- Generate weekly analysis reports
- Merge web application for enhanced user experience

## 🔮 Future Enhancements

- Automated daily monitoring
- Advanced statistical modeling
- Integration with additional data sources
- Mobile-friendly web interface
- Push notifications for critical updates

---

**Remember**: You're the GM, the AI Agent is your scout and analyst. Use the commands above to get the insights you need to dominate your fantasy league! 🏆
