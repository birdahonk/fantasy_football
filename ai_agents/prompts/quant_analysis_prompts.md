# Quant AI Agent - Analysis Prompts

## 📊 **Post-Game Analysis Prompt Templates**

### **1. Individual Player Performance Analysis**

```
Analyze the performance of [PLAYER_NAME] from [TEAM] in Week [WEEK_NUMBER]:

**Performance Data:**
- Projected Fantasy Points: [PROJECTED_POINTS]
- Actual Fantasy Points: [ACTUAL_POINTS]
- Performance Difference: [DIFFERENCE]
- Performance Percentage: [PERCENTAGE]%

**Context:**
- Position: [POSITION]
- Opponent: [OPPONENT]
- Game Situation: [GAME_CONTEXT]
- Recent Performance: [RECENT_TRENDS]

**Analysis Requirements:**
1. Evaluate performance accuracy vs. projection
2. Identify key factors that influenced performance
3. Assess consistency and reliability
4. Provide start/sit recommendation for next week
5. Rate confidence level in recommendation (High/Medium/Low)

**Output Format:**
- Performance Assessment: [Summary of performance]
- Key Factors: [What influenced the performance]
- Consistency Rating: [Reliability assessment]
- Recommendation: [Start/Sit/Hold with reasoning]
- Confidence Level: [High/Medium/Low]
- Next Week Outlook: [What to expect]
```

### **2. Roster Performance Analysis**

```
Analyze the overall performance of [ROSTER_TYPE] in Week [WEEK_NUMBER]:

**Roster Performance Data:**
- Total Projected Points: [TOTAL_PROJECTED]
- Total Actual Points: [TOTAL_ACTUAL]
- Performance Difference: [TOTAL_DIFFERENCE]
- Performance Percentage: [TOTAL_PERCENTAGE]%

**Player Breakdown:**
[LIST_OF_PLAYERS_WITH_PERFORMANCE_DATA]

**Analysis Requirements:**
1. Evaluate overall roster performance vs. projections
2. Identify top over-performers and under-performers
3. Assess roster balance and depth
4. Provide strategic recommendations for improvement
5. Identify potential roster changes needed

**Output Format:**
- Overall Performance: [Summary of roster performance]
- Top Performers: [List of over-performers with details]
- Under Performers: [List of under-performers with details]
- Roster Assessment: [Balance and depth evaluation]
- Strategic Recommendations: [Specific actions to take]
- Priority Changes: [Most important roster adjustments]
```

### **3. Matchup Analysis (My Team vs. Opponent)**

```
Analyze the head-to-head matchup between my team and [OPPONENT_TEAM] in Week [WEEK_NUMBER]:

**My Team Performance:**
- Total Points: [MY_TOTAL_POINTS]
- Performance vs. Projection: [MY_PERFORMANCE_PERCENTAGE]%
- Key Performers: [MY_TOP_PLAYERS]

**Opponent Team Performance:**
- Total Points: [OPPONENT_TOTAL_POINTS]
- Performance vs. Projection: [OPPONENT_PERFORMANCE_PERCENTAGE]%
- Key Performers: [OPPONENT_TOP_PLAYERS]

**Matchup Context:**
- Point Difference: [POINT_DIFFERENCE]
- Performance Gap: [PERFORMANCE_GAP]%
- Winner: [WINNER]

**Analysis Requirements:**
1. Compare overall team performance
2. Analyze head-to-head player matchups
3. Identify key factors that determined the outcome
4. Assess strategic advantages/disadvantages
5. Provide lessons learned for future matchups

**Output Format:**
- Matchup Summary: [Overall comparison and outcome]
- Key Matchups: [Head-to-head player analysis]
- Deciding Factors: [What determined the outcome]
- Strategic Insights: [Lessons learned and insights]
- Future Considerations: [What to apply going forward]
```

### **4. Waiver Wire Analysis**

