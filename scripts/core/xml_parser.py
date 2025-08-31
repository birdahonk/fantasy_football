#!/usr/bin/env python3
"""
XML Parser for Yahoo! Fantasy Sports API
Handles parsing of XML responses from Yahoo! Fantasy Sports API
Based on official API documentation structure
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class YahooXMLParser:
    """Parser for Yahoo! Fantasy Sports API XML responses"""
    
    def __init__(self):
        # Yahoo! XML namespaces
        self.namespaces = {
            'yahoo': 'http://yahooapis.com/v1/base.rng',
            'fantasy': 'http://fantasysports.yahooapis.com/fantasy/v2'
        }
    
    def parse_fantasy_content(self, xml_data: ET.Element) -> Dict[str, Any]:
        """Parse the main fantasy_content element from Yahoo! API responses"""
        try:
            result = {}
            
            # Find fantasy_content element - check if root or child
            fantasy_content = xml_data.find('.//fantasy_content')
            if fantasy_content is None:
                # Check if the root element is fantasy_content
                if xml_data.tag == 'fantasy_content':
                    fantasy_content = xml_data
                else:
                    logger.warning("No fantasy_content element found")
                    return {}
            
            # Parse based on content type
            for child in fantasy_content:
                if child.tag == 'users':
                    result['users'] = self._parse_users(child)
                elif child.tag == 'league':
                    result['league'] = self._parse_league(child)
                elif child.tag == 'team':
                    result['team'] = self._parse_team(child)
                elif child.tag == 'player':
                    result['player'] = self._parse_player(child)
                elif child.tag == 'games':
                    result['games'] = self._parse_games(child)
                elif child.tag == 'transactions':
                    result['transactions'] = self._parse_transactions(child)
                elif child.tag == 'standings':
                    result['standings'] = self._parse_standings(child)
                elif child.tag == 'matchups':
                    result['matchups'] = self._parse_matchups(child)
                else:
                    logger.debug(f"Unknown element type: {child.tag}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing fantasy content: {e}")
            return {}
    
    def _parse_users(self, users_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse users collection from API response"""
        try:
            users = []
            
            for user_elem in users_elem.findall('.//user'):
                user = {}
                
                # Parse user basic info
                user_id = user_elem.find('.//guid')
                if user_id is not None:
                    user['guid'] = user_id.text
                
                # Parse games
                games_elem = user_elem.find('.//games')
                if games_elem is not None:
                    user['games'] = self._parse_games(games_elem)
                
                users.append(user)
            
            return users
            
        except Exception as e:
            logger.error(f"Error parsing users: {e}")
            return []
    
    def _parse_games(self, games_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse games collection from API response"""
        try:
            games = []
            
            for game_elem in games_elem.findall('.//game'):
                game = {}
                
                # Parse game basic info
                game_key = game_elem.find('.//game_key')
                if game_key is not None:
                    game['game_key'] = game_key.text
                
                game_id = game_elem.find('.//game_id')
                if game_id is not None:
                    game['game_id'] = game_id.text
                
                name = game_elem.find('.//name')
                if name is not None:
                    game['name'] = name.text
                
                code = game_elem.find('.//code')
                if code is not None:
                    game['code'] = code.text
                
                # Parse teams if present
                teams_elem = game_elem.find('.//teams')
                if teams_elem is not None:
                    game['teams'] = self._parse_teams(teams_elem)
                
                games.append(game)
            
            return games
            
        except Exception as e:
            logger.error(f"Error parsing games: {e}")
            return []
    
    def _parse_teams(self, teams_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse teams collection from API response"""
        try:
            teams = []
            
            for team_elem in teams_elem.findall('.//team'):
                team = {}
                
                # Parse team basic info
                team_key = team_elem.find('.//team_key')
                if team_key is not None:
                    team['team_key'] = team_key.text
                
                team_id = team_elem.find('.//team_id')
                if team_id is not None:
                    team['team_id'] = team_id.text
                
                name = team_elem.find('.//name')
                if name is not None:
                    team['name'] = name.text
                
                # Parse league info
                league_elem = team_elem.find('.//league')
                if league_elem is not None:
                    team['league'] = self._parse_league(league_elem)
                
                # Parse roster if present
                roster_elem = team_elem.find('.//roster')
                if roster_elem is not None:
                    team['roster'] = self._parse_roster(roster_elem)
                
                teams.append(team)
            
            return teams
            
        except Exception as e:
            logger.error(f"Error parsing teams: {e}")
            return []
    
    def _parse_league(self, league_elem: ET.Element) -> Dict[str, Any]:
        """Parse league information from API response"""
        try:
            league = {}
            
            # Parse league basic info
            league_key = league_elem.find('.//league_key')
            if league_key is not None:
                league['league_key'] = league_key.text
            
            league_id = league_elem.find('.//league_id')
            if league_id is not None:
                league['league_id'] = league_id.text
            
            name = league_elem.find('.//name')
            if name is not None:
                league['name'] = name.text
            
            url = league_elem.find('.//url')
            if url is not None:
                league['url'] = url.text
            
            # Parse league settings
            settings_elem = league_elem.find('.//settings')
            if settings_elem is not None:
                league['settings'] = self._parse_settings(settings_elem)
            
            return league
            
        except Exception as e:
            logger.error(f"Error parsing league: {e}")
            return {}
    
    def _parse_roster(self, roster_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse roster information from API response"""
        try:
            players = []
            
            for player_elem in roster_elem.findall('.//player'):
                player = {}
                
                # Parse player basic info
                player_key = player_elem.find('.//player_key')
                if player_key is not None:
                    player['player_key'] = player_key.text
                
                player_id = player_elem.find('.//player_id')
                if player_id is not None:
                    player['player_id'] = player_id.text
                
                name = player_elem.find('.//name/full')
                if name is not None:
                    player['name'] = name.text
                
                # Parse position info
                position_elem = player_elem.find('.//display_position')
                if position_elem is not None:
                    player['position'] = position_elem.text
                
                # Parse team info
                team_elem = player_elem.find('.//editorial_team_abbr')
                if team_elem is not None:
                    player['team'] = team_elem.text
                
                # Parse status
                status_elem = player_elem.find('.//status')
                if status_elem is not None:
                    player['status'] = status_elem.text
                
                # Parse selected position
                selected_pos_elem = player_elem.find('.//selected_position')
                if selected_pos_elem is not None:
                    position = selected_pos_elem.find('.//position')
                    if position is not None:
                        player['selected_position'] = position.text
                    
                    roster_slot = selected_pos_elem.find('.//roster_slot')
                    if roster_slot is not None:
                        player['roster_slot'] = roster_slot.text
                
                # Parse player stats if available
                stats_elem = player_elem.find('.//player_stats')
                if stats_elem is not None:
                    player['stats'] = self._parse_player_stats(stats_elem)
                
                players.append(player)
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing roster: {e}")
            return []
    
    def _parse_player_stats(self, stats_elem: ET.Element) -> Dict[str, Any]:
        """Parse player statistics from API response"""
        try:
            stats = {}
            
            for stat_elem in stats_elem.findall('.//stat'):
                stat_id = stat_elem.find('.//stat_id')
                value = stat_elem.find('.//value')
                
                if stat_id is not None and value is not None:
                    stats[stat_id.text] = value.text
            
            return stats
            
        except Exception as e:
            logger.error(f"Error parsing player stats: {e}")
            return {}
    
    def _parse_settings(self, settings_elem: ET.Element) -> Dict[str, Any]:
        """Parse league settings from API response"""
        try:
            settings = {}
            
            # Parse scoring type
            scoring_type = settings_elem.find('.//scoring_type')
            if scoring_type is not None:
                settings['scoring_type'] = scoring_type.text
            
            # Parse roster positions
            roster_positions = settings_elem.find('.//roster_positions')
            if roster_positions is not None:
                settings['roster_positions'] = self._parse_roster_positions(roster_positions)
            
            return settings
            
        except Exception as e:
            logger.error(f"Error parsing settings: {e}")
            return {}
    
    def _parse_roster_positions(self, positions_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse roster positions from API response"""
        try:
            positions = []
            
            for pos_elem in positions_elem.findall('.//roster_position'):
                position = {}
                
                position_type = pos_elem.find('.//position_type')
                if position_type is not None:
                    position['type'] = position_type.text
                
                count = pos_elem.find('.//count')
                if count is not None:
                    position['count'] = count.text
                
                positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"Error parsing roster positions: {e}")
            return []
    
    def _parse_transactions(self, transactions_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse transactions from API response"""
        try:
            transactions = []
            
            for trans_elem in transactions_elem.findall('.//transaction'):
                transaction = {}
                
                # Parse transaction basic info
                transaction_key = trans_elem.find('.//transaction_key')
                if transaction_key is not None:
                    transaction['transaction_key'] = transaction_key.text
                
                transaction_id = trans_elem.find('.//transaction_id')
                if transaction_id is not None:
                    transaction['transaction_id'] = transaction_id.text
                
                type_elem = trans_elem.find('.//type')
                if type_elem is not None:
                    transaction['type'] = type_elem.text
                
                timestamp = trans_elem.find('.//timestamp')
                if timestamp is not None:
                    transaction['timestamp'] = timestamp.text
                
                # Parse players involved
                players_elem = trans_elem.find('.//players')
                if players_elem is not None:
                    transaction['players'] = self._parse_transaction_players(players_elem)
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error parsing transactions: {e}")
            return []
    
    def _parse_transaction_players(self, players_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse players involved in transactions"""
        try:
            players = []
            
            for player_elem in players_elem.findall('.//player'):
                player = {}
                
                player_key = player_elem.find('.//player_key')
                if player_key is not None:
                    player['player_key'] = player_key.text
                
                # Parse transaction data
                transaction_data = player_elem.find('.//transaction_data')
                if transaction_data is not None:
                    player['transaction_data'] = self._parse_transaction_data(transaction_data)
                
                players.append(player)
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing transaction players: {e}")
            return []
    
    def _parse_transaction_data(self, data_elem: ET.Element) -> Dict[str, Any]:
        """Parse transaction data for players"""
        try:
            data = {}
            
            type_elem = data_elem.find('.//type')
            if type_elem is not None:
                data['type'] = type_elem.text
            
            source_team = data_elem.find('.//source_team_key')
            if source_team is not None:
                data['source_team_key'] = source_team.text
            
            destination_team = data_elem.find('.//destination_team_key')
            if destination_team is not None:
                data['destination_team_key'] = destination_team.text
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing transaction data: {e}")
            return {}
    
    def _parse_standings(self, standings_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse league standings from API response"""
        try:
            teams = []
            
            for team_elem in standings_elem.findall('.//team'):
                team = {}
                
                # Parse team basic info
                team_key = team_elem.find('.//team_key')
                if team_key is not None:
                    team['team_key'] = team_key.text
                
                name = team_elem.find('.//name')
                if name is not None:
                    team['name'] = name.text
                
                # Parse standings info
                rank = team_elem.find('.//rank')
                if rank is not None:
                    team['rank'] = rank.text
                
                wins = team_elem.find('.//wins')
                if wins is not None:
                    team['wins'] = wins.text
                
                losses = team_elem.find('.//losses')
                if losses is not None:
                    team['losses'] = losses.text
                
                ties = team_elem.find('.//ties')
                if ties is not None:
                    team['ties'] = ties.text
                
                teams.append(team)
            
            return teams
            
        except Exception as e:
            logger.error(f"Error parsing standings: {e}")
            return []
    
    def _parse_matchups(self, matchups_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse team matchups from API response"""
        try:
            matchups = []
            
            for matchup_elem in matchups_elem.findall('.//matchup'):
                matchup = {}
                
                # Parse matchup basic info
                matchup_key = matchup_elem.find('.//matchup_key')
                if matchup_key is not None:
                    matchup['matchup_key'] = matchup_key.text
                
                week = matchup_elem.find('.//week')
                if week is not None:
                    matchup['week'] = week.text
                
                # Parse teams in matchup
                teams_elem = matchup_elem.find('.//0/teams')
                if teams_elem is not None:
                    matchup['teams'] = self._parse_teams(teams_elem)
                
                matchups.append(matchup)
            
            return matchups
            
        except Exception as e:
            logger.error(f"Error parsing matchups: {e}")
            return []
    
    def _parse_player(self, player_elem: ET.Element) -> Dict[str, Any]:
        """Parse individual player information from API response"""
        try:
            player = {}
            
            # Parse player basic info
            player_key = player_elem.find('.//player_key')
            if player_key is not None:
                player['player_key'] = player_key.text
            
            player_id = player_elem.find('.//player_id')
            if player_id is not None:
                player['player_id'] = player_id.text
            
            name = player_elem.find('.//name/full')
            if name is not None:
                player['name'] = name.text
            
            # Parse position info
            position_elem = player_elem.find('.//display_position')
            if position_elem is not None:
                player['position'] = position_elem.text
            
            # Parse team info
            team_elem = player_elem.find('.//editorial_team_abbr')
            if team_elem is not None:
                player['team'] = team_elem.text
            
            # Parse status
            status_elem = player_elem.find('.//status')
            if status_elem is not None:
                player['status'] = status_elem.text
            
            # Parse percent owned
            percent_owned = player_elem.find('.//percent_owned/value')
            if percent_owned is not None:
                player['percent_owned'] = percent_owned.text
            
            # Parse player stats if available
            stats_elem = player_elem.find('.//player_stats')
            if stats_elem is not None:
                player['stats'] = self._parse_player_stats(stats_elem)
            
            return player
            
        except Exception as e:
            logger.error(f"Error parsing player: {e}")
            return {}

def parse_yahoo_response(xml_text: str) -> Dict[str, Any]:
    """Convenience function to parse Yahoo! API XML response"""
    try:
        parser = YahooXMLParser()
        xml_data = ET.fromstring(xml_text)
        return parser.parse_fantasy_content(xml_data)
    except ET.ParseError as e:
        logger.error(f"XML parsing error: {e}")
        return {'error': 'XML parsing failed', 'raw_data': xml_text}
    except Exception as e:
        logger.error(f"Error parsing Yahoo! response: {e}")
        return {'error': str(e), 'raw_data': xml_text}
