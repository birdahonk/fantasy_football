#!/usr/bin/env python3
"""
Fantasy Football Analyst Agent

A specialized AI agent for analyzing fantasy football rosters, matchups, and player recommendations.
Supports multiple LLM providers (OpenAI GPT-4, Anthropic Claude) with conversation memory.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import pytz
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, '.env'))

# Import our utilities
from data_collection.scripts.shared.file_utils import DataFileManager
from ai_agents.analyst_tools import AnalystTools
from ai_agents.prompt_manager import PromptManager
from ai_agents.optimized_player_profiles import OptimizedPlayerProfiles
from ai_agents.model_selector import ModelSelector
from ai_agents.comprehensive_data_processor import ComprehensiveDataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalystAgent:
    """
    Fantasy Football Analyst Agent
    
    Provides comprehensive analysis of fantasy football rosters, matchups, and player recommendations.
    Supports multiple LLM providers with conversation memory and data collection orchestration.
    """
    
    def __init__(self, model_provider: str = "anthropic", model_name: str = "claude-opus-4-1-20250805"):
        """
        Initialize the Analyst Agent
        
        Args:
            model_provider: "openai" or "anthropic" (default: "anthropic")
            model_name: Specific model name (default: "claude-opus-4-1-20250805")
        """
        self.model_provider = model_provider.lower()
        self.model_name = model_name
        self.file_manager = DataFileManager()
        self.tools = AnalystTools()
        self.prompt_manager = PromptManager()
        self.pacific_tz = pytz.timezone('US/Pacific')
        
        # Conversation memory
        self.conversation_history = []
        self.session_id = datetime.now(self.pacific_tz).strftime("%Y%m%d_%H%M%S")
        
        # Initialize LLM client
        self._init_llm_client()
        
        # System prompt for the analyst (loaded from external file)
        self.system_prompt = self.prompt_manager.get_system_prompt('analyst_agent')
        
        logger.info(f"Analyst Agent initialized with {self.model_provider} ({self.model_name})")
    
    def _init_llm_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.model_provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI()
                logger.info("OpenAI client initialized")
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        elif self.model_provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic()
                logger.info("Anthropic client initialized")
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def reload_system_prompt(self):
        """Reload the system prompt from the external file"""
        self.prompt_manager.clear_cache()
        self.system_prompt = self.prompt_manager.get_system_prompt('analyst_agent')
        logger.info("System prompt reloaded from external file")
    
    def analyze(self, user_prompt: str, collect_data: Optional[bool] = None) -> Dict[str, Any]:
        """
        Perform comprehensive fantasy football analysis
        
        Args:
            user_prompt: User's question or request
            collect_data: Whether to collect fresh data (None=ask user, True=collect, False=use existing)
            
        Returns:
            Dictionary with analysis results, recommendations, and metadata
        """
        logger.info(f"Starting analysis for prompt: {user_prompt[:100]}...")
        
        # Step 1: Determine data collection strategy
        data_collection_results = {}
        if collect_data is None:
            # Check if existing data is current and ask user
            data_freshness = self.tools.check_data_freshness()
            if data_freshness["is_current"]:
                print(f"📊 Found current data from {data_freshness['most_recent_file']}")
                print("Would you like to:")
                print("1. Use existing data (faster)")
                print("2. Collect fresh data (slower, but most current)")
                choice = input("Enter choice (1 or 2): ").strip()
                collect_data = choice == "2"
            else:
                print(f"⚠️  Existing data is {data_freshness['age_hours']:.1f} hours old")
                print("Would you like to:")
                print("1. Collect fresh data (recommended)")
                print("2. Use existing data anyway")
                choice = input("Enter choice (1 or 2): ").strip()
                collect_data = choice == "1"
        
        # Step 2: Collect fresh data if requested
        if collect_data:
            logger.info("Collecting fresh data from all APIs...")
            data_collection_results = self.tools.collect_all_data(tank01_players_limit=5)  # Default to 5 for now
        
        # Step 3: Analyze the most recent data
        logger.info("Analyzing most recent data...")
        analysis_data = self.tools.analyze_recent_data()
        
        # Step 3: Perform web research for current context
        logger.info("Performing web research...")
        web_research = self.tools.research_current_nfl_news()
        
        # Step 4: Generate analysis using LLM
        logger.info("Generating analysis with LLM...")
        analysis_prompt = self._build_analysis_prompt(user_prompt, analysis_data, web_research)
        
        llm_response = self._call_llm(analysis_prompt)
        
        # Step 5: Structure the response
        result = {
            "session_id": self.session_id,
            "timestamp": datetime.now(self.pacific_tz).isoformat(),
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "user_prompt": user_prompt,
            "data_collection": data_collection_results,
            "analysis_data": analysis_data,
            "web_research": web_research,
            "analysis": llm_response,
            "resources_used": self._extract_resources_used(analysis_data, web_research)
        }
        
        # Step 6: Save to conversation history
        self.conversation_history.append(result)
        
        logger.info("Analysis completed successfully")
        return result
    
    def analyze_with_optimized_profiles(self, user_prompt: str, player_limits: Optional[Dict[str, int]] = None, 
                                      collect_data: Optional[bool] = None, 
                                      model_selection: Optional[bool] = None) -> Dict[str, Any]:
        """
        Enhanced analysis using optimized player profiles with configurable limits
        
        Args:
            user_prompt: User's question or request
            player_limits: Custom player limits per position (default: 20 per position, 10 for DEF)
            collect_data: Whether to collect fresh data (None=ask user, True=collect, False=use existing)
            model_selection: Whether to show model selection menu (None=ask user, True=show, False=use default)
            
        Returns:
            Dictionary with analysis results, recommendations, and metadata
        """
        logger.info(f"Starting optimized analysis for prompt: {user_prompt[:100]}...")
        
        # Step 1: Model selection
        if model_selection is None:
            print("\n🤖 Model Selection")
            print("Would you like to:")
            print("1. Use default model (Claude Opus 4.1)")
            print("2. Choose from available models")
            choice = input("Enter choice (1 or 2): ").strip()
            model_selection = choice == "2"
        
        if model_selection:
            model_selector = ModelSelector()
            self.model_provider, self.model_name = model_selector.get_model_selection()
            logger.info(f"Selected model: {self.model_provider} - {self.model_name}")
        else:
            logger.info(f"Using default model: {self.model_provider} - {self.model_name}")
        
        # Step 2: Data collection strategy
        data_collection_results = {}
        if collect_data is None:
            data_freshness = self.tools.check_data_freshness()
            if data_freshness["is_current"]:
                print(f"\n📊 Found current data from {data_freshness['most_recent_file']}")
                print("Would you like to:")
                print("1. Use existing data (faster)")
                print("2. Collect fresh data (slower, but most current)")
                choice = input("Enter choice (1 or 2): ").strip()
                collect_data = choice == "2"
            else:
                print(f"\n⚠️  Existing data is {data_freshness['age_hours']:.1f} hours old")
                print("Would you like to:")
                print("1. Collect fresh data (recommended)")
                print("2. Use existing data anyway")
                choice = input("Enter choice (1 or 2): ").strip()
                collect_data = choice == "1"
        
        # Step 3: Collect fresh data if requested
        if collect_data:
            logger.info("Collecting fresh data from all APIs...")
            data_collection_results = self.tools.collect_all_data()
        
        # Step 4: Create optimized player profiles
        logger.info("Creating optimized player profiles...")
        profile_builder = OptimizedPlayerProfiles(player_limits)
        
        # Get token estimate
        token_estimate = profile_builder.get_token_estimate()
        print(f"\n📊 Token Usage Estimate:")
        print(f"   Total players: {token_estimate['total_players']}")
        print(f"   Estimated tokens: {token_estimate['estimated_total_tokens']:,}")
        print(f"   Within 200k limit: {'✅ Yes' if token_estimate['within_200k_limit'] else '❌ No'}")
        
        # Create optimized available players
        data_dir = "data_collection/outputs"
        optimized_data = profile_builder.create_optimized_available_players(data_dir)
        
        # Step 5: Analyze roster data (my team)
        logger.info("Analyzing roster data...")
        roster_analysis = self.tools.analyze_recent_data()
        
        # Step 6: Perform web research
        logger.info("Performing web research...")
        web_research = self.tools.research_current_nfl_news()
        
        # Step 7: Build enhanced analysis prompt
        analysis_prompt = self._build_optimized_analysis_prompt(
            user_prompt, optimized_data, roster_analysis, web_research
        )
        
        # Step 8: Generate analysis using LLM
        logger.info("Generating analysis with LLM...")
        llm_response = self._call_llm(analysis_prompt)
        
        # Step 9: Structure the response
        result = {
            "timestamp": datetime.now(self.pacific_tz).isoformat(),
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "user_prompt": user_prompt,
            "data_collection_results": data_collection_results,
            "optimized_data": optimized_data,
            "roster_analysis": roster_analysis,
            "web_research": web_research,
            "analysis": llm_response,  # Use 'analysis' key for consistency
            "analysis_type": "optimized_profiles",
            "data_summary": self._create_data_summary(optimized_data, roster_analysis, web_research)
        }
        
        # Step 10: Save the analysis report
        logger.info("Saving analysis report...")
        saved_files = self.save_analysis_report(result, "optimized_analysis")
        result["saved_files"] = saved_files
        
        # Step 11: Save optimized player data as separate markdown
        self._save_optimized_player_data_markdown(optimized_data, saved_files)
        
        return result
    
    def _build_optimized_analysis_prompt(self, user_prompt: str, optimized_data: Dict[str, Any], 
                                       roster_analysis: Dict[str, Any], web_research: Dict[str, Any]) -> str:
        """Build enhanced prompt using optimized player profiles"""
        season_context = optimized_data.get("season_context", {})
        nfl_season = season_context.get("nfl_season", "current")
        season_phase = season_context.get("season_phase", "Regular Season")
        
        # Extract only essential roster data to reduce tokens
        my_roster_summary = self._extract_roster_summary(roster_analysis)
        
        # Extract only essential web research to reduce tokens
        web_summary = self._extract_web_summary(web_research)
        
        # Create detailed data summary for the agent
        data_summary = self._create_data_summary(optimized_data, roster_analysis, web_research)
        
        prompt = f"""USER REQUEST: {user_prompt}

