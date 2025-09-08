#!/usr/bin/env python3
"""
Token Analyzer for Anthropic Opus 4.1 Model
Analyzes token usage in data sent to LLM and identifies optimization opportunities
"""

import json
import os
import sys
from typing import Dict, Any, List, Tuple
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_tools import AnalystTools
from ai_agents.analyst_agent import AnalystAgent

class TokenAnalyzer:
    def __init__(self):
        self.model_name = "claude-opus-4-1-20250805"
        self.analysis_tools = AnalystTools()
        
    def count_tokens_anthropic(self, text: str) -> int:
        """
        Estimate token count for Anthropic models using tiktoken
        Anthropic uses cl100k_base encoding (same as GPT-4)
        """
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            print("tiktoken not available, using rough estimation")
            # Rough estimation: ~4 characters per token for English text
            return len(text) // 4
    
    def analyze_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure and token usage of analysis_data"""
        
        # Convert to JSON string to count tokens
        json_str = json.dumps(analysis_data, indent=2)
        total_tokens = self.count_tokens_anthropic(json_str)
        
        analysis = {
            "total_tokens": total_tokens,
            "breakdown": {},
            "recommendations": []
        }
        
        # Analyze each major section
        sections = [
            ("season_context", "Season Context"),
            ("data_files", "Data Files"),
            ("roster_analysis", "Roster Analysis"),
            ("available_players", "Available Players"),
            ("league_context", "League Context"),
            ("insights", "Insights")
        ]
        
        for key, name in sections:
            if key in analysis_data:
                section_json = json.dumps(analysis_data[key], indent=2)
                section_tokens = self.count_tokens_anthropic(section_json)
                analysis["breakdown"][name] = {
                    "tokens": section_tokens,
                    "percentage": round((section_tokens / total_tokens) * 100, 1)
                }
        
        # Analyze available players in detail
        if "available_players" in analysis_data:
            ap_data = analysis_data["available_players"]
            ap_analysis = self._analyze_available_players_section(ap_data)
            analysis["available_players_detail"] = ap_analysis
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_available_players_section(self, ap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed analysis of available players section"""
        detail = {
            "apis": {},
            "total_players": 0,
            "total_tokens": 0
        }
        
        for api, data in ap_data.items():
            if isinstance(data, dict) and "top_players_by_position" in data:
                api_players = 0
                api_tokens = 0
                
                for position, players in data["top_players_by_position"].items():
                    if isinstance(players, list):
                        api_players += len(players)
                        for player in players:
                            player_json = json.dumps(player, indent=2)
                            api_tokens += self.count_tokens_anthropic(player_json)
                
                detail["apis"][api] = {
                    "players": api_players,
                    "tokens": api_tokens,
                    "tokens_per_player": round(api_tokens / api_players, 1) if api_players > 0 else 0
                }
                detail["total_players"] += api_players
                detail["total_tokens"] += api_tokens
        
        return detail
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        total_tokens = analysis["total_tokens"]
        
        if total_tokens > 200000:
            recommendations.append(f"CRITICAL: {total_tokens:,} tokens exceeds 200k limit by {total_tokens - 200000:,} tokens")
        
        # Check available players usage
        if "available_players_detail" in analysis:
            ap_detail = analysis["available_players_detail"]
            if ap_detail["total_tokens"] > 50000:
                recommendations.append(f"Available players using {ap_detail['total_tokens']:,} tokens ({ap_detail['total_players']} players) - consider reducing")
        
        # Check roster analysis usage
        if "Roster Analysis" in analysis["breakdown"]:
            roster_tokens = analysis["breakdown"]["Roster Analysis"]["tokens"]
            if roster_tokens > 30000:
                recommendations.append(f"Roster analysis using {roster_tokens:,} tokens - consider summarizing")
        
        # Check league context usage
        if "League Context" in analysis["breakdown"]:
            league_tokens = analysis["breakdown"]["League Context"]["tokens"]
            if league_tokens > 40000:
                recommendations.append(f"League context using {league_tokens:,} tokens - consider filtering")
        
        return recommendations
    
    def analyze_current_data(self) -> Dict[str, Any]:
        """Analyze the current data that would be sent to the LLM"""
        print("Analyzing current data collection...")
        
        # Get the most recent analysis data
        analysis_data = self.analysis_tools.analyze_recent_data()
        
        print(f"Found analysis data with {len(analysis_data)} top-level keys")
        
        # Analyze the data
        analysis = self.analyze_analysis_data(analysis_data)
        
        return analysis
    
    def test_optimization_scenarios(self) -> Dict[str, Any]:
        """Test different optimization scenarios"""
        print("Testing optimization scenarios...")
        
        # Get current data
        analysis_data = self.analysis_tools.analyze_recent_data()
        
        scenarios = {}
        
        # Scenario 1: Current data
        scenarios["current"] = self.analyze_analysis_data(analysis_data)
        
        # Scenario 2: Reduce available players to top 5 per position
        if "available_players" in analysis_data:
            reduced_ap = self._reduce_available_players(analysis_data["available_players"], 5)
            test_data = analysis_data.copy()
            test_data["available_players"] = reduced_ap
            scenarios["top_5_per_position"] = self.analyze_analysis_data(test_data)
        
        # Scenario 3: Remove sample players
        if "available_players" in analysis_data:
            no_samples = self._remove_sample_players(analysis_data["available_players"])
            test_data = analysis_data.copy()
            test_data["available_players"] = no_samples
            scenarios["no_sample_players"] = self.analyze_analysis_data(test_data)
        
        return scenarios
    
    def _reduce_available_players(self, ap_data: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Reduce available players to top N per position"""
        reduced = {}
        for api, data in ap_data.items():
            if isinstance(data, dict) and "top_players_by_position" in data:
                reduced[api] = data.copy()
                reduced[api]["top_players_by_position"] = {}
                for position, players in data["top_players_by_position"].items():
                    if isinstance(players, list):
                        reduced[api]["top_players_by_position"][position] = players[:limit]
        return reduced
    
    def _remove_sample_players(self, ap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sample players from available players data"""
        reduced = {}
        for api, data in ap_data.items():
            if isinstance(data, dict):
                reduced[api] = data.copy()
                if "sample_players" in reduced[api]:
                    del reduced[api]["sample_players"]
        return reduced

def main():
    analyzer = TokenAnalyzer()
    
    print("=" * 60)
    print("TOKEN USAGE ANALYSIS FOR ANTHROPIC OPUS 4.1")
    print("=" * 60)
    
    # Analyze current data
    print("\n1. CURRENT DATA ANALYSIS")
    print("-" * 30)
    current_analysis = analyzer.analyze_current_data()
    
    print(f"Total Tokens: {current_analysis['total_tokens']:,}")
    print(f"Token Limit: 200,000")
    print(f"Over Limit: {current_analysis['total_tokens'] - 200000:,}" if current_analysis['total_tokens'] > 200000 else "Within Limit")
    
    print("\nToken Breakdown:")
    for section, data in current_analysis["breakdown"].items():
        print(f"  {section}: {data['tokens']:,} tokens ({data['percentage']}%)")
    
    if "available_players_detail" in current_analysis:
        print("\nAvailable Players Detail:")
        ap_detail = current_analysis["available_players_detail"]
        print(f"  Total Players: {ap_detail['total_players']}")
        print(f"  Total Tokens: {ap_detail['total_tokens']:,}")
        for api, data in ap_detail["apis"].items():
            print(f"    {api}: {data['players']} players, {data['tokens']:,} tokens ({data['tokens_per_player']} per player)")
    
    print("\nRecommendations:")
    for rec in current_analysis["recommendations"]:
        print(f"  - {rec}")
    
    # Test optimization scenarios
    print("\n\n2. OPTIMIZATION SCENARIOS")
    print("-" * 30)
    scenarios = analyzer.test_optimization_scenarios()
    
    for scenario_name, analysis in scenarios.items():
        print(f"\n{scenario_name.replace('_', ' ').title()}:")
        print(f"  Tokens: {analysis['total_tokens']:,}")
        print(f"  Change: {analysis['total_tokens'] - current_analysis['total_tokens']:+,}")
        print(f"  Status: {'✅ Within Limit' if analysis['total_tokens'] <= 200000 else '❌ Over Limit'}")

if __name__ == "__main__":
    main()
