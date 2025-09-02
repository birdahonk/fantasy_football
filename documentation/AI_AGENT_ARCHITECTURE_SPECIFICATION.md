# AI Agent Architecture Specification

## Overview

This document defines the architecture and specifications for the Fantasy Football AI Agent system. The system is designed as a personal tool for comprehensive fantasy football analysis and roster management, with a focus on simplicity, safety, and expert-level recommendations.

**Last Updated**: September 1, 2025  
**Version**: 1.0  
**Status**: Specification Complete - Ready for Implementation

---

## 🎯 **SYSTEM ARCHITECTURE**

### **Core Philosophy**
- **Simplicity First**: Avoid over-engineering for personal use case
- **Safety by Design**: Approval workflows for all roster changes
- **Expert Analysis**: AI-powered insights superior to manual analysis
- **Multi-Model Support**: Leverage different AI models for comprehensive analysis
- **Conversation Memory**: Persistent dialogue for iterative refinement

### **Agent Hierarchy**
```
General Manager (Orchestrator)
├── Analyst Agent (Analysis & Recommendations)
├── Coach Agent (Position Changes)
└── Scout Agent (Add/Drop Transactions)
```

---

## 🤖 **AGENT SPECIFICATIONS**

### **1. General Manager Agent**
**Role**: Primary interface and orchestrator  
**Capabilities**:
- Interprets user requests and routes to appropriate sub-agents
- Coordinates multi-model analysis and consolidates recommendations
- Manages conversation flow and context
- Provides unified interface for all fantasy football operations

**Tools**: None (orchestration only)  
**Interaction**: Primary chat interface (future web app)

### **2. Analyst Agent** ⭐ **PRIORITY 1**
**Role**: Comprehensive roster analysis and recommendations  
**Capabilities**:
- Triggers all data collection scripts automatically
- Analyzes roster health, matchups, and trends
- Researches current NFL news and injury reports
- Provides detailed analysis with actionable recommendations
- Saves analysis reports with timestamps and model identification

**Tools**:
- `analyst_tools.py`: Data collection, file reading, web research
- Data collection script orchestrator
- Analysis report generator

**Interaction**: Direct conversation or through General Manager

### **3. Coach Agent** (Future)
**Role**: Roster position changes only  
**Capabilities**:
- Changes player positions (bench ↔ starting lineup)
- Validates position changes via API responses
- Seeks approval before making changes

**Tools**:
- `coach_tools.py`: Position change utility script
- Yahoo API roster management

**Safety**: Approval required for all changes

### **4. Scout Agent** (Future)
**Role**: Add/drop transactions only  
**Capabilities**:
- Executes add/drop transactions
- Validates transactions via API responses
- Seeks approval before making changes

**Tools**:
- `scout_tools.py`: Add/drop transaction utility script
- Yahoo API transaction management

**Safety**: Approval required for all transactions

---

## 🛠️ **TECHNICAL IMPLEMENTATION**

### **Core Components**

#### **1. Agent Framework**
- **Single Python script** per agent (no complex frameworks)
- **Direct AI API calls** (OpenAI GPT-4, Anthropic Claude)
- **Simple conversation memory** (JSON message history)
- **Tool integration** via function calls

#### **2. Multi-Model Support**
- **Model Selection**: User chooses AI provider at conversation start
- **Analysis Comparison**: Compare recommendations across models
- **Consolidated Reports**: General Manager can synthesize multiple analyses
- **Model Identification**: All reports tagged with model used

#### **3. Data Integration**
- **Automatic Collection**: Analyst triggers all 9 data collection scripts
- **Timestamp Validation**: Ensures data is from current game week
- **File Versioning**: Uses most recent timestamped files
- **Pacific Time Zone**: Critical for NFL scheduling accuracy

#### **4. Conversation Memory**
- **Persistent Storage**: JSON file with message history
- **Session Management**: Continue conversations across runs
- **Context Preservation**: Maintains analysis context and refinements

### **File Structure**
```
ai_agents/
├── analyst_agent.py          # Main Analyst Agent script
├── analyst_tools.py          # Analyst-specific tools
├── conversation_memory.py    # Memory management
├── config.py                 # API keys and configuration
├── model_manager.py          # Multi-model support
└── reports/
    └── analysis_reports/     # Saved analysis reports
```

---

## 📊 **ANALYST AGENT SPECIFICATIONS**

### **Core Workflow**
1. **Auto-Data Collection**: Triggers all 9 data collection scripts
2. **Data Validation**: Verifies timestamps and game week relevance
3. **Comprehensive Analysis**: Roster health, matchups, trends, news
4. **Recommendation Generation**: Clear, actionable recommendations
5. **Report Generation**: Detailed analysis with concise action items

### **Analysis Components**

#### **Roster Analysis**
- **Starting Lineup Optimization**: Best players in starting positions
- **Bench Depth**: Quality of backup players
- **Positional Strengths/Weaknesses**: Identify roster gaps
- **Injury Impact**: Current injuries and their effects
- **Bye Week Planning**: Schedule conflicts and preparation

#### **Matchup Analysis**
- **Weekly Projections**: Player performance expectations
- **Opponent Analysis**: Defensive strengths/weaknesses
- **Weather/Context**: External factors affecting performance
- **Start/Sit Decisions**: Clear recommendations with justifications

#### **Free Agent Analysis**
- **Available Players**: Top targets from free agent pool
- **Add/Drop Candidates**: Specific players to acquire/drop
- **Waiver Wire**: Priority order for acquisitions
- **Trending Players**: Market intelligence and timing

#### **News & Research Integration**
- **Injury Reports**: Latest player health updates
- **Team News**: Coaching changes, depth chart updates
- **Market Trends**: Player values and availability
- **Expert Consensus**: Industry analysis and projections

