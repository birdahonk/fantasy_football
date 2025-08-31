#!/usr/bin/env python3
"""
Utility functions for Fantasy Football AI General Manager
Common helper functions used across all analysis scripts
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def format_timestamp() -> str:
    """Generate consistent timestamp format for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_current_week() -> int:
    """Get current NFL week number (approximate)"""
    # This is a simple approximation - could be enhanced with actual NFL schedule
    start_date = datetime(2024, 9, 5)  # Approximate NFL season start
    current_date = datetime.now()
    week = ((current_date - start_date).days // 7) + 1
    return max(1, min(18, week))  # NFL season is 18 weeks

def create_weekly_directory(week_number: int) -> Path:
    """Create and return path to weekly analysis directory"""
    week_dir = Path(f"analysis/week_{week_number}")
    week_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created weekly directory: {week_dir}")
    return week_dir

def save_markdown_report(content: str, filename: str, week_number: Optional[int] = None) -> str:
    """Save markdown report to appropriate directory"""
    if week_number is None:
        week_number = get_current_week()
    
    week_dir = create_weekly_directory(week_number)
    timestamp = format_timestamp()
    
    # Ensure filename has proper extension
    if not filename.endswith('.md'):
        filename += '.md'
    
    # Add timestamp prefix if not already present
    if not filename.startswith(timestamp):
        filename = f"{timestamp}_{filename}"
    
    filepath = week_dir / filename
    filepath.write_text(content, encoding='utf-8')
    
    logger.info(f"Saved markdown report: {filepath}")
    return str(filepath)

def load_config(config_name: str) -> Dict[str, Any]:
    """Load configuration from config directory"""
    config_path = Path(f"config/{config_name}.json")
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded config: {config_name}")
        return config
    except Exception as e:
        logger.error(f"Error loading config {config_name}: {e}")
        return {}

def save_config(config_name: str, config_data: Dict[str, Any]) -> bool:
    """Save configuration to config directory"""
    config_path = Path(f"config/{config_name}.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        logger.info(f"Saved config: {config_name}")
        return True
    except Exception as e:
        logger.error(f"Error saving config {config_name}: {e}")
        return False

def log_api_call(endpoint: str, response_time: float, status_code: int = 200) -> None:
    """Log API call details for monitoring"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'response_time': response_time,
        'status_code': status_code
    }
    
    # Log to file
    log_file = Path('logs/api_calls.log')
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Also log to main logger
    logger.info(f"API call: {endpoint} - {status_code} - {response_time:.2f}s")

def ensure_directories() -> None:
    """Ensure all required directories exist"""
    directories = [
        'analysis',
        'config',
        'logs',
        'scripts'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Create historical directory
    Path('analysis/historical').mkdir(parents=True, exist_ok=True)
    
    logger.info("Ensured all required directories exist")

def get_data_directory() -> Path:
    """Get the configured data directory path"""
    data_dir = os.getenv('DATA_DIR', './analysis')
    return Path(data_dir)

def format_player_name(name: str) -> str:
    """Format player name consistently"""
    # Remove extra spaces and standardize format
    return ' '.join(name.split())

def safe_filename(filename: str) -> str:
    """Convert filename to safe version for filesystem"""
    # Replace problematic characters
    safe_chars = filename.replace('/', '_').replace('\\', '_').replace(':', '_')
    safe_chars = safe_chars.replace('*', '_').replace('?', '_').replace('"', '_')
    safe_chars = safe_chars.replace('<', '_').replace('>', '_').replace('|', '_')
    return safe_chars

def create_historical_file(filename: str, data: Any) -> str:
    """Save data to historical directory"""
    historical_dir = Path('analysis/historical')
    historical_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = historical_dir / filename
    
    if isinstance(data, (dict, list)):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        filepath.write_text(str(data))
    
    logger.info(f"Saved historical data: {filepath}")
    return str(filepath)

def load_historical_file(filename: str) -> Any:
    """Load data from historical directory"""
    historical_dir = Path('analysis/historical')
    filepath = historical_dir / filename
    
    if not filepath.exists():
        logger.warning(f"Historical file not found: {filepath}")
        return None
    
    try:
        if filename.endswith('.json'):
            with open(filepath, 'r') as f:
                return json.load(f)
        else:
            return filepath.read_text()
    except Exception as e:
        logger.error(f"Error loading historical file {filename}: {e}")
        return None

if __name__ == "__main__":
    # Test utility functions
    ensure_directories()
    print(f"Current week: {get_current_week()}")
    print(f"Timestamp: {format_timestamp()}")
    print(f"Data directory: {get_data_directory()}")
    
    # Test config functions
    test_config = {'test': 'data', 'number': 42}
    save_config('test', test_config)
    loaded_config = load_config('test')
    print(f"Config test: {loaded_config}")
    
    # Test markdown save
    test_content = "# Test Report\n\nThis is a test report."
    saved_file = save_markdown_report(test_content, "test_report.md")
    print(f"Saved test report: {saved_file}")
    
    print("Utility functions test completed successfully!")
