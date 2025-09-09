#!/usr/bin/env python3
"""
Test Analyst Agent with Streamlined Data

Tests the analyst agent with the new streamlined comprehensive data structure.
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from ai_agents.analyst_agent import AnalystAgent

def test_analyst_agent():
    """Test the analyst agent with streamlined data"""
    
    print("🤖 TESTING ANALYST AGENT WITH STREAMLINED DATA")
    print("=" * 60)
    
    try:
        # Initialize analyst agent
        print("Initializing analyst agent...")
        agent = AnalystAgent()
        
        # Test comprehensive analysis
        print("Running comprehensive analysis...")
        result = agent.analyze_with_comprehensive_data(
            user_prompt="Analyze my roster and provide recommendations for Week 1"
        )
        
        if result.get("analysis_type") == "comprehensive_data":
            print("✅ Analyst agent analysis completed successfully!")
            
            # Show results summary
            print(f"\n📊 ANALYSIS RESULTS")
            print("-" * 40)
            print(f"Analysis type: {result.get('analysis_type')}")
            print(f"Model provider: {result.get('model_provider')}")
            print(f"Model name: {result.get('model_name')}")
            print(f"Total tokens: {result.get('total_tokens', 'Unknown')}")
            
            # Show saved files
            saved_files = result.get("saved_files", {})
            if saved_files:
                print(f"\n💾 SAVED FILES")
                print("-" * 40)
                for file_type, file_path in saved_files.items():
                    print(f"{file_type}: {file_path}")
            
            # Show analysis preview
            analysis = result.get("analysis", "")
            if analysis:
                print(f"\n📝 ANALYSIS PREVIEW")
                print("-" * 40)
                # Show first 500 characters
                preview = analysis[:500] + "..." if len(analysis) > 500 else analysis
                print(preview)
            
            return True
        else:
            print("❌ Analyst agent analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analyst agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_analyst_agent()
    
    if success:
        print(f"\n🎉 SUCCESS: Analyst agent is working with streamlined data!")
    else:
        print(f"\n❌ FAILED: Analyst agent needs troubleshooting")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
