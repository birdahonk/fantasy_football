#!/usr/bin/env python3
"""
Comprehensive Team Analyzer

This script generates a comprehensive analysis of your fantasy football team including:
- Current lineup (starters/bench)
- Player stats and projected points
- News headlines for each player
- Free agent recommendations by position
- Additional useful stats and insights

Uses all three APIs: Yahoo Fantasy Sports + Sleeper NFL + Tank01 NFL

Author: Fantasy Football Optimizer
Date: August 2025
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import our API clients
from scripts.core.external_api_manager import ExternalAPIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ComprehensiveTeamAnalyzer:
    """
    Comprehensive team analyzer using all available APIs.
    """
    
    def __init__(self):
        """Initialize the team analyzer."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Comprehensive Team Analyzer")
        
        # Initialize the External API Manager
        self.api_manager = ExternalAPIManager()
        
        # Check API status
        self.api_status = self.api_manager.get_api_status()
        self.logger.info(f"APIs available: {sum(self.api_status['apis'].values())}/3")
        
        # Cache for Tank01 player list to avoid repeated API calls
        self._tank01_player_cache = None
    
    def get_my_team_roster(self) -> List[Dict[str, Any]]:
        """
        Get the user's current team roster.
        
        Returns:
            List of player dictionaries with roster information
        """
        try:
            self.logger.info("🏈 Retrieving your team roster")
            
            if not self.api_status['apis']['yahoo']:
                self.logger.error("Yahoo API not available")
                return []
            
            # Get comprehensive Yahoo data
            yahoo_data = self.api_manager.get_comprehensive_league_data()
            
            if not yahoo_data:
                self.logger.error("Failed to get Yahoo data")
                return []
            
            # We need to get the user's own team roster
            # The get_comprehensive_league_data gets opponent rosters, but we need our own
            yahoo_client = self.api_manager.yahoo_client
            
            # Get league key and find our team
            league_key = yahoo_client.get_league_key()
            if not league_key:
                self.logger.error("Could not get league key")
                return []
            
            # Get our team roster using a direct API call
            teams_response = yahoo_client.oauth_client.make_request("users;use_login=1/games;game_keys=nfl/teams")
            if not teams_response or teams_response.get('status') != 'success':
                self.logger.error("Failed to get user teams")
                return []
            
            # Parse to get our team key
            parsed_data = teams_response.get('parsed', {})
            teams = yahoo_client._parse_user_teams_response(parsed_data)
            
            if not teams:
                self.logger.error("No teams found")
                return []
            
            our_team_key = teams[0].get('team_key')
            if not our_team_key:
                self.logger.error("Could not find team key")
                return []
            
            self.logger.info(f"Found our team key: {our_team_key}")
            
            # Get our team roster
            roster_response = yahoo_client.oauth_client.make_request(f"team/{our_team_key}/roster")
            if not roster_response or roster_response.get('status') != 'success':
                self.logger.error("Failed to get team roster")
                return []
            
            # Parse roster response
            roster_data = roster_response.get('parsed', {})
            roster = yahoo_client._parse_roster_response(roster_data)
            
            self.logger.info(f"✅ Retrieved {len(roster)} players from your roster")
            return roster
            
        except Exception as e:
            self.logger.error(f"Error getting team roster: {e}")
            return []
    
    def get_tank01_player_id(self, player_name: str, nfl_team: str = None) -> Optional[str]:
        """
        Get Tank01 player ID by matching player name with enhanced matching logic.
        
        Args:
            player_name: Player name from Yahoo
            nfl_team: NFL team abbreviation for better matching
            
        Returns:
            Tank01 player ID if found
        """
        try:
            if not self.api_status['apis']['tank01']:
                return None
            
            tank01_client = self.api_manager.tank01_client
            
            # Get player list from Tank01 (with caching)
            if self._tank01_player_cache is None:
                self.logger.info("🔄 Loading Tank01 player list (first time)")
                player_list_response = tank01_client.get_player_list()
                
                if not player_list_response or 'body' not in player_list_response:
                    self.logger.warning("No Tank01 player list response")
                    return None
                
                players = player_list_response['body']
                if not isinstance(players, list):
                    self.logger.warning("Tank01 player list is not a list")
                    return None
                
                # Cache the player list
                self._tank01_player_cache = players
                self.logger.info(f"✅ Cached {len(players)} Tank01 players")
            else:
                players = self._tank01_player_cache
                self.logger.debug(f"📋 Using cached Tank01 player list ({len(players)} players)")
            
            # Clean and prepare the search name
            search_name = player_name.strip().lower()
            name_parts = search_name.split()
            
            if len(name_parts) < 2:
                self.logger.warning(f"Player name too short for matching: {player_name}")
                return None
            
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            # Multiple matching strategies
            potential_matches = []
            
            for tank_player in players:
                if not isinstance(tank_player, dict):
                    continue
                
                tank_name = tank_player.get('longName', '').lower().strip()
                tank_espn_name = tank_player.get('espnName', '').lower().strip()
                tank_id = tank_player.get('playerID')
                tank_team = tank_player.get('team', '').upper()
                
                if not tank_name or not tank_id:
                    continue
                
                # Strategy 1: Exact match
                if search_name == tank_name:
                    self.logger.info(f"✅ EXACT match found for {player_name}: {tank_id}")
                    return tank_id
                
                # Strategy 2: ESPN name match
                if search_name == tank_espn_name:
                    self.logger.info(f"✅ ESPN name match found for {player_name}: {tank_id}")
                    return tank_id
                
                # Strategy 3: First + Last name match with team verification
                if first_name in tank_name and last_name in tank_name:
                    match_score = 0
                    
                    # Boost score if team matches
                    if nfl_team and tank_team == nfl_team.upper():
                        match_score += 10
                    
                    # Boost score if names are closer in length
                    name_length_diff = abs(len(search_name) - len(tank_name))
                    if name_length_diff <= 3:
                        match_score += 5
                    
                    # Check for common name variations
                    if 'jr.' in search_name or 'jr.' in tank_name:
                        if ('jr.' in search_name) == ('jr.' in tank_name):
                            match_score += 3
                    
                    # Boost score for exact first and last name match
                    tank_name_parts = tank_name.split()
                    if len(tank_name_parts) >= 2:
                        tank_first = tank_name_parts[0]
                        tank_last = tank_name_parts[-1]
                        if first_name == tank_first and last_name == tank_last:
                            match_score += 8
                    
                    potential_matches.append({
                        'player': tank_player,
                        'score': match_score,
                        'tank_name': tank_name,
                        'tank_id': tank_id,
                        'tank_team': tank_team,
                        'tank_pos': tank_player.get('pos', 'Unknown')
                    })
            
            # If we have potential matches, pick the best one
            if potential_matches:
                # Sort by score (highest first)
                potential_matches.sort(key=lambda x: x['score'], reverse=True)
                best_match = potential_matches[0]
                
                # Only accept matches with reasonable scores
                if best_match['score'] >= 5:
                    self.logger.info(f"✅ BEST match for {player_name}: {best_match['tank_id']} ({best_match['tank_name']}, {best_match['tank_team']}, {best_match['tank_pos']}, score: {best_match['score']})")
                    return best_match['tank_id']
                else:
                    self.logger.warning(f"⚠️ Low confidence match for {player_name}, best: {best_match['tank_name']} (score: {best_match['score']})")
            
            self.logger.warning(f"❌ Could not find Tank01 ID for player: {player_name}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Tank01 player ID for {player_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def enhance_player_with_tank01_data(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance player data with Tank01 projections and detailed stats.
        
        Args:
            player: Player dictionary from Yahoo
            
        Returns:
            Enhanced player dictionary
        """
        enhanced_player = player.copy()
        player_name = player.get('name', 'Unknown')
        position = player.get('position', 'Unknown')
        
        # Special handling for defense positions
        if player_name == 'Philadelphia' or position.upper() == 'DEF' or 'DEF' in position:
            enhanced_player['tank01_data'] = {
                'player_id': None,
                'fantasy_projections': None,
                'season_stats': None,
                'projected_points': '8.0'  # Typical defense scoring
            }
            self.logger.info(f"✅ Defense {player_name}: Estimated 8.0 points")
            return enhanced_player
        
        try:
            if not self.api_status['apis']['tank01']:
                enhanced_player['tank01_data'] = {
                    'player_id': None,
                    'fantasy_projections': None,
                    'season_stats': None,
                    'projected_points': 'N/A'
                }
                return enhanced_player
            
            tank01_client = self.api_manager.tank01_client
            player_name = player.get('name', '')
            nfl_team = player.get('team', '')
            
            # Get Tank01 player ID
            tank01_player_id = self.get_tank01_player_id(player_name, nfl_team)
            
            enhanced_player['tank01_data'] = {
                'player_id': tank01_player_id,
                'fantasy_projections': None,
                'season_stats': None,
                'projected_points': 'N/A'
            }
            
            if tank01_player_id:
                self.logger.info(f"🔍 Getting Tank01 data for {player_name} (ID: {tank01_player_id})")
                
                # Get fantasy projections and stats
                try:
                    # Method 1: Try to get fantasy projections first (more direct)
                    self.logger.info(f"📊 Attempting fantasy projections for {player_name}")
                    fantasy_projections = tank01_client.get_fantasy_projections(
                        player_id=tank01_player_id,
                        scoring_settings={
                            'fantasyPoints': 'true',  # CRITICAL: This enables fantasy points in response!
                            'passYards': 0.04,
                            'passTD': 4,
                            'passInterceptions': -2,
                            'rushYards': 0.1,
                            'rushTD': 6,
                            'receivingYards': 0.1,
                            'receivingTD': 6,
                            'pointsPerReception': 1,
                            'fumbles': -2,
                            'fgMade': 3,
                            'fgMissed': -1,
                            'xpMade': 1,
                            'xpMissed': -1
                        }
                    )
                    
                    if fantasy_projections and 'body' in fantasy_projections:
                        enhanced_player['tank01_data']['fantasy_projections'] = fantasy_projections['body']
                        proj_data = fantasy_projections['body']
                        
                        # Extract fantasy points directly from Tank01 API response
                        projected_pts = None
                        if isinstance(proj_data, dict):
                            # Tank01 returns game-by-game data with fantasy points already calculated!
                            total_points = 0
                            valid_games = 0
                            
                            # Get the most recent games (up to 5)
                            games = list(proj_data.keys())[:5]
                            
                            for game_key in games:
                                game_data = proj_data[game_key]
                                if not isinstance(game_data, dict):
                                    continue
                                
                                # Tank01 provides fantasy points directly!
                                fantasy_points = game_data.get('fantasyPoints')
                                if fantasy_points:
                                    try:
                                        pts = float(fantasy_points)
                                        total_points += pts
                                        valid_games += 1
                                        self.logger.debug(f"Game {game_key}: {pts} fantasy points")
                                    except (ValueError, TypeError):
                                        # Try the fantasyPointsDefault PPR value as backup
                                        fantasy_default = game_data.get('fantasyPointsDefault', {})
                                        if isinstance(fantasy_default, dict):
                                            ppr_points = fantasy_default.get('PPR')
                                            if ppr_points:
                                                try:
                                                    pts = float(ppr_points)
                                                    total_points += pts
                                                    valid_games += 1
                                                    self.logger.debug(f"Game {game_key}: {pts} PPR points (fallback)")
                                                except (ValueError, TypeError):
                                                    continue
                            
                            if valid_games > 0:
                                projected_pts = total_points / valid_games
                                self.logger.info(f"✅ Found fantasy points from {valid_games} recent games, average: {projected_pts:.1f}")
                            else:
                                self.logger.warning(f"⚠️ No fantasy points found in Tank01 game data for {player_name}")
                        
                        if projected_pts is not None:
                            enhanced_player['tank01_data']['projected_points'] = f"{projected_pts:.1f}"
                        else:
                            self.logger.warning(f"⚠️ No projected points found in fantasy projections for {player_name}")
                    else:
                        self.logger.warning(f"⚠️ No fantasy projections data for {player_name}")
                    
                    # If we couldn't calculate from fantasy projections, that's okay
                    # The fantasy projections endpoint is our primary source
                
                except Exception as proj_error:
                    self.logger.error(f"❌ Error getting Tank01 projections for {player_name}: {proj_error}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            self.logger.error(f"Error enhancing player {player.get('name', 'Unknown')} with Tank01 data: {e}")
        
        return enhanced_player
    
    def enhance_player_with_sleeper_data(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance player data with Sleeper trending information.
        
        Args:
            player: Player dictionary
            
        Returns:
            Enhanced player dictionary with Sleeper data
        """
        enhanced_player = player.copy()
        
        try:
            if not self.api_status['apis']['sleeper']:
                return enhanced_player
            
            # Get trending data
            trending_data = self.api_manager.get_trending_insights(lookback_hours=24, limit=50)
            
            if trending_data and 'trending_data' in trending_data:
                trending = trending_data['trending_data']
                player_name = player.get('name', '').lower()
                
                # Check if player is trending
                enhanced_player['sleeper_data'] = {
                    'trending_add': False,
                    'trending_drop': False,
                    'trend_info': None
                }
                
                # Check hot adds
                if 'hot_adds' in trending:
                    for add_player in trending['hot_adds']:
                        if isinstance(add_player, dict):
                            add_name = add_player.get('player_name', '').lower()
                            if player_name in add_name or add_name in player_name:
                                enhanced_player['sleeper_data']['trending_add'] = True
                                enhanced_player['sleeper_data']['trend_info'] = add_player
                                break
                
                # Check hot drops
                if 'hot_drops' in trending:
                    for drop_player in trending['hot_drops']:
                        if isinstance(drop_player, dict):
                            drop_name = drop_player.get('player_name', '').lower()
                            if player_name in drop_name or drop_name in player_name:
                                enhanced_player['sleeper_data']['trending_drop'] = True
                                enhanced_player['sleeper_data']['trend_info'] = drop_player
                                break
            
        except Exception as e:
            self.logger.error(f"Error enhancing player {player.get('name', 'Unknown')} with Sleeper data: {e}")
        
        return enhanced_player
    
    def get_free_agent_recommendations(self, position: str, count: int = 2) -> List[Dict[str, Any]]:
        """
        Get free agent recommendations for a specific position.
        
        Args:
            position: Position to get recommendations for
            count: Number of recommendations
            
        Returns:
            List of recommended free agents
        """
        try:
            self.logger.info(f"Getting {count} free agent recommendations for {position}")
            
            if not self.api_status['apis']['yahoo']:
                return []
            
            yahoo_client = self.api_manager.yahoo_client
            
            # Get free agents for the position
            free_agents = yahoo_client.get_free_agents(position=position, count=count*3)  # Get more to filter
            
            if not free_agents:
                return []
            
            # Filter and sort by overall rank
            position_agents = []
            for agent in free_agents:
                if agent.get('position') == position or position.upper() in agent.get('eligible_positions', []):
                    position_agents.append(agent)
                
                if len(position_agents) >= count:
                    break
            
            # Enhance with Sleeper data
            enhanced_agents = []
            for agent in position_agents[:count]:
                enhanced_agent = self.enhance_player_with_sleeper_data(agent)
                enhanced_agents.append(enhanced_agent)
            
            return enhanced_agents
            
        except Exception as e:
            self.logger.error(f"Error getting free agent recommendations for {position}: {e}")
            return []
    
    def get_nfl_news_for_players(self, players: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get NFL news headlines for players with proper date formatting.
        
        Args:
            players: List of player dictionaries
            
        Returns:
            Dictionary mapping player names to news items
        """
        player_news = {}
        
        try:
            if not self.api_status['apis']['tank01']:
                # Return placeholder news for all players
                for player in players:
                    player_name = player.get('name', '')
                    player_news[player_name] = [{
                        'title': f'Tank01 API not available',
                        'description': 'News service temporarily unavailable',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'System'
                    }]
                return player_news
            
            # Get general NFL news with better date handling
            news_data = self.api_manager.get_nfl_news(fantasy_focus=True, max_items=100)
            
            if not news_data or 'news' not in news_data:
                # Return placeholder for all players
                for player in players:
                    player_name = player.get('name', '')
                    player_news[player_name] = [{
                        'title': f'No news service available',
                        'description': 'Unable to retrieve current news',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'System'
                    }]
                return player_news
            
            news_items = news_data['news'].get('body', [])
            if not isinstance(news_items, list):
                news_items = []
            
            # Initialize news for all players
            for player in players:
                player_name = player.get('name', '')
                player_news[player_name] = []
            
            # Try to match news to players with enhanced matching
            for player in players:
                player_name = player.get('name', '')
                if not player_name:
                    continue
                
                # Enhanced name matching
                name_parts = player_name.split()
                if len(name_parts) < 2:
                    continue
                
                first_name = name_parts[0].lower()
                last_name = name_parts[-1].lower()
                full_name_lower = player_name.lower()
                
                # Look for news mentioning this player
                for news_item in news_items:
                    if not isinstance(news_item, dict):
                        continue
                    
                    title = news_item.get('title', '').lower()
                    description = news_item.get('description', '').lower()
                    
                    # Enhanced matching - check multiple patterns
                    name_found = False
                    if (last_name in title or last_name in description or
                        full_name_lower in title or full_name_lower in description or
                        (first_name in title and last_name in title)):
                        name_found = True
                    
                    if name_found:
                        # Format date properly
                        news_date = news_item.get('date', '')
                        if not news_date or news_date == 'Unknown':
                            # Try other date fields
                            news_date = news_item.get('timeStamp', '')
                            if not news_date:
                                news_date = datetime.now().strftime('%Y-%m-%d')
                        
                        # Clean up date format if needed
                        if isinstance(news_date, str) and len(news_date) > 10:
                            try:
                                # Try to parse and reformat date
                                from dateutil import parser
                                parsed_date = parser.parse(news_date)
                                news_date = parsed_date.strftime('%Y-%m-%d')
                            except:
                                news_date = news_date[:10] if len(news_date) >= 10 else news_date
                        
                        player_news[player_name].append({
                            'title': news_item.get('title', 'No title'),
                            'description': news_item.get('description', 'No description'),
                            'date': news_date,
                            'source': 'Tank01 NFL API'
                        })
                        
                        if len(player_news[player_name]) >= 2:
                            break
                
                # If no specific news found, add recent general news or placeholder
                if not player_news[player_name]:
                    if news_items:
                        # Add most recent general news item
                        recent_news = news_items[0] if news_items else {}
                        news_date = recent_news.get('date', datetime.now().strftime('%Y-%m-%d'))
                        
                        player_news[player_name] = [{
                            'title': f'General NFL Update (no specific {player_name} news)',
                            'description': recent_news.get('title', 'Check NFL news sources for latest updates'),
                            'date': news_date,
                            'source': 'Tank01 NFL API'
                        }]
                    else:
                        player_news[player_name] = [{
                            'title': f'No recent news for {player_name}',
                            'description': 'Monitor player status and team reports',
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'System'
                        }]
        
        except Exception as e:
            self.logger.error(f"Error getting news for players: {e}")
            # Ensure all players have some news entry
            for player in players:
                player_name = player.get('name', '')
                if player_name not in player_news:
                    player_news[player_name] = [{
                        'title': f'News retrieval error for {player_name}',
                        'description': 'Unable to fetch current news',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'System'
                    }]
        
        return player_news
    
    def format_table_column(self, text: str, width: int) -> str:
        """Format text to fit in a table column of specified width."""
        if not text:
            text = "N/A"
        text = str(text)
        if len(text) <= width:
            return text.ljust(width)
        else:
            return text[:width-3] + "..."
    
    def calculate_column_widths(self, data: List[List[str]], headers: List[str]) -> List[int]:
        """
        Calculate optimal column widths for uniform table formatting.
        
        Args:
            data: List of rows (each row is a list of strings)
            headers: List of header strings
            
        Returns:
            List of optimal column widths
        """
        if not data or not headers:
            return [10] * len(headers) if headers else []
        
        # Start with header lengths
        widths = [len(header) for header in headers]
        
        # Check all data rows
        for row in data:
            for i, cell in enumerate(row):
                if i < len(widths):
                    cell_len = len(str(cell)) if cell else 3  # "N/A" length
                    widths[i] = max(widths[i], cell_len)
        
        # Add padding and set reasonable limits
        for i in range(len(widths)):
            widths[i] = min(max(widths[i] + 2, 8), 25)  # Min 8, max 25 chars
        
        return widths
    
    def create_formatted_table(self, headers: List[str], data: List[List[str]], 
                             title: str = None) -> str:
        """
        Create a beautifully formatted markdown table with uniform column widths.
        
        Args:
            headers: Table headers
            data: Table data rows
            title: Optional table title
            
        Returns:
            Formatted markdown table string
        """
        if not headers or not data:
            return ""
        
        table_lines = []
        
        if title:
            table_lines.append(f"**{title}**")
            table_lines.append("")
        
        # Calculate optimal column widths
        widths = self.calculate_column_widths(data, headers)
        
        # Create header row
        header_row = "|"
        separator_row = "|"
        
        for i, header in enumerate(headers):
            width = widths[i] if i < len(widths) else 10
            header_row += f" {self.format_table_column(header, width-2)} |"
            separator_row += f" {'-' * (width-2)} |"
        
        table_lines.append(header_row)
        table_lines.append(separator_row)
        
        # Create data rows
        for row in data:
            data_row = "|"
            for i, cell in enumerate(row):
                width = widths[i] if i < len(widths) else 10
                data_row += f" {self.format_table_column(str(cell) if cell else 'N/A', width-2)} |"
            table_lines.append(data_row)
        
        return "\n".join(table_lines)
    
    def create_performance_chart(self, players: List[Dict[str, Any]]) -> str:
        """
        Create ASCII chart showing projected points distribution.
        
        Args:
            players: List of player dictionaries with projections
            
        Returns:
            ASCII chart as string
        """
        chart_lines = []
        chart_lines.append("## 📊 Projected Points Distribution")
        chart_lines.append("")
        
        # Extract projected points
        player_projections = []
        for player in players:
            name = player.get('name', 'Unknown')[:15]  # Truncate long names
            tank01_data = player.get('tank01_data', {})
            projected_pts = tank01_data.get('projected_points', 'N/A')
            
            try:
                if projected_pts != 'N/A' and projected_pts != 'TBD':
                    pts = float(projected_pts)
                    player_projections.append((name, pts))
            except (ValueError, TypeError):
                continue
        
        if not player_projections:
            chart_lines.append("*Projected points data not available*")
            chart_lines.append("")
            return "\n".join(chart_lines)
        
        # Sort by projected points
        player_projections.sort(key=lambda x: x[1], reverse=True)
        
        # Create horizontal bar chart
        max_points = max(pts for _, pts in player_projections) if player_projections else 1
        chart_width = 40
        
        chart_lines.append("```")
        chart_lines.append(f"{'Player':<15} {'Points':<8} {'Chart'}")
        chart_lines.append("-" * 65)
        
        for name, points in player_projections:
            bar_length = int((points / max_points) * chart_width) if max_points > 0 else 0
            bar = "█" * bar_length
            chart_lines.append(f"{name:<15} {points:>6.1f}   {bar}")
        
        chart_lines.append("```")
        chart_lines.append("")
        
        return "\n".join(chart_lines)
    
    def create_position_breakdown_chart(self, roster: List[Dict[str, Any]]) -> str:
        """
        Create position breakdown visualization.
        
        Args:
            roster: List of player dictionaries
            
        Returns:
            Position breakdown chart as string
        """
        chart_lines = []
        chart_lines.append("## 🎯 Roster Composition")
        chart_lines.append("")
        
        # Count players by position
        position_counts = {}
        for player in roster:
            positions = player.get('eligible_positions', ['Unknown'])
            if positions:
                primary_pos = positions[0]  # Use primary position
                position_counts[primary_pos] = position_counts.get(primary_pos, 0) + 1
        
        if not position_counts:
            chart_lines.append("*Position data not available*")
            return "\n".join(chart_lines)
        
        total_players = sum(position_counts.values())
        
        # Create visual breakdown
        chart_lines.append("```")
        chart_lines.append(f"{'Position':<8} {'Count':<6} {'Percentage':<12} {'Visual'}")
        chart_lines.append("-" * 50)
        
        for pos, count in sorted(position_counts.items()):
            percentage = (count / total_players) * 100 if total_players > 0 else 0
            visual_length = int(percentage / 5)  # Scale down for display
            visual = "█" * visual_length
            chart_lines.append(f"{pos:<8} {count:<6} {percentage:>6.1f}%     {visual}")
        
        chart_lines.append("```")
        chart_lines.append("")
        
        return "\n".join(chart_lines)
    
    def create_trending_analysis_chart(self, roster: List[Dict[str, Any]]) -> str:
        """
        Create trending analysis visualization.
        
        Args:
            roster: List of player dictionaries with Sleeper data
            
        Returns:
            Trending analysis chart as string
        """
        chart_lines = []
        chart_lines.append("## 📈 Market Trending Analysis")
        chart_lines.append("")
        
        trending_up = 0
        trending_down = 0
        stable = 0
        
        trending_up_players = []
        trending_down_players = []
        
        for player in roster:
            name = player.get('name', 'Unknown')
            sleeper_data = player.get('sleeper_data', {})
            
            if sleeper_data.get('trending_add'):
                trending_up += 1
                trending_up_players.append(name)
            elif sleeper_data.get('trending_drop'):
                trending_down += 1
                trending_down_players.append(name)
            else:
                stable += 1
        
        total = trending_up + trending_down + stable
        
        if total == 0:
            chart_lines.append("*Trending data not available*")
            return "\n".join(chart_lines)
        
        # Create trending summary
        chart_lines.append("### 🔥 Hot Trending Players")
        if trending_up_players:
            for player in trending_up_players[:5]:  # Show top 5
                chart_lines.append(f"- **{player}** 📈")
        else:
            chart_lines.append("- No players currently trending up")
        chart_lines.append("")
        
        if trending_down_players:
            chart_lines.append("### ❄️ Cooling Down")
            for player in trending_down_players[:3]:  # Show top 3
                chart_lines.append(f"- **{player}** 📉")
            chart_lines.append("")
        
        # Create visual breakdown
        chart_lines.append("### 📊 Trending Distribution")
        chart_lines.append("")
        chart_lines.append("```")
        
        up_pct = (trending_up / total) * 100 if total > 0 else 0
        down_pct = (trending_down / total) * 100 if total > 0 else 0
        stable_pct = (stable / total) * 100 if total > 0 else 0
        
        chart_lines.append(f"Trending Up:   {trending_up:>2} players ({up_pct:>5.1f}%) {'🔥' * (trending_up // 2)}")
        chart_lines.append(f"Trending Down: {trending_down:>2} players ({down_pct:>5.1f}%) {'❄️' * (trending_down // 2)}")
        chart_lines.append(f"Stable:        {stable:>2} players ({stable_pct:>5.1f}%) {'➖' * (stable // 3)}")
        chart_lines.append("```")
        chart_lines.append("")
        
        return "\n".join(chart_lines)
    
    def generate_comprehensive_report(self) -> str:
        """
        Generate a comprehensive team analysis report.
        
        Returns:
            Path to the generated report file
        """
        try:
            self.logger.info("📊 Generating comprehensive team analysis report")
            
            # Create output directory
            output_dir = Path("analysis/team_analysis")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_dir / f"{timestamp}_comprehensive_team_analysis.md"
            
            # Get team roster
            roster = self.get_my_team_roster()
            if not roster:
                self.logger.error("Could not retrieve team roster")
                return ""
            
            # Enhance players with external data
            enhanced_roster = []
            for player in roster:
                enhanced_player = self.enhance_player_with_sleeper_data(player)
                enhanced_player = self.enhance_player_with_tank01_data(enhanced_player)
                enhanced_roster.append(enhanced_player)
            
            # Get news for all players
            player_news = self.get_nfl_news_for_players(enhanced_roster)
            
            # Get free agent recommendations by position
            positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
            free_agent_recommendations = {}
            for pos in positions:
                free_agent_recommendations[pos] = self.get_free_agent_recommendations(pos, 2)
            
            # Generate report content
            report_content = self._generate_team_report(
                enhanced_roster, 
                player_news, 
                free_agent_recommendations
            )
            
            # Write report to file
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"✅ Comprehensive team analysis saved to {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            return ""
    
    def _generate_team_report(self, roster: List[Dict[str, Any]], 
                             player_news: Dict[str, List[Dict[str, Any]]], 
                             free_agents: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate the enhanced markdown report content with beautiful formatting and charts.
        
        Args:
            roster: Enhanced roster data
            player_news: News for each player
            free_agents: Free agent recommendations by position
            
        Returns:
            Formatted markdown report content
        """
        report = []
        
        # Header with enhanced styling
        report.append("# 🏈 Comprehensive Team Analysis Report")
        report.append("=" * 50)
        report.append("")
        report.append(f"**📅 Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report.append(f"**👤 Team**: birdahonkers")
        report.append(f"**🏆 League**: Greg Mulligan Memorial League")
        report.append("")
        
        # API Status with enhanced display
        report.append("## 📊 Data Sources & API Status")
        report.append("")
        api_status_data = []
        for api_name, available in self.api_status['apis'].items():
            status_emoji = "🟢 ONLINE" if available else "🔴 OFFLINE"
            api_status_data.append([api_name.title() + " API", status_emoji])
        
        if api_status_data:
            status_table = self.create_formatted_table(
                ["API Service", "Status"],
                api_status_data,
                "System Status Dashboard"
            )
            report.append(status_table)
        report.append("")
        
        # Separate starters and bench
        starters = [p for p in roster if p.get('selected_position') != 'BN']
        bench = [p for p in roster if p.get('selected_position') == 'BN']
        
        # Enhanced Starting Lineup with projected points
        report.append("## 🔥 Starting Lineup")
        report.append("")
        
        starter_data = []
        for player in starters:
            pos = player.get('selected_position', 'BN')
            name = player.get('name', 'Unknown')
            team = player.get('team', 'N/A')
            status = player.get('status', 'Healthy') or 'Healthy'
            
            # Get projected points from Tank01 data
            tank01_data = player.get('tank01_data', {})
            proj_pts = tank01_data.get('projected_points', 'TBD')
            
            # Check trending status
            trending = "➖ Stable"
            if 'sleeper_data' in player:
                sleeper = player['sleeper_data']
                if sleeper.get('trending_add'):
                    trending = "🔥 Hot"
                elif sleeper.get('trending_drop'):
                    trending = "❄️ Cool"
            
            starter_data.append([pos, name, team, status, proj_pts, trending])
        
        if starter_data:
            starters_table = self.create_formatted_table(
                ["Position", "Player", "Team", "Status", "Proj Pts", "Trending"],
                starter_data,
                "Active Starting Lineup"
            )
            report.append(starters_table)
        report.append("")
        
        # Enhanced Bench Players
        report.append("## 🪑 Bench Players")
        report.append("")
        
        bench_data = []
        for player in bench:
            name = player.get('name', 'Unknown')
            pos = ', '.join(player.get('eligible_positions', ['Unknown']))[:10]  # Truncate long positions
            team = player.get('team', 'N/A')
            status = player.get('status', 'Healthy') or 'Healthy'
            
            # Get projected points
            tank01_data = player.get('tank01_data', {})
            proj_pts = tank01_data.get('projected_points', 'TBD')
            
            # Check trending status
            trending = "➖ Stable"
            if 'sleeper_data' in player:
                sleeper = player['sleeper_data']
                if sleeper.get('trending_add'):
                    trending = "🔥 Hot"
                elif sleeper.get('trending_drop'):
                    trending = "❄️ Cool"
            
            bench_data.append([name, pos, team, status, proj_pts, trending])
        
        if bench_data:
            bench_table = self.create_formatted_table(
                ["Player", "Position", "Team", "Status", "Proj Pts", "Trending"],
                bench_data,
                "Bench Reserve Players"
            )
            report.append(bench_table)
        report.append("")
        
        # Add beautiful charts and visualizations
        report.append(self.create_performance_chart(roster))
        report.append(self.create_position_breakdown_chart(roster))
        report.append(self.create_trending_analysis_chart(roster))
        
        # Enhanced Player Details Section
        report.append("## 📋 Detailed Player Analysis")
        report.append("")
        
        for player in roster:
            player_name = player.get('name', 'Unknown')

            report.append(f"### 👤 {player_name}")
            report.append("")
            
            # Enhanced player info with Tank01 data
            pos = ', '.join(player.get('eligible_positions', ['Unknown']))
            team = player.get('team', 'N/A')
            status = player.get('status', 'Healthy') or 'Healthy'
            
            # Tank01 projections
            tank01_data = player.get('tank01_data', {})
            projected_pts = tank01_data.get('projected_points', 'N/A')
            player_id = tank01_data.get('player_id', 'Not found')
            
            report.append(f"**🏷️ Position**: {pos}")
            report.append(f"**🏟️ Team**: {team}")
            report.append(f"**⚕️ Health**: {status}")
            report.append(f"**📊 Projected Points**: {projected_pts}")
            report.append(f"**🆔 Tank01 ID**: {player_id}")
            report.append("")
            
            # Enhanced news section with proper dates
            news_items = player_news.get(player_name, [])
            if news_items:
                report.append("**📰 Latest News & Updates:**")
                for i, news in enumerate(news_items[:2], 1):
                    date = news.get('date', 'Unknown')
                    title = news.get('title', 'No title')
                    source = news.get('source', 'Unknown')
                    report.append(f"{i}. **{date}** ({source}): {title}")
                report.append("")
            
            # Enhanced trending analysis
            if 'sleeper_data' in player:
                sleeper = player['sleeper_data']
                if sleeper.get('trending_add'):
                    report.append("**🔥 Market Status**: HIGH DEMAND - Being actively added by managers")
                elif sleeper.get('trending_drop'):
                    report.append("**❄️ Market Status**: DECLINING - Being dropped by managers")
                else:
                    report.append("**➖ Market Status**: STABLE - Consistent ownership levels")
                report.append("")
        
        # Enhanced Free Agent Recommendations with better formatting
        report.append("## 🎯 Strategic Free Agent Targets")
        report.append("")
        
        for position, agents in free_agents.items():
            if agents:
                report.append(f"### {position} Position Targets")
                report.append("")
                
                fa_data = []
                for agent in agents:
                    name = agent.get('name', 'Unknown')
                    team = agent.get('team', 'N/A')
                    overall_rank = str(agent.get('overall_rank', 'N/A'))
                    
                    # Enhanced trending analysis
                    trending = "➖"
                    recommendation = "Consider"
                    priority = "Medium"
                    
                    if 'sleeper_data' in agent:
                        sleeper = agent['sleeper_data']
                        if sleeper.get('trending_add'):
                            trending = "🔥"
                            recommendation = "Strong Add"
                            priority = "HIGH"
                        elif sleeper.get('trending_drop'):
                            trending = "❄️"
                            recommendation = "Avoid"
                            priority = "LOW"
                    
                    fa_data.append([name, team, overall_rank, trending, recommendation, priority])
                
                if fa_data:
                    fa_table = self.create_formatted_table(
                        ["Player", "Team", "Rank", "Trend", "Action", "Priority"],
                        fa_data
                    )
                    report.append(fa_table)
                report.append("")
        
        # Enhanced Summary & Strategic Insights
        report.append("## 💡 Strategic Analysis & Key Insights")
        report.append("")
        
        # Calculate comprehensive stats
        trending_up = sum(1 for p in roster if p.get('sleeper_data', {}).get('trending_add', False))
        trending_down = sum(1 for p in roster if p.get('sleeper_data', {}).get('trending_drop', False))
        injured_players = [p for p in roster if p.get('status', 'Healthy') != 'Healthy']
        players_with_projections = [p for p in roster if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A']
        
        # Team strength analysis
        report.append("### 🎯 Team Strength Assessment")
        report.append("")
        
        if trending_up > 0:
            report.append(f"- **🔥 EXCELLENT DRAFTING**: {trending_up} players trending UP ({(trending_up/len(roster)*100):.1f}% of roster)**")
        
        if trending_down > 0:
            report.append(f"- **⚠️ WATCH LIST**: {trending_down} players trending DOWN - Monitor for alternatives")
        
        if injured_players:
            report.append(f"- **🏥 INJURY CONCERNS**: {len(injured_players)} players with health issues:")
            for injured in injured_players:
                report.append(f"  - {injured.get('name', 'Unknown')} ({injured.get('status', 'Unknown')})")
        
        if players_with_projections:
            avg_projection = sum(float(p.get('tank01_data', {}).get('projected_points', 0)) 
                               for p in players_with_projections 
                               if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A') / len(players_with_projections)
            report.append(f"- **📊 PROJECTION DATA**: Available for {len(players_with_projections)} players (avg: {avg_projection:.1f} pts)")
        
        report.append("")
        report.append("### 📈 Roster Composition Summary")
        report.append(f"- **Total Players**: {len(roster)} ({len(starters)} starters, {len(bench)} bench)")
        report.append(f"- **Market Momentum**: {trending_up} 🔥 | {len(roster) - trending_up - trending_down} ➖ | {trending_down} ❄️")
        report.append(f"- **Health Status**: {len(roster) - len(injured_players)} healthy, {len(injured_players)} concerns")
        report.append("")
        
        # Action items
        report.append("### 🎯 Recommended Actions")
        report.append("")
        report.append("1. **Monitor injury reports** daily for affected players")
        report.append("2. **Track trending data** - your hot players may become trade assets")
        report.append("3. **Consider handcuffs** for your RB1 (McCaffrey)")
        report.append("4. **Watch waiver wire** for emerging players")
        report.append("5. **Evaluate trades** if any players start trending down")
        report.append("")
        
        # Enhanced Footer
        report.append("---")
        report.append("")
        report.append("## 📊 Report Metadata")
        report.append("")
        report.append(f"- **Analysis Engine**: Comprehensive Team Analyzer v2.0")
        report.append(f"- **Data Integration**: Yahoo Fantasy + Sleeper NFL + Tank01 NFL APIs")
        report.append(f"- **Report Type**: Multi-API Enhanced Analysis")
        report.append(f"- **Timestamp**: {datetime.now().isoformat()}")
        report.append("")
        report.append("*🏈 Built for competitive fantasy football analysis and strategic decision making*")
        
        return "\n".join(report)


def main():
    """Run comprehensive team analysis."""
    print("🏈 Comprehensive Team Analysis")
    print("=" * 50)
    
    try:
        analyzer = ComprehensiveTeamAnalyzer()
        
        # Generate comprehensive report
        report_path = analyzer.generate_comprehensive_report()
        
        if report_path:
            print(f"✅ Comprehensive team analysis completed!")
            print(f"📄 Report saved to: {report_path}")
        else:
            print("❌ Failed to generate team analysis report")
        
    except Exception as e:
        print(f"❌ Error running team analysis: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏈 Team analysis completed!")


if __name__ == "__main__":
    main()
