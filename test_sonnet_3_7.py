#!/usr/bin/env python3
"""
Test Analyst Agent with Claude Sonnet 3.7 (Current Default)
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_sonnet_3_7():
    """Test Analyst Agent with Claude Sonnet 3.7"""
    print("🧠 Testing Analyst Agent with Claude Sonnet 3.7")
    print("=" * 60)
    
    try:
        from ai_agents.analyst_agent import AnalystAgent
        
        # Initialize with Sonnet 3.7
        print("Initializing Analyst Agent with Claude Sonnet 3.7...")
        agent = AnalystAgent(
            model_provider="anthropic", 
            model_name="claude-3-7-sonnet-20250219"
        )
        print("✅ Agent initialized successfully")
        
        # Test prompt
        user_prompt = "Analyze my current roster and recommend any add/drop moves I should consider from the available free agents. Focus on this week's matchups and provide specific player recommendations with detailed reasoning."
        
        print(f"\n📝 User Prompt: {user_prompt}")
        print("\n🔄 Starting analysis...")
        
        # Run analysis (use existing data, don't collect fresh data)
        start_time = datetime.now()
        result = agent.analyze(user_prompt, collect_data=False)  # Use existing data
        end_time = datetime.now()
        
        analysis_time = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️  Analysis completed in {analysis_time:.2f} seconds")
        print("\n" + "=" * 60)
        print("📊 ANALYSIS RESULTS:")
        print("=" * 60)
        print(result["analysis"])
        
        print("\n" + "=" * 60)
        print("📋 METADATA:")
        print("=" * 60)
        print(f"Model: {result['model_provider']} - {result['model_name']}")
        print(f"Session ID: {result['session_id']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Resources Used: {len(result['resources_used'])} files")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sonnet_3_7_test_{timestamp}.json"
        filepath = os.path.join("data_collection", "outputs", "analyst_reports", filename)
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")
        print("\n✅ Sonnet 3.7 test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Sonnet 3.7 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sonnet_3_7()
    sys.exit(0 if success else 1)
