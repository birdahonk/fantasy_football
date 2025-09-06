#!/usr/bin/env python3
"""
Test the fixed optimized analysis system
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_agent import AnalystAgent

def test_fixed_analysis():
    """Test the fixed optimized analysis system"""
    
    print("🧪 TESTING FIXED OPTIMIZED ANALYSIS SYSTEM")
    print("=" * 50)
    
    # Set custom limits: 5 per position, 3 for DEF
    custom_limits = {
        "QB": 5,
        "RB": 5,
        "WR": 5,
        "TE": 5,
        "K": 5,
        "DEF": 3,
        "FLEX": 5
    }
    
    print(f"Player limits: {custom_limits}")
    print(f"Total players: {sum(custom_limits.values())}")
    
    # Initialize agent
    print(f"\n🤖 Initializing Analyst Agent...")
    agent = AnalystAgent(model_provider="anthropic", model_name="claude-opus-4-1-20250805")
    
    # Run the analysis
    print(f"\n📊 Running fixed optimized analysis...")
    print("Expected fixes:")
    print("✅ Season context should show correctly in markdown")
    print("✅ File naming should have timestamp prefix only")
    print("✅ LLM should recognize user has a full roster")
    print("✅ Source files should be listed in markdown")
    print("✅ Only current week opponent should be included")
    
    try:
        result = agent.analyze_with_optimized_profiles(
            user_prompt="Analyze my roster and provide specific add/drop recommendations for Week 1. Focus on my starting lineup and identify the best available players to add.",
            player_limits=custom_limits,
            collect_data=False,  # Use existing data
            model_selection=False  # Use default Opus 4.1
        )
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"Analysis type: {result.get('analysis_type', 'unknown')}")
        print(f"Model used: {result.get('model_provider')} - {result.get('model_name')}")
        
        # Show token usage from the result
        if 'optimized_data' in result:
            optimized_data = result['optimized_data']
            print(f"Total players analyzed: {optimized_data.get('total_players', 0)}")
            print(f"Total tokens used: {optimized_data.get('total_tokens', 0):,}")
        
        # Show saved files
        if 'saved_files' in result:
            print(f"\n💾 Files saved:")
            for file_type, file_path in result['saved_files'].items():
                print(f"   {file_type}: {file_path}")
        
        # Show a preview of the LLM response
        if 'analysis' in result:
            response = result['analysis']
            print(f"\n📝 LLM Response Preview:")
            print("-" * 30)
            print(response[:500] + "..." if len(response) > 500 else response)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_analysis()
