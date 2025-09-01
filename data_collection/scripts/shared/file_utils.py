#!/usr/bin/env python3
"""
File Utilities for Data Collection Scripts

Provides consistent file naming, saving, and organization utilities
for all data extraction scripts.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class DataFileManager:
    """
    Manages file operations for data collection scripts.
    
    Provides consistent file naming, directory organization,
    and saving utilities for both clean markdown and raw JSON data.
    """
    
    def __init__(self, base_output_dir: str = None):
        """
        Initialize the file manager.
        
        Args:
            base_output_dir: Base directory for outputs (defaults to data_collection/outputs)
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Determine base output directory
        if base_output_dir:
            self.base_output_dir = Path(base_output_dir)
        else:
            # Default to data_collection/outputs relative to this script
            script_dir = Path(__file__).parent
            self.base_output_dir = script_dir.parent.parent / "outputs"
        
        # Ensure base directory exists
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Data file manager initialized with base directory: {self.base_output_dir}")
    
    def generate_timestamp(self) -> str:
        """Generate timestamp string for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_output_directory(self, api_name: str, script_name: str) -> Path:
        """
        Get the output directory for a specific API and script.
        
        Args:
            api_name: API name (yahoo, sleeper, tank01)
            script_name: Script name (my_roster, opponent_rosters, etc.)
            
        Returns:
            Path object for the output directory
        """
        output_dir = self.base_output_dir / api_name / script_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def generate_filename(self, timestamp: str, script_name: str, file_type: str) -> str:
        """
        Generate consistent filename for data files.
        
        Args:
            timestamp: Timestamp string
            script_name: Script name
            file_type: File type (clean, raw_data)
            
        Returns:
            Formatted filename
        """
        if file_type == "clean":
            return f"{timestamp}_{script_name}_clean.md"
        elif file_type == "raw_data":
            return f"{timestamp}_{script_name}_raw_data.json"
        else:
            return f"{timestamp}_{script_name}_{file_type}"
    
    def save_clean_data(self, api_name: str, script_name: str, data: str, timestamp: str = None) -> str:
        """
        Save clean markdown data to file.
        
        Args:
            api_name: API name (yahoo, sleeper, tank01)
            script_name: Script name (my_roster, etc.)
            data: Clean markdown content
            timestamp: Optional timestamp (generates new if not provided)
            
        Returns:
            Path to saved file
        """
        if not timestamp:
            timestamp = self.generate_timestamp()
        
        output_dir = self.get_output_directory(api_name, script_name)
        filename = self.generate_filename(timestamp, script_name, "clean")
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            
            self.logger.info(f"Clean data saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save clean data to {filepath}: {e}")
            raise
    
    def save_raw_data(self, api_name: str, script_name: str, data: Dict[str, Any], timestamp: str = None) -> str:
        """
        Save raw JSON data to file.
        
        Args:
            api_name: API name (yahoo, sleeper, tank01)
            script_name: Script name (my_roster, etc.)
            data: Raw API response data
            timestamp: Optional timestamp (generates new if not provided)
            
        Returns:
            Path to saved file
        """
        if not timestamp:
            timestamp = self.generate_timestamp()
        
        output_dir = self.get_output_directory(api_name, script_name)
        filename = self.generate_filename(timestamp, script_name, "raw_data")
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Raw data saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save raw data to {filepath}: {e}")
            raise
    
    def save_debug_data(self, api_name: str, script_name: str, data: Dict[str, Any], 
                       debug_type: str = "debug", timestamp: str = None) -> str:
        """
        Save debug data to debug directory.
        
        Args:
            api_name: API name
            script_name: Script name
            data: Debug data
            debug_type: Type of debug data
            timestamp: Optional timestamp
            
        Returns:
            Path to saved debug file
        """
        if not timestamp:
            timestamp = self.generate_timestamp()
        
        debug_dir = self.base_output_dir.parent / "debug" / "api_responses"
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{timestamp}_{api_name}_{script_name}_{debug_type}.json"
        filepath = debug_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Debug data saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save debug data to {filepath}: {e}")
            raise
    
    def save_execution_log(self, api_name: str, script_name: str, log_data: Dict[str, Any], 
                          timestamp: str = None) -> str:
        """
        Save execution log data.
        
        Args:
            api_name: API name
            script_name: Script name
            log_data: Execution log data
            timestamp: Optional timestamp
            
        Returns:
            Path to saved log file
        """
        if not timestamp:
            timestamp = self.generate_timestamp()
        
        log_dir = self.base_output_dir.parent / "debug" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{timestamp}_{api_name}_{script_name}_execution.json"
        filepath = log_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, default=str)
            
            self.logger.info(f"Execution log saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save execution log to {filepath}: {e}")
            raise
    
    def get_latest_file(self, api_name: str, script_name: str, file_type: str = "clean") -> Optional[str]:
        """
        Get the path to the latest file for a script.
        
        Args:
            api_name: API name
            script_name: Script name
            file_type: File type to look for
            
        Returns:
            Path to latest file or None if not found
        """
        output_dir = self.get_output_directory(api_name, script_name)
        
        # Look for files matching the pattern
        if file_type == "clean":
            pattern = f"*_{script_name}_clean.md"
        elif file_type == "raw_data":
            pattern = f"*_{script_name}_raw_data.json"
        else:
            pattern = f"*_{script_name}_*.{file_type}"
        
        files = list(output_dir.glob(pattern))
        
        if not files:
            return None
        
        # Sort by modification time and return the latest
        latest_file = max(files, key=os.path.getctime)
        return str(latest_file)
    
    def list_files(self, api_name: str, script_name: str) -> Dict[str, list]:
        """
        List all files for a script.
        
        Args:
            api_name: API name
            script_name: Script name
            
        Returns:
            Dict with 'clean' and 'raw_data' file lists
        """
        output_dir = self.get_output_directory(api_name, script_name)
        
        clean_files = list(output_dir.glob(f"*_{script_name}_clean.md"))
        raw_files = list(output_dir.glob(f"*_{script_name}_raw_data.json"))
        
        return {
            'clean': [str(f) for f in sorted(clean_files, reverse=True)],
            'raw_data': [str(f) for f in sorted(raw_files, reverse=True)]
        }

def main():
    """Test the file utilities."""
    print("📁 Testing Data File Manager")
    print("=" * 50)
    
    manager = DataFileManager()
    
    # Test timestamp generation
    timestamp = manager.generate_timestamp()
    print(f"Generated timestamp: {timestamp}")
    
    # Test directory creation
    test_dir = manager.get_output_directory("yahoo", "my_roster")
    print(f"Created directory: {test_dir}")
    
    # Test filename generation
    filename = manager.generate_filename(timestamp, "my_roster", "clean")
    print(f"Generated filename: {filename}")
    
    # Test saving sample data
    sample_clean = "# Test Clean Data\n\nThis is a test."
    sample_raw = {"test": "data", "timestamp": timestamp}
    
    try:
        clean_path = manager.save_clean_data("yahoo", "test", sample_clean, timestamp)
        raw_path = manager.save_raw_data("yahoo", "test", sample_raw, timestamp)
        
        print(f"✅ Test files saved:")
        print(f"   Clean: {clean_path}")
        print(f"   Raw: {raw_path}")
        
        # Test file listing
        files = manager.list_files("yahoo", "test")
        print(f"✅ Files found: {len(files['clean'])} clean, {len(files['raw_data'])} raw")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