CRITICAL CONTEXT: This is the {nfl_season} NFL season ({season_phase}). Use ONLY the data provided below and current {nfl_season} season information. Do NOT use training data from previous seasons.

## DATA AVAILABILITY SUMMARY
- **My Roster Players**: {data_summary['my_roster_count']} players
- **Available Players**: {data_summary['available_players_count']} players
- **Web Research Items**: {data_summary['web_research_items']} news articles
- **Data Sources**: {', '.join(data_summary['data_sources'])}

## PLAYER DATA BREAKDOWN BY POSITION
{json.dumps(data_summary['player_data_breakdown'], indent=2)}

## MY CURRENT ROSTER ({data_summary['my_roster_count']} PLAYERS)
The user has a complete roster with the following players:
{json.dumps(my_roster_summary, indent=2)}

## AVAILABLE PLAYERS FOR ADD/DROP ANALYSIS
{optimized_data.get('total_players', 0)} top available players by position:
{json.dumps(optimized_data, indent=2)}

## CURRENT NFL NEWS & CONTEXT
{json.dumps(web_summary, indent=2)}

## DETAILED ANALYSIS INSTRUCTIONS

### 1. DATA UTILIZATION REQUIREMENTS
- **MUST** analyze each player's projected points from Tank01 data
- **MUST** follow and summarize news links provided in player data
- **MUST** consider depth chart positions from Sleeper data
- **MUST** cross-reference player IDs across all 3 APIs
- **MUST** use web research findings in your analysis

