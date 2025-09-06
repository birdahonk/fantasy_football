#!/usr/bin/env python3
"""
Test the comprehensive fixes for Tank01 roster data, opponent detection, and player summaries
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_agents.analyst_agent import AnalystAgent

def test_comprehensive_fixes():
    """Test all comprehensive fixes"""
    
    print("🔧 TESTING COMPREHENSIVE FIXES")
    print("=" * 60)
    
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
    print(f"\n📊 Running comprehensive analysis with all fixes...")
    print("Expected fixes:")
    print("✅ Tank01 roster data should be included for ALL roster players")
    print("✅ Tank01 projected points should be used for roster players")
    print("✅ News links from Tank01 data should be utilized for roster players")
    print("✅ Current week opponent should be detected (Kissyface)")
    print("✅ Individual player summaries should include Tank01 data")
    print("✅ Data sources section should be populated")
    print("✅ All 119 available players should have Tank01 data")
    
    try:
        result = agent.analyze_with_optimized_profiles(
            user_prompt="Analyze my roster and provide specific add/drop recommendations for Week 1. For each player on my roster, provide a detailed summary based on the web research and news links provided in their Tank01 data. Include their projected fantasy points from Tank01. Focus on my starting lineup and identify the best available players to add. Make sure to use the projected points data from Tank01 and analyze my current week opponent matchup against Kissyface.",
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
            print(f"   Current Week Opponent: {data_summary.get('current_week_opponent', 'Unknown')}")
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
        
        # Check if all fixes are working
        print(f"\n🔍 Checking comprehensive fixes...")
        if 'saved_files' in result and 'markdown' in result['saved_files']:
            markdown_file = result['saved_files']['markdown']
            print(f"   Markdown file: {markdown_file}")
            
            with open(markdown_file, 'r') as f:
                content = f.read()
                
                # Check data sources
                if "No data sources available" in content:
                    print("   ❌ Data sources still empty")
                else:
                    print("   ✅ Data sources populated")
                
                # Check Tank01 data
                if "tank01_data" in content and "null" not in content:
                    print("   ✅ Tank01 data included")
                else:
                    print("   ❌ Tank01 data still missing")
                
                # Check individual player summaries
                if "Individual Player Summaries" in content:
                    print("   ✅ Individual player summaries included")
                else:
                    print("   ❌ Individual player summaries missing")
                
                # Check Tank01 projected points
                if "fantasyPoints" in content:
                    print("   ✅ Tank01 projected points being used")
                else:
                    print("   ❌ Tank01 projected points not found")
                
                # Check opponent detection
                if "Kissyface" in content:
                    print("   ✅ Current week opponent detected (Kissyface)")
                else:
                    print("   ❌ Current week opponent not detected")
                
                # Check for roster player Tank01 data
                if "Without Tank01 data available for roster players" in content:
                    print("   ❌ Roster players still missing Tank01 data")
                else:
                    print("   ✅ Roster players have Tank01 data")
        
        # Show a preview of the LLM response
        if 'analysis' in result:
            response = result['analysis']
            print(f"\n📝 LLM Response Preview:")
            print("-" * 30)
            print(response[:2000] + "..." if len(response) > 2000 else response)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_fixes()
