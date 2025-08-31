# Fantasy Football Scripts

This directory contains all the Python scripts for the Fantasy Football optimization tool.

## 📁 Directory Structure

### `/oauth/` - OAuth Authentication
- **`oauth2_client.py`** - Main OAuth 2.0 client for Yahoo Fantasy Sports API
- **`exchange_oauth2_code.py`** - Exchange authorization codes for access tokens
- **`get_oauth2_url.py`** - Generate fresh OAuth 2.0 authorization URLs

### `/core/` - Core Application Logic
- **`yahoo_connect.py`** - Legacy OAuth 1.0a client (kept for reference)
- **`xml_parser.py`** - Parse Yahoo's XML responses
- **`utils.py`** - Utility functions and helpers
- **`main_analyzer.py`** - Main analysis orchestration
- **`roster_analyzer.py`** - Roster analysis and optimization
- **`matchup_analyzer.py`** - Weekly matchup analysis
- **`free_agent_analyzer.py`** - Free agent evaluation and recommendations
- **`performance_tracker.py`** - Track team and player performance

### `/testing/` - Testing and Development
- **`test_oauth2.py`** - Test OAuth 2.0 authentication flow
- **`test_fantasy_api.py`** - Test Yahoo Fantasy Sports API calls
- **`single_oauth_test.py`** - Single OAuth 1.0a test (legacy)
- **`safe_api_test.py`** - Safe API connectivity test
- **`test_api_compliance.py`** - Test API compliance with Yahoo documentation
- **`test_minimal_api.py`** - Minimal API connectivity test
- **`test_oauth1.py`** - OAuth 1.0a testing (legacy)
- **`test_oauth_signature.py`** - OAuth signature validation (legacy)
- **`test_multiple_scopes.py`** - Test different OAuth scopes
- **`simple_scope_test.py`** - Simple scope testing
- **`debug_yahoo_auth.py`** - Debug Yahoo authentication issues
- **`simple_test.py`** - Simple connection testing
- **`test_yahoo_connection.py`** - Test Yahoo connection
- **`test_setup.py`** - Test overall setup

### `/config/` - Configuration and Tokens
- **`yahoo_oauth2_tokens.json`** - OAuth 2.0 access and refresh tokens

### `/analysis/` - Analysis Output
- **`weeklies/`** - Weekly analysis reports
- **`YYYYMMDD_HHMMSS_*`** - Timestamped analysis reports

## 🚀 Quick Start

### 1. OAuth 2.0 Authentication
```bash
cd scripts/oauth
python3 get_oauth2_url.py          # Get authorization URL
# Complete authentication in browser, then:
python3 exchange_oauth2_code.py    # Exchange code for tokens
```

### 2. Test API Connection
```bash
cd scripts/testing
python3 test_fantasy_api.py        # Verify OAuth 2.0 is working
```

### 3. Run Analysis
```bash
cd scripts/core
python3 main_analyzer.py           # Run full analysis
```

## 🔐 OAuth 2.0 Status

**✅ WORKING PERFECTLY!** 

- OAuth 2.0 authentication successful
- Access tokens received and stored
- API calls working (0.15s response time)
- No rate limiting issues
- Ready for production use

## 📝 Notes

- **OAuth 1.0a** is kept for reference but no longer used
- **OAuth 2.0** is the current authentication method
- All tokens are stored in `/config/` directory
- Analysis outputs go to `/analysis/` directory

## 🚀 Current Status

**✅ OAuth 2.0 Authentication Working Perfectly!**

- Authentication flow complete and tested
- Yahoo Fantasy Sports API responding in 0.15s
- No rate limiting issues
- Ready for core functionality development

## 🔄 Next Steps

1. **Core Development**: Implement roster analysis, player evaluation
2. **Data Retrieval**: Build team data, player stats, matchups
3. **AI Integration**: Integrate OpenAI/Anthropic APIs
4. **Web App**: Merge Flask web application from feature branch

## 📚 Related Documentation

- **Main Project**: See root `README.md` for complete project overview
- **OAuth 2.0 Guide**: See `documentation/OAUTH_2_0_IMPLEMENTATION.md`
- **Project Requirements**: See `documentation/pre-mvp-fantasy-football-prd.md`