### 2. PLAYER ANALYSIS FRAMEWORK
For each roster player, analyze:
- **Projected Points**: Use tank01_data.projection.fantasyPoints (primary projection)
- **Alternative Projections**: Also check tank01_data.projection.fantasyPointsDefault for PPR/half-PPR
- **News Context**: Follow news links in tank01_data.news for latest updates
- **Depth Chart**: Check sleeper_data.depth_chart_position for role clarity
- **Injury Status**: Review injury_status across all APIs
- **Transaction Trends**: Consider tank01_data.transaction_trends for ownership changes

**IMPORTANT**: Tank01 provides fantasyPoints (standard) and fantasyPointsDefault (PPR variants). Use fantasyPoints as primary projection for analysis.

### 3. AVAILABLE PLAYERS EVALUATION
For each recommended add/drop:
- **Compare projected points** with current roster players
- **Analyze news links** for injury updates and role changes
- **Check depth chart position** for playing time expectations
- **Review transaction trends** for league-wide interest

### 4. WEB RESEARCH INTEGRATION
- **Summarize key findings** from the {data_summary['web_research_items']} news items
- **Connect news to specific players** in your recommendations
- **Use current NFL context** to inform lineup decisions

### 5. OPPONENT ANALYSIS (REQUIRED)
- **Identify current week opponent** from matchup data in league_context
- **Analyze opponent's key players** and their projected performance
- **Consider defensive matchups** for your players
- **Compare your projected points vs opponent's projected points**
- **Identify key matchup advantages/disadvantages**

### 6. ACTUAL POINTS INTEGRATION
- **Check if any games have been played** (Thursday games, etc.)
- **If actual points are available**, factor them into lineup decisions
- **Recommend lineup changes** based on actual performance vs projections

## REQUIRED OUTPUT FORMAT
1. **Data Visibility Confirmation**: Show what data you can see
2. **Web Research Summary**: Key findings from news articles and URLs accessed
3. **Resources Used**: List all news articles, URLs, and data sources you utilized
4. **Individual Player Summaries**: For EACH player on your roster, provide a summary paragraph based on:
   - Web research findings about that specific player
   - News links provided in their Tank01 data
   - Current injury status and role clarity
   - Recent performance trends and expectations
5. **Roster Analysis**: Detailed analysis of each position group
6. **Specific Recommendations**: Exact add/drop suggestions with reasoning
7. **News Integration**: How news links influenced your recommendations
8. **Projected Points Analysis**: Detailed comparison of fantasy projections from Tank01 data
9. **Matchup Analysis**: Analysis of your current week opponent and defensive matchups

