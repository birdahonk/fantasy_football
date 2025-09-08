#!/usr/bin/env python3
"""
Centralized API Usage Manager

This module provides centralized API usage tracking and formatting for all data collection scripts.
It ensures consistent reset time calculations, timezone handling, and usage reporting across all APIs.

Features:
- Unified API usage tracking interface
- Consistent Pacific Time Zone handling
- Centralized reset time calculations
- Standardized usage reporting format
- Rate limit monitoring and alerts

Author: Fantasy Football Data Collection
Date: September 2025
"""

import pytz
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union

class APIUsageManager:
    """
    Centralized manager for API usage tracking and reporting.
    
    Provides consistent interface for all data collection scripts to track
    API usage, calculate reset times, and format usage reports.
    """
    
    def __init__(self, client, api_name: str = "unknown"):
        """
        Initialize the API usage manager.
        
        Args:
            client: API client instance (Tank01, Sleeper, etc.)
            api_name: Name of the API for logging and identification
        """
        self.client = client
        self.api_name = api_name
        self.logger = logging.getLogger(__name__)
        
        # Pacific Time Zone for consistent reporting
        self.pacific_tz = pytz.timezone('US/Pacific')
    
    def get_current_time_pacific(self) -> datetime:
        """Get current time in Pacific Time Zone."""
        return datetime.now(self.pacific_tz)
    
    def format_timestamp_pacific(self, timestamp: Optional[Union[int, float]]) -> str:
        """
        Format timestamp to Pacific Time Zone.
        
        Args:
            timestamp: Timestamp in seconds (can be Unix timestamp or seconds until reset)
            
        Returns:
            Formatted timestamp string in Pacific Time Zone
        """
        if not timestamp:
            return "N/A"
        
        try:
            # Handle different timestamp formats
            if isinstance(timestamp, (int, float)):
                # If timestamp is very large (> 1e10), it's likely a Unix timestamp
                if timestamp > 1e10:
                    # Unix timestamp - convert directly
                    dt = datetime.fromtimestamp(timestamp, tz=self.pacific_tz)
                else:
                    # Seconds until reset - add to current time
                    current_time = self.get_current_time_pacific()
                    dt = current_time + timedelta(seconds=timestamp)
                
                return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
            else:
                return f"Invalid timestamp: {timestamp}"
                
        except (ValueError, TypeError, OSError) as e:
            self.logger.warning(f"Error formatting timestamp {timestamp}: {e}")
            return f"Invalid timestamp: {timestamp}"
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get comprehensive API usage information.
        
        Returns:
            Dict containing usage statistics and metadata
        """
        try:
            # Get usage info from the client
            if hasattr(self.client, 'get_api_usage'):
                usage = self.client.get_api_usage()
            elif hasattr(self.client, 'get_usage_info'):
                usage = self.client.get_usage_info()
            else:
                # Fallback for clients without usage tracking
                usage = {
                    "calls_made_this_session": 0,
                    "daily_limit": 1000,
                    "remaining_calls": 1000,
                    "percentage_used": 0.0,
                    "reset_timestamp": None,
                    "data_source": "fallback"
                }
            
            # Add current time and formatted reset time
            current_time = self.get_current_time_pacific()
            usage.update({
                "current_time_pacific": current_time.isoformat(),
                "current_time_formatted": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "reset_time_pacific": self.format_timestamp_pacific(usage.get('reset_timestamp')),
                "api_name": self.api_name,
                "last_updated": current_time.isoformat()
            })
            
            return usage
            
        except Exception as e:
            self.logger.error(f"Error getting usage info for {self.api_name}: {e}")
            return {
                "calls_made_this_session": 0,
                "daily_limit": 1000,
                "remaining_calls": 1000,
                "percentage_used": 0.0,
                "reset_timestamp": None,
                "current_time_pacific": self.get_current_time_pacific().isoformat(),
                "reset_time_pacific": "N/A",
                "api_name": self.api_name,
                "data_source": "error_fallback",
                "error": str(e)
            }
    
    def get_usage_summary_for_markdown(self) -> str:
        """
        Get formatted usage summary for markdown reports.
        
        Returns:
            Formatted markdown string with usage information
        """
        usage = self.get_usage_info()
        
        summary = f"## API Usage ({self.api_name.upper()})\n"
        summary += f"- **Current Time (Pacific):** {usage.get('current_time_formatted', 'N/A')}\n"
        summary += f"- **Total API Calls:** {usage.get('calls_made_this_session', 0)}\n"
        summary += f"- **Daily Limit:** {usage.get('daily_limit', 'N/A')}\n"
        summary += f"- **Remaining Calls:** {usage.get('remaining_calls', 'N/A')}\n"
        
        if usage.get('reset_time_pacific') and usage.get('reset_time_pacific') != 'N/A':
            summary += f"- **Limit Resets:** {usage.get('reset_time_pacific')}\n"
        
        # Add percentage used if available
        if 'percentage_used' in usage:
            summary += f"- **Usage Percentage:** {usage.get('percentage_used', 0):.1f}%\n"
        
        # Add data source for debugging
        if 'data_source' in usage:
            summary += f"- **Data Source:** {usage.get('data_source', 'unknown')}\n"
        
        return summary
    
    def get_usage_summary_for_json(self) -> Dict[str, Any]:
        """
        Get usage summary for JSON output.
        
        Returns:
            Dict containing usage information for JSON serialization
        """
        usage = self.get_usage_info()
        
        return {
            "api_name": self.api_name,
            "current_time_pacific": usage.get('current_time_pacific'),
            "current_time_formatted": usage.get('current_time_formatted'),
            "calls_made_this_session": usage.get('calls_made_this_session', 0),
            "daily_limit": usage.get('daily_limit'),
            "remaining_calls": usage.get('remaining_calls'),
            "percentage_used": usage.get('percentage_used', 0.0),
            "reset_timestamp": usage.get('reset_timestamp'),
            "reset_time_pacific": usage.get('reset_time_pacific'),
            "data_source": usage.get('data_source', 'unknown'),
            "last_updated": usage.get('last_updated')
        }
    
    def check_rate_limit_warning(self, threshold: float = 0.8) -> Optional[str]:
        """
        Check if API usage is approaching rate limit threshold.
        
        Args:
            threshold: Warning threshold as percentage (0.0 to 1.0)
            
        Returns:
            Warning message if threshold exceeded, None otherwise
        """
        usage = self.get_usage_info()
        
        percentage_used = usage.get('percentage_used', 0.0)
        if percentage_used >= threshold * 100:
            remaining = usage.get('remaining_calls', 0)
            limit = usage.get('daily_limit', 1000)
            
            return (f"⚠️ WARNING: API usage at {percentage_used:.1f}% "
                   f"({remaining}/{limit} calls remaining). "
                   f"Consider reducing batch size or waiting for reset.")
        
        return None
    
    def get_reset_time_hours(self) -> Optional[float]:
        """
        Get hours until API limit resets.
        
        Returns:
            Hours until reset, or None if not available
        """
        usage = self.get_usage_info()
        reset_timestamp = usage.get('reset_timestamp')
        
        if reset_timestamp and isinstance(reset_timestamp, (int, float)):
            # If it's seconds until reset (typical for RapidAPI)
            if reset_timestamp < 1e10:
                return reset_timestamp / 3600.0
            # If it's a Unix timestamp
            else:
                current_time = self.get_current_time_pacific()
                reset_time = datetime.fromtimestamp(reset_timestamp, tz=self.pacific_tz)
                delta = reset_time - current_time
                return delta.total_seconds() / 3600.0
        
        return None


def create_usage_manager(client, api_name: str) -> APIUsageManager:
    """
    Factory function to create an API usage manager.
    
    Args:
        client: API client instance
        api_name: Name of the API
        
    Returns:
        Configured APIUsageManager instance
    """
    return APIUsageManager(client, api_name)


# Convenience functions for common operations
def get_current_time_pacific() -> datetime:
    """Get current time in Pacific Time Zone (convenience function)."""
    pacific_tz = pytz.timezone('US/Pacific')
    return datetime.now(pacific_tz)


def format_timestamp_pacific(timestamp: Optional[Union[int, float]]) -> str:
    """Format timestamp to Pacific Time Zone (convenience function)."""
    pacific_tz = pytz.timezone('US/Pacific')
    
    if not timestamp:
        return "N/A"
    
    try:
        if isinstance(timestamp, (int, float)):
            if timestamp > 1e10:
                dt = datetime.fromtimestamp(timestamp, tz=pacific_tz)
            else:
                current_time = datetime.now(pacific_tz)
                dt = current_time + timedelta(seconds=timestamp)
            
            return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return f"Invalid timestamp: {timestamp}"
            
    except (ValueError, TypeError, OSError):
        return f"Invalid timestamp: {timestamp}"


if __name__ == "__main__":
    """Test the API usage manager."""
    print("🔧 Testing API Usage Manager")
    print("=" * 50)
    
    # Test timestamp formatting
    test_timestamps = [
        84751,  # Seconds until reset (typical RapidAPI)
        1757357115,  # Unix timestamp
        None,  # None value
        "invalid"  # Invalid value
    ]
    
    for ts in test_timestamps:
        formatted = format_timestamp_pacific(ts)
        print(f"Timestamp {ts} -> {formatted}")
    
    print(f"\nCurrent time (Pacific): {get_current_time_pacific().strftime('%Y-%m-%d %H:%M:%S %Z')}")
