# Yahoo Fantasy Football AI Assistant - Product Requirements Document

## Project Overview

**Product Name:** Fantasy Football AI Assistant  
**User:** Haven (single user, personal application)  
**Purpose:** AI-powered fantasy football optimization tool for Yahoo Fantasy Football platform

## Core Problem Statement

Haven needs an intelligent assistant to optimize his Yahoo Fantasy Football roster throughout the season by:
- Monitoring roster health and available players automatically
- Analyzing opponent matchups before games
- Providing AI-powered recommendations with justification
- Executing approved roster changes via API
- Tracking performance for season-long improvement

## Technical Architecture (Simple, Personal Scale)

### Core Components
1. **Vercel Web Application** (Built with Claude Code)
   - Responsive web interface
   - AI chatbot for interaction and approvals
   - Manual trigger buttons for analysis
   - Dashboard for roster/opponent viewing

2. **n8n Workflows** 
   - Scheduled monitoring tasks
   - Webhook endpoints for manual triggers
   - Yahoo API integrations
   - AI API orchestration

3. **Supabase Database**
   - User data and roster history
   - Analysis results and recommendations
   - Conversation state for chatbot

4. **External APIs**
   - Yahoo Fantasy Sports API (primary data source)
   - OpenAI API (primary AI analysis)
   - Anthropic API (fallback/additional insights)
   - News APIs for player updates

## MVP Phase - Core Functionality

### MVP Goal: Get Live Yahoo Fantasy Data Working with Basic AI Analysis

#### MVP Features:
1. **Yahoo API Integration**
   - Authenticate with Yahoo Fantasy Sports API
   - Fetch current roster data
   - Display roster in web interface

2. **Basic AI Chat Interface**
   - Simple chatbot using OpenAI/Anthropic APIs
   - Answer questions about current roster
   - Provide basic player analysis

3. **Manual Analysis Triggers**
   - "Analyze Roster" button
   - "Check Available Players" button
   - Results displayed in web interface

4. **Simple Database Storage**
   - Store roster snapshots
   - Track analysis results
   - Basic user preferences

#### MVP Success Criteria:
- Successfully connects to Yahoo Fantasy API
- Displays live roster data in web interface
- AI chatbot provides meaningful roster analysis
- Data persists between sessions in Supabase

## Post-MVP Enhancements (Phase 2+)

### Advanced Features:
1. **Automated Scheduling**
   - Daily roster health checks
   - Pre-game opponent analysis
   - Waiver wire monitoring
   - Post-game performance tracking

2. **Intelligent Recommendations**
   - Proactive optimization suggestions
   - News-based injury alerts
   - Matchup-based lineup changes
   - Historical performance analysis

3. **Enhanced UI/UX**
   - Dashboard with analytics
   - Mobile-responsive design
   - Notification system
   - Historical trends visualization

## User Journey & Workflow

### Primary Use Cases:

#### 1. Daily Roster Check
- n8n workflow runs daily morning check
- AI analyzes roster for issues (injuries, byes, etc.)
- Results stored in database
- Haven views recommendations on web app
- Chat with AI about specific concerns
- Approve/execute changes through chat interface

#### 2. Pre-Game Optimization
- 2 days before games: Enhanced monitoring begins
- Opponent roster analysis triggered automatically
- AI provides matchup insights and recommendations
- Haven reviews through web interface and chat
- Manual triggers available for updated analysis
- Final approval and execution of roster changes

#### 3. Waiver Wire Management
- Tuesday monitoring for available players
- AI compares available players to current roster
- Recommendations with add/drop suggestions
- Haven discusses options with AI chatbot
- Approved changes executed via Yahoo API

## Database Schema (Supabase)

### Core Tables:

```sql
-- User configuration and preferences
CREATE TABLE user_config (
    id SERIAL PRIMARY KEY,
    yahoo_league_id VARCHAR(50),
    yahoo_team_id VARCHAR(50),
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Current and historical roster data
CREATE TABLE roster_snapshots (
    id SERIAL PRIMARY KEY,
    week INTEGER,
    player_data JSONB,
    snapshot_date TIMESTAMP DEFAULT NOW()
);

-- AI analysis results and recommendations
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR(50), -- 'roster_check', 'opponent_analysis', 'waiver_suggestion'
    input_data JSONB,
    ai_response TEXT,
    recommendations JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'executed', 'rejected'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat conversation history
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    message_type VARCHAR(20), -- 'user', 'ai'
    content TEXT,
    context_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## Manual Setup Instructions for Haven

### 1. Yahoo Fantasy Sports API Setup

1. **Create Yahoo Developer Account**
   - Go to https://developer.yahoo.com/apps/create/
   - Sign in with your Yahoo account
   - Click "Create an App"

2. **Configure Yahoo App**
   - Application Name: "Haven's Fantasy Assistant"
   - Description: "Personal fantasy football optimization tool"
   - Home Page URL: `https://your-app.vercel.app` (will get this after Vercel deployment)
   - Redirect URI: `https://your-app.vercel.app/api/auth/callback`
   - API Permissions: Select "Fantasy Sports" with "Read/Write" access
   - Click "Create App"

3. **Save Credentials**
   - Copy "Consumer Key" (Client ID)
   - Copy "Consumer Secret" (Client Secret)
   - Store these securely - you'll need them for environment variables

