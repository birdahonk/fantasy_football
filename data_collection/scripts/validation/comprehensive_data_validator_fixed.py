#!/usr/bin/env python3
"""
Comprehensive Data Validation Script - FIXED VERSION

This script validates that ALL data collection scripts are working correctly
and that NO players or enrichment data is missing from the final output.

Requirements:
- Yahoo scripts: Must collect ALL players from roster/opponent/available
- Sleeper scripts: Must match and enrich EVERY player from Yahoo data
- Tank01 scripts: Must match and enrich EVERY player from Yahoo data
- Final output: Must have 100% enrichment with NO missing data

Usage:
    python3 data_collection/scripts/validation/comprehensive_data_validator_fixed.py
"""

import os
import sys
import json
import glob
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from ai_agents.comprehensive_data_processor import ComprehensiveDataProcessor
from config.player_limits import DEFAULT_PLAYER_LIMITS

class ComprehensiveDataValidator:
    """Validates that all data collection scripts are working correctly."""
    
    def __init__(self, outputs_dir: str = "data_collection/outputs"):
        self.outputs_dir = outputs_dir
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'total_errors': 0,
            'critical_errors': [],
            'warnings': [],
            'validation_summary': {}
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_all_data(self) -> Dict[str, Any]:
        """Run comprehensive validation of all data collection outputs."""
        self.logger.info("🔍 COMPREHENSIVE DATA VALIDATION STARTING")
        self.logger.info("=" * 60)
        
        # 1. Validate data collection script outputs
        self._validate_yahoo_data()
        self._validate_sleeper_data()
        self._validate_tank01_data()
        
        # 2. Validate comprehensive data processor
        self._validate_comprehensive_processor()
        
        # 3. Generate validation report
        self._generate_validation_report()
        
        return self.validation_results
    
    def _validate_yahoo_data(self):
        """Validate Yahoo data collection completeness."""
        self.logger.info("📊 VALIDATING YAHOO DATA COLLECTION")
        self.logger.info("-" * 40)
        
        # Check my roster
        my_roster_files = self._find_latest_files("yahoo/my_roster", "*_raw_data.json")
        if not my_roster_files:
            self._add_critical_error("No Yahoo my_roster data found")
            return
        
        my_roster_data = self._load_json_file(my_roster_files[0])
        my_roster_players = self._extract_roster_players(my_roster_data)
        
        self.logger.info(f"✅ My roster: {len(my_roster_players)} players")
        
        # Check opponent roster
        opponent_files = self._find_latest_files("yahoo/opponent_rosters", "*_raw_data.json")
        if not opponent_files:
            self._add_critical_error("No Yahoo opponent_rosters data found")
            return
        
        opponent_data = self._load_json_file(opponent_files[0])
        opponent_players = self._extract_opponent_players(opponent_data)
        
        self.logger.info(f"✅ Opponent roster: {len(opponent_players)} players")
        
        # Check available players
        available_files = self._find_latest_files("yahoo/available_players", "*_raw_data.json")
        if not available_files:
            self._add_critical_error("No Yahoo available_players data found")
            return
        
        available_data = self._load_json_file(available_files[0])
        available_players = self._extract_available_players(available_data)
        
        self.logger.info(f"✅ Available players: {len(available_players)} players")
        
        # Store for later validation
        self.validation_results['yahoo_data'] = {
            'my_roster_players': my_roster_players,
            'opponent_players': opponent_players,
            'available_players': available_players
        }
    
    def _validate_sleeper_data(self):
        """Validate Sleeper data collection and matching."""
        self.logger.info("📊 VALIDATING SLEEPER DATA COLLECTION")
        self.logger.info("-" * 40)
        
        # Check my roster
        my_roster_files = self._find_latest_files("sleeper/my_roster", "*_raw_data.json")
        if not my_roster_files:
            self._add_critical_error("No Sleeper my_roster data found")
            return
        
        my_roster_data = self._load_json_file(my_roster_files[0])
        my_roster_matched = len(my_roster_data.get('matched_players', []))
        my_roster_unmatched = len(my_roster_data.get('unmatched_players', []))
        
        if my_roster_unmatched > 0:
            self._add_critical_error(f"Sleeper my_roster: {my_roster_unmatched} unmatched players")
        else:
            self.logger.info(f"✅ My roster: {my_roster_matched} matched, {my_roster_unmatched} unmatched")
        
        # Check opponent roster
        opponent_files = self._find_latest_files("sleeper/opponent_roster", "*_raw_data.json")
        if not opponent_files:
            self._add_critical_error("No Sleeper opponent_roster data found")
            return
        
        opponent_data = self._load_json_file(opponent_files[0])
        opponent_matched = len(opponent_data.get('matched_players', []))
        opponent_unmatched = len(opponent_data.get('unmatched_players', []))
        
        if opponent_unmatched > 0:
            self._add_critical_error(f"Sleeper opponent_roster: {opponent_unmatched} unmatched players")
        else:
            self.logger.info(f"✅ Opponent roster: {opponent_matched} matched, {opponent_unmatched} unmatched")
        
        # Check available players
        available_files = self._find_latest_files("sleeper/available_players", "*_raw_data.json")
        if not available_files:
            self._add_critical_error("No Sleeper available_players data found")
            return
        
        available_data = self._load_json_file(available_files[0])
        available_matched = len(available_data.get('matched_players', []))
        available_unmatched = len(available_data.get('unmatched_players', []))
        
        if available_unmatched > 0:
            self._add_critical_error(f"Sleeper available_players: {available_unmatched} unmatched players")
        else:
            self.logger.info(f"✅ Available players: {available_matched} matched, {available_unmatched} unmatched")
        
        # Store for later validation
        self.validation_results['sleeper_data'] = {
            'my_roster_matched': my_roster_matched,
            'my_roster_unmatched': my_roster_unmatched,
            'opponent_matched': opponent_matched,
            'opponent_unmatched': opponent_unmatched,
            'available_matched': available_matched,
            'available_unmatched': available_unmatched
        }
    
    def _validate_tank01_data(self):
        """Validate Tank01 data collection and matching."""
        self.logger.info("📊 VALIDATING TANK01 DATA COLLECTION")
        self.logger.info("-" * 40)
        
        # Check my roster
        my_roster_files = self._find_latest_files("tank01/my_roster", "*_raw_data.json")
        if not my_roster_files:
            self._add_critical_error("No Tank01 my_roster data found")
            return
        
        my_roster_data = self._load_json_file(my_roster_files[0])
        my_roster_matched = len(my_roster_data.get('matched_players', []))
        my_roster_unmatched = len(my_roster_data.get('unmatched_players', []))
        
        if my_roster_unmatched > 0:
            self._add_critical_error(f"Tank01 my_roster: {my_roster_unmatched} unmatched players")
        else:
            self.logger.info(f"✅ My roster: {my_roster_matched} matched, {my_roster_unmatched} unmatched")
        
        # Check opponent roster
        opponent_files = self._find_latest_files("tank01/opponent_roster", "*_raw_data.json")
        if not opponent_files:
            self._add_critical_error("No Tank01 opponent_roster data found")
            return
        
        opponent_data = self._load_json_file(opponent_files[0])
        opponent_matched = len(opponent_data.get('matched_players', []))
        opponent_unmatched = len(opponent_data.get('unmatched_players', []))
        
        if opponent_unmatched > 0:
            self._add_critical_error(f"Tank01 opponent_roster: {opponent_unmatched} unmatched players")
        else:
            self.logger.info(f"✅ Opponent roster: {opponent_matched} matched, {opponent_unmatched} unmatched")
        
        # Check available players
        available_files = self._find_latest_files("tank01/available_players", "*_raw_data.json")
        if not available_files:
            self._add_critical_error("No Tank01 available_players data found")
            return
        
        available_data = self._load_json_file(available_files[0])
        processed_data = available_data.get('processed_data', {})
        available_players = processed_data.get('available_players', [])
        available_matched = len(available_players)
        
        # Check for unmatched players in efficiency metrics
        efficiency_metrics = processed_data.get('efficiency_metrics', {})
        available_unmatched = efficiency_metrics.get('players_unmatched', 0)
        
        if available_unmatched > 0:
            self._add_critical_error(f"Tank01 available_players: {available_unmatched} unmatched players")
        else:
            self.logger.info(f"✅ Available players: {available_matched} matched, {available_unmatched} unmatched")
        
        # Store for later validation
        self.validation_results['tank01_data'] = {
            'my_roster_matched': my_roster_matched,
            'my_roster_unmatched': my_roster_unmatched,
            'opponent_matched': opponent_matched,
            'opponent_unmatched': opponent_unmatched,
            'available_matched': available_matched,
            'available_unmatched': available_unmatched
        }
    
    def _validate_comprehensive_processor(self):
        """Validate comprehensive data processor output."""
        self.logger.info("📊 VALIDATING COMPREHENSIVE DATA PROCESSOR")
        self.logger.info("-" * 40)
        
        try:
            # Initialize ComprehensiveDataProcessor with required parameters
            data_dir = "data_collection/outputs"
            player_limits = DEFAULT_PLAYER_LIMITS
            processor = ComprehensiveDataProcessor(data_dir, player_limits)
            data = processor.process_all_data()
            
            # Validate my roster
            my_roster = data.get('my_roster', {})
            my_roster_players = my_roster.get('players', [])
            my_roster_total = len(my_roster_players)
            
            my_roster_tank01_count = 0
            my_roster_sleeper_count = 0
            
            if isinstance(my_roster_players, list):
                for player in my_roster_players:
                    if isinstance(player, dict):
                        if player.get('tank01_data'):
                            my_roster_tank01_count += 1
                        if player.get('sleeper_data'):
                            my_roster_sleeper_count += 1
            
            if my_roster_tank01_count < my_roster_total:
                self._add_critical_error(f"My roster Tank01 enrichment: {my_roster_tank01_count}/{my_roster_total}")
            else:
                self.logger.info(f"✅ My roster Tank01 enrichment: {my_roster_tank01_count}/{my_roster_total}")
            
            if my_roster_sleeper_count < my_roster_total:
                self._add_critical_error(f"My roster Sleeper enrichment: {my_roster_sleeper_count}/{my_roster_total}")
            else:
                self.logger.info(f"✅ My roster Sleeper enrichment: {my_roster_sleeper_count}/{my_roster_total}")
            
            # Validate opponent roster
            opponent_roster = data.get('opponent_roster', {})
            opponent_roster_players = opponent_roster.get('players', [])
            opponent_roster_total = len(opponent_roster_players)
            
            opponent_tank01_count = 0
            opponent_sleeper_count = 0
            
            if isinstance(opponent_roster_players, list):
                for player in opponent_roster_players:
                    if isinstance(player, dict):
                        if player.get('tank01_data'):
                            opponent_tank01_count += 1
                        if player.get('sleeper_data'):
                            opponent_sleeper_count += 1
            
            if opponent_tank01_count < opponent_roster_total:
                self._add_critical_error(f"Opponent roster Tank01 enrichment: {opponent_tank01_count}/{opponent_roster_total}")
            else:
                self.logger.info(f"✅ Opponent roster Tank01 enrichment: {opponent_tank01_count}/{opponent_roster_total}")
            
            if opponent_sleeper_count < opponent_roster_total:
                self._add_critical_error(f"Opponent roster Sleeper enrichment: {opponent_sleeper_count}/{opponent_roster_total}")
            else:
                self.logger.info(f"✅ Opponent roster Sleeper enrichment: {opponent_sleeper_count}/{opponent_roster_total}")
            
            # Validate available players
            available_players = data.get('available_players', {})
            players_by_position = available_players.get('players_by_position', {})
            available_players_total = sum(len(players) for players in players_by_position.values() if isinstance(players, list))
            
            # Log position counts for debugging
            self.logger.info(f"Available players by position:")
            for position, players in players_by_position.items():
                if isinstance(players, list):
                    self.logger.info(f"  {position}: {len(players)} players")
            
            # Count enrichment and identify missing players
            available_tank01_count = 0
            available_sleeper_count = 0
            missing_tank01_players = []
            missing_sleeper_players = []
            
            for position, players in players_by_position.items():
                if isinstance(players, list):
                    for player in players:
                        if isinstance(player, dict):
                            player_name = player.get('name', 'Unknown')
                            yahoo_data = player.get('yahoo_data', {})
                            yahoo_name = yahoo_data.get('name', {}).get('full', 'Unknown') if isinstance(yahoo_data, dict) else 'Unknown'
                            
                            if player.get('tank01_data'):
                                available_tank01_count += 1
                            else:
                                missing_tank01_players.append(f"{position}: {player_name} (Yahoo: {yahoo_name})")
                            
                            if player.get('sleeper_data'):
                                available_sleeper_count += 1
                            else:
                                missing_sleeper_players.append(f"{position}: {player_name} (Yahoo: {yahoo_name})")
            
            if available_tank01_count < available_players_total:
                self._add_critical_error(f"Available players Tank01 enrichment: {available_tank01_count}/{available_players_total}")
                self.logger.error(f"Missing Tank01 data for {len(missing_tank01_players)} players:")
                for player in missing_tank01_players:
                    self.logger.error(f"  - {player}")
            else:
                self.logger.info(f"✅ Available players Tank01 enrichment: {available_tank01_count}/{available_players_total}")
            
            if available_sleeper_count < available_players_total:
                self._add_critical_error(f"Available players Sleeper enrichment: {available_sleeper_count}/{available_players_total}")
                self.logger.error(f"Missing Sleeper data for {len(missing_sleeper_players)} players:")
                for player in missing_sleeper_players:
                    self.logger.error(f"  - {player}")
            else:
                self.logger.info(f"✅ Available players Sleeper enrichment: {available_sleeper_count}/{available_players_total}")
            
            # Store results
            self.validation_results['comprehensive_processor'] = {
                'my_roster_total': my_roster_total,
                'my_roster_tank01': my_roster_tank01_count,
                'my_roster_sleeper': my_roster_sleeper_count,
                'opponent_total': opponent_roster_total,
                'opponent_tank01': opponent_tank01_count,
                'opponent_sleeper': opponent_sleeper_count,
                'available_total': available_players_total,
                'available_tank01': available_tank01_count,
                'available_sleeper': available_sleeper_count
            }
            
        except Exception as e:
            self._add_critical_error(f"Comprehensive data processor failed: {str(e)}")
    
    def _generate_validation_report(self):
        """Generate final validation report."""
        self.logger.info("📋 GENERATING VALIDATION REPORT")
        self.logger.info("-" * 40)
        
        total_errors = len(self.validation_results['critical_errors'])
        total_warnings = len(self.validation_results['warnings'])
        
        if total_errors == 0:
            self.logger.info("🎉 VALIDATION PASSED - ALL DATA COLLECTION SCRIPTS WORKING CORRECTLY!")
            self.logger.info("✅ 100% player matching and enrichment achieved")
        else:
            self.logger.error(f"❌ VALIDATION FAILED - {total_errors} critical errors found")
            for error in self.validation_results['critical_errors']:
                self.logger.error(f"   - {error}")
        
        if total_warnings > 0:
            self.logger.warning(f"⚠️  {total_warnings} warnings found")
            for warning in self.validation_results['warnings']:
                self.logger.warning(f"   - {warning}")
        
        # Save validation report
        self._save_validation_report()
    
    def _save_validation_report(self):
        """Save validation report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"data_collection/outputs/validation_tests/{timestamp}_validation_report.json"
        
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        self.logger.info(f"📄 Validation report saved: {report_file}")
    
    def _find_latest_files(self, subdir: str, pattern: str) -> List[str]:
        """Find latest files matching pattern in subdirectory."""
        search_path = os.path.join(self.outputs_dir, subdir, "**", pattern)
        files = glob.glob(search_path, recursive=True)
        # Sort by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        return files
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file safely."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self._add_critical_error(f"Failed to load {file_path}: {str(e)}")
            return {}
    
    def _extract_roster_players(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract players from Yahoo roster data."""
        players = []
        # Yahoo my_roster data structure - CORRECTED based on documented schema
        roster_raw = data.get('roster_raw', {})
        fantasy_content = roster_raw.get('fantasy_content', {})
        team_data = fantasy_content.get('team', [])
        
        if team_data and len(team_data) > 1:
            # team_data[0] is team metadata array, team_data[1] is roster data
            roster_data = team_data[1]
            if isinstance(roster_data, dict) and 'roster' in roster_data:
                roster = roster_data['roster']
                # Extract players from roster structure - CORRECTED
                for key, value in roster.items():
                    if key.isdigit() and isinstance(value, dict) and 'players' in value:
                        players_data = value['players']
                        for player_key, player_data in players_data.items():
                            if player_key.isdigit() and isinstance(player_data, dict) and 'player' in player_data:
                                player_info = player_data['player']
                                if isinstance(player_info, list) and len(player_info) > 0:
                                    players.append(player_info[0])
        
        return players
    
    def _extract_opponent_players(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract players from Yahoo opponent roster data."""
        players = []
        # Yahoo opponent_rosters data structure - CORRECTED based on documented schema
        rosters = data.get('rosters', {})
        
        for team_key, team_data in rosters.items():
            if isinstance(team_data, dict) and 'players' in team_data:
                # team_data is already the roster data with players array
                players_data = team_data['players']
                if isinstance(players_data, list):
                    players.extend(players_data)
        
        return players
    
    def _extract_available_players(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract players from Yahoo available players data."""
        return data.get('players', [])
    
    def _add_critical_error(self, error: str):
        """Add critical error to validation results."""
        self.validation_results['critical_errors'].append(error)
        self.validation_results['total_errors'] += 1
        self.logger.error(f"❌ CRITICAL: {error}")
    
    def _add_warning(self, warning: str):
        """Add warning to validation results."""
        self.validation_results['warnings'].append(warning)
        self.logger.warning(f"⚠️  WARNING: {warning}")

def main():
    """Main validation function."""
    validator = ComprehensiveDataValidator()
    results = validator.validate_all_data()
    
    # Exit with error code if validation failed
    if results['total_errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