```
Analyze available players for potential waiver wire pickups based on Week [WEEK_NUMBER] performance:

**Available Players Performance Data:**
[LIST_OF_AVAILABLE_PLAYERS_WITH_PERFORMANCE_DATA]

**Current Roster Needs:**
- Weak Positions: [POSITIONS_NEEDING_IMPROVEMENT]
- Drop Candidates: [PLAYERS_TO_CONSIDER_DROPPING]
- Priority Needs: [MOST_IMPORTANT_POSITIONS]

**Analysis Requirements:**
1. Identify top-performing available players
2. Assess fit with current roster needs
3. Evaluate pickup priority and urgency
4. Consider long-term vs. short-term value
5. Provide specific waiver wire recommendations

**Output Format:**
- Top Targets: [List of recommended pickups with priority]
- Fit Analysis: [How players fit current roster needs]
- Pickup Priority: [Urgency and importance ranking]
- Drop Candidates: [Players to consider dropping]
- Long-term Value: [Sustained value assessment]
- Action Items: [Specific waiver wire moves to make]
```

### **5. Trend Analysis & Future Outlook**

```
Analyze performance trends and provide future outlook based on Week [WEEK_NUMBER] data:

**Historical Performance Data:**
[WEEKLY_PERFORMANCE_DATA_FOR_PLAYERS]

**Current Trends:**
- Performance Patterns: [IDENTIFIED_PATTERNS]
- Consistency Metrics: [RELIABILITY_INDICATORS]
- Usage Trends: [OPPORTUNITY_PATTERNS]

**Analysis Requirements:**
1. Identify performance trends and patterns
2. Assess consistency and reliability
3. Evaluate usage and opportunity trends
4. Predict future performance outlook
5. Provide strategic recommendations based on trends

**Output Format:**
- Trend Analysis: [Key patterns and trends identified]
- Consistency Assessment: [Reliability evaluation]
- Usage Analysis: [Opportunity and usage patterns]
- Future Outlook: [Performance predictions]
- Strategic Implications: [How trends affect strategy]
- Action Recommendations: [Specific actions based on trends]
```

## 🎯 **Specialized Analysis Prompts**

### **6. Injury Impact Analysis**

```
Analyze the impact of injuries on performance in Week [WEEK_NUMBER]:

**Injury Data:**
[INJURY_INFORMATION_AND_IMPACT_DATA]

**Analysis Requirements:**
1. Assess impact of injuries on affected players
2. Evaluate opportunity for backup players
3. Identify potential waiver wire targets
4. Provide injury management recommendations
5. Assess long-term implications

**Output Format:**
- Injury Impact: [How injuries affected performance]
- Opportunity Analysis: [Backup player opportunities]
- Waiver Targets: [Injury-related pickup recommendations]
- Management Strategy: [How to handle injured players]
- Long-term Outlook: [Recovery and future implications]
```

### **7. Position Group Analysis**

```
Analyze [POSITION_GROUP] performance in Week [WEEK_NUMBER]:

**Position Group Data:**
[POSITION_SPECIFIC_PERFORMANCE_DATA]

**Analysis Requirements:**
1. Evaluate overall position group performance
2. Compare individual players within the group
3. Assess depth and reliability
4. Identify improvement opportunities
5. Provide position-specific recommendations

**Output Format:**
- Group Performance: [Overall position group assessment]
- Individual Analysis: [Player-by-player breakdown]
- Depth Assessment: [Reliability and depth evaluation]
- Improvement Areas: [Where the group needs improvement]
- Recommendations: [Specific actions for the position group]
```

## 📋 **Prompt Usage Guidelines**

### **Data Integration**
- Always include relevant performance metrics
- Provide context for analysis (matchup, situation, etc.)
- Include both projected and actual performance data
- Consider multiple data sources when available

### **Analysis Depth**
- Provide both quantitative and qualitative analysis
- Include specific examples and evidence
- Consider multiple scenarios and outcomes
- Balance short-term and long-term perspectives

### **Recommendation Quality**
- Make specific, actionable recommendations
- Provide clear reasoning for each recommendation
- Include confidence levels and risk assessments
- Consider implementation feasibility

### **Output Consistency**
- Use consistent formatting and structure
- Include all required analysis components
- Maintain professional tone and clarity
- Provide comprehensive but concise analysis

---

**Note**: These prompts serve as templates for Quant's analysis. The agent should adapt and customize these prompts based on specific analysis requirements and available data while maintaining consistency in approach and output quality.
