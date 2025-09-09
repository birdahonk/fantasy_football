#!/usr/bin/env python3
"""
Master Data Validation Script

This script runs all validation checks to ensure 100% accuracy across
all data collection scripts and the comprehensive data processor.

Usage:
    python3 validate_all_data.py
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_validation_script(script_path: str, description: str) -> bool:
    """Run a validation script and return success status."""
    print(f"\n🔍 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {str(e)}")
        return False

def main():
    """Run all validation checks."""
    print("🚀 MASTER DATA VALIDATION STARTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    validation_scripts = [
        (
            "data_collection/scripts/validation/script_health_check.py",
            "Script Health Check - Validating all 14 data collection scripts"
        ),
        (
            "data_collection/scripts/validation/comprehensive_data_validator.py",
            "Comprehensive Data Validator - Checking data enrichment and matching"
        )
    ]
    
    all_passed = True
    
    for script_path, description in validation_scripts:
        if not run_validation_script(script_path, description):
            all_passed = False
    
    print("\n" + "=" * 60)
    print("📋 MASTER VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ All data collection scripts are working correctly")
        print("✅ 100% player matching and enrichment achieved")
        print("✅ No missing players or enrichment data")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED!")
        print("❌ Some data collection scripts are not working correctly")
        print("❌ Missing players or enrichment data detected")
        print("\nPlease check the individual validation reports for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
