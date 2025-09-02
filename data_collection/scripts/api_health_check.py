#!/usr/bin/env python3
"""
API Health Check Script

This script checks the health and usage status of all APIs used in the fantasy football system:
- Yahoo Fantasy Sports API
- Sleeper NFL API  
- Tank01 NFL API (via RapidAPI)

It tests all individual endpoints and displays the actual response data,
including usage statistics for the Tank01 API.

Usage:
    python api_health_check.py
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
import pytz
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Import our existing utilities
from data_collection.scripts.shared.yahoo_auth import SimpleYahooAuth
from data_collection.scripts.shared.file_utils import DataFileManager

class APIHealthChecker:
    """Comprehensive API health check for all fantasy football APIs"""
    
    def __init__(self):
        self.yahoo_auth = SimpleYahooAuth()
        self.file_manager = DataFileManager()
        self.results = {}
        self.pacific_tz = pytz.timezone('US/Pacific')
        
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check on all APIs"""
        print("🔍 Starting API Health Check...")
        print("=" * 60)
        
        # Check Yahoo Fantasy Sports API
        self.check_yahoo_api()
        
        # Check Sleeper NFL API
        self.check_sleeper_api()
        
        # Check Tank01 NFL API
        self.check_tank01_api()
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def check_yahoo_api(self):
        """Check Yahoo Fantasy Sports API endpoints"""
        print("\n📊 YAHOO FANTASY SPORTS API")
        print("-" * 40)
        
        yahoo_results = {
            "status": "unknown",
            "endpoints": {},
            "errors": []
        }
        
        try:
            # Test authentication
            print("🔐 Testing authentication...")
            if not self.yahoo_auth.is_authenticated():
                print("❌ Not authenticated. Attempting to authenticate...")
                if not self.yahoo_auth.authenticate():
                    yahoo_results["errors"].append("Authentication failed")
                    yahoo_results["status"] = "failed"
                    self.results["yahoo"] = yahoo_results
                    return
            
            print("✅ Authentication successful")
            yahoo_results["status"] = "authenticated"
            
            # Test key endpoints
            endpoints = [
                ("User Games", "users;use_login=1/games"),
                ("My Team", "team/461.l.595012.t.3"),
                ("League Info", "league/461.l.595012"),
                ("Current Week", "league/461.l.595012/settings"),
                ("Available Players", "league/461.l.595012/players;position=QB;status=A;count=5"),
                ("Transactions", "league/461.l.595012/transactions;count=5")
            ]
            
            for name, endpoint in endpoints:
                print(f"\n🔍 Testing {name}...")
                try:
                    result = self.yahoo_auth.make_request(endpoint)
                    if result and result.get('status') == 'success':
                        data = result.get('data', {})
                        yahoo_results["endpoints"][name] = {
                            "status": "success",
                            "status_code": 200,
                            "response_size": len(json.dumps(data)),
                            "response_preview": self._get_response_preview(data, 3)
                        }
                        print(f"✅ {name}: Success (200)")
                    else:
                        yahoo_results["endpoints"][name] = {
                            "status": "failed",
                            "status_code": "no_response" if not result else "api_error",
                            "error": "API request failed" if result else "No response"
                        }
                        print(f"❌ {name}: Failed ({'api_error' if result else 'no_response'})")
                except Exception as e:
                    yahoo_results["endpoints"][name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    print(f"❌ {name}: Error - {str(e)}")
            
        except Exception as e:
            yahoo_results["status"] = "error"
            yahoo_results["errors"].append(str(e))
            print(f"❌ Yahoo API check failed: {str(e)}")
        
        self.results["yahoo"] = yahoo_results
    
    def check_sleeper_api(self):
        """Check Sleeper NFL API endpoints"""
        print("\n🏈 SLEEPER NFL API")
        print("-" * 40)
        
        sleeper_results = {
            "status": "unknown",
            "endpoints": {},
            "errors": []
        }
        
        try:
            base_url = "https://api.sleeper.app/v1"
            
            # Test key endpoints
            endpoints = [
                ("NFL State", "state/nfl"),
                ("Players", "players/nfl"),
                ("Trending Adds", "players/nfl/trending/add"),
                ("Trending Drops", "players/nfl/trending/drop"),
                ("Trending Waivers", "players/nfl/trending/waiver")
            ]
            
            for name, endpoint in endpoints:
                print(f"\n🔍 Testing {name}...")
                try:
                    url = f"{base_url}/{endpoint}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        sleeper_results["endpoints"][name] = {
                            "status": "success",
                            "status_code": response.status_code,
                            "response_size": len(json.dumps(data)),
                            "response_preview": self._get_response_preview(data, 3)
                        }
                        print(f"✅ {name}: Success ({response.status_code})")
                    else:
                        sleeper_results["endpoints"][name] = {
                            "status": "failed",
                            "status_code": response.status_code,
                            "error": "Non-200 status code"
                        }
                        print(f"❌ {name}: Failed ({response.status_code})")
                        
                except Exception as e:
                    sleeper_results["endpoints"][name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    print(f"❌ {name}: Error - {str(e)}")
            
            sleeper_results["status"] = "success"
            
        except Exception as e:
            sleeper_results["status"] = "error"
            sleeper_results["errors"].append(str(e))
            print(f"❌ Sleeper API check failed: {str(e)}")
        
        self.results["sleeper"] = sleeper_results
    
    def check_tank01_api(self):
        """Check Tank01 NFL API endpoints"""
        print("\n⚡ TANK01 NFL API (RapidAPI)")
        print("-" * 40)
        
        tank01_results = {
            "status": "unknown",
            "endpoints": {},
            "usage_data": {},
            "errors": []
        }
        
        try:
            # Get RapidAPI key
            rapidapi_key = os.getenv('RAPIDAPI_KEY')
            if not rapidapi_key:
                tank01_results["status"] = "error"
                tank01_results["errors"].append("RAPIDAPI_KEY environment variable not set")
                print("❌ RAPIDAPI_KEY not found in environment variables")
                self.results["tank01"] = tank01_results
                return
            
            base_url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
            headers = {
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
            }
            
            # Test key endpoints
            endpoints = [
                ("NFL Teams", "getNFLTeams"),
                ("NFL Players", "getNFLPlayerList"),
                ("Weekly Projections", "getNFLProjections"),
                ("Depth Charts", "getNFLDepthCharts"),
                ("NFL News", "getNFLNews"),
                ("Player Stats", "getNFLGamesForPlayer?playerID=5981"),
                ("Team Roster", "getNFLTeamRoster?teamAbv=PHI")
            ]
            
            for name, endpoint in endpoints:
                print(f"\n🔍 Testing {name}...")
                try:
                    url = f"{base_url}/{endpoint}"
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    # Extract usage data from headers
                    usage_headers = self._extract_usage_headers(response.headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        tank01_results["endpoints"][name] = {
                            "status": "success",
                            "status_code": response.status_code,
                            "response_size": len(json.dumps(data)),
                            "response_preview": self._get_response_preview(data, 3),
                            "usage_headers": usage_headers
                        }
                        print(f"✅ {name}: Success ({response.status_code})")
                        
                        # Store usage data
                        if usage_headers:
                            tank01_results["usage_data"][name] = usage_headers
                            
                    else:
                        tank01_results["endpoints"][name] = {
                            "status": "failed",
                            "status_code": response.status_code,
                            "error": "Non-200 status code",
                            "usage_headers": usage_headers
                        }
                        print(f"❌ {name}: Failed ({response.status_code})")
                        
                except Exception as e:
                    tank01_results["endpoints"][name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    print(f"❌ {name}: Error - {str(e)}")
            
            # Generate formatted usage summary
            if tank01_results["usage_data"]:
                tank01_results["formatted_usage"] = self._format_tank01_usage(tank01_results["usage_data"])
            
            tank01_results["status"] = "success"
            
        except Exception as e:
            tank01_results["status"] = "error"
            tank01_results["errors"].append(str(e))
            print(f"❌ Tank01 API check failed: {str(e)}")
        
        self.results["tank01"] = tank01_results
    
    def _extract_usage_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Extract usage data from RapidAPI response headers"""
        usage_data = {}
        
        # RapidAPI usage headers
        usage_headers = [
            'X-RateLimit-Requests-Limit',
            'X-RateLimit-Requests-Remaining', 
            'X-RateLimit-Requests-Reset',
            'X-RateLimit-Requests-Used'
        ]
        
        for header in usage_headers:
            if header in headers:
                usage_data[header] = headers[header]
        
        return usage_data
    
    def _format_tank01_usage(self, usage_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Format Tank01 usage data like in the tank01 scripts"""
        if not usage_data:
            return {}
        
        # Get the most recent usage data (last endpoint tested)
        latest_usage = list(usage_data.values())[-1]
        
        try:
            # Extract usage information
            daily_limit = int(latest_usage.get('X-RateLimit-Requests-Limit', 0))
            remaining_calls = int(latest_usage.get('X-RateLimit-Requests-Remaining', 0))
            used_calls = int(latest_usage.get('X-RateLimit-Requests-Used', 0))
            reset_timestamp = int(latest_usage.get('X-RateLimit-Requests-Reset', 0))
            
            # Calculate usage percentage
            percentage_used = (used_calls / daily_limit * 100) if daily_limit > 0 else 0
            
            # Convert reset timestamp to Pacific Time
            if reset_timestamp > 0:
                reset_datetime = datetime.fromtimestamp(reset_timestamp, tz=self.pacific_tz)
                reset_formatted = reset_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
            else:
                reset_formatted = "Unknown"
            
            # Get current Pacific Time
            current_pacific = datetime.now(self.pacific_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            
            return {
                "current_time_pacific": current_pacific,
                "daily_limit": daily_limit,
                "remaining_calls": remaining_calls,
                "used_calls": used_calls,
                "percentage_used": round(percentage_used, 1),
                "reset_time_pacific": reset_formatted,
                "raw_headers": latest_usage
            }
            
        except (ValueError, TypeError) as e:
            return {
                "error": f"Failed to parse usage data: {str(e)}",
                "raw_headers": latest_usage
            }
    
    def _get_response_preview(self, data: Any, max_depth: int = 2) -> Any:
        """Get a preview of the response data"""
        if max_depth <= 0:
            return "..."
        
        if isinstance(data, dict):
            preview = {}
            for key, value in list(data.items())[:3]:  # Show first 3 keys
                preview[key] = self._get_response_preview(value, max_depth - 1)
            if len(data) > 3:
                preview["..."] = f"({len(data) - 3} more keys)"
            return preview
        elif isinstance(data, list):
            preview = []
            for item in data[:3]:  # Show first 3 items
                preview.append(self._get_response_preview(item, max_depth - 1))
            if len(data) > 3:
                preview.append(f"... ({len(data) - 3} more items)")
            return preview
        else:
            return str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
    
    def generate_summary(self):
        """Generate a summary of all API health checks"""
        print("\n" + "=" * 60)
        print("📋 API HEALTH CHECK SUMMARY")
        print("=" * 60)
        
        current_time = datetime.now(self.pacific_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        print(f"🕐 Check completed at: {current_time}")
        
        for api_name, results in self.results.items():
            print(f"\n🔍 {api_name.upper()} API:")
            print(f"   Status: {results.get('status', 'unknown')}")
            
            if 'endpoints' in results:
                successful = sum(1 for ep in results['endpoints'].values() if ep.get('status') == 'success')
                total = len(results['endpoints'])
                print(f"   Endpoints: {successful}/{total} successful")
            
            if 'errors' in results and results['errors']:
                print(f"   Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"     - {error}")
        
        # Tank01 usage summary
        if 'tank01' in self.results and 'formatted_usage' in self.results['tank01']:
            usage = self.results['tank01']['formatted_usage']
            if 'error' not in usage:
                print(f"\n⚡ TANK01 USAGE STATUS:")
                print(f"   Daily Limit: {usage.get('daily_limit', 'Unknown')}")
                print(f"   Remaining Calls: {usage.get('remaining_calls', 'Unknown')}")
                print(f"   Used Calls: {usage.get('used_calls', 'Unknown')}")
                print(f"   Usage Percentage: {usage.get('percentage_used', 'Unknown')}%")
                print(f"   Reset Time: {usage.get('reset_time_pacific', 'Unknown')}")
    
    def save_results(self, filename: Optional[str] = None):
        """Save health check results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_health_check_{timestamp}.json"
        
        output_dir = os.path.join(project_root, "data_collection", "outputs", "health_checks")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filepath}")
        return filepath

def main():
    """Main function to run the API health check"""
    print("🏈 Fantasy Football API Health Check")
    print("=" * 60)
    
    checker = APIHealthChecker()
    
    try:
        # Run health check
        results = checker.run_health_check()
        
        # Save results
        output_file = checker.save_results()
        
        print(f"\n✅ Health check completed successfully!")
        print(f"📁 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Health check failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