### **Recommendation Format**

#### **Detailed Analysis Section**
- **Comprehensive paragraph** explaining each recommendation
- **Data-driven justifications** with specific metrics
- **Context and reasoning** for each suggested action
- **Risk assessment** and alternative options

#### **Action Items Section**
```
IMMEDIATE MOVES (Before Week X)

DROP → ADD
Player A (Position) → Player B (Position)
    - Brief justification for the move

OPTIONAL DEPTH MOVES
- Secondary recommendations with lower priority

DO NOT DROP
- Players to protect with reasoning

PRIORITY ORDER
1. Player B (highest priority)
2. Player C (second priority)
3. Player D (third priority)

Execute moves #1-3 immediately. [Brief summary of impact]
```

### **Report Generation**
- **Timestamped Filename**: `YYYYMMDD_HHMMSS_analysis_report_{model}_{topic}.md`
- **Model Identification**: Clear indication of AI model used
- **Data Sources**: List of all files and resources used
- **Analysis Summary**: Key findings and recommendations
- **Full Conversation**: Complete dialogue for reference

---

## 🔧 **TOOL SPECIFICATIONS**

### **analyst_tools.py Functions**

#### **Data Collection Tools**
```python
def collect_all_data():
    """Trigger all 9 data collection scripts"""
    # Returns: status, file_paths, execution_time

def validate_data_freshness():
    """Check if data is from current game week"""
    # Returns: is_fresh, game_week, data_age

def get_latest_files():
    """Get most recent timestamped files"""
    # Returns: file_paths, timestamps
```

#### **Analysis Tools**
```python
def analyze_roster():
    """Comprehensive roster analysis"""
    # Returns: roster_health, strengths, weaknesses

def analyze_matchups():
    """Weekly matchup analysis"""
    # Returns: projections, start_sit, recommendations

def analyze_free_agents():
    """Available player analysis"""
    # Returns: top_targets, add_drop_candidates
```

#### **Research Tools**
```python
def web_research(topic):
    """Current NFL news and research"""
    # Returns: relevant_articles, injury_reports, trends

def get_expert_consensus():
    """Industry analysis and projections"""
    # Returns: expert_rankings, consensus_picks
```

#### **Report Tools**
```python
def generate_analysis_report(conversation, model, topic):
    """Create comprehensive analysis report"""
    # Returns: report_content, file_path

def save_report(report_content, filename):
    """Save report to outputs directory"""
    # Returns: success_status, file_path
```

---

## 🎯 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Analyst Agent Foundation** ⭐ **IMMEDIATE**
1. **Core Agent Framework**
   - Create `analyst_agent.py` with conversation loop
   - Implement multi-model support (OpenAI, Anthropic)
   - Add conversation memory management
   - Create configuration system

2. **Tool Integration**
   - Build `analyst_tools.py` with all required functions
   - Implement data collection orchestrator
   - Add data validation and freshness checks
   - Create analysis report generator

3. **Analysis Engine**
   - Implement comprehensive roster analysis
   - Add matchup and free agent analysis
   - Integrate web research capabilities
   - Create recommendation formatting system

4. **Testing & Validation**
   - Test with real data collection scripts
   - Validate analysis quality and accuracy
   - Test multi-model comparison functionality
   - Verify report generation and saving

### **Phase 2: Enhanced Features** (Future)
1. **General Manager Orchestrator**
2. **Coach Agent** (Position Changes)
3. **Scout Agent** (Add/Drop Transactions)
4. **Web Interface Integration**

---

## 🔒 **SAFETY & VALIDATION**

### **Data Validation**
- **Timestamp Verification**: Ensure data is from current game week
- **File Integrity**: Validate data collection script outputs
- **API Response Validation**: Check all API responses for errors
- **Pacific Time Zone**: Accurate time calculations for NFL scheduling

### **Analysis Validation**
- **Source Attribution**: All data sources clearly identified
- **Model Identification**: Clear indication of AI model used
- **Recommendation Justification**: Every recommendation backed by data
- **Risk Assessment**: Potential downsides of each recommendation

### **Report Validation**
- **Completeness Check**: Ensure all analysis components included
- **Format Validation**: Verify recommendation format compliance
- **File Naming**: Consistent timestamp and model identification
- **Content Review**: Human-readable and actionable content

---

## 📋 **SUCCESS CRITERIA**

### **Analyst Agent Success Metrics**
1. **Data Integration**: Successfully triggers and validates all 9 data collection scripts
2. **Analysis Quality**: Provides expert-level insights superior to manual analysis
3. **Recommendation Clarity**: Clear, actionable recommendations with justifications
4. **Multi-Model Support**: Seamless switching between AI providers
5. **Report Generation**: Comprehensive, timestamped analysis reports
6. **Conversation Memory**: Persistent dialogue across sessions
7. **Web Research**: Current NFL news and injury report integration

### **User Experience Goals**
1. **Simplicity**: Easy to use, no complex setup required
2. **Expertise**: Analysis quality exceeds manual fantasy football management
3. **Efficiency**: Faster than manual research and analysis
4. **Transparency**: Clear data sources and reasoning for all recommendations
5. **Flexibility**: Support for both terminal and chat-based interaction

---

## 🚀 **NEXT STEPS**

1. **Create Implementation Plan**: Detailed development roadmap
2. **Build Analyst Agent**: Core functionality and tools
3. **Test & Validate**: Comprehensive testing with real data
4. **Iterate & Improve**: Refine based on usage and feedback
5. **Extend to Other Agents**: Coach and Scout agents

---

**Status**: Specification Complete  
**Ready for**: Implementation Phase  
**Priority**: Analyst Agent Development
