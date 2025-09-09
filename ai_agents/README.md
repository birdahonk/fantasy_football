# 🤖 AI Agents Directory

This directory contains AI agents for fantasy football analysis and management.

## 📁 **Directory Structure**

```
ai_agents/
├── prompts/                          # Agent prompt templates
│   ├── quant_system_prompt.md        # Quant agent system prompt
│   ├── quant_analysis_prompts.md     # Quant agent analysis prompts
│   └── quant_output_formatting.md    # Quant agent output formatting
├── quant_agent.py                    # Quant AI agent implementation
├── quant_token_validation.py         # Token usage validation script
├── sample_post_game_data.json        # Sample data for testing
└── README.md                         # This file
```

## 🤖 **Available Agents**

### **Quant Agent** - Post-Game Analysis Specialist
- **Role**: Post-game fantasy football analysis
- **Expertise**: Performance vs. projections analysis, strategic recommendations
- **Features**: Roster analysis, matchup comparison, waiver wire insights
- **Status**: ✅ **Ready for Testing**

## 📊 **Quant Agent Capabilities**

### **Core Analysis Functions**
1. **Performance vs. Projections Analysis**
   - Individual player performance comparison
   - Roster-level performance assessment
   - Over/under performer identification
   - Performance trend analysis

2. **Strategic Insights & Recommendations**
   - Start/sit decisions based on performance patterns
   - Waiver wire targets and drop candidates
   - Trade opportunities and roster optimization
   - Matchup strategy recommendations

3. **Data-Driven Decision Making**
   - Statistical analysis of performance metrics
   - Pattern recognition in player performance
   - Risk assessment for roster decisions
   - Long-term strategic planning

### **Analysis Types**
- **Individual Player Analysis** - Performance evaluation for specific players
- **Roster Performance Analysis** - Overall team performance assessment
- **Matchup Analysis** - Head-to-head team comparison
- **Waiver Wire Analysis** - Available players evaluation
- **Trend Analysis** - Performance patterns and future outlook
- **Injury Impact Analysis** - Injury effects on performance
- **Position Group Analysis** - Position-specific performance evaluation

## 🚀 **Usage**

### **Basic Usage**
```bash
# Run Quant agent analysis for Week 1
python3 ai_agents/quant_agent.py --week 1 --season 2025
```

### **Token Validation**
```bash
# Validate token usage with sample data
python3 ai_agents/quant_token_validation.py --test-data ai_agents/sample_post_game_data.json

# Generate validation report
python3 ai_agents/quant_token_validation.py --test-data ai_agents/sample_post_game_data.json --output validation_report.md
```

## 📝 **Prompt System**

### **System Prompt** (`quant_system_prompt.md`)
- **Agent Identity**: Defines Quant's role and personality
- **Analysis Framework**: Core methodology and approach
- **Communication Style**: Tone, voice, and response structure
- **Quality Guidelines**: Standards for analysis and recommendations

### **Analysis Prompts** (`quant_analysis_prompts.md`)
- **Individual Player Analysis**: Performance evaluation templates
- **Roster Analysis**: Team performance assessment templates
- **Matchup Analysis**: Head-to-head comparison templates
- **Waiver Wire Analysis**: Available players evaluation templates
- **Trend Analysis**: Performance pattern analysis templates

### **Output Formatting** (`quant_output_formatting.md`)
- **Report Structure**: Standard markdown report format
- **Data Presentation**: Tables, charts, and formatting standards
- **Recommendation Format**: Action items and strategic advice format
- **Quality Assurance**: Content and formatting quality checklist

## 🔧 **Token Usage Validation**

### **Validation Process**
1. **Token Counting**: Count tokens for all prompt components
2. **Data Optimization**: Ensure data fits within 200k token limit
3. **Prompt Refinement**: Optimize prompts based on token usage
4. **Validation Testing**: Test with actual post-game data

### **Current Token Usage**
- **System Prompt**: 1,171 tokens
- **Analysis Prompts**: 1,672 tokens
- **Output Formatting**: 1,750 tokens
- **Sample Data**: 1,482 tokens
- **Total**: 6,075 tokens
- **Status**: ✅ **Within 200k token limit**

