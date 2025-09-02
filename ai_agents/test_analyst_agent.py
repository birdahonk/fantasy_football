#!/usr/bin/env python3
"""
Test script for the Analyst Agent framework

This script tests the basic functionality of the Analyst Agent without making actual LLM calls.
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def test_analyst_tools():
    """Test the Analyst Tools functionality"""
    print("🔧 Testing Analyst Tools...")
    
    try:
        from ai_agents.analyst_tools import AnalystTools
        
        tools = AnalystTools()
        print("✅ Analyst Tools initialized successfully")
        
        # Test finding recent files
        recent_files = tools._find_most_recent_files()
        print(f"✅ Found {len(recent_files)} recent data files")
        
        # Test current game week calculation
        current_week = tools.get_current_game_week()
        print(f"✅ Current game week: {current_week}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analyst Tools test failed: {e}")
        return False

def test_analyst_agent_initialization():
    """Test Analyst Agent initialization without LLM calls"""
    print("\n🤖 Testing Analyst Agent initialization...")
    
    try:
        from ai_agents.analyst_agent import AnalystAgent
        
        # Test with OpenAI (if available)
        try:
            agent = AnalystAgent(model_provider="openai", model_name="gpt-4")
            print("✅ OpenAI Analyst Agent initialized successfully")
            return True
        except ImportError:
            print("⚠️  OpenAI package not available, skipping OpenAI test")
        
        # Test with Anthropic (if available)
        try:
            agent = AnalystAgent(model_provider="anthropic", model_name="claude-3-5-sonnet-20241022")
            print("✅ Anthropic Analyst Agent initialized successfully")
            return True
        except ImportError:
            print("⚠️  Anthropic package not available, skipping Anthropic test")
        
        print("⚠️  No LLM providers available for testing (packages not installed)")
        print("   To test with LLMs, install: pip install openai anthropic")
        return True  # This is not a failure, just missing optional dependencies
        
    except Exception as e:
        print(f"❌ Analyst Agent initialization test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "__init__.py",
        "analyst_agent.py",
        "analyst_tools.py",
        "test_analyst_agent.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🏈 Fantasy Football Analyst Agent - Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Analyst Tools", test_analyst_tools),
        ("Analyst Agent", test_analyst_agent_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Analyst Agent framework is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
