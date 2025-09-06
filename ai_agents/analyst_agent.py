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
            "llm_response": llm_response,
            "analysis_type": "optimized_profiles"
        }
        
        return result
    
    def _build_optimized_analysis_prompt(self, user_prompt: str, optimized_data: Dict[str, Any], 
                                       roster_analysis: Dict[str, Any], web_research: Dict[str, Any]) -> str:
        """Build enhanced prompt using optimized player profiles"""
        season_context = optimized_data.get("season_context", {})
        nfl_season = season_context.get("nfl_season", "current")
        season_phase = season_context.get("season_phase", "Regular Season")
        
        prompt = f"""USER REQUEST: {user_prompt}

CRITICAL CONTEXT: This is the {nfl_season} NFL season ({season_phase}). Use ONLY the data provided below and current {nfl_season} season information. Do NOT use training data from previous seasons.

OPTIMIZED PLAYER DATA ({optimized_data.get('total_players', 0)} players, {optimized_data.get('total_tokens', 0):,} tokens):
{json.dumps(optimized_data, indent=2)}

MY ROSTER ANALYSIS:
{json.dumps(roster_analysis, indent=2)}

CURRENT NFL NEWS & CONTEXT:
{json.dumps(web_research, indent=2)}

INSTRUCTIONS:
1. Focus heavily on MY ROSTER players for detailed analysis and recommendations
2. Use the optimized player profiles for available players analysis
3. Cross-reference player IDs across Yahoo, Sleeper, and Tank01 data
4. Follow news links provided in player data for additional context
5. Provide specific add/drop recommendations based on projected points and depth charts
6. Consider bye weeks, injury status, and transaction trends in recommendations
7. Prioritize players with the best projected points and favorable matchups

Please provide a comprehensive analysis with specific recommendations."""
        
        return prompt
    
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
        model_suffix = f"{self.model_provider}_{self.model_name.replace('-', '_')}"
        
        # Save to outputs directory
        output_dir = os.path.join(project_root, "data_collection", "outputs", "analyst_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON version
        json_filename = f"{filename_prefix}_{timestamp}_{model_suffix}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        with open(json_filepath, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        # Save Markdown version
        markdown_filename = f"{filename_prefix}_{timestamp}_{model_suffix}.md"
        markdown_filepath = os.path.join(output_dir, markdown_filename)
        
        # Extract the analysis content for markdown
        analysis_content = analysis_result.get('analysis', 'No analysis content available')
        
        # Create markdown report
        analysis_data = analysis_result.get('analysis_data', {})
        season_context = analysis_data.get('season_context', {})
        nfl_season = season_context.get('nfl_season', 'Unknown')
        current_week = season_context.get('current_week', 'Unknown')
        season_phase = season_context.get('season_phase', 'Unknown')
        
        markdown_content = f"""# Fantasy Football Analysis Report

**Generated:** {datetime.now(self.pacific_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}
**Model:** {self.model_provider} - {self.model_name}
**Season Context:** {nfl_season} - Week {current_week} ({season_phase})

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
    
    def _format_data_sources(self, analysis_result: Dict[str, Any]) -> str:
        """Format data sources for markdown report"""
        data_files = analysis_result.get('data_files', {})
        if not data_files:
            return "No data sources available"
        
        sources = []
        for data_type, filepath in data_files.items():
            if filepath:
                filename = os.path.basename(filepath)
                sources.append(f"- **{data_type.replace('_', ' ').title()}:** {filename}")
        
        return "\n".join(sources) if sources else "No data sources available"
    
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