## 📊 **Output Structure**

### **Analysis Reports**
```
data_collection/outputs/analysis/post_game/2025/week_01/
├── 20250114_090000_wk01_quant_post_game_analysis.md
└── 20250114_090000_wk01_quant_post_game_analysis_raw.json
```

### **Report Sections**
1. **Executive Summary** - Key findings and priority actions
2. **Performance Analysis** - Detailed performance metrics
3. **Strategic Recommendations** - Actionable advice
4. **Matchup Analysis** - Head-to-head comparison
5. **Waiver Wire Analysis** - Available players insights
6. **Summary** - Overall assessment and next steps

## 🧪 **Testing**

### **Manual Testing**
```bash
# Test with sample data
python3 ai_agents/quant_token_validation.py --test-data ai_agents/sample_post_game_data.json

# Test Quant agent
python3 ai_agents/quant_agent.py --week 1 --season 2025
```

### **Integration Testing**
- Test with actual post-game data
- Validate analysis quality
- Verify output formatting
- Check token usage limits

## 🔄 **Integration with Post-Game Analysis System**

### **Data Flow**
1. **Projection Collection** - Collect weekly projections (Thursday/Sunday/Monday)
2. **Data Processing** - Process projections vs. actual performance
3. **Quant Analysis** - Generate comprehensive analysis report
4. **Output Generation** - Create markdown and JSON outputs

### **Automation**
- **Thursday 2:00 PM**: Collect Thursday projections
- **Sunday 8:00 AM**: Collect Sunday projections
- **Monday 2:00 PM**: Collect Monday projections
- **Tuesday 9:00 AM**: Run Quant analysis

## 📈 **Performance Metrics**

### **Analysis Quality**
- **Quantitative Analysis**: Performance metrics and statistics
- **Qualitative Insights**: Strategic recommendations and insights
- **Actionable Recommendations**: Specific, implementable advice
- **Risk Assessment**: Potential risks and considerations

### **Output Quality**
- **Professional Formatting**: Clear, organized reports
- **Data Visualization**: Tables, charts, and visual elements
- **Priority Indicators**: High/medium/low priority recommendations
- **Confidence Levels**: High/medium/low confidence in recommendations

## 🚀 **Next Steps**

### **Phase 1: Prompt Testing** ✅
- [x] System prompt creation
- [x] Analysis prompts creation
- [x] Output formatting guidelines
- [x] Token usage validation

### **Phase 2: Agent Implementation** ✅
- [x] Quant agent implementation
- [x] Integration with data processing
- [x] Output generation
- [x] Error handling and logging

### **Phase 3: Testing & Validation** 🔄
- [ ] Manual testing with sample data
- [ ] Integration testing with actual data
- [ ] Analysis quality validation
- [ ] Performance optimization

### **Phase 4: Production Deployment** 📋
- [ ] Deploy to production environment
- [ ] Enable automation
- [ ] Monitor performance
- [ ] Continuous improvement

## 📚 **Documentation**

- **System Prompt**: `ai_agents/prompts/quant_system_prompt.md`
- **Analysis Prompts**: `ai_agents/prompts/quant_analysis_prompts.md`
- **Output Formatting**: `ai_agents/prompts/quant_output_formatting.md`
- **Token Validation**: `ai_agents/quant_token_validation.py`
- **Agent Implementation**: `ai_agents/quant_agent.py`

## ⚠️ **Important Notes**

### **Token Limits**
- Anthropic Opus 4.1: 200,000 tokens
- Current usage: ~6,075 tokens
- Safety buffer: 10,000 tokens
- Effective limit: 190,000 tokens

### **Data Requirements**
- Processed post-game data from `post_game_analysis_data_processor.py`
- Projection archive data from `tank01_weekly_projections_archive.py`
- Player stats data from Tank01 season stats scripts

### **Dependencies**
- Python 3.8+
- tiktoken for token counting
- pytz for timezone handling
- json for data processing
- pathlib for file management

---

**Status**: ✅ **Quant Agent Ready for Testing** - All components implemented and validated
