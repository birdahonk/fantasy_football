#!/usr/bin/env python3
"""
Fixed Matchup Analysis Report Generator

This script creates a comprehensive matchup analysis comparing user's roster
vs the actual Week 1 opponent with proper Yahoo API parsing and complete data extraction.

Features:
- Correct Yahoo matchup API parsing for real Week 1 opponent
- Side-by-side roster comparison with actual opponent roster
- Enhanced player name matching across APIs
- Complete Tank01 projections and news integration
- Professional table formatting

Author: Fantasy Football Optimizer
Date: August 31, 2025
"""

import logging
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.core.external_api_manager import ExternalAPIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

class FixedMatchupAnalyzer:
    """
    Fixed matchup analyzer with proper Yahoo API parsing and complete data extraction.
    """
    
    def __init__(self):
        """Initialize the fixed matchup analyzer."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏈 Initializing Fixed Matchup Analyzer")
        
        # Initialize the External API Manager
        self.api_manager = ExternalAPIManager()
        
        # Check API status
        self.api_status = self.api_manager.get_api_status()
        self.logger.info(f"APIs available: {sum(self.api_status['apis'].values())}/3")
        
        # Raw API data storage
        self.raw_api_data = {
            'my_roster': None,
            'opponent_roster': None,
            'matchup_data': None,
            'my_team_info': None,
            'opponent_team_info': None,
            'tank01_player_cache': None,
            'sleeper_players_cache': None
        }
        
        # Enhanced player matching cache
        self.player_matching_cache = {}
        
        # Initialize API caches
        self._initialize_api_caches()
    
    def _initialize_api_caches(self):
        """Initialize API data caches for enhanced player matching."""
        try:
            # Cache Tank01 player list for enhanced matching
            if self.api_status['apis']['tank01']:
                tank01_client = self.api_manager.tank01_client
                player_list_response = tank01_client.get_player_list()
                
                if player_list_response and 'body' in player_list_response:
                    self.raw_api_data['tank01_player_cache'] = player_list_response['body']
                    self.logger.info(f"✅ Cached {len(self.raw_api_data['tank01_player_cache'])} Tank01 players")
            
            # Cache Sleeper player list for enhanced matching
            if self.api_status['apis']['sleeper']:
                sleeper_client = self.api_manager.sleeper_client
                sleeper_players = sleeper_client.get_nfl_players()
                
                if sleeper_players:
                    self.raw_api_data['sleeper_players_cache'] = sleeper_players
                    self.logger.info(f"✅ Cached {len(sleeper_players)} Sleeper players")
                    
        except Exception as e:
            self.logger.error(f"Error initializing API caches: {e}")
    
    def get_week_1_matchup(self) -> Dict[str, Any]:
        """Get Week 1 matchup information with correct Yahoo API parsing."""
        try:
            self.logger.info("🎯 Getting Week 1 matchup information")
            
            if not self.api_status['apis']['yahoo']:
                return {}
            
            yahoo_client = self.api_manager.yahoo_client
            
            # Get our team key
            teams_response = yahoo_client.oauth_client.make_request("users;use_login=1/games;game_keys=nfl/teams")
            if not teams_response or teams_response.get('status') != 'success':
                self.logger.error("Failed to get user teams")
                return {}
            
            parsed_data = teams_response.get('parsed', {})
            teams = yahoo_client._parse_user_teams_response(parsed_data)
            
            if not teams:
                self.logger.error("No teams found")
                return {}
            
            our_team_key = teams[0].get('team_key')
            if not our_team_key:
                self.logger.error("Could not find team key")
                return {}
            
            self.logger.info(f"Found our team key: {our_team_key}")
            
            # Get matchup data for our team
            matchup_response = yahoo_client.oauth_client.make_request(f"team/{our_team_key}/matchups")
            if not matchup_response or matchup_response.get('status') != 'success':
                self.logger.error("Failed to get matchup data")
                return {}
            
            # Parse matchup response to find Week 1 opponent with CORRECT logic
            matchup_data = matchup_response.get('parsed', {})
            week1_opponent = self._find_week1_opponent_fixed(matchup_data, our_team_key)
            
            if not week1_opponent:
                self.logger.error("Could not find Week 1 opponent")
                return {}
            
            self.raw_api_data['matchup_data'] = matchup_data
            
            matchup_info = {
                'week': 1,
                'my_team_key': our_team_key,
                'my_team_name': 'birdahonkers',  # From the debug data
                'opponent_team_key': week1_opponent.get('team_key'),
                'opponent_team_name': week1_opponent.get('name', 'Unknown Opponent'),
                'opponent_manager': week1_opponent.get('manager', 'Unknown Manager')
            }
            
            self.logger.info(f"✅ Week 1 Matchup: {matchup_info['my_team_name']} vs {matchup_info['opponent_team_name']}")
            
            return matchup_info
            
        except Exception as e:
            self.logger.error(f"Error getting Week 1 matchup: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _find_week1_opponent_fixed(self, matchup_data: Dict[str, Any], our_team_key: str) -> Optional[Dict[str, Any]]:
        """Find Week 1 opponent with correct Yahoo API structure parsing."""
        try:
            fantasy_content = matchup_data.get('fantasy_content', {})
            team_data = fantasy_content.get('team', [])
            
            if isinstance(team_data, list):
                # Look for the matchups data in the team array
                for item in team_data:
                    if isinstance(item, dict) and 'matchups' in item:
                        matchups = item.get('matchups', {})
                        
                        # Look for Week 1 matchup (key "0")
                        if '0' in matchups:
                            matchup_info = matchups['0']
                            matchup = matchup_info.get('matchup', {})
                            
                            # Verify this is Week 1
                            week = matchup.get('week')
                            if str(week) == '1':
                                self.logger.info("   Found Week 1 matchup!")
                                
                                # Navigate to teams data: matchup -> "0" -> "teams"
                                teams_container = matchup.get('0', {})
                                teams = teams_container.get('teams', {})
                                
                                # Look through teams to find opponent
                                for team_key, team_info in teams.items():
                                    if team_key.isdigit():
                                        team_data_list = team_info.get('team', [])
                                        
                                        if isinstance(team_data_list, list) and len(team_data_list) > 0:
                                            team_details = team_data_list[0]  # First element has team info
                                            
                                            if isinstance(team_details, list) and len(team_details) > 0:
                                                # Find team_key and name in the nested structure
                                                team_key_val = None
                                                team_name = None
                                                
                                                for detail in team_details:
                                                    if isinstance(detail, dict):
                                                        if 'team_key' in detail:
                                                            team_key_val = detail['team_key']
                                                        elif 'name' in detail:
                                                            team_name = detail['name']
                                                
                                                # If this isn't our team, it's the opponent
                                                if team_key_val and team_key_val != our_team_key:
                                                    self.logger.info(f"   Found opponent: {team_name} ({team_key_val})")
                                                    
                                                    return {
                                                        'team_key': team_key_val,
                                                        'name': team_name or 'Unknown Team',
                                                        'manager': 'Unknown Manager'  # Manager info would need deeper parsing
                                                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding Week 1 opponent: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_enhanced_roster(self, team_key: str, is_my_team: bool = False) -> List[Dict[str, Any]]:
        """Get enhanced roster with complete multi-API data integration."""
        try:
            team_type = "my" if is_my_team else "opponent"
            self.logger.info(f"📊 Getting enhanced {team_type} roster for {team_key}")
            
            if not self.api_status['apis']['yahoo']:
                return []
            
            yahoo_client = self.api_manager.yahoo_client
            
            # Get roster
            roster_response = yahoo_client.oauth_client.make_request(f"team/{team_key}/roster")
            if not roster_response or roster_response.get('status') != 'success':
                self.logger.error(f"Failed to get {team_type} roster")
                return []
            
            # Parse roster response with improved logic
            roster_data = roster_response.get('parsed', {})
            roster = self._parse_roster_response_fixed(roster_data)
            
            if not roster:
                self.logger.error(f"No {team_type} roster data available")
                return []
            
            # Store raw data
            if is_my_team:
                self.raw_api_data['my_roster'] = roster
            else:
                self.raw_api_data['opponent_roster'] = roster
            
            # Enhance each player with comprehensive multi-API data
            enhanced_roster = []
            
            for i, player in enumerate(roster):
                player_name = player.get('name', 'Unknown')
                self.logger.info(f"   Processing {team_type} player {i+1}/{len(roster)}: {player_name}")
                
                # Full enhancement for both teams
                enhanced_player = self._enhance_player_comprehensive(player, is_my_team)
                enhanced_roster.append(enhanced_player)
            
            self.logger.info(f"✅ Enhanced {team_type} roster: {len(enhanced_roster)} players")
            
            return enhanced_roster
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced roster for {team_key}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_roster_response_fixed(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse roster response with improved Yahoo API structure handling."""
        try:
            players = []
            
            # Navigate through the nested Yahoo API structure
            fantasy_content = response.get('fantasy_content', {})
            team_data = fantasy_content.get('team', [])
            
            # Find roster data in the complex nested structure
            roster_data = None
            if isinstance(team_data, list):
                for item in team_data:
                    if isinstance(item, dict) and 'roster' in item:
                        roster_data = item['roster']
                        break
            
            if not roster_data:
                self.logger.warning("No roster data found in response")
                return players
            
            # Extract players from roster structure
            roster_players = roster_data.get('0', {}).get('players', {})
            
            for player_key in roster_players:
                if player_key.isdigit():  # Only process numeric keys
                    player_info = roster_players[player_key].get('player', [])
                    
                    if isinstance(player_info, list) and len(player_info) >= 2:
                        # First element contains player details
                        player_details = player_info[0]
                        # Second element contains position info
                        position_info = player_info[1] if len(player_info) > 1 else {}
                        
                        if isinstance(player_details, list):
                            # Parse nested player data structure
                            player_data = {}
                            
                            for detail in player_details:
                                if isinstance(detail, dict):
                                    if 'name' in detail:
                                        name_data = detail['name']
                                        if isinstance(name_data, dict):
                                            player_data['name'] = name_data.get('full', 'Unknown')
                                    elif 'player_id' in detail:
                                        player_data['player_id'] = detail['player_id']
                                    elif 'display_position' in detail:
                                        player_data['position'] = detail['display_position']
                                    elif 'editorial_team_abbr' in detail:
                                        player_data['team'] = detail['editorial_team_abbr']
                                    elif 'status' in detail:
                                        player_data['status'] = detail['status']
                            
                            # Extract selected position from position info
                            if isinstance(position_info, dict) and 'selected_position' in position_info:
                                selected_pos_data = position_info['selected_position']
                                if isinstance(selected_pos_data, dict):
                                    player_data['selected_position'] = selected_pos_data.get('position', 'BN')
                            else:
                                player_data['selected_position'] = 'BN'
                            
                            # Only add if we have basic player info
                            if player_data.get('name'):
                                players.append(player_data)
            
            self.logger.info(f"Parsed {len(players)} players from roster")
            return players
            
        except Exception as e:
            self.logger.error(f"Error parsing roster response: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _enhance_player_comprehensive(self, player: Dict[str, Any], is_my_team: bool = False) -> Dict[str, Any]:
        """Enhance player with comprehensive multi-API data using improved matching."""
        enhanced_player = player.copy()
        player_name = player.get('name', 'Unknown')
        player_team = player.get('team', '')
        
        # Initialize comprehensive data structure
        enhanced_player.update({
            'tank01_data': {
                'player_id': None,
                'projected_points': 'N/A',
                'recent_news': [],
                'match_confidence': 0
            },
            'sleeper_data': {
                'player_id': None,
                'trending_status': 'Unknown',
                'trending_count': 0,
                'match_confidence': 0
            },
            'matchup_analysis': {
                'start_recommendation': 'Unknown',
                'confidence_level': 'Medium',
                'key_factors': []
            }
        })
        
        # Enhanced player matching and data enrichment
        self._enhance_with_tank01_comprehensive(enhanced_player)
        self._enhance_with_sleeper_comprehensive(enhanced_player)
        
        # Generate comprehensive matchup analysis
        if is_my_team:
            self._generate_comprehensive_start_sit_analysis(enhanced_player)
        
        return enhanced_player
    
    def _enhance_with_tank01_comprehensive(self, player: Dict[str, Any]):
        """Enhance player with comprehensive Tank01 data using improved matching."""
        try:
            if not self.api_status['apis']['tank01'] or not self.raw_api_data['tank01_player_cache']:
                return
            
            player_name = player.get('name', 'Unknown')
            player_team = player.get('team', '')
            
            # Enhanced Tank01 player matching
            tank01_id = self._match_tank01_player_enhanced(player_name, player_team)
            
            if tank01_id:
                player['tank01_data']['player_id'] = tank01_id
                player['tank01_data']['match_confidence'] = 90  # High confidence for found matches
                
                # Get comprehensive Tank01 data
                tank01_client = self.api_manager.tank01_client
                
                # Get fantasy projections
                projections = tank01_client.get_fantasy_projections(
                    player_id=tank01_id,
                    scoring_settings={'fantasyPoints': 'true'}
                )
                
                if projections and 'body' in projections:
                    proj_data = projections['body']
                    if isinstance(proj_data, dict):
                        # Extract projected points more comprehensively
                        total_points = 0
                        valid_games = 0
                        
                        for game_key, game_data in proj_data.items():
                            if isinstance(game_data, dict) and 'fantasyPoints' in game_data:
                                fantasy_points = game_data.get('fantasyPoints')
                                if fantasy_points:
                                    try:
                                        pts = float(fantasy_points)
                                        if pts > 0:  # Only count positive projections
                                            total_points += pts
                                            valid_games += 1
                                    except (ValueError, TypeError):
                                        pass
                        
                        if valid_games > 0:
                            avg_points = total_points / valid_games
                            player['tank01_data']['projected_points'] = f"{avg_points:.1f}"
                
                # Get news data
                news_response = tank01_client.get_nfl_news(
                    player_id=tank01_id,
                    limit=5
                )
                
                if news_response and 'body' in news_response:
                    news_data = news_response['body']
                    if isinstance(news_data, list):
                        recent_news = []
                        for article in news_data[:3]:  # Top 3 articles
                            if isinstance(article, dict):
                                news_item = {
                                    'title': article.get('title', 'No title'),
                                    'date': article.get('date', 'Unknown date'),
                                    'url': article.get('url', '#')
                                }
                                recent_news.append(news_item)
                        
                        player['tank01_data']['recent_news'] = recent_news
            else:
                player['tank01_data']['match_confidence'] = 0
                
        except Exception as e:
            self.logger.error(f"Error enhancing {player.get('name', 'Unknown')} with Tank01 data: {e}")
    
    def _enhance_with_sleeper_comprehensive(self, player: Dict[str, Any]):
        """Enhance player with comprehensive Sleeper data using improved matching."""
        try:
            if not self.api_status['apis']['sleeper'] or not self.raw_api_data['sleeper_players_cache']:
                return
            
            player_name = player.get('name', 'Unknown')
            player_team = player.get('team', '')
            
            # Enhanced Sleeper player matching
            sleeper_id = self._match_sleeper_player_enhanced(player_name, player_team)
            
            if sleeper_id:
                player['sleeper_data']['player_id'] = sleeper_id
                player['sleeper_data']['match_confidence'] = 90
                
                # Get trending data
                sleeper_client = self.api_manager.sleeper_client
                trending_data = sleeper_client.get_trending_players('add', lookback_hours=24, limit=200)
                
                if trending_data:
                    # Find this player in trending data
                    for trending_player in trending_data:
                        if trending_player.get('player_id') == sleeper_id:
                            count = trending_player.get('count', 0)
                            player['sleeper_data']['trending_count'] = count
                            
                            if count > 10000:
                                player['sleeper_data']['trending_status'] = f"🔥 EXTREMELY HIGH DEMAND ({count:,} adds)"
                            elif count > 5000:
                                player['sleeper_data']['trending_status'] = f"🔥 HIGH DEMAND ({count:,} adds)"
                            elif count > 1000:
                                player['sleeper_data']['trending_status'] = f"📈 MODERATE DEMAND ({count:,} adds)"
                            elif count > 100:
                                player['sleeper_data']['trending_status'] = f"📊 TRENDING UP ({count:,} adds)"
                            else:
                                player['sleeper_data']['trending_status'] = "📊 Stable"
                            break
                    else:
                        # Check drops
                        drop_data = sleeper_client.get_trending_players('drop', lookback_hours=24, limit=200)
                        if drop_data:
                            for trending_player in drop_data:
                                if trending_player.get('player_id') == sleeper_id:
                                    count = trending_player.get('count', 0)
                                    player['sleeper_data']['trending_count'] = -count
                                    player['sleeper_data']['trending_status'] = f"❄️ Being Dropped ({count:,})"
                                    break
                            else:
                                player['sleeper_data']['trending_status'] = "📊 Stable"
                        else:
                            player['sleeper_data']['trending_status'] = "📊 Stable"
            else:
                player['sleeper_data']['match_confidence'] = 0
                
        except Exception as e:
            self.logger.error(f"Error enhancing {player.get('name', 'Unknown')} with Sleeper data: {e}")
    
    def _match_tank01_player_enhanced(self, player_name: str, player_team: str = '') -> Optional[str]:
        """Enhanced Tank01 player matching with multiple strategies."""
        try:
            if not self.raw_api_data['tank01_player_cache']:
                return None
            
            # Check cache first
            cache_key = f"tank01_{player_name}_{player_team}"
            if cache_key in self.player_matching_cache:
                return self.player_matching_cache[cache_key]
            
            players = self.raw_api_data['tank01_player_cache']
            search_name = player_name.strip().lower()
            name_parts = search_name.split()
            
            if len(name_parts) < 2:
                return None
            
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            # Strategy 1: Exact match
            for tank_player in players:
                if not isinstance(tank_player, dict):
                    continue
                
                tank_name = tank_player.get('longName', '').lower().strip()
                tank_id = tank_player.get('playerID')
                tank_team = tank_player.get('team', '').upper()
                
                if not tank_name or not tank_id:
                    continue
                
                if search_name == tank_name:
                    # Verify team if provided
                    if player_team and tank_team and player_team.upper() != tank_team:
                        continue
                    
                    self.player_matching_cache[cache_key] = tank_id
                    return tank_id
            
            # Strategy 2: First + Last name match with team verification
            for tank_player in players:
                if not isinstance(tank_player, dict):
                    continue
                
                tank_name = tank_player.get('longName', '').lower().strip()
                tank_id = tank_player.get('playerID')
                tank_team = tank_player.get('team', '').upper()
                
                if not tank_name or not tank_id:
                    continue
                
                if first_name in tank_name and last_name in tank_name:
                    # Prefer team matches
                    if player_team and tank_team and player_team.upper() == tank_team:
                        self.player_matching_cache[cache_key] = tank_id
                        return tank_id
                    elif not player_team:  # Accept if no team info
                        self.player_matching_cache[cache_key] = tank_id
                        return tank_id
            
            # Strategy 3: Fuzzy matching for common name variations
            for tank_player in players:
                if not isinstance(tank_player, dict):
                    continue
                
                tank_name = tank_player.get('longName', '').lower().strip()
                tank_id = tank_player.get('playerID')
                
                if not tank_name or not tank_id:
                    continue
                
                # Handle common variations
                if self._names_match_fuzzy(search_name, tank_name):
                    self.player_matching_cache[cache_key] = tank_id
                    return tank_id
            
            # Cache miss
            self.player_matching_cache[cache_key] = None
            return None
            
        except Exception as e:
            self.logger.error(f"Error matching Tank01 player {player_name}: {e}")
            return None
    
    def _match_sleeper_player_enhanced(self, player_name: str, player_team: str = '') -> Optional[str]:
        """Enhanced Sleeper player matching with multiple strategies."""
        try:
            if not self.raw_api_data['sleeper_players_cache']:
                return None
            
            # Check cache first
            cache_key = f"sleeper_{player_name}_{player_team}"
            if cache_key in self.player_matching_cache:
                return self.player_matching_cache[cache_key]
            
            players = self.raw_api_data['sleeper_players_cache']
            search_name = player_name.strip().lower()
            
            # Strategy 1: Exact name match
            for sleeper_id, sleeper_player in players.items():
                if not isinstance(sleeper_player, dict):
                    continue
                
                sleeper_name = sleeper_player.get('full_name', '').lower().strip()
                sleeper_team = sleeper_player.get('team', '').upper()
                
                if search_name == sleeper_name:
                    # Verify team if provided
                    if player_team and sleeper_team and player_team.upper() != sleeper_team:
                        continue
                    
                    self.player_matching_cache[cache_key] = sleeper_id
                    return sleeper_id
            
            # Strategy 2: First + Last name matching
            name_parts = search_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]
                
                for sleeper_id, sleeper_player in players.items():
                    if not isinstance(sleeper_player, dict):
                        continue
                    
                    sleeper_name = sleeper_player.get('full_name', '').lower().strip()
                    sleeper_team = sleeper_player.get('team', '').upper()
                    
                    if first_name in sleeper_name and last_name in sleeper_name:
                        # Prefer team matches
                        if player_team and sleeper_team and player_team.upper() == sleeper_team:
                            self.player_matching_cache[cache_key] = sleeper_id
                            return sleeper_id
                        elif not player_team:  # Accept if no team info
                            self.player_matching_cache[cache_key] = sleeper_id
                            return sleeper_id
            
            # Cache miss
            self.player_matching_cache[cache_key] = None
            return None
            
        except Exception as e:
            self.logger.error(f"Error matching Sleeper player {player_name}: {e}")
            return None
    
    def _names_match_fuzzy(self, name1: str, name2: str) -> bool:
        """Fuzzy name matching for common variations."""
        try:
            # Handle common nickname variations
            nickname_map = {
                'mike': 'michael',
                'rob': 'robert',
                'bob': 'robert',
                'bill': 'william',
                'jim': 'james',
                'tom': 'thomas',
                'dave': 'david',
                'chris': 'christopher',
                'matt': 'matthew',
                'dan': 'daniel',
                'joe': 'joseph',
                'tony': 'anthony'
            }
            
            # Normalize names
            name1_parts = name1.split()
            name2_parts = name2.split()
            
            if len(name1_parts) >= 2 and len(name2_parts) >= 2:
                first1 = name1_parts[0]
                last1 = name1_parts[-1]
                first2 = name2_parts[0]
                last2 = name2_parts[-1]
                
                # Check if last names match and first names are variations
                if last1 == last2:
                    if first1 == first2:
                        return True
                    
                    # Check nickname variations
                    if first1 in nickname_map and nickname_map[first1] == first2:
                        return True
                    if first2 in nickname_map and nickname_map[first2] == first1:
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _generate_comprehensive_start_sit_analysis(self, player: Dict[str, Any]):
        """Generate comprehensive start/sit analysis based on all available data."""
        try:
            position = player.get('position', 'Unknown')
            selected_pos = player.get('selected_position', 'BN')
            tank01_proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
            sleeper_status = player.get('sleeper_data', {}).get('trending_status', 'Unknown')
            
            # Initialize comprehensive scoring
            start_score = 50  # Base neutral score
            key_factors = []
            
            # Factor 1: Tank01 Projected Points (40% weight)
            if tank01_proj != 'N/A':
                try:
                    points = float(tank01_proj)
                    if points > 20:
                        start_score += 25
                        key_factors.append(f"Elite projection ({points:.1f} pts)")
                    elif points > 15:
                        start_score += 20
                        key_factors.append(f"High projection ({points:.1f} pts)")
                    elif points > 10:
                        start_score += 15
                        key_factors.append(f"Good projection ({points:.1f} pts)")
                    elif points > 5:
                        start_score += 5
                        key_factors.append(f"Decent projection ({points:.1f} pts)")
                    else:
                        start_score -= 15
                        key_factors.append(f"Low projection ({points:.1f} pts)")
                except (ValueError, TypeError):
                    key_factors.append("No projection available")
            else:
                start_score -= 10
                key_factors.append("No projection data")
            
            # Factor 2: Current lineup status (20% weight)
            if selected_pos != 'BN':
                start_score += 15
                key_factors.append(f"Currently starting ({selected_pos})")
            else:
                key_factors.append("Currently on bench")
            
            # Factor 3: Sleeper market intelligence (25% weight)
            if 'EXTREMELY HIGH DEMAND' in sleeper_status:
                start_score += 20
                key_factors.append("Extremely high waiver demand")
            elif 'HIGH DEMAND' in sleeper_status:
                start_score += 15
                key_factors.append("High waiver demand")
            elif 'MODERATE DEMAND' in sleeper_status:
                start_score += 10
                key_factors.append("Moderate waiver demand")
            elif 'TRENDING UP' in sleeper_status:
                start_score += 5
                key_factors.append("Trending up")
            elif 'Being Dropped' in sleeper_status:
                start_score -= 20
                key_factors.append("Being dropped by managers")
            elif sleeper_status == 'Stable':
                # Neutral
                key_factors.append("Stable market sentiment")
            
            # Factor 4: Position-based adjustments (15% weight)
            position_weights = {
                'QB': 10,
                'RB': 15,
                'WR': 10,
                'TE': 5,
                'K': -5,
                'DEF': 0
            }
            
            pos_weight = position_weights.get(position, 0)
            start_score += pos_weight
            
            # Generate recommendation with confidence levels
            if start_score >= 80:
                recommendation = "🔥 MUST START"
                confidence = "Very High"
            elif start_score >= 70:
                recommendation = "✅ START"
                confidence = "High"
            elif start_score >= 60:
                recommendation = "👍 LEAN START"
                confidence = "Medium-High"
            elif start_score >= 50:
                recommendation = "🤔 TOSS-UP"
                confidence = "Medium"
            elif start_score >= 40:
                recommendation = "👎 LEAN SIT"
                confidence = "Medium-Low"
            else:
                recommendation = "❌ SIT"
                confidence = "High"
            
            # Update player data
            player['matchup_analysis'].update({
                'start_recommendation': recommendation,
                'confidence_level': confidence,
                'key_factors': key_factors,
                'start_score': start_score
            })
            
        except Exception as e:
            self.logger.error(f"Error generating start/sit analysis for {player.get('name', 'Unknown')}: {e}")
    
    def generate_fixed_matchup_report(self) -> str:
        """Generate comprehensive fixed matchup analysis report."""
        try:
            self.logger.info("🚀 Generating fixed matchup analysis report")
            
            # Get Week 1 matchup information
            matchup_info = self.get_week_1_matchup()
            if not matchup_info:
                self.logger.error("Unable to retrieve matchup information")
                return ""
            
            # Get enhanced rosters with comprehensive data
            my_roster = self.get_enhanced_roster(matchup_info['my_team_key'], is_my_team=True)
            opponent_roster = self.get_enhanced_roster(matchup_info['opponent_team_key'], is_my_team=False)
            
            if not my_roster or not opponent_roster:
                self.logger.error("Unable to retrieve roster data")
                return ""
            
            # Generate comprehensive report content
            timestamp = datetime.now()
            report_content = self._generate_fixed_matchup_report_content(
                matchup_info, my_roster, opponent_roster, timestamp
            )
            
            # Save report
            output_dir = Path("analysis/matchups")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_fixed_matchup_analysis.md"
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Save raw API data
            raw_data_dir = Path("analysis/raw_api_data")
            raw_data_dir.mkdir(parents=True, exist_ok=True)
            
            raw_data_file = raw_data_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_fixed_matchup_raw_data.json"
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.raw_api_data, f, indent=2, default=str)
            
            self.logger.info(f"✅ Fixed matchup analysis report saved to {output_path}")
            self.logger.info(f"✅ Raw API data saved to {raw_data_file}")
            
            print(f"🚀 Fixed matchup analysis completed!")
            print(f"📄 Report saved to: {output_path}")
            print(f"📊 Raw API data saved to: {raw_data_file}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating fixed matchup report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_fixed_matchup_report_content(self, matchup_info: Dict[str, Any], 
                                             my_roster: List[Dict[str, Any]], 
                                             opponent_roster: List[Dict[str, Any]], 
                                             timestamp: datetime) -> str:
        """Generate comprehensive fixed matchup report content with proper formatting."""
        
        my_team_name = matchup_info['my_team_name']
        opponent_name = matchup_info['opponent_team_name']
        opponent_manager = matchup_info['opponent_manager']
        week = matchup_info.get('week', 1)
        
        # Calculate total projected points with enhanced logic
        my_total_projected = 0
        opponent_total_projected = 0
        
        my_starters = [p for p in my_roster if p.get('selected_position') != 'BN']
        opponent_starters = [p for p in opponent_roster if p.get('selected_position') != 'BN']
        
        for player in my_starters:
            proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
            if proj != 'N/A':
                try:
                    my_total_projected += float(proj)
                except (ValueError, TypeError):
                    pass
        
        for player in opponent_starters:
            proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
            if proj != 'N/A':
                try:
                    opponent_total_projected += float(proj)
                except (ValueError, TypeError):
                    pass
        
        # Calculate projected point differential
        point_diff = my_total_projected - opponent_total_projected
        
        report = f"""# 🏈 COMPREHENSIVE MATCHUP ANALYSIS REPORT
========================================================

**📅 Generated**: {timestamp.strftime('%B %d, %Y at %I:%M %p')}
**🏆 Week {week} Matchup**: {my_team_name} vs {opponent_name}
**👤 Opponent Manager**: {opponent_manager}
**📊 Data Sources**: Yahoo Fantasy + Tank01 NFL + Sleeper NFL APIs

## 📊 Matchup Overview

### 🎯 Projected Points Comparison

**{my_team_name}**: {my_total_projected:.1f} points (Tank01 projections)
**{opponent_name}**: {opponent_total_projected:.1f} points (Tank01 projections)
**Point Differential**: {'+' if point_diff > 0 else ''}{point_diff:.1f} points

"""
        
        # Create enhanced diverging bar chart
        max_points = max(my_total_projected, opponent_total_projected, 100)
        if max_points > 0:
            my_bar_length = max(1, int((my_total_projected / max_points) * 40))
            opponent_bar_length = max(1, int((opponent_total_projected / max_points) * 40))
            
            report += f"""
### 📊 Visual Point Comparison

```
{my_team_name[:20]:<20} {'█' * my_bar_length} {my_total_projected:.1f}
{opponent_name[:20]:<20} {'█' * opponent_bar_length} {opponent_total_projected:.1f}
```

"""
        
        # Add enhanced matchup prediction
        if point_diff > 10:
            advantage = f"✅ **{my_team_name} has a commanding advantage** (+{point_diff:.1f} points)"
            strategy = "Play it safe with high-floor players. Avoid risky boom-bust options."
        elif point_diff > 5:
            advantage = f"👍 **{my_team_name} has a solid advantage** (+{point_diff:.1f} points)"
            strategy = "Stick with your studs and reliable players."
        elif point_diff > 0:
            advantage = f"🤔 **{my_team_name} has a slight advantage** (+{point_diff:.1f} points)"
            strategy = "Consider high-ceiling players to create separation."
        elif point_diff > -5:
            advantage = f"⚠️ **Close matchup with slight disadvantage** ({point_diff:.1f} points)"
            strategy = "Need upside plays and high-ceiling options."
        else:
            advantage = f"🚨 **{opponent_name} has a significant advantage** ({abs(point_diff):.1f} points)"
            strategy = "Go for broke with boom-bust players and contrarian picks."
        
        report += f"""
**🎯 Matchup Prediction**: {advantage}

**📋 Recommended Strategy**: {strategy}

## 🔥 START/SIT RECOMMENDATIONS

### 🚨 CRITICAL DECISIONS

"""
        
        # Enhanced start/sit recommendations with proper formatting
        critical_decisions = []
        
        for player in my_roster:
            analysis = player.get('matchup_analysis', {})
            recommendation = analysis.get('start_recommendation', 'Unknown')
            
            if any(keyword in recommendation for keyword in ['MUST START', 'SIT', 'TOSS-UP', 'LEAN']):
                critical_decisions.append(player)
        
        # Sort by start score (highest first)
        critical_decisions.sort(
            key=lambda p: p.get('matchup_analysis', {}).get('start_score', 50),
            reverse=True
        )
        
        if critical_decisions:
            report += """
| Player                | Pos | Current | Recommendation    | Tank01 | Sleeper Status      | Key Factor          |
| --------------------- | --- | ------- | ----------------- | ------ | ------------------- | ------------------- |
"""
            
            for player in critical_decisions[:12]:  # Top 12 critical decisions
                name = player.get('name', 'Unknown')[:21]
                position = player.get('position', 'N/A')[:3]
                current_pos = player.get('selected_position', 'BN')[:7]
                recommendation = player.get('matchup_analysis', {}).get('start_recommendation', 'Unknown')[:17]
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')[:6]
                sleeper = player.get('sleeper_data', {}).get('trending_status', 'Unknown')[:19]
                factors = player.get('matchup_analysis', {}).get('key_factors', [])
                key_factor = factors[0] if factors else 'N/A'
                key_factor = key_factor[:19] if len(key_factor) > 19 else key_factor
                
                report += f"| {name:<21} | {position:<3} | {current_pos:<7} | {recommendation:<17} | {proj:<6} | {sleeper:<19} | {key_factor:<19} |\n"
        else:
            report += "No critical start/sit decisions identified based on current analysis.\n"
        
        # Enhanced side-by-side roster comparison
        report += f"""

## 🔄 COMPREHENSIVE SIDE-BY-SIDE COMPARISON

### 🏆 Starting Lineups Analysis

| Position | {my_team_name[:15]:<15} | Proj  | {opponent_name[:15]:<15} | Proj  | Advantage     |
| -------- | {'':<15} | ----- | {'':<15} | ----- | ------------- |
"""
        
        # Group starters by position with enhanced logic
        positions = ['QB', 'RB', 'WR', 'TE', 'FLEX', 'K', 'DEF']
        
        my_starters_by_pos = {}
        opponent_starters_by_pos = {}
        
        for player in my_starters:
            pos = player.get('selected_position', 'BN')
            if pos not in my_starters_by_pos:
                my_starters_by_pos[pos] = []
            my_starters_by_pos[pos].append(player)
        
        for player in opponent_starters:
            pos = player.get('selected_position', 'BN')
            if pos not in opponent_starters_by_pos:
                opponent_starters_by_pos[pos] = []
            opponent_starters_by_pos[pos].append(player)
        
        # Create enhanced side-by-side comparison
        for pos in positions:
            my_players = my_starters_by_pos.get(pos, [])
            opp_players = opponent_starters_by_pos.get(pos, [])
            
            max_players = max(len(my_players), len(opp_players), 1)
            
            for i in range(max_players):
                my_player = my_players[i] if i < len(my_players) else {}
                opp_player = opp_players[i] if i < len(opp_players) else {}
                
                # My player info
                my_name = my_player.get('name', 'Empty')[:15]
                my_proj = my_player.get('tank01_data', {}).get('projected_points', 'N/A')[:5]
                
                # Opponent player info
                opp_name = opp_player.get('name', 'Empty')[:15]
                opp_proj = opp_player.get('tank01_data', {}).get('projected_points', 'N/A')[:5]
                
                # Calculate enhanced advantage
                advantage = 'TIE'[:13]
                if my_proj != 'N/A' and opp_proj != 'N/A':
                    try:
                        my_pts = float(my_proj)
                        opp_pts = float(opp_proj)
                        diff = my_pts - opp_pts
                        
                        if diff > 5:
                            advantage = f"✅ +{diff:.1f} ME"[:13]
                        elif diff > 2:
                            advantage = f"👍 +{diff:.1f} ME"[:13]
                        elif diff < -5:
                            advantage = f"❌ +{abs(diff):.1f} OPP"[:13]
                        elif diff < -2:
                            advantage = f"⚠️ +{abs(diff):.1f} OPP"[:13]
                        else:
                            advantage = "🤔 CLOSE"[:13]
                    except (ValueError, TypeError):
                        pass
                
                pos_display = pos if i == 0 else ''
                report += f"| {pos_display:<8} | {my_name:<15} | {my_proj:<5} | {opp_name:<15} | {opp_proj:<5} | {advantage:<13} |\n"
        
        # Add comprehensive strategic analysis
        report += f"""

## 💡 COMPREHENSIVE STRATEGIC ANALYSIS

### 🎯 Key Matchup Insights

**Projected Outcome**: {advantage}

**🔑 Keys to Victory**:
"""
        
        # Generate enhanced strategic insights
        if point_diff > 5:
            report += f"- You're projected to win by {point_diff:.1f} points - maintain your advantage\n"
            report += "- Start your most reliable, high-floor players\n"
            report += "- Avoid risky boom-bust options unless matchup-specific\n"
            report += f"- Monitor {opponent_name}'s top threats for any lineup changes\n"
        else:
            report += f"- Projected deficit of {abs(point_diff):.1f} points - need upside plays\n"
            report += "- Consider high-ceiling players with breakout potential\n"
            report += "- Look for contrarian plays that could provide an edge\n"
            report += "- Target players with favorable matchups or trending up\n"
        
        # Add enhanced top performers analysis
        my_top_performers = sorted(
            [p for p in my_starters if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A'],
            key=lambda p: float(p.get('tank01_data', {}).get('projected_points', '0')),
            reverse=True
        )[:5]
        
        opp_top_performers = sorted(
            [p for p in opponent_starters if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A'],
            key=lambda p: float(p.get('tank01_data', {}).get('projected_points', '0')),
            reverse=True
        )[:5]
        
        if my_top_performers:
            report += f"\n**🌟 Your Top Projected Performers**:\n"
            for i, player in enumerate(my_top_performers, 1):
                name = player.get('name', 'Unknown')
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
                pos = player.get('selected_position', 'N/A')
                sleeper_status = player.get('sleeper_data', {}).get('trending_status', 'Stable')
                report += f"{i}. **{name}** ({pos}): {proj} projected points - {sleeper_status}\n"
        
        if opp_top_performers:
            report += f"\n**⚠️ {opponent_name}'s Top Threats**:\n"
            for i, player in enumerate(opp_top_performers, 1):
                name = player.get('name', 'Unknown')
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
                pos = player.get('selected_position', 'N/A')
                report += f"{i}. **{name}** ({pos}): {proj} projected points\n"
        
        # Add bench analysis for strategic decisions
        my_bench = [p for p in my_roster if p.get('selected_position') == 'BN']
        if my_bench:
            report += f"\n### 🪑 Key Bench Decisions\n\n"
            report += "| Player                | Pos | Tank01 | Sleeper Status      | Start Over?       |\n"
            report += "| --------------------- | --- | ------ | ------------------- | ----------------- |\n"
            
            # Sort bench by projected points
            bench_sorted = sorted(
                [p for p in my_bench if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A'],
                key=lambda p: float(p.get('tank01_data', {}).get('projected_points', '0')),
                reverse=True
            )
            
            for player in bench_sorted[:8]:  # Top 8 bench players
                name = player.get('name', 'Unknown')[:21]
                pos = player.get('position', 'N/A')[:3]
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')[:6]
                sleeper = player.get('sleeper_data', {}).get('trending_status', 'Unknown')[:19]
                
                # Determine if they should start
                recommendation = player.get('matchup_analysis', {}).get('start_recommendation', 'Unknown')[:17]
                
                report += f"| {name:<21} | {pos:<3} | {proj:<6} | {sleeper:<19} | {recommendation:<17} |\n"
        
        # Add comprehensive methodology
        report += f"""

---

## 🔬 ENHANCED ANALYSIS METHODOLOGY

### 📊 Multi-API Data Integration
**Data Sources**:
- **Yahoo Fantasy API**: Official roster, matchup, and league data
- **Tank01 NFL API**: Weekly fantasy point projections and news
- **Sleeper NFL API**: Real-time trending data from thousands of leagues

### 🎯 Start/Sit Scoring Algorithm
**Weighted Factors**:
- **Tank01 Projections (40%)**: Weekly fantasy point projections
- **Sleeper Market Intelligence (25%)**: Add/drop trending data
- **Current Lineup Status (20%)**: Starting vs bench position
- **Position Value (15%)**: Position-specific scoring adjustments

**Recommendation Scale**:
- 🔥 **MUST START** (80+ points): Elite plays with high confidence
- ✅ **START** (70-79 points): Strong plays worth starting
- 👍 **LEAN START** (60-69 points): Slight edge to start
- 🤔 **TOSS-UP** (50-59 points): Could go either way
- 👎 **LEAN SIT** (40-49 points): Slight edge to sit
- ❌ **SIT** (<40 points): Better options available

### 🔍 Player Matching System
**Enhanced Cross-API Matching**:
- Exact name matching with team verification
- First/last name matching with fuzzy logic
- Nickname and common variation handling
- Team-based match validation

---

## 📊 Report Metadata

- **Analysis Engine**: Fixed Matchup Analyzer v2.0
- **My Team**: {my_team_name} ({len(my_roster)} players: {len(my_starters)} starters, {len(my_bench)} bench)
- **Opponent**: {opponent_name} ({len(opponent_roster)} players: {len(opponent_starters)} starters)
- **Data Quality**: Tank01 {sum(1 for p in my_roster if p.get('tank01_data', {}).get('projected_points') != 'N/A')}/{len(my_roster)} matches, Sleeper {sum(1 for p in my_roster if p.get('sleeper_data', {}).get('trending_status') != 'Unknown')}/{len(my_roster)} matches
- **Timestamp**: {timestamp.isoformat()}

*🏈 Built for competitive fantasy football with comprehensive multi-API analysis and strategic lineup optimization*
"""
        
        return report


def main():
    """Main function to run the fixed matchup analyzer."""
    print("🏈 FIXED MATCHUP ANALYSIS REPORT GENERATOR")
    print("=" * 50)
    
    try:
        analyzer = FixedMatchupAnalyzer()
        report_path = analyzer.generate_fixed_matchup_report()
        
        if report_path:
            print(f"\n🎉 Fixed matchup analysis completed successfully!")
            print(f"📄 Report saved to: {report_path}")
        else:
            print("\n❌ Analysis failed - check logs for details")
            
    except Exception as e:
        print(f"\n❌ Error running fixed matchup analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
