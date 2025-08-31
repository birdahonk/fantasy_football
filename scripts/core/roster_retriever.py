#!/usr/bin/env python3
"""
Roster Retriever for Yahoo Fantasy Sports API
Uses OAuth 2.0 client to fetch team roster data
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from oauth.oauth2_client import YahooOAuth2Client
except ImportError:
    # Fallback for when running from root directory
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from oauth.oauth2_client import YahooOAuth2Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RosterRetriever:
    """Retrieves roster data from Yahoo Fantasy Sports API using OAuth 2.0"""
    
    def __init__(self):
        """Initialize the roster retriever with OAuth 2.0 client"""
        try:
            self.oauth_client = YahooOAuth2Client()
            self.base_url = "https://fantasysports.yahooapis.com/fantasy/v2"
            logger.info("RosterRetriever initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RosterRetriever: {e}")
            raise
    
    def test_basic_api_connection(self) -> bool:
        """Test basic API connection with a simple endpoint"""
        try:
            logger.info("Testing basic API connection...")
            
            # Use a simple endpoint that doesn't require user-specific data
            endpoint = "game/nfl"
            
            response = self.oauth_client.make_request(endpoint)
            if not response:
                logger.error("Failed to get basic game info")
                return False
            
            # Extract the parsed data from the response wrapper
            if isinstance(response, dict) and response.get('status') == 'success':
                parsed_data = response.get('parsed')
                if parsed_data:
                    logger.info("✅ Basic API connection successful!")
                    logger.info(f"Game info: {parsed_data}")
                    return True
                else:
                    logger.error("No parsed data in basic response")
                    return False
            else:
                logger.error("Invalid basic response format")
                return False
                
        except Exception as e:
            logger.error(f"Error testing basic API connection: {e}")
            return False
    
    def get_user_teams(self) -> List[Dict[str, Any]]:
        """Get all fantasy teams for the authenticated user"""
        try:
            if not self.oauth_client.is_authenticated():
                logger.error("Not authenticated with Yahoo API")
                return []
            
            # Based on Yahoo API docs, get teams directly from user's games
            endpoint = "users;use_login=1/games;game_keys=nfl/teams"
            logger.info(f"Getting user teams with endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response:
                logger.error("Failed to get user teams")
                return []
            
            # Extract the parsed data from the response wrapper
            if isinstance(response, dict) and response.get('status') == 'success':
                parsed_data = response.get('parsed')
                if parsed_data:
                    logger.info("Using parsed data from response")
                else:
                    logger.error("No parsed data in response")
                    return []
            else:
                logger.error("Invalid response format")
                return []
            
            # Parse the response to extract team information
            teams = self._parse_user_teams_response(parsed_data)
            logger.info(f"Found {len(teams)} fantasy teams")
            return teams
            
        except Exception as e:
            logger.error(f"Error getting user teams: {e}")
            return []
    
    def get_team_roster(self, team_key: str) -> List[Dict[str, Any]]:
        """Get the current roster for a specific team"""
        try:
            if not self.oauth_client.is_authenticated():
                logger.error("Not authenticated with Yahoo API")
                return []
            
            # Yahoo API endpoint for team roster
            endpoint = f"team/{team_key}/roster"
            logger.info(f"Requesting roster for team key: {team_key}")
            logger.info(f"Using endpoint: {endpoint}")
            
            response = self.oauth_client.make_request(endpoint)
            if not response:
                logger.error(f"Failed to get roster for team {team_key}")
                return []
            
            # Extract the parsed data from the response wrapper
            if isinstance(response, dict) and response.get('status') == 'success':
                parsed_data = response.get('parsed')
                if not parsed_data:
                    logger.error("No parsed data in roster response")
                    return []
            else:
                logger.error("Invalid roster response format")
                return []
            
            # Parse the response to extract roster data
            roster = self._parse_roster_response(parsed_data)
            logger.info(f"Retrieved roster with {len(roster)} players for team {team_key}")
            return roster
            
        except Exception as e:
            logger.error(f"Error getting team roster: {e}")
            return []
    
    def get_team_info(self, team_key: str) -> Optional[Dict[str, Any]]:
        """Get basic team information"""
        try:
            if not self.oauth_client.is_authenticated():
                logger.error("Not authenticated with Yahoo API")
                return None
            
            # Yahoo API endpoint for team info
            endpoint = f"team/{team_key}"
            
            response = self.oauth_client.make_request(endpoint)
            if not response:
                logger.error(f"Failed to get team info for {team_key}")
                return None
            
            # Extract the parsed data from the response wrapper
            if isinstance(response, dict) and response.get('status') == 'success':
                parsed_data = response.get('parsed')
                if not parsed_data:
                    logger.error("No parsed data in team info response")
                    return None
            else:
                logger.error("Invalid team info response format")
                return None
            
            # Parse the response to extract team information
            team_info = self._parse_team_response(parsed_data)
            logger.info(f"Retrieved team info for {team_key}")
            return team_info
            
        except Exception as e:
            logger.error(f"Error getting team info: {e}")
            return None
    
    def discover_primary_team(self) -> Optional[Dict[str, Any]]:
        """Automatically discover the user's primary fantasy team"""
        try:
            logger.info("Discovering primary fantasy team...")
            
            # Get user's teams directly (this is the correct approach per Yahoo API docs)
            teams = self.get_user_teams()
            if not teams:
                logger.error("No teams found for user")
                return None
            
            # Find the user's team (should be the first one since we're using use_login=1)
            if teams:
                primary_team = teams[0]
                logger.info(f"Primary team discovered: {primary_team.get('name', 'Unknown')}")
                logger.info(f"Team key: {primary_team.get('team_key')}")
                logger.info(f"League key: {primary_team.get('league_key')}")
                return primary_team
            else:
                logger.error("No teams found in response")
                return None
            
        except Exception as e:
            logger.error(f"Error discovering primary team: {e}")
            return None
    
    def get_complete_roster_data(self) -> Dict[str, Any]:
        """Get complete roster data including team info and players"""
        try:
            logger.info("Getting complete roster data...")
            
            # Discover primary team
            team_info = self.discover_primary_team()
            if not team_info:
                logger.error("Could not discover primary team")
                return {}
            
            team_key = team_info.get('team_key')
            if not team_key:
                logger.error("No team key found in team info")
                return {}
            
            # Get roster
            roster = self.get_team_roster(team_key)
            if not roster:
                logger.error("Could not retrieve team roster")
                return {}
            
            # Compile complete data
            complete_data = {
                'team_info': team_info,
                'roster': roster,
                'retrieved_at': datetime.now().isoformat(),
                'total_players': len(roster),
                'position_breakdown': self._get_position_breakdown(roster)
            }
            
            logger.info(f"Complete roster data retrieved: {complete_data['total_players']} players")
            return complete_data
            
        except Exception as e:
            logger.error(f"Error getting complete roster data: {e}")
            return {}
    
    def _get_league_teams(self, league_key: str) -> List[Dict[str, Any]]:
        """Get all teams in a specific league"""
        try:
            endpoint = f"league/{league_key}/teams"
            response = self.oauth_client.make_request(endpoint)
            
            if not response:
                return []
            
            # Extract the parsed data from the response wrapper
            if isinstance(response, dict) and response.get('status') == 'success':
                parsed_data = response.get('parsed')
                if not parsed_data:
                    logger.error("No parsed data in league teams response")
                    return []
            else:
                logger.error("Invalid league teams response format")
                return []
            
            # Parse teams from response
            teams = self._parse_teams_response(parsed_data)
            return teams
            
        except Exception as e:
            logger.error(f"Error getting league teams: {e}")
            return []
    
    def _get_position_breakdown(self, roster: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of players by position"""
        breakdown = {}
        for player in roster:
            position = player.get('position', 'Unknown')
            breakdown[position] = breakdown.get(position, 0) + 1
        return breakdown
    
    def _parse_leagues_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo API response to extract league information"""
        try:
            leagues = []
            
            # Debug: Log the response structure
            logger.info(f"Parsing leagues response. Response type: {type(response)}")
            logger.info(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                logger.info(f"FULL RESPONSE STRUCTURE:")
                logger.info(json.dumps(response, indent=2))
                
                # Let's also check the specific path we're looking for
                fantasy_content = response.get('fantasy_content', {})
                users = fantasy_content.get('users', {})
                logger.info(f"Users structure: {json.dumps(users, indent=2)}")
                
                if users:
                    for user_key, user_data in users.items():
                        logger.info(f"User {user_key}: {json.dumps(user_data, indent=2)}")
                        if user_key != '0':  # Skip metadata
                            user_obj = user_data.get('user', {})
                            logger.info(f"User object: {json.dumps(user_obj, indent=2)}")
                            
                            if isinstance(user_obj, list):
                                for i, user_item in enumerate(user_obj):
                                    logger.info(f"User item {i}: {json.dumps(user_item, indent=2)}")
                                    if 'games' in user_item:
                                        games = user_item['games']
                                        logger.info(f"Games found: {json.dumps(games, indent=2)}")
                                        
                                        for game_key, game_data in games.items():
                                            if game_key != '0':
                                                logger.info(f"Game {game_key}: {json.dumps(game_data, indent=2)}")
                                                game = game_data.get('game', {})
                                                if isinstance(game, list):
                                                    for j, game_item in enumerate(game):
                                                        logger.info(f"Game item {j}: {json.dumps(game_item, indent=2)}")
                                                        if game_item.get('code') == 'nfl':
                                                            logger.info(f"NFL game found: {json.dumps(game_item, indent=2)}")
                                                            leagues_data = game_item.get('leagues', {})
                                                            logger.info(f"Leagues data: {json.dumps(leagues_data, indent=2)}")
            
            # Navigate through the response structure
            fantasy_content = response.get('fantasy_content', {})
            users = fantasy_content.get('users', {})
            
            # Handle the user structure
            for user_key, user_data in users.items():
                if user_key == '0':  # Skip metadata
                    continue
                
                games = user_data.get('user', {}).get('games', {})
                for game_key, game_data in games.items():
                    if game_key == '0':  # Skip metadata
                        continue
                    
                    game = game_data.get('game', {})
                    if game.get('code') == 'nfl':  # NFL fantasy football
                        leagues_data = game.get('leagues', {})
                        for league_key, league_data in leagues_data.items():
                            if league_key == '0':  # Skip metadata
                                continue
                            
                            league = league_data.get('league', {})
                            leagues.append({
                                'league_key': league.get('league_key'),
                                'name': league.get('name'),
                                'season': league.get('season'),
                                'game_code': game.get('code'),
                                'league_id': league.get('league_id')
                            })
            
            return leagues
            
        except Exception as e:
            logger.error(f"Error parsing leagues response: {e}")
            return []
    
    def _parse_teams_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo API response to extract team information"""
        try:
            teams = []
            
            fantasy_content = response.get('fantasy_content', {})
            league = fantasy_content.get('league', {})
            teams_data = league.get('teams', {})
            
            for team_key, team_data in teams_data.items():
                if team_key == '0':  # Skip metadata
                    continue
                
                team = team_data.get('team', {})
                teams.append({
                    'team_key': team.get('team_key'),
                    'name': team.get('name'),
                    'is_my_team': team.get('is_my_team', False),
                    'league_key': league.get('league_key')
                })
            
            return teams
            
        except Exception as e:
            logger.error(f"Error parsing teams response: {e}")
            return []
    
    def _parse_roster_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo API response to extract roster data"""
        try:
            roster = []
            
            fantasy_content = response.get('fantasy_content', {})
            team = fantasy_content.get('team', {})
            roster_data = team.get('roster', {})
            players = roster_data.get('0', {}).get('players', {})
            
            for player_key, player_data in players.items():
                if player_key == '0':  # Skip metadata
                    continue
                
                player = player_data.get('player', {})
                roster.append({
                    'player_key': player.get('player_key'),
                    'name': player.get('name', {}).get('full', 'Unknown'),
                    'position': player.get('display_position', 'Unknown'),
                    'team': player.get('editorial_team_abbr', 'Unknown'),
                    'status': player.get('status', ''),
                    'selected_position': player.get('selected_position', {}).get('position', 'Unknown'),
                    'bye_week': player.get('bye_weeks', {}).get('week', ''),
                    'percent_owned': player.get('percent_owned', 0),
                    'rank': player.get('rank', 0)
                })
            
            return roster
            
        except Exception as e:
            logger.error(f"Error parsing roster response: {e}")
            return []
    
    def _parse_user_teams_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse user teams response from Yahoo API"""
        try:
            teams = []
            logger.info(f"Parsing user teams response. Response type: {type(response)}")
            logger.info(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if isinstance(response, dict):
                logger.info(f"User teams response structure: {json.dumps(response, indent=2)}")
                
                # Navigate through the response structure
                fantasy_content = response.get('fantasy_content', {})
                users = fantasy_content.get('users', {})
                
                # Handle the user structure
                for user_key, user_data in users.items():
                    logger.info(f"Processing user_key: {user_key}, user_data type: {type(user_data)}")
                    # Skip non-numeric keys (like 'count'), but allow '0' as it contains actual user data
                    if not user_key.isdigit():
                        logger.info(f"Skipping key: {user_key} (non-numeric)")
                        continue
                    
                    user_obj = user_data.get('user', {})
                    logger.info(f"User obj: {user_obj}, type: {type(user_obj)}")
                    if isinstance(user_obj, list):
                        for i, user_item in enumerate(user_obj):
                            logger.info(f"User item {i}: {user_item}, type: {type(user_item)}")
                            if isinstance(user_item, dict) and 'games' in user_item:
                                games = user_item['games']
                                logger.info(f"Games found: {games}, type: {type(games)}")
                                for game_key, game_data in games.items():
                                    logger.info(f"Game key: {game_key}, game_data type: {type(game_data)}")
                                    # Skip non-numeric keys (like 'count'), but allow '0' as it contains actual game data
                                    if not game_key.isdigit():
                                        logger.info(f"Skipping game key: {game_key} (non-numeric)")
                                        continue
                                    
                                    game = game_data.get('game', {})
                                    logger.info(f"Game: {game}, type: {type(game)}")
                                    if isinstance(game, list):
                                        for j, game_item in enumerate(game):
                                            logger.info(f"Game item {j}: {game_item}, type: {type(game_item)}")
                                            if isinstance(game_item, dict):
                                                # Check if this is an NFL game OR if it contains teams data
                                                if game_item.get('code') == 'nfl' or 'teams' in game_item:
                                                    # Look for teams in the game
                                                    teams_data = game_item.get('teams', {})
                                                    logger.info(f"Teams data found: {teams_data}")
                                                    if teams_data:
                                                        for team_key, team_data in teams_data.items():
                                                            logger.info(f"Processing team_key: {team_key}, team_data type: {type(team_data)}")
                                                            # Skip non-numeric keys (like 'count'), but allow '0' as it contains actual team data
                                                            if not team_key.isdigit():
                                                                logger.info(f"Skipping team key: {team_key} (non-numeric)")
                                                                continue
                                                            team_array = team_data.get('team', [])
                                                            logger.info(f"Team array: {team_array}, type: {type(team_array)}")
                                                            if isinstance(team_array, list):
                                                                for i, team_item in enumerate(team_array):
                                                                    logger.info(f"Team item {i}: {team_item}, type: {type(team_item)}")
                                                                    if team_item is not None and isinstance(team_item, list):
                                                                        logger.info(f"Processing team item list: {team_item}")
                                                                        # Extract team info from the array
                                                                        team_info = {}
                                                                        for j, info_item in enumerate(team_item):
                                                                            logger.info(f"Info item {j}: {info_item}, type: {type(info_item)}")
                                                                            if isinstance(info_item, dict):
                                                                                if 'team_key' in info_item:
                                                                                    team_info['team_key'] = info_item['team_key']
                                                                                    logger.info(f"Found team_key: {info_item['team_key']}")
                                                                                elif 'name' in info_item:
                                                                                    team_info['name'] = info_item['name']
                                                                                    logger.info(f"Found name: {info_item['name']}")
                                                                                elif 'is_owned_by_current_login' in info_item:
                                                                                    team_info['is_my_team'] = bool(info_item['is_owned_by_current_login'])
                                                                                    logger.info(f"Found is_owned_by_current_login: {info_item['is_owned_by_current_login']}")
                                                                        
                                                                        logger.info(f"Extracted team_info: {team_info}")
                                                                        if team_info.get('team_key') and team_info.get('name'):
                                                                            # Extract league key from team key (format: 461.l.595012.t.3)
                                                                            team_key_parts = team_info['team_key'].split('.')
                                                                            if len(team_key_parts) >= 3:
                                                                                league_key = f"{team_key_parts[0]}.{team_key_parts[1]}"
                                                                            else:
                                                                                league_key = None
                                                                            
                                                                            team_obj = {
                                                                                'team_key': team_info['team_key'],
                                                                                'name': team_info['name'],
                                                                                'league_key': league_key,
                                                                                'season': game_item.get('season', '2025'),
                                                                                'game_code': game_item.get('code'),
                                                                                'is_my_team': team_info.get('is_my_team', True)
                                                                            }
                                                                            teams.append(team_obj)
                                                                            logger.info(f"Added team: {team_obj}")
                                                                        else:
                                                                            logger.warning(f"Incomplete team_info: {team_info}")
                                                                    else:
                                                                        logger.info(f"Skipping team_item (not a list): {team_item}")
                                                            else:
                                                                logger.warning(f"Team array is not a list: {team_array}")
                                                else:
                                                    logger.warning("No teams data found in game")
            
            logger.info(f"Parsed {len(teams)} teams from user teams response")
            return teams
            
        except Exception as e:
            logger.error(f"Error parsing user teams response: {e}")
            return []
    
    def _parse_team_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Yahoo API response to extract team information"""
        try:
            fantasy_content = response.get('fantasy_content', {})
            team = fantasy_content.get('team', {})
            
            return {
                'team_key': team.get('team_key'),
                'name': team.get('name'),
                'league_key': team.get('league_key'),
                'season': team.get('season'),
                'game_code': team.get('game_code'),
                'is_my_team': team.get('is_my_team', False)
            }
            
        except Exception as e:
            logger.error(f"Error parsing team response: {e}")
            return None
    
    def _parse_roster_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Yahoo API response to extract roster data"""
        try:
            logger.info(f"Parsing roster response. Response type: {type(response)}")
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                team = fantasy_content.get('team', {})
                
                if not team:
                    logger.error("No team data found in roster response")
                    return []
                
                # The team structure is a list with [team_info, roster_data]
                if isinstance(team, list) and len(team) >= 2:
                    roster_data = team[1]  # Second element contains roster
                    if isinstance(roster_data, dict) and 'roster' in roster_data:
                        roster = roster_data['roster']
                        
                        # Look for the '0' key which contains the players
                        if '0' in roster and isinstance(roster['0'], dict) and 'players' in roster['0']:
                            players_data = roster['0']['players']
                            
                            players = []
                            for player_key, player_data in players_data.items():
                                logger.info(f"Processing player_key: {player_key}, player_data type: {type(player_data)}")
                                # Skip non-numeric keys (like 'count')
                                if not player_key.isdigit():
                                    logger.info(f"Skipping player key: {player_key} (non-numeric)")
                                    continue
                                
                                if 'player' in player_data:
                                    player_array = player_data['player']
                                    if isinstance(player_array, list) and len(player_array) >= 1:
                                        # First element contains player info
                                        player_info_array = player_array[0]
                                        if isinstance(player_info_array, list):
                                            player_info = self._extract_player_info_from_list(player_info_array)
                                            
                                            # Second element contains selected position info
                                            if len(player_array) >= 2 and isinstance(player_array[1], dict):
                                                selected_pos_data = player_array[1].get('selected_position', [])
                                                if isinstance(selected_pos_data, list):
                                                    for pos_item in selected_pos_data:
                                                        if isinstance(pos_item, dict) and 'position' in pos_item:
                                                            player_info['selected_position'] = pos_item['position']
                                                            break
                                            
                                            if player_info and player_info.get('player_key') and player_info.get('name'):
                                                players.append(player_info)
                                                logger.info(f"Added player: {player_info.get('name')} ({player_info.get('position')}) - {player_info.get('selected_position', 'N/A')}")
                            
                            logger.info(f"Successfully parsed {len(players)} players from roster")
                            return players
                        else:
                            logger.error("No players data found in roster structure")
                            return []
                    else:
                        logger.error("No roster found in team data")
                        return []
                else:
                    logger.error(f"Team structure is not a list or has insufficient elements: {type(team)}")
                    return []
            else:
                logger.error(f"Roster response is not a dict: {type(response)}")
                return []
            
        except Exception as e:
            logger.error(f"Error parsing roster response: {e}")
            return []
    
    def _parse_team_players_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse team players response (alternative approach)"""
        try:
            logger.info(f"Parsing team players response. Response type: {type(response)}")
            
            players = []
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                team = fantasy_content.get('team', {})
                
                # Handle team as list or dict
                if isinstance(team, list):
                    for team_item in team:
                        if isinstance(team_item, dict) and 'players' in team_item:
                            players_data = team_item['players']
                            players = self._extract_players_from_data(players_data)
                            break
                elif isinstance(team, dict) and 'players' in team:
                    players_data = team['players']
                    players = self._extract_players_from_data(players_data)
            
            logger.info(f"Parsed {len(players)} players from team players response")
            return players
            
        except Exception as e:
            logger.error(f"Error parsing team players response: {e}")
            return []
    
    def _parse_league_team_roster(self, response: Dict[str, Any], target_team_key: str) -> List[Dict[str, Any]]:
        """Parse league teams response to find specific team's roster"""
        try:
            logger.info(f"Looking for team {target_team_key} in league teams response")
            
            if isinstance(response, dict):
                fantasy_content = response.get('fantasy_content', {})
                league = fantasy_content.get('league', {})
                
                # Handle league as list
                if isinstance(league, list):
                    for league_item in league:
                        if isinstance(league_item, dict) and 'teams' in league_item:
                            teams = league_item['teams']
                            for team_key, team_data in teams.items():
                                if team_key.isdigit():
                                    team = team_data.get('team', {})
                                    if isinstance(team, list):
                                        for team_item in team:
                                            if isinstance(team_item, list):
                                                # Find team key in the team data
                                                found_team_key = None
                                                for info_item in team_item:
                                                    if isinstance(info_item, dict) and 'team_key' in info_item:
                                                        found_team_key = info_item['team_key']
                                                        break
                                                
                                                if found_team_key == target_team_key:
                                                    logger.info(f"Found target team {target_team_key}")
                                                    # Look for roster in this team
                                                    for info_item in team_item:
                                                        if isinstance(info_item, dict) and 'roster' in info_item:
                                                            roster_data = info_item['roster']
                                                            return self._extract_players_from_roster(roster_data)
            
            logger.warning(f"Could not find team {target_team_key} in league teams response")
            return []
            
        except Exception as e:
            logger.error(f"Error parsing league team roster: {e}")
            return []
    
    def _extract_players_from_data(self, players_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player information from players data structure"""
        try:
            players = []
            
            if isinstance(players_data, dict):
                for player_key, player_data in players_data.items():
                    if player_key.isdigit():
                        player = player_data.get('player', {})
                        if isinstance(player, list):
                            player_info = self._extract_player_info_from_list(player)
                            if player_info:
                                players.append(player_info)
            
            return players
            
        except Exception as e:
            logger.error(f"Error extracting players from data: {e}")
            return []
    
    def _extract_players_from_roster(self, roster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player information from roster data structure"""
        try:
            players = []
            
            if isinstance(roster_data, dict):
                for player_key, player_data in roster_data.items():
                    if player_key.isdigit():
                        player = player_data.get('player', {})
                        if isinstance(player, list):
                            player_info = self._extract_player_info_from_list(player)
                            if player_info:
                                players.append(player_info)
            
            return players
            
        except Exception as e:
            logger.error(f"Error extracting players from roster: {e}")
            return []
    
    def _extract_player_info_from_list(self, player_list: List[Any]) -> Optional[Dict[str, Any]]:
        """Extract player information from a list structure"""
        try:
            player_info = {}
            
            for item in player_list:
                if isinstance(item, dict):
                    if 'player_key' in item:
                        player_info['player_key'] = item['player_key']
                    elif 'name' in item:
                        name_data = item['name']
                        if isinstance(name_data, dict) and 'full' in name_data:
                            player_info['name'] = name_data['full']
                        elif isinstance(name_data, list):
                            for name_item in name_data:
                                if isinstance(name_item, dict) and 'full' in name_item:
                                    player_info['name'] = name_item['full']
                                    break
                    elif 'display_position' in item:
                        player_info['position'] = item['display_position']
                    elif 'editorial_team_abbr' in item:
                        player_info['team'] = item['editorial_team_abbr']
                    elif 'status' in item:
                        player_info['status'] = item['status']
                    elif 'selected_position' in item:
                        pos_data = item['selected_position']
                        if isinstance(pos_data, dict) and 'position' in pos_data:
                            player_info['selected_position'] = pos_data['position']
                        elif isinstance(pos_data, list):
                            for pos_item in pos_data:
                                if isinstance(pos_item, dict) and 'position' in pos_item:
                                    player_info['selected_position'] = pos_item['position']
                                    break
            
            # Only return if we have essential info
            if player_info.get('player_key') and player_info.get('name'):
                return {
                    'player_key': player_info['player_key'],
                    'name': player_info['name'],
                    'position': player_info.get('position'),
                    'team': player_info.get('team'),
                    'status': player_info.get('status'),
                    'selected_position': player_info.get('selected_position')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting player info from list: {e}")
            return None
    
    def get_account_metadata(self) -> Dict[str, Any]:
        """Get comprehensive metadata about user account, leagues, and teams"""
        try:
            logger.info("Getting comprehensive account metadata...")
            
            metadata = {}
            
            # 1. Get user profile info
            logger.info("Getting user profile...")
            profile_endpoint = "users;use_login=1/profile"
            profile_response = self.oauth_client.make_request(profile_endpoint)
            if profile_response and profile_response.get('status') == 'success':
                metadata['profile'] = profile_response.get('parsed', {})
                logger.info("✅ Retrieved user profile")
            else:
                logger.warning("❌ Failed to get user profile")
            
            # 2. Get all user's games (not just NFL)
            logger.info("Getting all user games...")
            games_endpoint = "users;use_login=1/games"
            games_response = self.oauth_client.make_request(games_endpoint)
            if games_response and games_response.get('status') == 'success':
                metadata['games'] = games_response.get('parsed', {})
                logger.info("✅ Retrieved all user games")
            else:
                logger.warning("❌ Failed to get user games")
            
            # 3. Get current NFL teams and league info
            logger.info("Getting current NFL teams and league info...")
            teams_endpoint = "users;use_login=1/games;game_keys=nfl/teams"
            teams_response = self.oauth_client.make_request(teams_endpoint)
            if teams_response and teams_response.get('status') == 'success':
                metadata['current_teams'] = teams_response.get('parsed', {})
                logger.info("✅ Retrieved current NFL teams")
                
                # Try to extract league key from teams response - simplified approach
                teams_data = teams_response.get('parsed', {})
                if teams_data:
                    # We already know the team key from previous discovery: 461.l.595012.t.3
                    # Extract league key: 461.l.595012
                    league_key = "461.l.595012"
                    team_key = "461.l.595012.t.3"
                    
                    # Now get league details
                    logger.info(f"Getting league details for {league_key}...")
                    league_endpoint = f"league/{league_key}"
                    league_response = self.oauth_client.make_request(league_endpoint)
                    if league_response and league_response.get('status') == 'success':
                        metadata['league'] = league_response.get('parsed', {})
                        logger.info("✅ Retrieved league details")
                    else:
                        logger.warning("❌ Failed to get league details")
                    
                    # Get team details
                    logger.info(f"Getting team details for {team_key}...")
                    team_endpoint = f"team/{team_key}"
                    team_response = self.oauth_client.make_request(team_endpoint)
                    if team_response and team_response.get('status') == 'success':
                        metadata['team'] = team_response.get('parsed', {})
                        logger.info("✅ Retrieved team details")
                    else:
                        logger.warning("❌ Failed to get team details")
                    
                    # Get league standings
                    logger.info(f"Getting league standings for {league_key}...")
                    standings_endpoint = f"league/{league_key}/standings"
                    standings_response = self.oauth_client.make_request(standings_endpoint)
                    if standings_response and standings_response.get('status') == 'success':
                        metadata['standings'] = standings_response.get('parsed', {})
                        logger.info("✅ Retrieved league standings")
                    else:
                        logger.warning("❌ Failed to get league standings")
            else:
                logger.warning("❌ Failed to get current NFL teams")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting account metadata: {e}")
            return {}

def main():
    """Test the roster retriever with multiple approaches"""
    try:
        print("🏈 Testing Roster Retriever with Multiple Approaches...")
        
        retriever = RosterRetriever()
        
        # First test basic API connection
        print("\n🔌 Testing basic API connection...")
        if retriever.test_basic_api_connection():
            print("✅ Basic API connection successful!")
        else:
            print("❌ Basic API connection failed")
            return
        
        # Test different roster retrieval approaches
        team_key = "461.l.595012.t.3"
        
        print(f"\n🔍 Testing multiple roster endpoints for team {team_key}...")
        
        # Approach 1: Standard roster endpoint
        print("\n📋 Approach 1: Standard roster endpoint")
        try:
            endpoint1 = f"team/{team_key}/roster"
            response1 = retriever.oauth_client.make_request(endpoint1)
            if response1 and response1.get('status') == 'success':
                print("✅ Standard roster endpoint successful")
                raw_data1 = response1.get('data', '')
                parsed_data1 = response1.get('parsed', {})
                
                # Save raw response for analysis
                with open("scripts/analysis/roster_raw_standard.json", 'w') as f:
                    json.dump(parsed_data1, f, indent=2)
                print("💾 Raw response saved to roster_raw_standard.json")
                
                # Try parsing
                roster1 = retriever._parse_roster_response(parsed_data1)
                print(f"📊 Parsed {len(roster1)} players from standard endpoint")
                if roster1:
                    print("👥 Players found:")
                    for player in roster1[:5]:  # Show first 5
                        print(f"   - {player.get('name', 'Unknown')} ({player.get('position', 'N/A')})")
            else:
                print("❌ Standard roster endpoint failed")
        except Exception as e:
            print(f"❌ Standard roster endpoint error: {e}")
        
        # Approach 2: Team with roster subresource
        print("\n📋 Approach 2: Team with roster subresource")
        try:
            endpoint2 = f"team/{team_key};out=roster"
            response2 = retriever.oauth_client.make_request(endpoint2)
            if response2 and response2.get('status') == 'success':
                print("✅ Team with roster subresource successful")
                parsed_data2 = response2.get('parsed', {})
                
                # Save raw response for analysis
                with open("scripts/analysis/roster_raw_subresource.json", 'w') as f:
                    json.dump(parsed_data2, f, indent=2)
                print("💾 Raw response saved to roster_raw_subresource.json")
                
                # Try parsing
                roster2 = retriever._parse_roster_response(parsed_data2)
                print(f"📊 Parsed {len(roster2)} players from subresource endpoint")
                if roster2:
                    print("👥 Players found:")
                    for player in roster2[:5]:  # Show first 5
                        print(f"   - {player.get('name', 'Unknown')} ({player.get('position', 'N/A')})")
            else:
                print("❌ Team with roster subresource failed")
        except Exception as e:
            print(f"❌ Team with roster subresource error: {e}")
        
        # Approach 3: Team with players subresource
        print("\n📋 Approach 3: Team with players subresource")
        try:
            endpoint3 = f"team/{team_key};out=players"
            response3 = retriever.oauth_client.make_request(endpoint3)
            if response3 and response3.get('status') == 'success':
                print("✅ Team with players subresource successful")
                parsed_data3 = response3.get('parsed', {})
                
                # Save raw response for analysis
                with open("scripts/analysis/roster_raw_players.json", 'w') as f:
                    json.dump(parsed_data3, f, indent=2)
                print("💾 Raw response saved to roster_raw_players.json")
                
                # Try parsing with different approach
                roster3 = retriever._parse_team_players_response(parsed_data3)
                print(f"📊 Parsed {len(roster3)} players from players endpoint")
                if roster3:
                    print("👥 Players found:")
                    for player in roster3[:5]:  # Show first 5
                        print(f"   - {player.get('name', 'Unknown')} ({player.get('position', 'N/A')})")
            else:
                print("❌ Team with players subresource failed")
        except Exception as e:
            print(f"❌ Team with players subresource error: {e}")
        
        # Approach 4: League teams with rosters
        print("\n📋 Approach 4: League teams with rosters")
        try:
            league_key = "461.l.595012"
            endpoint4 = f"league/{league_key}/teams;out=roster"
            response4 = retriever.oauth_client.make_request(endpoint4)
            if response4 and response4.get('status') == 'success':
                print("✅ League teams with rosters successful")
                parsed_data4 = response4.get('parsed', {})
                
                # Save raw response for analysis
                with open("scripts/analysis/roster_raw_league_teams.json", 'w') as f:
                    json.dump(parsed_data4, f, indent=2)
                print("💾 Raw response saved to roster_raw_league_teams.json")
                
                # Try to find your team in the league data
                your_roster = retriever._parse_league_team_roster(parsed_data4, team_key)
                print(f"📊 Found your roster with {len(your_roster)} players from league endpoint")
                if your_roster:
                    print("👥 Your players:")
                    for player in your_roster[:5]:  # Show first 5
                        print(f"   - {player.get('name', 'Unknown')} ({player.get('position', 'N/A')})")
            else:
                print("❌ League teams with rosters failed")
        except Exception as e:
            print(f"❌ League teams with rosters error: {e}")
        
        print("\n🔍 Analysis complete! Check the saved JSON files for detailed API responses.")
            
    except Exception as e:
        print(f"❌ Error testing roster retriever: {e}")

if __name__ == "__main__":
    main()
