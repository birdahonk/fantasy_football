#!/usr/bin/env python3
"""
Yahoo Fantasy Sports Data Retriever

This script provides comprehensive data retrieval capabilities for Yahoo Fantasy Sports,
including free agents, opponent rosters, player stats, news, and research data.

Author: Fantasy Football AI Assistant
Date: January 2025
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the oauth directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
oauth_dir = os.path.join(script_dir, "..", "oauth")
sys.path.append(oauth_dir)

from oauth2_client import YahooOAuth2Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YahooDataRetriever:
    """Comprehensive Yahoo Fantasy Sports data retrieval"""
    
    def __init__(self):
        """Initialize the data retriever"""
        self.oauth_client = YahooOAuth2Client()
        self._cached_league_key = None
        self._cached_team_key = None
        self._cached_teams = None
        
    def test_basic_connection(self) -> bool:
        """Test basic API connectivity"""
        try:
            logger.info("Testing basic Yahoo API connection...")
            
            if not self.oauth_client.is_authenticated():
                logger.error("Not authenticated with Yahoo API")
                return False
            
            # Test with a simple endpoint
            response = self.oauth_client.make_request("users;use_login=1/profile")
            if response and response.get('status') == 'success':
                logger.info("✅ Basic API connection successful")
                return True
            else:
                logger.error("❌ Basic API connection failed")
                return False
                
        except Exception as e:
            logger.error(f"Error testing API connection: {e}")
            return False
    
    def get_league_key(self) -> Optional[str]:
        """Get the user's primary league key"""
        if self._cached_league_key:
            return self._cached_league_key
            
        try:
            # Get user's teams to extract league key
            teams_response = self.oauth_client.make_request("users;use_login=1/games;game_keys=nfl/teams")
            if not teams_response or teams_response.get('status') != 'success':
                logger.error("Failed to get user teams")
                return None
                
            parsed_data = teams_response.get('parsed', {})
            teams = self._parse_user_teams_response(parsed_data)
            
            if teams:
                # Extract league key from first team
                team_key = teams[0].get('team_key')
                if team_key:
                    team_key_parts = team_key.split('.')
                    if len(team_key_parts) >= 3:
                        # League key format: game.l.league_id (e.g., 461.l.595012)
                        self._cached_league_key = f"{team_key_parts[0]}.{team_key_parts[1]}.{team_key_parts[2]}"
                        self._cached_team_key = team_key
                        logger.info(f"League key: {self._cached_league_key}")
                        return self._cached_league_key
            
            logger.error("Could not extract league key")
            return None
            
        except Exception as e:
            logger.error(f"Error getting league key: {e}")
            return None
    
    def get_free_agents(self, position: Optional[str] = None, count: int = 25) -> List[Dict[str, Any]]:
        """
        Get available free agents
        
        Args:
            position: Filter by position (QB, RB, WR, TE, K, DEF)
            count: Number of players to retrieve
        """
        try:
            logger.info(f"Getting free agents (position: {position}, count: {count})...")
            
            league_key = self.get_league_key()
            if not league_key:
                return []
            
            # Build endpoint for free agents
            endpoint = f"league/{league_key}/players"
            
            # Add filters
            filters = []
            if position:
                filters.append(f"position={position}")
            filters.append(f"status=A")  # Available players
            filters.append(f"sort=OR")   # Sort by ownership percentage
            filters.append(f"count={count}")
            
            if filters:
                endpoint += ";" + ";".join(filters)
            
            logger.info(f"Free agents endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response or response.get('status') != 'success':
                logger.error("Failed to get free agents")
                return []
            
            # Save raw response for debugging
            self._save_debug_response(response, f"free_agents_{position or 'all'}")
            
            parsed_data = response.get('parsed', {})
            players = self._parse_players_response(parsed_data)
            
            logger.info(f"Retrieved {len(players)} free agents")
            return players
            
        except Exception as e:
            logger.error(f"Error getting free agents: {e}")
            return []
    
    def get_all_league_teams(self) -> List[Dict[str, Any]]:
        """Get all teams in the league"""
        try:
            if self._cached_teams:
                return self._cached_teams
                
            logger.info("Getting all league teams...")
            
            league_key = self.get_league_key()
            if not league_key:
                return []
            
            endpoint = f"league/{league_key}/teams"
            logger.info(f"League teams endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response or response.get('status') != 'success':
                logger.error("Failed to get league teams")
                return []
            
            # Save raw response for debugging
            self._save_debug_response(response, "league_teams")
            
            parsed_data = response.get('parsed', {})
            teams = self._parse_league_teams_response(parsed_data)
            
            self._cached_teams = teams
            logger.info(f"Retrieved {len(teams)} league teams")
            return teams
            
        except Exception as e:
            logger.error(f"Error getting league teams: {e}")
            return []
    
    def get_opponent_rosters(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get rosters for all opponent teams"""
        try:
            logger.info("Getting all opponent rosters...")
            
            teams = self.get_all_league_teams()
            if not teams:
                return {}
            
            rosters = {}
            my_team_key = self._cached_team_key
            
            for team in teams:
                team_key = team.get('team_key')
                team_name = team.get('name', 'Unknown')
                
                if team_key == my_team_key:
                    logger.info(f"Skipping own team: {team_name}")
                    continue
                
                logger.info(f"Getting roster for: {team_name}")
                
                endpoint = f"team/{team_key}/roster"
                response = self.oauth_client.make_request(endpoint)
                
                if response and response.get('status') == 'success':
                    parsed_data = response.get('parsed', {})
                    roster = self._parse_roster_response(parsed_data)
                    rosters[team_name] = roster
                    logger.info(f"✅ Retrieved {len(roster)} players for {team_name}")
                else:
                    logger.warning(f"❌ Failed to get roster for {team_name}")
                    rosters[team_name] = []
            
            logger.info(f"Retrieved rosters for {len(rosters)} opponent teams")
            return rosters
            
        except Exception as e:
            logger.error(f"Error getting opponent rosters: {e}")
            return {}
    
    def get_player_stats(self, player_keys: List[str], stat_type: str = "season") -> List[Dict[str, Any]]:
        """
        Get player statistics
        
        Args:
            player_keys: List of player keys to get stats for
            stat_type: 'season', 'lastweek', 'lastmonth'
        """
        try:
            logger.info(f"Getting player stats for {len(player_keys)} players (type: {stat_type})...")
            
            if not player_keys:
                return []
            
            # Yahoo API can handle multiple players in one request
            player_keys_str = ",".join(player_keys)
            endpoint = f"players;player_keys={player_keys_str}/stats"
            
            if stat_type != "season":
                endpoint += f";type={stat_type}"
            
            logger.info(f"Player stats endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response or response.get('status') != 'success':
                logger.error("Failed to get player stats")
                return []
            
            # Save raw response for debugging
            self._save_debug_response(response, f"player_stats_{stat_type}")
            
            parsed_data = response.get('parsed', {})
            stats = self._parse_player_stats_response(parsed_data)
            
            logger.info(f"Retrieved stats for {len(stats)} players")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return []
    
    def get_player_news(self, player_keys: List[str]) -> List[Dict[str, Any]]:
        """Get news for specific players"""
        try:
            logger.info(f"Getting news for {len(player_keys)} players...")
            
            if not player_keys:
                return []
            
            # Try to get news from Yahoo API
            player_keys_str = ",".join(player_keys)
            endpoint = f"players;player_keys={player_keys_str}/news"
            
            logger.info(f"Player news endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response or response.get('status') != 'success':
                logger.warning("Failed to get player news from Yahoo API")
                return []
            
            # Save raw response for debugging
            self._save_debug_response(response, "player_news")
            
            parsed_data = response.get('parsed', {})
            news = self._parse_player_news_response(parsed_data)
            
            logger.info(f"Retrieved news for {len(news)} players")
            return news
            
        except Exception as e:
            logger.error(f"Error getting player news: {e}")
            return []
    
    def get_research_data(self) -> Dict[str, Any]:
        """Get Yahoo Fantasy research data"""
        try:
            logger.info("Getting Yahoo Fantasy research data...")
            
            league_key = self.get_league_key()
            if not league_key:
                return {}
            
            research_data = {}
            
            # Try different research endpoints
            research_endpoints = [
                f"league/{league_key}/players/stats",
                f"league/{league_key}/draftresults",
                f"league/{league_key}/transactions",
                "game/nfl/players/stats"
            ]
            
            for endpoint in research_endpoints:
                try:
                    logger.info(f"Trying research endpoint: {endpoint}")
                    response = self.oauth_client.make_request(endpoint)
                    
                    if response and response.get('status') == 'success':
                        endpoint_name = endpoint.split('/')[-1]
                        research_data[endpoint_name] = response.get('parsed', {})
                        logger.info(f"✅ Retrieved research data: {endpoint_name}")
                        
                        # Save raw response for debugging
                        self._save_debug_response(response, f"research_{endpoint_name}")
                    else:
                        logger.warning(f"❌ Failed to get research data from: {endpoint}")
                        
                except Exception as e:
                    logger.warning(f"Error with research endpoint {endpoint}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(research_data)} research data sets")
            return research_data
            
        except Exception as e:
            logger.error(f"Error getting research data: {e}")
            return {}
    
    def get_top_available_players(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get top available players by Yahoo rankings"""
        try:
            logger.info(f"Getting top {count} available players...")
            
            league_key = self.get_league_key()
            if not league_key:
                return []
            
            # Get top available players sorted by Yahoo rank
            endpoint = f"league/{league_key}/players;status=A;sort=AR;count={count}"
            
            logger.info(f"Top available players endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response or response.get('status') != 'success':
                logger.error("Failed to get top available players")
                return []
            
            # Save raw response for debugging
            self._save_debug_response(response, "top_available_players")
            
            parsed_data = response.get('parsed', {})
            players = self._parse_players_response(parsed_data)
            
            logger.info(f"Retrieved {len(players)} top available players")
            return players
            
        except Exception as e:
            logger.error(f"Error getting top available players: {e}")
            return []
    
    def _parse_user_teams_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse user teams response from Yahoo API"""
        try:
            teams = []
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                users = fantasy_content.get('users', {})
                
                for user_key, user_data in users.items():
                    if not user_key.isdigit():
                        continue
                    
                    user_obj = user_data.get('user', {})
                    if isinstance(user_obj, list):
                        for user_item in user_obj:
                            if isinstance(user_item, dict) and 'games' in user_item:
                                games = user_item['games']
                                for game_key, game_data in games.items():
                                    if not game_key.isdigit():
                                        continue
                                    
                                    game = game_data.get('game', {})
                                    if isinstance(game, list):
                                        for game_item in game:
                                            if isinstance(game_item, dict) and 'teams' in game_item:
                                                teams_data = game_item.get('teams', {})
                                                for team_key, team_data in teams_data.items():
                                                    if not team_key.isdigit():
                                                        continue
                                                    
                                                    team_array = team_data.get('team', [])
                                                    if isinstance(team_array, list):
                                                        for team_item in team_array:
                                                            if isinstance(team_item, list):
                                                                team_info = {}
                                                                for info_item in team_item:
                                                                    if isinstance(info_item, dict):
                                                                        if 'team_key' in info_item:
                                                                            team_info['team_key'] = info_item['team_key']
                                                                        elif 'name' in info_item:
                                                                            team_info['name'] = info_item['name']
                                                                        elif 'is_owned_by_current_login' in info_item:
                                                                            team_info['is_my_team'] = bool(info_item['is_owned_by_current_login'])
                                                                
                                                                if team_info.get('team_key') and team_info.get('name'):
                                                                    team_key_parts = team_info['team_key'].split('.')
                                                                    if len(team_key_parts) >= 3:
                                                                        league_key = f"{team_key_parts[0]}.{team_key_parts[1]}.{team_key_parts[2]}"
                                                                    else:
                                                                        league_key = None
                                                                    
                                                                    team_obj = {
                                                                        'team_key': team_info['team_key'],
                                                                        'name': team_info['name'],
                                                                        'league_key': league_key,
                                                                        'is_my_team': team_info.get('is_my_team', True)
                                                                    }
                                                                    teams.append(team_obj)
            
            return teams
            
        except Exception as e:
            logger.error(f"Error parsing user teams response: {e}")
            return []
    
    def _parse_league_teams_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse league teams response"""
        try:
            teams = []
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                league = fantasy_content.get('league', {})
                
                # Handle league as list or dict
                if isinstance(league, list):
                    for league_item in league:
                        if isinstance(league_item, dict) and 'teams' in league_item:
                            teams_data = league_item.get('teams', {})
                            teams = self._extract_teams_from_data(teams_data)
                            break
                elif isinstance(league, dict) and 'teams' in league:
                    teams_data = league.get('teams', {})
                    teams = self._extract_teams_from_data(teams_data)
            
            return teams
            
        except Exception as e:
            logger.error(f"Error parsing league teams response: {e}")
            return []
    
    def _extract_teams_from_data(self, teams_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract team information from teams data structure"""
        teams = []
        
        for team_key, team_data in teams_data.items():
            if not team_key.isdigit():
                continue
            
            team_array = team_data.get('team', [])
            if isinstance(team_array, list):
                # Handle nested array structure: team is a list containing a list of dicts
                team_info = {}
                for team_item in team_array:
                    if isinstance(team_item, list):
                        # This is the nested array we need to process
                        for info_item in team_item:
                            if isinstance(info_item, dict):
                                if 'team_key' in info_item:
                                    team_info['team_key'] = info_item['team_key']
                                elif 'name' in info_item:
                                    team_info['name'] = info_item['name']
                                elif 'is_owned_by_current_login' in info_item:
                                    team_info['is_my_team'] = bool(info_item['is_owned_by_current_login'])
                                elif 'draft_position' in info_item:
                                    team_info['draft_position'] = info_item['draft_position']
                                elif 'previous_season_team_rank' in info_item:
                                    team_info['previous_rank'] = info_item['previous_season_team_rank']
                                elif 'managers' in info_item:
                                    managers = info_item['managers']
                                    if isinstance(managers, list) and managers:
                                        manager = managers[0].get('manager', {})
                                        team_info['manager'] = manager.get('nickname', 'Unknown')
                    elif isinstance(team_item, dict):
                        # Handle direct dict structure (fallback)
                        if 'team_key' in team_item:
                            team_info['team_key'] = team_item['team_key']
                        elif 'name' in team_item:
                            team_info['name'] = team_item['name']
                        elif 'is_owned_by_current_login' in team_item:
                            team_info['is_my_team'] = bool(team_item['is_owned_by_current_login'])
                
                if team_info.get('team_key') and team_info.get('name'):
                    teams.append(team_info)
        
        return teams
    
    def _parse_roster_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse roster response from Yahoo API"""
        try:
            players = []
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                team = fantasy_content.get('team', {})
                
                # Handle team as list or dict
                if isinstance(team, list):
                    for team_item in team:
                        if isinstance(team_item, dict) and 'roster' in team_item:
                            roster_data = team_item.get('roster', {})
                            # The roster structure is: roster -> '0' -> 'players' -> player data
                            if '0' in roster_data and 'players' in roster_data['0']:
                                players_data = roster_data['0']['players']
                                players = self._extract_players_from_data(players_data)
                            else:
                                players = self._extract_players_from_roster(roster_data)
                            break
                elif isinstance(team, dict) and 'roster' in team:
                    roster_data = team.get('roster', {})
                    # The roster structure is: roster -> '0' -> 'players' -> player data
                    if '0' in roster_data and 'players' in roster_data['0']:
                        players_data = roster_data['0']['players']
                        players = self._extract_players_from_data(players_data)
                    else:
                        players = self._extract_players_from_roster(roster_data)
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing roster response: {e}")
            return []
    
    def _extract_players_from_roster(self, roster: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player information from roster data structure"""
        players = []
        
        for player_key, player_data in roster.items():
            if not player_key.isdigit():
                continue
            
            player = player_data.get('player', {})
            if player:
                player_info = {}
                if isinstance(player, list):
                    # Handle nested array structure: player is a list containing a list of dicts
                    for player_item in player:
                        if isinstance(player_item, list):
                            # This is the nested array we need to process
                            for info_item in player_item:
                                if isinstance(info_item, dict):
                                    if 'player_key' in info_item:
                                        player_info['player_key'] = info_item['player_key']
                                    elif 'name' in info_item:
                                        name_data = info_item['name']
                                        if isinstance(name_data, dict) and 'full' in name_data:
                                            player_info['name'] = name_data['full']
                                        elif isinstance(name_data, str):
                                            player_info['name'] = name_data
                                    elif 'display_position' in info_item:
                                        player_info['position'] = info_item['display_position']
                                    elif 'editorial_team_abbr' in info_item:
                                        player_info['team'] = info_item['editorial_team_abbr']
                                    elif 'status' in info_item:
                                        player_info['status'] = info_item['status']
                                    elif 'status_full' in info_item:
                                        player_info['status_full'] = info_item['status_full']
                                    elif 'injury_note' in info_item:
                                        player_info['injury_note'] = info_item['injury_note']
                                    elif 'selected_position' in info_item:
                                        pos_data = info_item['selected_position']
                                        if isinstance(pos_data, list):
                                            for pos_item in pos_data:
                                                if isinstance(pos_item, dict) and 'position' in pos_item:
                                                    player_info['selected_position'] = pos_item['position']
                                                    break
                                        elif isinstance(pos_data, dict) and 'position' in pos_data:
                                            player_info['selected_position'] = pos_data['position']
                                        elif isinstance(pos_data, str):
                                            player_info['selected_position'] = pos_data
                        elif isinstance(player_item, dict):
                            # Handle direct dict structure (fallback)
                            if 'player_key' in player_item:
                                player_info['player_key'] = player_item['player_key']
                            elif 'name' in player_item:
                                name_data = player_item['name']
                                if isinstance(name_data, dict) and 'full' in name_data:
                                    player_info['name'] = name_data['full']
                                elif isinstance(name_data, str):
                                    player_info['name'] = name_data
                            elif 'display_position' in player_item:
                                player_info['position'] = player_item['display_position']
                            elif 'editorial_team_abbr' in player_item:
                                player_info['team'] = player_item['editorial_team_abbr']
                            elif 'status' in player_item:
                                player_info['status'] = player_item['status']
                            elif 'selected_position' in player_item:
                                pos_data = player_item['selected_position']
                                if isinstance(pos_data, dict) and 'position' in pos_data:
                                    player_info['selected_position'] = pos_data['position']
                                elif isinstance(pos_data, str):
                                    player_info['selected_position'] = pos_data
                
                if player_info.get('player_key') and player_info.get('name'):
                    players.append(player_info)
        
        return players
    
    def _parse_players_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse general players response (for free agents, etc.)"""
        try:
            players = []
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                
                # Could be league/players or just players
                if 'league' in fantasy_content:
                    league = fantasy_content['league']
                    if isinstance(league, list):
                        # Look through the league array for the players object
                        for league_item in league:
                            if isinstance(league_item, dict) and 'players' in league_item:
                                players_data = league_item.get('players', {})
                                players = self._extract_players_from_data(players_data)
                                break
                    elif isinstance(league, dict) and 'players' in league:
                        players_data = league.get('players', {})
                        players = self._extract_players_from_data(players_data)
                elif 'players' in fantasy_content:
                    players_data = fantasy_content.get('players', {})
                    players = self._extract_players_from_data(players_data)
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing players response: {e}")
            return []
    
    def _extract_players_from_data(self, players_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player information from players data structure"""
        players = []
        
        for player_key, player_data in players_data.items():
            if not player_key.isdigit():
                continue
            
            player = player_data.get('player', {})
            if isinstance(player, list):
                # Handle nested array structure: player is a list containing a list of dicts
                player_info = {}
                for player_item in player:
                    if isinstance(player_item, list):
                        # This is the nested array we need to process
                        for info_item in player_item:
                            if isinstance(info_item, dict):
                                if 'player_key' in info_item:
                                    player_info['player_key'] = info_item['player_key']
                                elif 'name' in info_item:
                                    name_data = info_item['name']
                                    if isinstance(name_data, dict) and 'full' in name_data:
                                        player_info['name'] = name_data['full']
                                    elif isinstance(name_data, str):
                                        player_info['name'] = name_data
                                elif 'display_position' in info_item:
                                    player_info['position'] = info_item['display_position']
                                elif 'editorial_team_abbr' in info_item:
                                    player_info['team'] = info_item['editorial_team_abbr']
                                elif 'status' in info_item:
                                    player_info['status'] = info_item['status']
                                elif 'status_full' in info_item:
                                    player_info['status_full'] = info_item['status_full']
                                elif 'injury_note' in info_item:
                                    player_info['injury_note'] = info_item['injury_note']
                                elif 'ownership' in info_item:
                                    player_info['ownership_pct'] = info_item['ownership'].get('ownership_percentage', 0)
                                elif 'percent_owned' in info_item:
                                    player_info['ownership_pct'] = info_item['percent_owned']
                    elif isinstance(player_item, dict):
                        # Handle direct dict structure (fallback)
                        if 'player_key' in player_item:
                            player_info['player_key'] = player_item['player_key']
                        elif 'name' in player_item:
                            name_data = player_item['name']
                            if isinstance(name_data, dict) and 'full' in name_data:
                                player_info['name'] = name_data['full']
                            elif isinstance(name_data, str):
                                player_info['name'] = name_data
                        elif 'display_position' in player_item:
                            player_info['position'] = player_item['display_position']
                        elif 'editorial_team_abbr' in player_item:
                            player_info['team'] = player_item['editorial_team_abbr']
                        elif 'status' in player_item:
                            player_info['status'] = player_item['status']
                
                if player_info.get('player_key') and player_info.get('name'):
                    players.append(player_info)
        
        return players
    
    def _parse_player_stats_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse player stats response"""
        try:
            stats = []
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                players_data = fantasy_content.get('players', {})
                
                for player_key, player_data in players_data.items():
                    if not player_key.isdigit():
                        continue
                    
                    player = player_data.get('player', {})
                    if isinstance(player, list):
                        player_stats = {'player_key': None, 'name': None, 'stats': {}}
                        
                        for info_item in player:
                            if isinstance(info_item, dict):
                                if 'player_key' in info_item:
                                    player_stats['player_key'] = info_item['player_key']
                                elif 'name' in info_item:
                                    name_data = info_item['name']
                                    if isinstance(name_data, dict) and 'full' in name_data:
                                        player_stats['name'] = name_data['full']
                                elif 'player_stats' in info_item:
                                    stats_data = info_item['player_stats']
                                    if isinstance(stats_data, dict) and 'stats' in stats_data:
                                        player_stats['stats'] = stats_data['stats']
                        
                        if player_stats.get('player_key') and player_stats.get('name'):
                            stats.append(player_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error parsing player stats response: {e}")
            return []
    
    def _parse_player_news_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse player news response"""
        try:
            news = []
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                players_data = fantasy_content.get('players', {})
                
                for player_key, player_data in players_data.items():
                    if not player_key.isdigit():
                        continue
                    
                    player = player_data.get('player', {})
                    if isinstance(player, list):
                        player_news = {'player_key': None, 'name': None, 'news': []}
                        
                        for info_item in player:
                            if isinstance(info_item, dict):
                                if 'player_key' in info_item:
                                    player_news['player_key'] = info_item['player_key']
                                elif 'name' in info_item:
                                    name_data = info_item['name']
                                    if isinstance(name_data, dict) and 'full' in name_data:
                                        player_news['name'] = name_data['full']
                                elif 'news' in info_item:
                                    player_news['news'] = info_item['news']
                        
                        if player_news.get('player_key') and player_news.get('name'):
                            news.append(player_news)
            
            return news
            
        except Exception as e:
            logger.error(f"Error parsing player news response: {e}")
            return []
    
    def _save_debug_response(self, response: Dict[str, Any], filename: str):
        """Save API response for debugging"""
        try:
            debug_dir = os.path.join(script_dir, "debug_responses")
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = os.path.join(debug_dir, f"{filename}_{timestamp}.json")
            
            with open(debug_file, 'w') as f:
                json.dump(response, f, indent=2)
            
            logger.debug(f"Debug response saved: {debug_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save debug response: {e}")

def main():
    """Test the data retriever"""
    try:
        print("🏈 Testing Yahoo Fantasy Sports Data Retriever...")
        
        retriever = YahooDataRetriever()
        
        # Test basic connection
        print("\n🔌 Testing basic API connection...")
        if not retriever.test_basic_connection():
            print("❌ Basic API connection failed")
            return
        
        print("✅ Basic API connection successful!")
        
        # Test getting league key
        print("\n🏆 Getting league key...")
        league_key = retriever.get_league_key()
        if league_key:
            print(f"✅ League key: {league_key}")
        else:
            print("❌ Failed to get league key")
            return
        
        # Test free agents
        print("\n🔍 Testing free agents retrieval...")
        free_agents = retriever.get_free_agents(count=10)
        print(f"✅ Retrieved {len(free_agents)} free agents")
        if free_agents:
            print("Sample free agents:")
            for i, player in enumerate(free_agents[:3]):
                print(f"  {i+1}. {player.get('name')} ({player.get('position')}) - {player.get('team')}")
        
        # Test opponent rosters
        print("\n👥 Testing opponent rosters retrieval...")
        opponent_rosters = retriever.get_opponent_rosters()
        print(f"✅ Retrieved rosters for {len(opponent_rosters)} opponent teams")
        for team_name, roster in list(opponent_rosters.items())[:2]:
            print(f"  {team_name}: {len(roster)} players")
        
        # Test top available players
        print("\n⭐ Testing top available players...")
        top_players = retriever.get_top_available_players(count=10)
        print(f"✅ Retrieved {len(top_players)} top available players")
        if top_players:
            print("Top available players:")
            for i, player in enumerate(top_players[:3]):
                print(f"  {i+1}. {player.get('name')} ({player.get('position')}) - {player.get('team')}")
        
        # Test research data
        print("\n📊 Testing research data retrieval...")
        research_data = retriever.get_research_data()
        print(f"✅ Retrieved {len(research_data)} research data sets")
        for data_type in research_data.keys():
            print(f"  - {data_type}")
        
        print("\n🎉 All data retrieval tests completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