## CRITICAL INSTRUCTIONS
- **MUST** use Tank01 projected points data (tank01_data.projection.fantasyPoints)
- **MUST** follow and summarize news links from player data (tank01_data.news)
- **MUST** identify and analyze your current week opponent
- **MUST** report all resources and data sources you used
- **MUST** show specific projected points comparisons
- **MUST** provide individual summary for each roster player based on web research and news
- **MUST** use Tank01 fantasy points for all projections (not Yahoo's 0 values)

Please provide a comprehensive analysis with specific recommendations for improving their existing roster."""
        
        return prompt
    
    def analyze_with_comprehensive_data(self, user_prompt: str, player_limits: Dict[str, int] = None, 
                                      collect_data: bool = False, model_selection: bool = True) -> Dict[str, Any]:
        """Analyze with comprehensive data including roster, opponent, and available players"""
        
        if player_limits is None:
            from config.player_limits import DEFAULT_PLAYER_LIMITS
            player_limits = DEFAULT_PLAYER_LIMITS
        
        logger.info("Starting comprehensive analysis...")
        
        # Initialize comprehensive data processor
        data_processor = ComprehensiveDataProcessor(
            data_dir=os.path.join(project_root, "data_collection", "outputs"),
            player_limits=player_limits
        )
        
        # Process all data
        comprehensive_data = data_processor.process_all_data()
        
        # Perform web research
        logger.info("Performing web research...")
        web_research = self.tools.research_current_nfl_news()
        
        # Build comprehensive prompt
        prompt = self._build_comprehensive_analysis_prompt(
            user_prompt, comprehensive_data, web_research
        )
        
        # Generate analysis with LLM
        logger.info("Generating analysis with LLM...")
        analysis = self._call_llm(prompt)
        
        # Save comprehensive reports
        saved_files = self._save_comprehensive_reports(
            comprehensive_data, web_research, analysis
        )
        
        return {
            "analysis_type": "comprehensive_data",
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "analysis": analysis,
            "comprehensive_data": comprehensive_data,
            "web_research": web_research,
            "saved_files": saved_files,
            "total_tokens": comprehensive_data.get("total_tokens", 0)
        }
    
    def _build_comprehensive_analysis_prompt(self, user_prompt: str, comprehensive_data: Dict[str, Any], 
                                           web_research: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt with all data"""
        
        season_context = comprehensive_data.get("season_context", {})
        league_metadata = comprehensive_data.get("league_metadata", {})
        my_roster = comprehensive_data.get("my_roster", {})
        opponent_roster = comprehensive_data.get("opponent_roster", {})
        available_players = comprehensive_data.get("available_players", {})
        transaction_trends = comprehensive_data.get("transaction_trends", {})
        
        nfl_season = season_context.get("nfl_season", "2025")
        current_week = season_context.get("current_week", 1)
        league_name = league_metadata.get("league_name", "Unknown League")
        team_name = league_metadata.get("team_name", "Unknown Team")
        opponent_name = opponent_roster.get("opponent_name", "Unknown Opponent")
        
        prompt = f"""USER REQUEST: {user_prompt}

CRITICAL CONTEXT: This is the {nfl_season} NFL season, Week {current_week}. You are analyzing for {team_name} in {league_name}.

## LEAGUE METADATA
- **League Name**: {league_name}
- **Team Name**: {team_name}
- **Current Week**: {current_week}
- **NFL Season**: {nfl_season}
- **Opponent**: {opponent_name}

## MY ROSTER PLAYERS ({my_roster.get('total_players', 0)} players)
{json.dumps(my_roster.get('players_by_position', {}), indent=2)}

## OPPONENT ROSTER PLAYERS ({opponent_roster.get('total_players', 0)} players)
{json.dumps(opponent_roster.get('players_by_position', {}), indent=2)}

## AVAILABLE PLAYERS ({available_players.get('total_players', 0)} players)
{json.dumps(available_players.get('players_by_position', {}), indent=2)}

## TRANSACTION TRENDS
{json.dumps(transaction_trends, indent=2)}

## WEB RESEARCH
{json.dumps(web_research, indent=2)}

## ANALYSIS INSTRUCTIONS

### 1. DATA UTILIZATION REQUIREMENTS
- **MUST** analyze each player's projected points from Tank01 data (tank01_data.projection.fantasyPoints)
- **MUST** follow and summarize news links from Tank01 data (tank01_data.news)
- **MUST** consider depth chart positions from Sleeper data (sleeper_data.depth_chart_position)
- **MUST** cross-reference player IDs across all 3 APIs
- **MUST** use web research findings in your analysis

### 2. REQUIRED OUTPUT FORMAT
1. **Data Visibility Confirmation**: Show exactly what data you can see
2. **Individual Player Summaries**: For EACH player on your roster, provide a detailed summary based on:
   - Web research findings about that specific player
   - News links provided in their Tank01 data
   - Current injury status and role clarity
   - Recent performance trends and expectations
   - Projected fantasy points from Tank01 data
3. **Opponent Analysis**: Detailed analysis of your Week {current_week} opponent ({opponent_name})
4. **Available Players Analysis**: Top recommendations with specific reasoning
5. **Specific Recommendations**: Exact add/drop suggestions with projected points comparisons
6. **News Integration**: How news links influenced your recommendations

### 3. CRITICAL INSTRUCTIONS
- **MUST** use Tank01 projected points data (tank01_data.projection.fantasyPoints)
- **MUST** follow and summarize news links from player data (tank01_data.news)
- **MUST** provide individual summary for each roster player based on web research and news
- **MUST** use Tank01 fantasy points for all projections (not Yahoo's 0 values)
- **MUST** analyze your opponent's key players and their projected performance

Please provide a comprehensive analysis with specific recommendations for improving your roster."""
        
        return prompt
    
    def _save_comprehensive_reports(self, comprehensive_data: Dict[str, Any], 
                                  web_research: Dict[str, Any], analysis: str) -> Dict[str, str]:
        """Save comprehensive reports including JSON and markdown"""
        
        timestamp = datetime.now(self.pacific_tz).strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_root, "data_collection", "outputs", "analyst_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save comprehensive JSON
        json_filepath = os.path.join(output_dir, f"{timestamp}_comprehensive_analysis.json")
        with open(json_filepath, 'w') as f:
            json.dump({
                "analysis": analysis,
                "comprehensive_data": comprehensive_data,
                "web_research": web_research,
                "model_provider": self.model_provider,
                "model_name": self.model_name,
                "timestamp": timestamp
            }, f, indent=2)
        
        # Save comprehensive markdown
        markdown_filepath = os.path.join(output_dir, f"{timestamp}_comprehensive_analysis.md")
        self._save_comprehensive_markdown_report(
            comprehensive_data, web_research, analysis, markdown_filepath
        )
        
        # Save comprehensive player data markdown
        player_data_filepath = os.path.join(output_dir, f"{timestamp}_comprehensive_player_data.md")
        self._save_comprehensive_player_data_markdown(comprehensive_data, player_data_filepath)
        
        logger.info(f"Comprehensive analysis saved to: {json_filepath}")
        logger.info(f"Comprehensive markdown saved to: {markdown_filepath}")
        logger.info(f"Comprehensive player data saved to: {player_data_filepath}")
        
        return {
            "json": json_filepath,
            "markdown": markdown_filepath,
            "player_data": player_data_filepath
        }
    
    def _save_comprehensive_markdown_report(self, comprehensive_data: Dict[str, Any], 
                                          web_research: Dict[str, Any], analysis: str, 
                                          filepath: str) -> None:
        """Save comprehensive markdown report"""
        
        season_context = comprehensive_data.get("season_context", {})
        league_metadata = comprehensive_data.get("league_metadata", {})
        
        markdown_content = f"""# Fantasy Football Comprehensive Analysis Report

**Generated:** {datetime.now(self.pacific_tz).strftime("%Y-%m-%d %H:%M:%S PDT")}
**Model:** {self.model_provider} - {self.model_name}
**Season Context:** {season_context.get('nfl_season', 'Unknown')} - Week {season_context.get('current_week', 'Unknown')} ({season_context.get('season_phase', 'Unknown')})

## League Information
- **League Name:** {league_metadata.get('league_name', 'Unknown')}
- **Team Name:** {league_metadata.get('team_name', 'Unknown')}
- **Current Week:** {season_context.get('current_week', 'Unknown')}
- **NFL Season:** {season_context.get('nfl_season', 'Unknown')}

## Data Summary
- **My Roster Players:** {comprehensive_data.get('my_roster', {}).get('total_players', 0)}
- **Opponent Roster Players:** {comprehensive_data.get('opponent_roster', {}).get('total_players', 0)}
- **Available Players:** {comprehensive_data.get('available_players', {}).get('total_players', 0)}
- **Web Research Items:** {len(web_research.get('news_items', []))}
- **Total Tokens Used:** {comprehensive_data.get('total_tokens', 0):,}

## Analysis

{analysis}

## Data Sources

{self._format_comprehensive_data_sources(comprehensive_data)}

## Resources Used

{self._format_comprehensive_resources_used(comprehensive_data, web_research)}
"""
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
    
    def _save_comprehensive_player_data_markdown(self, comprehensive_data: Dict[str, Any], filepath: str) -> None:
        """Save comprehensive player data as markdown"""
        
        markdown_content = f"""# Comprehensive Player Data

**Generated:** {datetime.now(self.pacific_tz).strftime("%Y-%m-%d %H:%M:%S PDT")}
**Total Players:** {comprehensive_data.get('my_roster', {}).get('total_players', 0)} roster + {comprehensive_data.get('opponent_roster', {}).get('total_players', 0)} opponent + {comprehensive_data.get('available_players', {}).get('total_players', 0)} available

## My Roster Players

{self._format_players_by_position(comprehensive_data.get('my_roster', {}).get('players_by_position', {}))}

## Opponent Roster Players

{self._format_players_by_position(comprehensive_data.get('opponent_roster', {}).get('players_by_position', {}))}

## Available Players

{self._format_players_by_position(comprehensive_data.get('available_players', {}).get('players_by_position', {}))}
"""
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
    
    def _format_players_by_position(self, players_by_position: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format players by position for markdown"""
        content = ""
        
        for position, players in players_by_position.items():
            content += f"### {position} ({len(players)} players)\n\n"
            for i, player in enumerate(players):
                content += f"#### Player {i+1}\n"
                content += f"```json\n{json.dumps(player, indent=2)}\n```\n\n"
        
        return content
    
    def _format_comprehensive_data_sources(self, comprehensive_data: Dict[str, Any]) -> str:
        """Format data sources for comprehensive report"""
        data_files = comprehensive_data.get("data_files", {})
        sources = []
        
        for data_type, file_path in data_files.items():
            if file_path:
                filename = os.path.basename(file_path)
                sources.append(f"- **{data_type.replace('_', ' ').title()}**: {filename}")
        
        return "\n".join(sources) if sources else "No data sources available"
    
    def _format_comprehensive_resources_used(self, comprehensive_data: Dict[str, Any], web_research: Dict[str, Any]) -> str:
        """Format resources used for comprehensive report"""
        resources = []
        
        # Add data summary
        my_roster_count = comprehensive_data.get('my_roster', {}).get('total_players', 0)
        opponent_roster_count = comprehensive_data.get('opponent_roster', {}).get('total_players', 0)
        available_players_count = comprehensive_data.get('available_players', {}).get('total_players', 0)
        web_research_items = len(web_research.get('news_items', []))
        
        resources.append(f"- **My Roster Players**: {my_roster_count}")
        resources.append(f"- **Opponent Roster Players**: {opponent_roster_count}")
        resources.append(f"- **Available Players**: {available_players_count}")
        resources.append(f"- **Web Research Items**: {web_research_items}")
        resources.append(f"- **Model**: {self.model_provider} - {self.model_name}")
        
        return "\n".join(resources)
    
    def _extract_roster_summary(self, roster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only essential roster data to reduce token usage"""
        summary = {
            "season_context": roster_analysis.get("season_context", {}),
            "my_roster": {},
            "current_week": roster_analysis.get("current_week")
        }
        
        # Extract only essential roster data
        if "roster_analysis" in roster_analysis:
            for api, roster_data in roster_analysis["roster_analysis"].items():
                if isinstance(roster_data, dict):
                    # Check for different player data structures
                    players = []
                    
                    # Try to find players in different possible keys
                    player_lists = []
                    if "players" in roster_data:
                        player_lists.extend(roster_data["players"])
                    if "starters" in roster_data:
                        player_lists.extend(roster_data["starters"])
                    if "bench" in roster_data:
                        player_lists.extend(roster_data["bench"])
                    
                    # Process all found players
                    for player in player_lists[:15]:  # Limit to 15 players
                        if isinstance(player, dict):
                            # Handle different player data structures
                            name = "Unknown"
                            if "name" in player:
                                if isinstance(player["name"], dict):
                                    name = player["name"].get("full", "Unknown")
                                else:
                                    name = str(player["name"])
                            
                            position = player.get("display_position", player.get("position", "Unknown"))
                            team = "Unknown"
                            if "team" in player:
                                if isinstance(player["team"], dict):
                                    team = player["team"].get("abbr", "Unknown")
                                else:
                                    team = str(player["team"])
                            
                            # Extract Tank01 projected points if available
                            projected_points = player.get("projected_points", 0)
                            if "tank01_data" in player and "projection" in player["tank01_data"]:
                                projection = player["tank01_data"]["projection"]
                                tank01_points = projection.get("fantasyPoints", 0)
                                if isinstance(tank01_points, str):
                                    try:
                                        projected_points = float(tank01_points)
                                    except:
                                        projected_points = 0
                                else:
                                    projected_points = tank01_points
                            
                            players.append({
                                "name": name,
                                "position": position,
                                "team": team,
                                "projected_points": projected_points,
                                "injury_status": player.get("injury_status", "Healthy"),
                                "tank01_data": player.get("tank01_data", {}),
                                "news": player.get("news", [])
                            })
                    
                    if players:  # Only add if we found players
                        summary["my_roster"][api] = {
                            "total_players": len(players),
                            "players": players
                        }
        
        return summary
    
    def _extract_web_summary(self, web_research: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only essential web research to reduce token usage"""
        summary = {
            "total_news_items": len(web_research.get("news_items", [])),
            "key_headlines": []
        }
        
        # Include only first 5 news items with headlines
        for item in web_research.get("news_items", [])[:5]:
            if isinstance(item, dict):
                summary["key_headlines"].append({
                    "title": item.get("title", "No title"),
                    "url": item.get("url", ""),
                    "published": item.get("published", "")
                })
        
        return summary
    
    def _create_data_summary(self, optimized_data: Dict[str, Any], roster_analysis: Dict[str, Any], web_research: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of all data available to the agent"""
        summary = {
            "my_roster_count": 0,
            "opponent_roster_count": 0,
            "available_players_count": optimized_data.get("total_players", 0),
            "web_research_items": len(web_research.get("news_items", [])),
            "data_sources": [],
            "player_data_breakdown": {},
            "current_week_opponent": "Unknown"
        }
        
        # Count my roster players
        if "roster_analysis" in roster_analysis:
            for api, data in roster_analysis["roster_analysis"].items():
                if isinstance(data, dict) and "total_players" in data:
                    summary["my_roster_count"] += data["total_players"]
                    summary["data_sources"].append(f"{api}_roster")
        
        # Count available players by position
        if "players_by_position" in optimized_data:
            for position, players in optimized_data["players_by_position"].items():
                summary["player_data_breakdown"][position] = len(players)
        
        # Add web research sources
        if "urls" in web_research:
            summary["data_sources"].extend(web_research["urls"])
        
        # Try to extract current week opponent from matchup data
        if "league_context" in roster_analysis:
            league_context = roster_analysis["league_context"]
            if "matchups" in league_context:
                matchups = league_context["matchups"]
                # Look for current week matchup
                if "week_1" in matchups and "matchups" in matchups["week_1"]:
                    week1_matchups = matchups["week_1"]["matchups"]
                    # Find the matchup that contains the user's team
                    user_team_key = "461.l.595012.t.3"  # This should be extracted from league info
                    for matchup in week1_matchups:
                        if "teams" in matchup and len(matchup["teams"]) == 2:
                            team1 = matchup["teams"][0]
                            team2 = matchup["teams"][1]
                            
                            # Check if user's team is in this matchup
                            if (team1.get("team_key") == user_team_key or 
                                team2.get("team_key") == user_team_key):
                                # Find the opponent
                                if team1.get("team_key") == user_team_key:
                                    opponent = team2
                                else:
                                    opponent = team1
                                
                                summary["current_week_opponent"] = opponent.get("name", "Week 1 Opponent")
                                break
        
        return summary
    
    def _save_optimized_player_data_markdown(self, optimized_data: Dict[str, Any], saved_files: Dict[str, str]) -> None:
        """Save the optimized player data as a separate markdown file"""
        timestamp = datetime.now(self.pacific_tz).strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_root, "data_collection", "outputs", "analyst_reports")
        
        # Create markdown content
        markdown_content = f"""# Optimized Player Data - Raw Input to Agent

**Generated:** {datetime.now(self.pacific_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}
**Total Players:** {optimized_data.get('total_players', 0)}
**Total Tokens:** {optimized_data.get('total_tokens', 0):,}

## Season Context
```json
{json.dumps(optimized_data.get('season_context', {}), indent=2)}
```

## Player Limits
```json
{json.dumps(optimized_data.get('player_limits', {}), indent=2)}
```

## Players by Position

"""
        
        # Add players by position - show ALL players
        for position, players in optimized_data.get("players_by_position", {}).items():
            markdown_content += f"### {position} ({len(players)} players)\n\n"
            for i, player in enumerate(players):  # Show ALL players per position
                markdown_content += f"#### Player {i+1}\n"
                markdown_content += f"```json\n{json.dumps(player, indent=2)}\n```\n\n"
        
        # Save the file
        filename = f"{timestamp}_optimized_player_data.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        logger.info(f"Optimized player data saved to: {filepath}")
    
    def _format_data_sources(self, analysis_result: Dict[str, Any]) -> str:
        """Format data sources for markdown report"""
        sources = []
        
        # Add data files from roster analysis
        if 'roster_analysis' in analysis_result:
            roster_analysis = analysis_result['roster_analysis']
            if 'data_files' in roster_analysis:
                for file_type, file_path in roster_analysis['data_files'].items():
                    if file_path:
                        filename = os.path.basename(file_path)
                        sources.append(f"- **{file_type.replace('_', ' ').title()}**: {filename}")
        
        # Add web research sources
        if 'web_research' in analysis_result:
            web_research = analysis_result['web_research']
            if 'urls' in web_research:
                for url in web_research['urls']:
                    sources.append(f"- **Web Research**: {url}")
        
        # Add optimized player data info
        if 'optimized_data' in analysis_result:
            optimized_data = analysis_result['optimized_data']
            sources.append(f"- **Optimized Player Data**: {optimized_data.get('total_players', 0)} players, {optimized_data.get('total_tokens', 0):,} tokens")
        
        # Add data summary info
        if 'data_summary' in analysis_result:
            data_summary = analysis_result['data_summary']
            sources.append(f"- **Data Summary**: {data_summary.get('my_roster_count', 0)} roster players, {data_summary.get('available_players_count', 0)} available players")
        
        return "\n".join(sources) if sources else "No data sources available"
    
    def _format_resources_used(self, analysis_result: Dict[str, Any]) -> str:
        """Format resources used for markdown report"""
        resources = []
        
        # Add data summary
        if 'data_summary' in analysis_result:
            data_summary = analysis_result['data_summary']
            resources.append(f"- **My Roster Players**: {data_summary.get('my_roster_count', 0)}")
            resources.append(f"- **Available Players**: {data_summary.get('available_players_count', 0)}")
            resources.append(f"- **Web Research Items**: {data_summary.get('web_research_items', 0)}")
        
        # Add model info
        resources.append(f"- **Model**: {analysis_result.get('model_provider', 'Unknown')} - {analysis_result.get('model_name', 'Unknown')}")
        
        return "\n".join(resources) if resources else "No resources used"
    
    def _build_analysis_prompt(self, user_prompt: str, analysis_data: Dict, web_research: Dict) -> str:
        """Build the complete prompt for LLM analysis"""
        # Extract season context from analysis data
        season_context = analysis_data.get("season_context", {})
        nfl_season = season_context.get("nfl_season", "current")
        season_phase = season_context.get("season_phase", "Regular Season")
        confidence = season_context.get("confidence_level", "medium")
        
        prompt = f"""USER REQUEST: {user_prompt}

CRITICAL CONTEXT: This is the {nfl_season} NFL season ({season_phase}). Use ONLY the data provided below and current {nfl_season} season information. Do NOT use training data from previous seasons.

SEASON CONTEXT VERIFICATION:
- NFL Season: {nfl_season}
- Season Phase: {season_phase}
- Confidence Level: {confidence}
- Verification Notes: {season_context.get('verification_notes', [])}

CURRENT DATA ANALYSIS ({nfl_season} SEASON):
{json.dumps(analysis_data, indent=2)}

WEB RESEARCH FINDINGS ({nfl_season} SEASON):
{json.dumps(web_research, indent=2)}

IMPORTANT: Before making any recommendations, verify all player-team relationships and current situations against the provided data. Do not assume player situations from your training data. Use only the {nfl_season} season information provided above.

Please provide a comprehensive analysis following the format specified in your system prompt. Focus on actionable recommendations with clear justifications based on {nfl_season} season data only."""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the appropriate LLM with the prompt"""
        try:
            if self.model_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                return response.choices[0].message.content
            elif self.model_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=4000,
                    temperature=0.7,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error generating analysis: {e}"
    
    def _extract_resources_used(self, analysis_data: Dict, web_research: Dict) -> List[str]:
        """Extract list of resources used in analysis"""
        resources = []
        
        # Add data files used
        if "data_files" in analysis_data:
            resources.extend(analysis_data["data_files"])
        
        # Add web URLs used
        if "urls" in web_research:
            resources.extend(web_research["urls"])
        
        return resources
    
    def save_analysis_report(self, analysis_result: Dict[str, Any], filename_prefix: str = "analysis") -> Dict[str, str]:
        """
        Save analysis results to disk in both JSON and Markdown formats
        
        Args:
            analysis_result: Result from analyze() method
            filename_prefix: Prefix for the filename
            
        Returns:
            Dictionary with paths to saved files
        """
        timestamp = datetime.now(self.pacific_tz).strftime("%Y%m%d_%H%M%S")
        
        # Save to outputs directory
        output_dir = os.path.join(project_root, "data_collection", "outputs", "analyst_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON version with timestamp as prefix only
        json_filename = f"{timestamp}_{filename_prefix}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        with open(json_filepath, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        # Save Markdown version with timestamp as prefix only
        markdown_filename = f"{timestamp}_{filename_prefix}.md"
        markdown_filepath = os.path.join(output_dir, markdown_filename)
        
        # Extract the analysis content for markdown
        analysis_content = analysis_result.get('analysis', 'No analysis content available')
        
        # Create markdown report - get season context from optimized data or analysis data
        optimized_data = analysis_result.get('optimized_data', {})
        analysis_data = analysis_result.get('analysis_data', {})
        
        # Try to get season context from optimized data first, then analysis data
        season_context = optimized_data.get('season_context', analysis_data.get('season_context', {}))
        nfl_season = season_context.get('nfl_season', 'Unknown')
        current_week = season_context.get('current_week', 'Unknown')
        season_phase = season_context.get('season_phase', 'Unknown')
        
        # Extract source files information
        source_files = []
        if 'roster_analysis' in analysis_result and 'data_files' in analysis_result['roster_analysis']:
            for file_type, file_path in analysis_result['roster_analysis']['data_files'].items():
                if file_path:
                    filename = os.path.basename(file_path)
                    source_files.append(f"- {file_type}: {filename}")
        
        # Add web research sources
        if 'web_research' in analysis_result and 'urls' in analysis_result['web_research']:
            for url in analysis_result['web_research']['urls']:
                source_files.append(f"- Web Research: {url}")
        
        source_files_text = "\n".join(source_files) if source_files else "No source files identified"
        
        markdown_content = f"""# Fantasy Football Analysis Report

**Generated:** {datetime.now(self.pacific_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}
**Model:** {self.model_provider} - {self.model_name}
**Season Context:** {nfl_season} - Week {current_week} ({season_phase})

## Source Files Used
{source_files_text}

## Analysis

{analysis_content}

## Data Sources

{self._format_data_sources(analysis_result)}

## Resources Used

{self._format_resources_used(analysis_result)}
"""
        
        with open(markdown_filepath, 'w') as f:
            f.write(markdown_content)
        
        logger.info(f"Analysis report saved to: {json_filepath}")
        logger.info(f"Markdown report saved to: {markdown_filepath}")
        
        return {
            "json": json_filepath,
            "markdown": markdown_filepath
        }
    
    
    def _format_resources_used(self, analysis_result: Dict[str, Any]) -> str:
        """Format resources used for markdown report"""
        resources = analysis_result.get('resources_used', [])
        if not resources:
            return "No additional resources used"
        
        return "\n".join(f"- {resource}" for resource in resources)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")


def main():
    """Main function for testing the Analyst Agent"""
    print("🏈 Fantasy Football Analyst Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = AnalystAgent()  # Uses default: Anthropic Claude Sonnet 3.7
    
    # Example analysis
    user_prompt = "Analyze my current roster and recommend any add/drop moves I should consider from the available free agents."
    
    print(f"User Prompt: {user_prompt}")
    print("\nStarting analysis...")
    
    result = agent.analyze(user_prompt)
    
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS:")
    print("=" * 50)
    print(result["analysis"])
    
    print("\n" + "=" * 50)
    print("RESOURCES USED:")
    print("=" * 50)
    for resource in result["resources_used"]:
        print(f"- {resource}")
    
    # Save report
    report_path = agent.save_analysis_report(result)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
