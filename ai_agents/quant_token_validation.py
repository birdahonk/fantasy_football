#!/usr/bin/env python3
"""
Quant AI Agent - Token Usage Validation Script

This script validates token usage for Quant AI agent prompts and data
to ensure they fit within the Anthropic Opus 4.1 model's 200k token limit.

Usage:
    python3 ai_agents/quant_token_validation.py --test-data sample_data.json
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import tiktoken

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_current_time_pacific():
    """Get current time in Pacific Time Zone."""
    import pytz
    from datetime import datetime
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific)

class QuantTokenValidator:
    """
    Validates token usage for Quant AI agent prompts and data.
    
    This class ensures that the combination of system prompts, analysis prompts,
    and post-game data fits within the Anthropic Opus 4.1 model's 200k token limit.
    """
    
    def __init__(self):
        """Initialize the token validator."""
        self.logger = logging.getLogger(__name__)
        
        # Token limits
        self.max_tokens = 200000  # Anthropic Opus 4.1 limit
        self.safety_buffer = 10000  # Safety buffer for response tokens
        self.effective_limit = self.max_tokens - self.safety_buffer
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            self.logger.error(f"Failed to initialize tokenizer: {e}")
            self.tokenizer = None
        
        # Track validation results
        self.validation_results = {
            "system_prompt_tokens": 0,
            "analysis_prompts_tokens": 0,
            "sample_data_tokens": 0,
            "total_tokens": 0,
            "within_limit": False,
            "excess_tokens": 0,
            "optimization_needed": False
        }
        
        self.logger.info("Quant Token Validator initialized")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not self.tokenizer:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
        
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            self.logger.error(f"Error counting tokens: {e}")
            return len(text) // 4
    
    def load_system_prompt(self) -> str:
        """
        Load the Quant system prompt.
        
        Returns:
            System prompt text
        """
        try:
            prompt_file = Path("ai_agents/prompts/quant_system_prompt.md")
            if not prompt_file.exists():
                self.logger.error(f"System prompt file not found: {prompt_file}")
                return ""
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            self.logger.error(f"Error loading system prompt: {e}")
            return ""
    
    def load_analysis_prompts(self) -> str:
        """
        Load the Quant analysis prompts.
        
        Returns:
            Analysis prompts text
        """
        try:
            prompts_file = Path("ai_agents/prompts/quant_analysis_prompts.md")
            if not prompts_file.exists():
                self.logger.error(f"Analysis prompts file not found: {prompts_file}")
                return ""
            
            with open(prompts_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            self.logger.error(f"Error loading analysis prompts: {e}")
            return ""
    
    def load_output_formatting(self) -> str:
        """
        Load the Quant output formatting guidelines.
        
        Returns:
            Output formatting text
        """
        try:
            formatting_file = Path("ai_agents/prompts/quant_output_formatting.md")
            if not formatting_file.exists():
                self.logger.error(f"Output formatting file not found: {formatting_file}")
                return ""
            
            with open(formatting_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            self.logger.error(f"Error loading output formatting: {e}")
            return ""
    
    def load_sample_data(self, data_file: str) -> Dict[str, Any]:
        """
        Load sample post-game data for testing.
        
        Args:
            data_file: Path to sample data file
            
        Returns:
            Sample data dictionary
        """
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading sample data: {e}")
            return {}
    
    def create_sample_data(self) -> Dict[str, Any]:
        """
        Create sample post-game data for testing.
        
        Returns:
            Sample data dictionary
        """
        return {
            "analysis_metadata": {
                "source": "Post-Game Analysis Data Processor",
                "processing_timestamp": get_current_time_pacific().isoformat(),
                "week": 1,
                "season": 2025,
                "execution_stats": {
                    "players_analyzed": 25,
                    "errors": 0
                }
            },
            "projections_summary": {
                "total_projections": 500,
                "collection_timestamp": "2025-01-08T14:00:00-08:00"
            },
            "roster_analyses": {
                "my_roster": {
                    "roster_type": "my_roster",
                    "total_players": 15,
                    "players_analyzed": 15,
                    "total_projected_points": 120.5,
                    "total_actual_points": 135.2,
                    "total_performance_difference": 14.7,
                    "over_performers_count": 8,
                    "under_performers_count": 4,
                    "even_performers_count": 3,
                    "player_analysis": [
                        {
                            "player_name": "Josh Allen",
                            "position": "QB",
                            "team": "BUF",
                            "projected_fantasy_points": 25.5,
                            "actual_fantasy_points": 28.2,
                            "performance_difference": 2.7,
                            "performance_percentage": 110.6,
                            "over_under": "over"
                        },
                        {
                            "player_name": "Christian McCaffrey",
                            "position": "RB",
                            "team": "SF",
                            "projected_fantasy_points": 22.0,
                            "actual_fantasy_points": 18.5,
                            "performance_difference": -3.5,
                            "performance_percentage": 84.1,
                            "over_under": "under"
                        }
                    ]
                },
                "opponent_roster": {
                    "roster_type": "opponent_roster",
                    "total_players": 15,
                    "players_analyzed": 15,
                    "total_projected_points": 118.3,
                    "total_actual_points": 142.8,
                    "total_performance_difference": 24.5,
                    "over_performers_count": 10,
                    "under_performers_count": 3,
                    "even_performers_count": 2,
                    "player_analysis": [
                        {
                            "player_name": "Lamar Jackson",
                            "position": "QB",
                            "team": "BAL",
                            "projected_fantasy_points": 24.0,
                            "actual_fantasy_points": 31.5,
                            "performance_difference": 7.5,
                            "performance_percentage": 131.3,
                            "over_under": "over"
                        }
                    ]
                },
                "available_players": {
                    "roster_type": "available_players",
                    "total_players": 50,
                    "players_analyzed": 50,
                    "total_projected_points": 0,
                    "total_actual_points": 0,
                    "total_performance_difference": 0,
                    "over_performers_count": 15,
                    "under_performers_count": 20,
                    "even_performers_count": 15,
                    "player_analysis": [
                        {
                            "player_name": "Tyler Lockett",
                            "position": "WR",
                            "team": "SEA",
                            "projected_fantasy_points": 12.5,
                            "actual_fantasy_points": 18.2,
                            "performance_difference": 5.7,
                            "performance_percentage": 145.6,
                            "over_under": "over"
                        }
                    ]
                }
            },
            "matchup_data": {
                "my_team": "birdahonkers",
                "opponent_team": "Team 2",
                "my_score": 135.2,
                "opponent_score": 142.8,
                "point_difference": -7.6,
                "winner": "opponent"
            },
            "summary": {
                "total_players_analyzed": 80,
                "total_projected_points": 238.8,
                "total_actual_points": 278.0,
                "overall_performance_difference": 39.2
            }
        }
    
    def validate_token_usage(self, sample_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate token usage for Quant AI agent.
        
        Args:
            sample_data: Optional sample data for testing
            
        Returns:
            Validation results dictionary
        """
        self.logger.info("Starting token usage validation for Quant AI agent")
        
        # Load prompts
        system_prompt = self.load_system_prompt()
        analysis_prompts = self.load_analysis_prompts()
        output_formatting = self.load_output_formatting()
        
        # Count prompt tokens
        self.validation_results["system_prompt_tokens"] = self.count_tokens(system_prompt)
        self.validation_results["analysis_prompts_tokens"] = self.count_tokens(analysis_prompts)
        output_formatting_tokens = self.count_tokens(output_formatting)
        
        # Load or create sample data
        if sample_data is None:
            sample_data = self.create_sample_data()
        
        # Convert sample data to JSON string for token counting
        sample_data_json = json.dumps(sample_data, indent=2)
        self.validation_results["sample_data_tokens"] = self.count_tokens(sample_data_json)
        
        # Calculate total tokens
        total_tokens = (
            self.validation_results["system_prompt_tokens"] +
            self.validation_results["analysis_prompts_tokens"] +
            output_formatting_tokens +
            self.validation_results["sample_data_tokens"]
        )
        
        self.validation_results["total_tokens"] = total_tokens
        self.validation_results["within_limit"] = total_tokens <= self.effective_limit
        
        if total_tokens > self.effective_limit:
            self.validation_results["excess_tokens"] = total_tokens - self.effective_limit
            self.validation_results["optimization_needed"] = True
        
        # Log results
        self.logger.info(f"Token usage validation complete:")
        self.logger.info(f"  System prompt: {self.validation_results['system_prompt_tokens']:,} tokens")
        self.logger.info(f"  Analysis prompts: {self.validation_results['analysis_prompts_tokens']:,} tokens")
        self.logger.info(f"  Output formatting: {output_formatting_tokens:,} tokens")
        self.logger.info(f"  Sample data: {self.validation_results['sample_data_tokens']:,} tokens")
        self.logger.info(f"  Total: {total_tokens:,} tokens")
        self.logger.info(f"  Effective limit: {self.effective_limit:,} tokens")
        self.logger.info(f"  Within limit: {self.validation_results['within_limit']}")
        
        if self.validation_results["optimization_needed"]:
            self.logger.warning(f"  Excess tokens: {self.validation_results['excess_tokens']:,}")
            self.logger.warning("  Optimization needed to fit within token limit")
        
        return self.validation_results
    
    def generate_optimization_recommendations(self) -> List[str]:
        """
        Generate optimization recommendations based on token usage.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        if not self.validation_results["within_limit"]:
            excess_tokens = self.validation_results["excess_tokens"]
            
            # System prompt optimization
            if self.validation_results["system_prompt_tokens"] > 5000:
                recommendations.append(
                    f"Consider reducing system prompt length (currently {self.validation_results['system_prompt_tokens']:,} tokens)"
                )
            
            # Analysis prompts optimization
            if self.validation_results["analysis_prompts_tokens"] > 10000:
                recommendations.append(
                    f"Consider reducing analysis prompts length (currently {self.validation_results['analysis_prompts_tokens']:,} tokens)"
                )
            
            # Sample data optimization
            if self.validation_results["sample_data_tokens"] > 150000:
                recommendations.append(
                    f"Consider reducing sample data size (currently {self.validation_results['sample_data_tokens']:,} tokens)"
                )
                recommendations.append("  - Filter to only essential players (my roster + opponent + top available)")
                recommendations.append("  - Remove detailed game stats, keep only summary metrics")
                recommendations.append("  - Compress JSON structure and remove redundant fields")
            
            # General recommendations
            recommendations.append(f"Need to reduce {excess_tokens:,} tokens to fit within limit")
            recommendations.append("Consider implementing data filtering based on analysis type")
            recommendations.append("Use more concise prompt templates for specific analysis types")
        
        return recommendations
    
    def generate_validation_report(self) -> str:
        """
        Generate a comprehensive validation report.
        
        Returns:
            Markdown validation report
        """
        report = []
        report.append("# Quant AI Agent - Token Usage Validation Report")
        report.append("")
        report.append(f"**Validation Date:** {get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        report.append(f"**Model:** Anthropic Opus 4.1")
        report.append(f"**Token Limit:** {self.max_tokens:,} tokens")
        report.append(f"**Effective Limit:** {self.effective_limit:,} tokens (with safety buffer)")
        report.append("")
        
        # Token usage breakdown
        report.append("## 📊 Token Usage Breakdown")
        report.append("")
        report.append("| Component | Tokens | Percentage |")
        report.append("|-----------|--------|------------|")
        
        total_tokens = self.validation_results["total_tokens"]
        system_pct = (self.validation_results["system_prompt_tokens"] / total_tokens) * 100
        analysis_pct = (self.validation_results["analysis_prompts_tokens"] / total_tokens) * 100
        data_pct = (self.validation_results["sample_data_tokens"] / total_tokens) * 100
        
        report.append(f"| System Prompt | {self.validation_results['system_prompt_tokens']:,} | {system_pct:.1f}% |")
        report.append(f"| Analysis Prompts | {self.validation_results['analysis_prompts_tokens']:,} | {analysis_pct:.1f}% |")
        report.append(f"| Sample Data | {self.validation_results['sample_data_tokens']:,} | {data_pct:.1f}% |")
        report.append(f"| **Total** | **{total_tokens:,}** | **100.0%** |")
        report.append("")
        
        # Validation results
        report.append("## ✅ Validation Results")
        report.append("")
        if self.validation_results["within_limit"]:
            report.append("✅ **PASSED** - Token usage is within the effective limit")
            report.append(f"   - Used: {total_tokens:,} tokens")
            report.append(f"   - Available: {self.effective_limit - total_tokens:,} tokens")
        else:
            report.append("❌ **FAILED** - Token usage exceeds the effective limit")
            report.append(f"   - Used: {total_tokens:,} tokens")
            report.append(f"   - Limit: {self.effective_limit:,} tokens")
            report.append(f"   - Excess: {self.validation_results['excess_tokens']:,} tokens")
        report.append("")
        
        # Optimization recommendations
        if self.validation_results["optimization_needed"]:
            report.append("## 🔧 Optimization Recommendations")
            report.append("")
            recommendations = self.generate_optimization_recommendations()
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Next steps
        report.append("## 🚀 Next Steps")
        report.append("")
        if self.validation_results["within_limit"]:
            report.append("1. ✅ Proceed with prompt testing")
            report.append("2. ✅ Test with actual post-game data")
            report.append("3. ✅ Validate analysis quality")
            report.append("4. ✅ Deploy to production")
        else:
            report.append("1. 🔧 Implement optimization recommendations")
            report.append("2. 🔄 Re-run token validation")
            report.append("3. ✅ Proceed with prompt testing once within limits")
            report.append("4. ✅ Test with actual post-game data")
        
        return "\n".join(report)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Quant AI Agent Token Usage Validation')
    parser.add_argument('--test-data', type=str, help='Path to sample data file for testing')
    parser.add_argument('--output', type=str, help='Output file for validation report')
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        validator = QuantTokenValidator()
        
        # Load sample data if provided
        sample_data = None
        if args.test_data and os.path.exists(args.test_data):
            sample_data = validator.load_sample_data(args.test_data)
        
        # Run validation
        results = validator.validate_token_usage(sample_data)
        
        # Generate report
        report = validator.generate_validation_report()
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Validation report saved to: {args.output}")
        else:
            print(report)
        
        # Print summary
        if results["within_limit"]:
            print(f"\n✅ Token validation PASSED - {results['total_tokens']:,} tokens used")
        else:
            print(f"\n❌ Token validation FAILED - {results['excess_tokens']:,} tokens over limit")
            print("See optimization recommendations above")
        
        return 0 if results["within_limit"] else 1
        
    except Exception as e:
        print(f"❌ Token validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
