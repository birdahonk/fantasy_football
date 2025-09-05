#!/usr/bin/env python3
"""
Test Analyst Agent with Anthropic Opus 4.1
"""

import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from ai_agents.analyst_agent import AnalystAgent

def main():
    print("🏈 Testing Analyst Agent with Anthropic Opus 4.1")
    print("=" * 60)
    
    # Initialize agent with Opus 4.1
    agent = AnalystAgent(
        model_provider="anthropic",
        model_name="claude-3-5-sonnet-20241022"
    )
    
    print(f"✅ Agent initialized with {agent.model_provider} - {agent.model_name}")
    
    # Test analysis
    user_prompt = "Analyze my current roster and recommend any add/drop moves I should consider from the available free agents. Focus on Week 1 matchups and current season context."
    
    print(f"\n📝 User Prompt: {user_prompt}")
    print("\n🔄 Starting analysis...")
    
    try:
        # Run analysis
        result = agent.analyze(user_prompt)
        
        print("✅ Analysis completed successfully!")
        print(f"📊 Analysis length: {len(result.get('analysis', ''))} characters")
        
        # Save report
        saved_files = agent.save_analysis_report(result, "opus_4_1_analysis")
        
        print(f"\n💾 Reports saved:")
        print(f"   JSON: {saved_files['json']}")
        print(f"   Markdown: {saved_files['markdown']}")
        
        # Show season context
        season_context = result.get('season_context', {})
        print(f"\n📅 Season Context:")
        print(f"   NFL Season: {season_context.get('nfl_season', 'Unknown')}")
        print(f"   Current Week: {season_context.get('current_week', 'Unknown')}")
        print(f"   Season Phase: {season_context.get('season_phase', 'Unknown')}")
        
        # Show data sources
        data_files = result.get('data_files', {})
        print(f"\n📁 Data Sources Used:")
        for data_type, filepath in data_files.items():
            if filepath:
                filename = os.path.basename(filepath)
                print(f"   {data_type}: {filename}")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