### 2. Supabase Database Setup

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Sign up/login and click "New Project"
   - Project Name: "fantasy-football-db"
   - Database Password: Generate strong password and save it
   - Region: Choose closest to your location
   - Wait for project creation (2-3 minutes)

2. **Get Database Credentials**
   - Go to Project Settings > API
   - Copy "Project URL"
   - Copy "anon public" API key
   - Copy "service_role secret" API key
   - Go to Settings > Database
   - Copy connection string

3. **Initialize Database Tables**
   - Go to SQL Editor in Supabase
   - Run the SQL schema provided above
   - Verify tables are created successfully

### 3. AI API Keys Setup

1. **OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Sign in and click "Create new secret key"
   - Name: "Fantasy Football Assistant"
   - Copy and save the API key securely

2. **Anthropic API Key**
   - Go to https://console.anthropic.com/
   - Sign in and go to "API Keys"
   - Click "Create Key"
   - Name: "Fantasy Football Assistant"
   - Copy and save the API key securely

### 4. n8n Setup

1. **Choose n8n Deployment**
   - **Option A (Recommended):** n8n Cloud at https://app.n8n.io
     - Sign up for account
     - Start with free tier
     - Upgrade to Starter plan ($20/month) when needed
   
   - **Option B:** Self-hosted on DigitalOcean
     - Create DigitalOcean droplet ($5/month)
     - Follow n8n self-hosting guide
     - More technical but cheaper long-term

2. **Initial n8n Configuration**
   - Create new workflow
   - Test connection to external services
   - Set up webhook URLs (format: `https://your-n8n-instance.app.n8n.cloud/webhook/test`)

## Environment Variables Configuration

### Vercel Environment Variables:
```bash
# Yahoo Fantasy API
YAHOO_CLIENT_ID=your_consumer_key_here
YAHOO_CLIENT_SECRET=your_consumer_secret_here
YAHOO_REDIRECT_URI=https://your-app.vercel.app/api/auth/callback

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# AI APIs
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# n8n Integration
N8N_WEBHOOK_BASE_URL=https://your-n8n-instance.app.n8n.cloud/webhook
N8N_API_KEY=your_n8n_api_key_here

# App Configuration
NEXTAUTH_SECRET=your_random_secret_here
NEXTAUTH_URL=https://your-app.vercel.app
```

## Development Approach for Claude Code

### Phase 1: MVP Development

#### Step 1: Project Setup
- Initialize Next.js project with TypeScript
- Set up Supabase client configuration
- Configure environment variables
- Install required dependencies

#### Step 2: Yahoo API Integration
- Implement OAuth 2.0 flow for Yahoo Fantasy API
- Create API routes for fetching roster data
- Test with live Yahoo Fantasy data
- Handle authentication and token refresh

#### Step 3: Basic Web Interface
- Create roster display page
- Add simple navigation
- Implement responsive design
- Test with live data

#### Step 4: AI Chat Integration
- Set up OpenAI API client
- Create chat interface component
- Implement basic roster analysis prompts
- Add conversation persistence

#### Step 5: Database Integration
- Implement Supabase database operations
- Store roster snapshots
- Persist chat history
- Test data persistence

### Phase 2: n8n Workflows

#### Step 1: Basic Webhook Setup
- Create webhook endpoints in Vercel app
- Set up first n8n workflow with webhook trigger
- Test communication between systems
- Implement error handling

#### Step 2: Scheduled Monitoring
- Create daily roster check workflow
- Implement Yahoo API calls from n8n
- Store results in Supabase
- Test scheduled execution

### Phase 3: Advanced Features
- Opponent analysis workflows
- News monitoring integration
- Advanced AI analysis
- Performance tracking

## Success Metrics

### MVP Success:
- Successfully authenticate with Yahoo Fantasy API
- Display live roster data in web interface
- AI chatbot responds meaningfully to roster questions
- Data persists correctly in Supabase database

### Full Application Success:
- Automated daily roster monitoring working reliably
- AI provides actionable recommendations with >80% relevance
- Roster changes executed successfully through Yahoo API
- Season-long performance tracking and insights

## Risk Mitigation

### Technical Risks:
- **Yahoo API Rate Limits:** Implement caching and request throttling
- **API Authentication:** Robust token refresh and error handling
- **Data Consistency:** Transaction handling between systems
- **AI API Costs:** Usage monitoring and budget alerts

### Operational Risks:
- **Service Downtime:** Graceful error handling and retry logic
- **Data Loss:** Regular backups of critical data
- **API Changes:** Version monitoring and update procedures

## Cost Structure

### Monthly Operating Costs:
- **Vercel:** Free tier (sufficient for personal use)
- **Supabase:** Free tier (500MB database limit)
- **n8n:** $20/month (cloud) or $5/month (self-hosted)
- **OpenAI API:** ~$5-15/month (estimated usage)
- **Anthropic API:** ~$5-10/month (estimated usage)
- **Total:** $35-50/month

### One-Time Setup:
- Domain name (optional): $10-15/year
- SSL certificate: Free (included with Vercel)

## Conclusion

This PRD provides a complete roadmap for building a personal Yahoo Fantasy Football AI assistant. The MVP-first approach ensures core functionality works reliably before adding advanced features. The hybrid architecture leverages each platform's strengths while maintaining simplicity appropriate for single-user personal use.

The step-by-step manual setup instructions ensure Haven can configure all external services correctly. The development approach guides Claude Code through systematic implementation, building and testing each component incrementally.