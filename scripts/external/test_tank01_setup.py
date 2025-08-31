#!/usr/bin/env python3
"""
Test Tank01 API Setup

Simple test to verify RapidAPI connection and Tank01 API access.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv

def test_rapidapi_setup():
    """Test if RapidAPI key is properly configured."""
    print("🔧 Testing RapidAPI Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv('RAPIDAPI_KEY')
    
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in environment")
        print("\n🔧 Setup Instructions:")
        print("1. Create .env file in project root:")
        print("   echo 'RAPIDAPI_KEY=your_key_here' >> .env")
        print("2. Replace 'your_key_here' with your actual RapidAPI key")
        print("3. Your key should be ~50 characters long")
        return False
    
    # Validate key format (basic check)
    if len(api_key) < 20:
        print(f"⚠️  API key seems too short: {len(api_key)} characters")
        print("   RapidAPI keys are typically 40-60 characters")
        return False
    
    # Mask key for display
    masked_key = api_key[:8] + "..." + api_key[-8:] if len(api_key) > 16 else "***"
    
    print(f"✅ RAPIDAPI_KEY found: {masked_key}")
    print(f"📏 Key length: {len(api_key)} characters")
    
    return True

def test_tank01_import():
    """Test if Tank01 client can be imported."""
    print("\n📦 Testing Tank01 Client Import")
    print("=" * 40)
    
    try:
        from tank01_client import Tank01Client
        print("✅ Tank01Client imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Tank01Client: {e}")
        return False

def main():
    """Run all setup tests."""
    print("🏈 Tank01 API Setup Test")
    print("=" * 50)
    
    # Test 1: RapidAPI key setup
    api_key_ok = test_rapidapi_setup()
    
    # Test 2: Import test
    import_ok = test_tank01_import()
    
    # Summary
    print("\n📊 Setup Summary:")
    print(f"  • RapidAPI Key: {'✅ OK' if api_key_ok else '❌ Missing'}")
    print(f"  • Tank01 Client: {'✅ OK' if import_ok else '❌ Error'}")
    
    if api_key_ok and import_ok:
        print("\n🎉 Setup complete! Ready to test Tank01 API")
        print("Next step: Run tank01_client.py to test API connection")
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above.")
    
    return api_key_ok and import_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
