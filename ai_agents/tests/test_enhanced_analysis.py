#!/usr/bin/env python3
"""
Test the enhanced analysis system with all fixes
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_agent import AnalystAgent

def test_enhanced_analysis():
    """Test the enhanced analysis system with all fixes"""
    
    print("🧪 TESTING ENHANCED ANALYSIS SYSTEM")
    print("=" * 50)
    
    # Use default limits: 20 per position, 10 for DEF
    custom_limits = {
        "QB": 20,
        "RB": 20,
        "WR": 20,
        "TE": 20,
        "K": 20,
        "DEF": 10,
        "FLEX": 15
    }
    
    print(f"Player limits: {custom_limits}")
    print(f"Total players: {sum(custom_limits.values())}")
    
    # Initialize agent
    print(f"\n🤖 Initializing Analyst Agent...")
    agent = AnalystAgent(model_provider="anthropic", model_name="claude-opus-4-1-20250805")
    
    # Run the analysis
    print(f"\n📊 Running enhanced analysis...")
    print("Expected enhancements:")
    print("✅ Data sources and resources should be populated")
    print("✅ Agent should show data visibility confirmation")
    print("✅ Web research should be integrated into analysis")
    print("✅ Optimized player data should be saved as separate markdown")
    print("✅ Agent should analyze projected points and news links")
    print("✅ Agent should identify current week opponent")
    
    try:
        result = agent.analyze_with_optimized_profiles(
            user_prompt="Analyze my roster and provide specific add/drop recommendations for Week 1. Focus on my starting lineup and identify the best available players to add. Make sure to use the projected points data and news links provided.",
            player_limits=custom_limits,
            collect_data=False,  # Use existing data
            model_selection=False  # Use default Opus 4.1
        )
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"Analysis type: {result.get('analysis_type', 'unknown')}")
        print(f"Model used: {result.get('model_provider')} - {result.get('model_name')}")
        
        # Show data summary
        if 'data_summary' in result:
            data_summary = result['data_summary']
            print(f"\n📊 Data Summary:")
            print(f"   My Roster Players: {data_summary.get('my_roster_count', 0)}")
            print(f"   Available Players: {data_summary.get('available_players_count', 0)}")
            print(f"   Web Research Items: {data_summary.get('web_research_items', 0)}")
            print(f"   Data Sources: {len(data_summary.get('data_sources', []))}")
        
        # Show token usage from the result
        if 'optimized_data' in result:
            optimized_data = result['optimized_data']
            print(f"\n📈 Token Usage:")
            print(f"   Total players analyzed: {optimized_data.get('total_players', 0)}")
            print(f"   Total tokens used: {optimized_data.get('total_tokens', 0):,}")
        
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
            print(response[:800] + "..." if len(response) > 800 else response)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_analysis()
