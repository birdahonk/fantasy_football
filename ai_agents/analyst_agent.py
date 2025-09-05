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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalystAgent:
    """
    Fantasy Football Analyst Agent
    
    Provides comprehensive analysis of fantasy football rosters, matchups, and player recommendations.
    Supports multiple LLM providers with conversation memory and data collection orchestration.
    """
    
    def __init__(self, model_provider: str = "anthropic", model_name: str = "claude-3-7-sonnet-20250219"):
        """
        Initialize the Analyst Agent
        
        Args:
            model_provider: "openai" or "anthropic" (default: "anthropic")
            model_name: Specific model name (default: "claude-3-7-sonnet-20250219")
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
    
    def _build_analysis_prompt(self, user_prompt: str, analysis_data: Dict, web_research: Dict) -> str:
        """Build the complete prompt for LLM analysis"""
        prompt = f"""USER REQUEST: {user_prompt}

CRITICAL CONTEXT: This is the 2025 NFL season. Use ONLY the data provided below and current 2025 season information. Do NOT use training data from 2024 or earlier seasons.

CURRENT DATA ANALYSIS (2025 SEASON):
{json.dumps(analysis_data, indent=2)}

WEB RESEARCH FINDINGS (2025 SEASON):
{json.dumps(web_research, indent=2)}

IMPORTANT: Before making any recommendations, verify all player-team relationships and current situations against the provided data. Do not assume player situations from your training data.

Please provide a comprehensive analysis following the format specified in your system prompt. Focus on actionable recommendations with clear justifications based on 2025 season data only."""
        
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
    
    def save_analysis_report(self, analysis_result: Dict[str, Any], filename_prefix: str = "analysis") -> str:
        """
        Save analysis results to disk
        
        Args:
            analysis_result: Result from analyze() method
            filename_prefix: Prefix for the filename
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now(self.pacific_tz).strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}_{self.model_provider}_{self.model_name.replace('-', '_')}.json"
        
        # Save to outputs directory
        output_dir = os.path.join(project_root, "data_collection", "outputs", "analyst_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        logger.info(f"Analysis report saved to: {filepath}")
        return filepath
    
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
