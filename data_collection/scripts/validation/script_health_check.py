#!/usr/bin/env python3
"""
Script Health Check System

This script validates that all 14 data collection scripts are working correctly
by running them individually and checking their outputs.

Usage:
    python3 data_collection/scripts/validation/script_health_check.py
"""

import os
import sys
import subprocess
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

class ScriptHealthChecker:
    """Checks health of all data collection scripts."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "data_collection" / "scripts"
        self.outputs_dir = self.project_root / "data_collection" / "outputs"
        
        self.health_results = {
            'timestamp': datetime.now().isoformat(),
            'total_scripts': 0,
            'passed_scripts': 0,
            'failed_scripts': 0,
            'script_results': {}
        }
        
        # Define all 14 scripts to check
        self.scripts_to_check = [
            # Yahoo scripts
            ('yahoo', 'my_roster.py', 'My Roster'),
            ('yahoo', 'opponent_rosters.py', 'Opponent Rosters'),
            ('yahoo', 'available_players.py', 'Available Players'),
            ('yahoo', 'team_matchups.py', 'Team Matchups'),
            ('yahoo', 'transaction_trends.py', 'Transaction Trends'),
            ('yahoo', 'league_settings.py', 'League Settings'),
            ('yahoo', 'season_info.py', 'Season Info'),
            
            # Sleeper scripts
            ('sleeper', 'my_roster.py', 'Sleeper My Roster'),
            ('sleeper', 'opponent_roster.py', 'Sleeper Opponent Roster'),
            ('sleeper', 'available_players.py', 'Sleeper Available Players'),
            ('sleeper', 'trending.py', 'Sleeper Trending'),
            
            # Tank01 scripts
            ('tank01', 'my_roster.py', 'Tank01 My Roster'),
            ('tank01', 'opponent_roster.py', 'Tank01 Opponent Roster'),
            ('tank01', 'available_players.py', 'Tank01 Available Players'),
        ]
    
    def check_all_scripts(self) -> Dict[str, Any]:
        """Check health of all scripts."""
        print("🔍 SCRIPT HEALTH CHECK STARTING")
        print("=" * 60)
        
        for api, script_name, display_name in self.scripts_to_check:
            self._check_script(api, script_name, display_name)
        
        self._generate_health_report()
        return self.health_results
    
    def _check_script(self, api: str, script_name: str, display_name: str):
        """Check individual script health."""
        print(f"\n🔍 Checking {display_name}...")
        
        script_path = self.scripts_dir / api / script_name
        if not script_path.exists():
            self._record_script_failure(api, script_name, display_name, "Script file not found")
            return
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Check if output files were created
                output_files = self._find_script_outputs(api, script_name)
                if output_files:
                    self._record_script_success(api, script_name, display_name, output_files)
                else:
                    self._record_script_failure(api, script_name, display_name, "No output files created")
            else:
                self._record_script_failure(api, script_name, display_name, f"Script failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self._record_script_failure(api, script_name, display_name, "Script timed out")
        except Exception as e:
            self._record_script_failure(api, script_name, display_name, f"Unexpected error: {str(e)}")
    
    def _find_script_outputs(self, api: str, script_name: str) -> List[str]:
        """Find output files created by script."""
        # Look for recent files in the appropriate output directory
        search_patterns = {
            'my_roster.py': f"{api}/my_roster/**/*_raw_data.json",
            'opponent_roster.py': f"{api}/opponent_roster/**/*_raw_data.json",
            'opponent_rosters.py': f"{api}/opponent_rosters/**/*_raw_data.json",
            'available_players.py': f"{api}/available_players/**/*_raw_data.json",
            'team_matchups.py': f"{api}/team_matchups/**/*_raw_data.json",
            'transaction_trends.py': f"{api}/transaction_trends/**/*_raw_data.json",
            'league_settings.py': f"{api}/league_settings/**/*_raw_data.json",
            'season_info.py': f"{api}/season_info/**/*_raw_data.json",
            'trending.py': f"{api}/trending/**/*_raw_data.json",
        }
        
        pattern = search_patterns.get(script_name, f"{api}/**/*_raw_data.json")
        search_path = self.outputs_dir / pattern
        
        files = glob.glob(str(search_path), recursive=True)
        
        # Filter to recent files (last 10 minutes)
        recent_files = []
        cutoff_time = datetime.now().timestamp() - 600  # 10 minutes ago
        
        for file_path in files:
            if os.path.getmtime(file_path) > cutoff_time:
                recent_files.append(file_path)
        
        return sorted(recent_files)
    
    def _record_script_success(self, api: str, script_name: str, display_name: str, output_files: List[str]):
        """Record successful script execution."""
        self.health_results['passed_scripts'] += 1
        self.health_results['script_results'][f"{api}_{script_name}"] = {
            'status': 'PASSED',
            'display_name': display_name,
            'output_files': output_files,
            'error': None
        }
        print(f"   ✅ PASSED - {len(output_files)} output files created")
    
    def _record_script_failure(self, api: str, script_name: str, display_name: str, error: str):
        """Record failed script execution."""
        self.health_results['failed_scripts'] += 1
        self.health_results['script_results'][f"{api}_{script_name}"] = {
            'status': 'FAILED',
            'display_name': display_name,
            'output_files': [],
            'error': error
        }
        print(f"   ❌ FAILED - {error}")
    
    def _generate_health_report(self):
        """Generate health check report."""
        self.health_results['total_scripts'] = len(self.scripts_to_check)
        
        print("\n" + "=" * 60)
        print("📋 SCRIPT HEALTH CHECK REPORT")
        print("=" * 60)
        
        print(f"Total Scripts: {self.health_results['total_scripts']}")
        print(f"Passed: {self.health_results['passed_scripts']}")
        print(f"Failed: {self.health_results['failed_scripts']}")
        
        if self.health_results['failed_scripts'] > 0:
            print("\n❌ FAILED SCRIPTS:")
            for script_id, result in self.health_results['script_results'].items():
                if result['status'] == 'FAILED':
                    print(f"   - {result['display_name']}: {result['error']}")
        else:
            print("\n🎉 ALL SCRIPTS PASSED!")
        
        # Save health report
        self._save_health_report()
    
    def _save_health_report(self):
        """Save health check report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"data_collection/outputs/validation_tests/{timestamp}_health_check_report.json"
        
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.health_results, f, indent=2)
        
        print(f"\n📄 Health check report saved: {report_file}")

def main():
    """Main health check function."""
    checker = ScriptHealthChecker()
    results = checker.check_all_scripts()
    
    # Exit with error code if any scripts failed
    if results['failed_scripts'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
