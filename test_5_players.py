#!/usr/bin/env python3
"""
Test optimized analysis with 5 players per position
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_agent import AnalystAgent
from config.player_limits import get_player_limits, get_total_available_players

def test_5_players_per_position():
    """Test with 5 players per position"""
    
    print("🧪 TESTING OPTIMIZED ANALYSIS WITH 5 PLAYERS PER POSITION")
    print("=" * 65)
    
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
    
    print(f"Custom player limits: {custom_limits}")
    print(f"Total players: {get_total_available_players(custom_limits)}")
    
    # Initialize agent
    print(f"\n🤖 Initializing Analyst Agent...")
    agent = AnalystAgent(model_provider="anthropic", model_name="claude-opus-4-1-20250805")
    
    # Test the optimized analysis (this will prompt for data collection choice)
    print(f"\n📊 Running optimized analysis...")
    print("This will:")
    print("1. Ask if you want to use existing data or collect fresh data")
    print("2. Show token usage estimate")
    print("3. Create optimized player profiles from existing output files")
    print("4. Run analysis with focus on your roster")
    
    # Run the analysis
    try:
        result = agent.analyze_with_optimized_profiles(
            user_prompt="Analyze my roster and provide specific add/drop recommendations for Week 1",
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
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("This might be because:")
        print("1. No recent data files found - run data collection first")
        print("2. Missing API keys in .env file")
        print("3. Network connectivity issues")

if __name__ == "__main__":
    test_5_players_per_position()
