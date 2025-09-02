#!/usr/bin/env python3
"""
Prompt Manager for AI Agents

Handles loading, caching, and managing system prompts from external files.
Provides a clean interface for agents to access their system prompts.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
import pytz

# Configure logging
logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages system prompts for AI agents
    
    Features:
    - Load prompts from external markdown files
    - Support for dynamic placeholders (e.g., current date)
    - Caching for performance
    - Validation and error handling
    """
    
    def __init__(self, prompts_dir: str = None):
        """
        Initialize the Prompt Manager
        
        Args:
            prompts_dir: Directory containing prompt files (default: ai_agents/prompts)
        """
        if prompts_dir is None:
            # Default to prompts directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompts_dir = os.path.join(current_dir, "prompts")
        
        self.prompts_dir = prompts_dir
        self.pacific_tz = pytz.timezone('US/Pacific')
        self._prompt_cache = {}
        
        logger.info(f"Prompt Manager initialized with prompts directory: {prompts_dir}")
    
    def get_system_prompt(self, agent_name: str, **kwargs) -> str:
        """
        Get the system prompt for a specific agent
        
        Args:
            agent_name: Name of the agent (e.g., 'analyst_agent')
            **kwargs: Additional context variables for prompt formatting
            
        Returns:
            Formatted system prompt string
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If prompt file is invalid
        """
        # Check cache first
        cache_key = f"{agent_name}_{hash(str(kwargs))}"
        if cache_key in self._prompt_cache:
            logger.debug(f"Using cached prompt for {agent_name}")
            return self._prompt_cache[cache_key]
        
        # Load prompt from file
        prompt_file = os.path.join(self.prompts_dir, f"{agent_name}_system_prompt.md")
        
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"System prompt file not found: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            # Add default context variables
            context = {
                'current_date': datetime.now(self.pacific_tz).strftime("%A, %B %d, %Y"),
                'current_time': datetime.now(self.pacific_tz).strftime("%I:%M %p %Z"),
                'current_week': self._get_current_nfl_week(),
                **kwargs
            }
            
            # Format the prompt with context variables
            formatted_prompt = prompt_template.format(**context)
            
            # Cache the result
            self._prompt_cache[cache_key] = formatted_prompt
            
            logger.info(f"Loaded system prompt for {agent_name}")
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"Error loading system prompt for {agent_name}: {e}")
            raise ValueError(f"Failed to load system prompt: {e}")
    
    def _get_current_nfl_week(self) -> int:
        """
        Determine the current NFL game week
        
        Returns:
            Current game week number (1-18)
        """
        try:
            # Simple calculation based on current date
            # NFL season typically starts first week of September
            current_date = datetime.now(self.pacific_tz)
            season_start = datetime(current_date.year, 9, 1, tzinfo=self.pacific_tz)
            
            if current_date < season_start:
                return 0  # Preseason
            
            weeks_elapsed = (current_date - season_start).days // 7
            return min(weeks_elapsed + 1, 18)  # Max 18 weeks
            
        except Exception as e:
            logger.warning(f"Could not determine current NFL week: {e}")
            return 1  # Default to week 1
    
    def list_available_prompts(self) -> list:
        """
        List all available system prompt files
        
        Returns:
            List of agent names with available prompts
        """
        if not os.path.exists(self.prompts_dir):
            return []
        
        prompts = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith('_system_prompt.md'):
                agent_name = filename.replace('_system_prompt.md', '')
                prompts.append(agent_name)
        
        return sorted(prompts)
    
    def validate_prompt_file(self, agent_name: str) -> Dict[str, any]:
        """
        Validate a prompt file for common issues
        
        Args:
            agent_name: Name of the agent to validate
            
        Returns:
            Dictionary with validation results
        """
        prompt_file = os.path.join(self.prompts_dir, f"{agent_name}_system_prompt.md")
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'file_exists': False,
            'file_size': 0
        }
        
        if not os.path.exists(prompt_file):
            result['valid'] = False
            result['errors'].append(f"Prompt file not found: {prompt_file}")
            return result
        
        result['file_exists'] = True
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result['file_size'] = len(content)
            
            # Check for common issues
            if len(content.strip()) == 0:
                result['valid'] = False
                result['errors'].append("Prompt file is empty")
            
            if len(content) < 100:
                result['warnings'].append("Prompt file is very short (less than 100 characters)")
            
            # Check for unclosed placeholders
            import re
            placeholders = re.findall(r'\{[^}]+\}', content)
            for placeholder in placeholders:
                if placeholder.count('{') != placeholder.count('}'):
                    result['warnings'].append(f"Potential unclosed placeholder: {placeholder}")
            
            # Test formatting with default context
            try:
                context = {
                    'current_date': datetime.now(self.pacific_tz).strftime("%A, %B %d, %Y"),
                    'current_time': datetime.now(self.pacific_tz).strftime("%I:%M %p %Z"),
                    'current_week': 1
                }
                content.format(**context)
            except KeyError as e:
                result['warnings'].append(f"Missing context variable: {e}")
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Formatting error: {e}")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error reading file: {e}")
        
        return result
    
    def clear_cache(self):
        """Clear the prompt cache"""
        self._prompt_cache.clear()
        logger.info("Prompt cache cleared")


def main():
    """Test the Prompt Manager"""
    print("🔧 Prompt Manager Test")
    print("=" * 40)
    
    manager = PromptManager()
    
    # List available prompts
    print("Available prompts:")
    prompts = manager.list_available_prompts()
    for prompt in prompts:
        print(f"  - {prompt}")
    
    # Test loading analyst agent prompt
    if 'analyst_agent' in prompts:
        print(f"\nTesting analyst_agent prompt...")
        try:
            prompt = manager.get_system_prompt('analyst_agent')
            print(f"✅ Successfully loaded prompt ({len(prompt)} characters)")
            print(f"Preview: {prompt[:200]}...")
        except Exception as e:
            print(f"❌ Error loading prompt: {e}")
        
        # Validate the prompt
        print(f"\nValidating analyst_agent prompt...")
        validation = manager.validate_prompt_file('analyst_agent')
        print(f"Valid: {validation['valid']}")
        if validation['errors']:
            print(f"Errors: {validation['errors']}")
        if validation['warnings']:
            print(f"Warnings: {validation['warnings']}")
    
    print("\n✅ Prompt Manager test completed!")


if __name__ == "__main__":
    main()
