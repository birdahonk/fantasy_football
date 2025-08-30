#!/usr/bin/env python3
"""
Test Setup Script
Verifies basic functionality of the Fantasy Football AI General Manager
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append('scripts')

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from utils import format_timestamp, get_current_week, ensure_directories
        print("✅ Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    try:
        from yahoo_connect import YahooFantasyAPI
        print("✅ Yahoo API module imported successfully")
    except ImportError as e:
        print(f"❌ Yahoo API import failed: {e}")
        return False
    
    try:
        from roster_analyzer import RosterAnalyzer
        print("✅ Roster analyzer imported successfully")
    except ImportError as e:
        print(f"❌ Roster analyzer import failed: {e}")
        return False
    
    try:
        from free_agent_analyzer import FreeAgentAnalyzer
        print("✅ Free agent analyzer imported successfully")
    except ImportError as e:
        print(f"❌ Free agent analyzer import failed: {e}")
        return False
    
    try:
        from matchup_analyzer import MatchupAnalyzer
        print("✅ Matchup analyzer imported successfully")
    except ImportError as e:
        print(f"❌ Matchup analyzer import failed: {e}")
        return False
    
    try:
        from performance_tracker import PerformanceTracker
        print("✅ Performance tracker imported successfully")
    except ImportError as e:
        print(f"❌ Performance tracker import failed: {e}")
        return False
    
    try:
        from main_analyzer import FantasyFootballAnalyzer
        print("✅ Main analyzer imported successfully")
    except ImportError as e:
        print(f"❌ Main analyzer import failed: {e}")
        return False
    
    return True

def test_utility_functions():
    """Test basic utility functions"""
    print("\n🔧 Testing utility functions...")
    
    try:
        from utils import format_timestamp, get_current_week, ensure_directories
        
        # Test timestamp formatting
        timestamp = format_timestamp()
        print(f"✅ Timestamp format: {timestamp}")
        
        # Test week calculation
        week = get_current_week()
        print(f"✅ Current week: {week}")
        
        # Test directory creation
        ensure_directories()
        print("✅ Directory structure verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility function test failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'scripts',
        'analysis',
        'config',
        'logs',
        'documentation'
    ]
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    return True

def test_file_permissions():
    """Test that scripts are executable"""
    print("\n🔐 Testing file permissions...")
    
    script_files = [
        'scripts/utils.py',
        'scripts/yahoo_connect.py',
        'scripts/roster_analyzer.py',
        'scripts/free_agent_analyzer.py',
        'scripts/matchup_analyzer.py',
        'scripts/performance_tracker.py',
        'scripts/main_analyzer.py'
    ]
    
    for script_file in script_files:
        if Path(script_file).exists():
            if os.access(script_file, os.X_OK):
                print(f"✅ {script_file} is executable")
            else:
                print(f"❌ {script_file} is not executable")
                return False
        else:
            print(f"❌ {script_file} does not exist")
            return False
    
    return True

def test_environment_setup():
    """Test environment configuration"""
    print("\n⚙️ Testing environment setup...")
    
    # Check for .env file
    if Path('.env').exists():
        print("✅ .env file exists")
    else:
        print("⚠️ .env file not found (copy from env_template.txt)")
    
    # Check for requirements.txt
    if Path('requirements.txt').exists():
        print("✅ requirements.txt exists")
    else:
        print("❌ requirements.txt missing")
        return False
    
    # Check for README
    if Path('README.md').exists():
        print("✅ README.md exists")
    else:
        print("❌ README.md missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🏈 Fantasy Football AI General Manager - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Utility Functions", test_utility_functions),
        ("Directory Structure", test_directory_structure),
        ("File Permissions", test_file_permissions),
        ("Environment Setup", test_environment_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready for use.")
        print("\n📋 Next steps:")
        print("1. Copy env_template.txt to .env and fill in your API keys")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Set up Yahoo Fantasy API credentials")
        print("4. Test with: python3 scripts/main_analyzer.py status")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
