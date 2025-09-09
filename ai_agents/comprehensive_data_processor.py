#!/usr/bin/env python3
"""
Comprehensive Data Processor for Fantasy Football Analysis
Processes all data sources and creates complete optimized profiles
"""

import json
import os
import glob
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ComprehensiveDataProcessor:
    """Processes all fantasy football data sources comprehensively"""
    
    def __init__(self, data_dir: str, player_limits: Dict[str, int]):
        self.data_dir = data_dir
        self.player_limits = player_limits
        
    def process_all_data(self) -> Dict[str, Any]:
        """Process all data sources and return comprehensive structured data"""
        
        logger.info("Starting comprehensive data processing...")
        
        # Load all data sources
        league_metadata = self._load_league_metadata()
        my_roster = self._load_my_roster_data()
        opponent_roster = self._load_opponent_roster_data()
        available_players = self._load_available_players_data()
        nfl_matchups = self._load_nfl_matchups_data()
        # transaction_trends = self._load_transaction_trends()  # Excluded for now
        
        # Calculate total token usage
        total_tokens = (
            self._calculate_token_usage(my_roster.get("players_by_position", {})) +
            self._calculate_token_usage(opponent_roster.get("players_by_position", {})) +
            self._calculate_token_usage(available_players.get("players_by_position", {})) +
            self._calculate_nfl_matchups_tokens(nfl_matchups)
        )
        
        return {
            "season_context": league_metadata.get("season_context", {}),
            "league_metadata": league_metadata,
            "my_roster": my_roster,
            "opponent_roster": opponent_roster,
            "available_players": available_players,
            "nfl_matchups": nfl_matchups,
            # "transaction_trends": transaction_trends,  # Excluded for now
            "total_tokens": total_tokens,
            "data_files": self._extract_all_data_files(),
            "processing_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
    
    def _load_league_metadata(self) -> Dict[str, Any]:
        """Load league metadata from Yahoo data"""
        try:
            # Load from Yahoo roster data (has league info)
            yahoo_roster_file = self._find_latest_file("yahoo/my_roster", "*_raw_data.json")
            if yahoo_roster_file:
                with open(yahoo_roster_file, 'r') as f:
                    data = json.load(f)
                
                league_info = data.get("league_info", {})
                team_info = data.get("team_info", {})
                season_context = data.get("season_context", {})
                
                # Get league name from season_context if available
                season_league_info = season_context.get("league_info", {})
                league_name = (league_info.get("league_name") or 
                             season_league_info.get("league_name") or 
                             "Unknown League")
                
                return {
                    "league_name": league_name,
                    "team_name": team_info.get("team_name", "Unknown Team"),
                    "team_key": team_info.get("team_key", "Unknown"),
                    "league_key": league_info.get("league_key", "Unknown"),
                    "season_context": season_context,
                    "current_week": season_context.get("current_week", 1),
                    "nfl_season": season_context.get("nfl_season", "2025")
                }
        except Exception as e:
            logger.error(f"Error loading league metadata: {e}")
            return {}
    
    def _load_my_roster_data(self) -> Dict[str, Any]:
        """Load and process my roster data with all API enrichments"""
        try:
            # Load Yahoo roster
            yahoo_roster = self._load_yahoo_roster()
            # Load Sleeper roster
            sleeper_roster = self._load_sleeper_roster()
            # Load Tank01 roster
            tank01_roster = self._load_tank01_roster()
            
            # Process and enrich roster players, organizing by starting vs bench
            starting_lineup = {}
            bench_players = {}
            
            for yahoo_player in yahoo_roster:
                roster_position = yahoo_player.get("roster_position", "Unknown")
                display_position = yahoo_player.get("display_position", "Unknown")
                
                # Find matching Sleeper and Tank01 data
                sleeper_match = self._find_matching_player(yahoo_player, sleeper_roster)
                tank01_match = self._find_matching_tank01_player(yahoo_player, tank01_roster)
                
                # Create enriched player profile
                enriched_player = self._create_enriched_player_profile(
                    yahoo_player, sleeper_match, tank01_match
                )
                
                # Add roster position info
                enriched_player["roster_position"] = roster_position
                
                # Organize by starting vs bench
                if roster_position == "BN":
                    if display_position not in bench_players:
                        bench_players[display_position] = []
                    bench_players[display_position].append(enriched_player)
                else:
                    if roster_position not in starting_lineup:
                        starting_lineup[roster_position] = []
                    starting_lineup[roster_position].append(enriched_player)
            
            # Combine starting lineup and bench
            players_by_position = {
                "starting_lineup": starting_lineup,
                "bench_players": bench_players
            }
            
            # Get team and league info from Yahoo roster data
            team_info = self._get_team_and_league_info()
            
            # Calculate totals
            starting_count = sum(len(players) for players in starting_lineup.values())
            bench_count = sum(len(players) for players in bench_players.values())
            
            return {
                "players_by_position": players_by_position,
                "total_players": starting_count + bench_count,
                "starting_count": starting_count,
                "bench_count": bench_count,
                "team_name": team_info.get("team_name", "Unknown"),
                "league_name": team_info.get("league_name", "Unknown"),
                "data_sources": ["yahoo", "sleeper", "tank01"]
            }
            
        except Exception as e:
            logger.error(f"Error loading my roster data: {e}")
            return {"players_by_position": {}, "total_players": 0, "data_sources": []}
    
    def _get_team_and_league_info(self) -> Dict[str, str]:
        """Get team name and league name from Yahoo roster data"""
        try:
            roster_file = self._find_latest_file("yahoo/my_roster", "*_raw_data.json")
            if roster_file:
                with open(roster_file, 'r') as f:
                    data = json.load(f)
                
                team_info = data.get("team_info", {})
                league_info = data.get("league_info", {})
                season_context = data.get("season_context", {})
                
                # Get league name from season_context if available
                season_league_info = season_context.get("league_info", {})
                league_name = (league_info.get("league_name") or 
                             season_league_info.get("league_name") or 
                             "Unknown")
                
                return {
                    "team_name": team_info.get("team_name", "Unknown"),
                    "league_name": league_name
                }
        except Exception as e:
            logger.error(f"Error getting team and league info: {e}")
        
        return {"team_name": "Unknown", "league_name": "Unknown"}
    
    def _load_opponent_roster_data(self) -> Dict[str, Any]:
        """Load and process opponent roster data with all API enrichments"""
        try:
            # Load Yahoo opponent rosters
            yahoo_opponents = self._load_yahoo_opponents()
            # Load Sleeper opponent rosters
            sleeper_opponents = self._load_sleeper_opponents()
            # Load Tank01 opponent rosters
            tank01_opponents = self._load_tank01_opponents()
            
            # Find current week opponent
            current_week_opponent = self._find_current_week_opponent(yahoo_opponents)
            
            if not current_week_opponent:
                return {"players_by_position": {}, "total_players": 0, "opponent_name": "Unknown"}
            
            # Find the opponent's roster data from the loaded opponent rosters
            opponent_team_key = current_week_opponent.get("team_key")
            opponent_roster_data = None
            
            for roster in yahoo_opponents:
                if roster.get("team_key") == opponent_team_key:
                    opponent_roster_data = roster
                    break
            
            if not opponent_roster_data:
                logger.warning(f"No roster data found for opponent {current_week_opponent.get('name')}")
                return {"players_by_position": {}, "total_players": 0, "opponent_name": current_week_opponent.get("name", "Unknown")}
            
            # Process opponent roster players, organizing by starting vs bench
            starting_lineup = {}
            bench_players = {}
            opponent_players = opponent_roster_data.get("players", [])
            
            for yahoo_player in opponent_players:
                roster_position = yahoo_player.get("selected_position", "Unknown")
                display_position = yahoo_player.get("display_position", "Unknown")
                
                # Find matching Sleeper and Tank01 data
                sleeper_match = self._find_matching_player(yahoo_player, sleeper_opponents)
                tank01_match = self._find_matching_tank01_player(yahoo_player, tank01_opponents)
                
                # Create enriched player profile
                enriched_player = self._create_enriched_player_profile(
                    yahoo_player, sleeper_match, tank01_match
                )
                
                # Add roster position info
                enriched_player["roster_position"] = roster_position
                
                # Organize by starting vs bench
                if roster_position == "BN":
                    if display_position not in bench_players:
                        bench_players[display_position] = []
                    bench_players[display_position].append(enriched_player)
                else:
                    if roster_position not in starting_lineup:
                        starting_lineup[roster_position] = []
                    starting_lineup[roster_position].append(enriched_player)
            
            # Combine starting lineup and bench
            players_by_position = {
                "starting_lineup": starting_lineup,
                "bench_players": bench_players
            }
            
            # Calculate totals
            starting_count = sum(len(players) for players in starting_lineup.values())
            bench_count = sum(len(players) for players in bench_players.values())
            
            return {
                "players_by_position": players_by_position,
                "total_players": starting_count + bench_count,
                "starting_count": starting_count,
                "bench_count": bench_count,
                "opponent_name": current_week_opponent.get("name", "Unknown"),
                "opponent_team_key": current_week_opponent.get("team_key", "Unknown"),
                "data_sources": ["yahoo", "sleeper", "tank01"]
            }
            
        except Exception as e:
            logger.error(f"Error loading opponent roster data: {e}")
            return {"players_by_position": {}, "total_players": 0, "opponent_name": "Unknown"}
    
    def _load_available_players_data(self) -> Dict[str, Any]:
        """Load and process available players data with all API enrichments"""
        try:
            # Load Yahoo available players
            yahoo_available = self._load_yahoo_available()
            # Load Sleeper available players
            sleeper_available = self._load_sleeper_available()
            # Load Tank01 available players
            tank01_available = self._load_tank01_available()
            
            # Process and enrich available players
            players_by_position = {}
            
            for yahoo_player in yahoo_available:
                position = yahoo_player.get("display_position", "Unknown")
                
                # Handle multi-position players (FLEX) - same logic as data collection scripts
                if position in ['W/R/T', 'W/R', 'Q/W/R/T', 'WR,TE', 'RB,TE', 'WR,RB', 'QB,WR']:
                    position = 'FLEX'
                
                if position not in players_by_position:
                    players_by_position[position] = []
                
                # Find matching Sleeper and Tank01 data
                sleeper_match = self._find_matching_player(yahoo_player, sleeper_available)
                tank01_match = self._find_matching_tank01_player(yahoo_player, tank01_available)
                
                # Create enriched player profile
                enriched_player = self._create_enriched_player_profile(
                    yahoo_player, sleeper_match, tank01_match
                )
                players_by_position[position].append(enriched_player)
            
            # Apply position limits (same logic as data collection scripts)
            limited_players = {}
            position_counts = {pos: 0 for pos in self.player_limits.keys()}
            
            for position, players in players_by_position.items():
                limited_players[position] = []
                limit = self.player_limits.get(position, 20)
                
                for player in players:
                    if position_counts[position] < limit:
                        limited_players[position].append(player)
                        position_counts[position] += 1
            
            return {
                "players_by_position": limited_players,
                "total_players": sum(len(players) for players in limited_players.values()),
                "data_sources": ["yahoo", "sleeper", "tank01"]
            }
            
        except Exception as e:
            logger.error(f"Error loading available players data: {e}")
            return {"players_by_position": {}, "total_players": 0, "data_sources": []}
    
    def _load_nfl_matchups_data(self) -> Dict[str, Any]:
        """Load NFL matchups data from Tank01"""
        try:
            matchups_file = self._find_latest_file("tank01/nfl_matchups", "*_raw_data.json")
            if matchups_file:
                with open(matchups_file, 'r') as f:
                    data = json.load(f)
                
                # Extract relevant matchups data
                games = data.get("games", [])
                season_context = data.get("season_context", {})
                
                return {
                    "games": games,
                    "total_games": len(games),
                    "season": season_context.get("nfl_season"),
                    "current_week": season_context.get("current_week"),
                    "season_phase": season_context.get("season_phase"),
                    "data_source": "tank01"
                }
        except Exception as e:
            logger.error(f"Error loading NFL matchups: {e}")
            return {"games": [], "total_games": 0, "data_source": "tank01"}
    
    def _load_transaction_trends(self) -> Dict[str, Any]:
        """Load transaction trends data"""
        try:
            trends_file = self._find_latest_file("yahoo/transaction_trends", "*_raw_data.json")
            if trends_file:
                with open(trends_file, 'r') as f:
                    data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Error loading transaction trends: {e}")
            return {}
    
    def _create_enriched_player_profile(self, yahoo_player: Dict[str, Any], 
                                      sleeper_data: Optional[Dict[str, Any]], 
                                      tank01_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create enriched player profile with all API data"""
        
        # Extract Yahoo data
        yahoo_data = {
            "player_key": yahoo_player.get("player_key"),
            "player_id": yahoo_player.get("player_id"),
            "name": yahoo_player.get("name", {}),
            "display_position": yahoo_player.get("display_position"),
            "team": yahoo_player.get("editorial_team_abbr"),
            "bye_week": yahoo_player.get("bye_week"),
            "injury_status": yahoo_player.get("status", "Healthy"),
            "percent_owned": yahoo_player.get("percent_owned_value", "0")
        }
        
        # Extract Sleeper data
        sleeper_enriched = {}
        if sleeper_data:
            sleeper_enriched = {
                "player_id": sleeper_data.get("player_id"),
                "name": sleeper_data.get("full_name"),
                "position": sleeper_data.get("position"),
                "team": sleeper_data.get("team"),
                "team_abbr": sleeper_data.get("team_abbr"),
                "depth_chart_position": sleeper_data.get("depth_chart_position"),
                "injury_status": sleeper_data.get("injury_status"),
                "status": sleeper_data.get("status"),
                "active": sleeper_data.get("active"),
                "years_exp": sleeper_data.get("years_exp"),
                "age": sleeper_data.get("age"),
                "height": sleeper_data.get("height"),
                "weight": sleeper_data.get("weight"),
                "college": sleeper_data.get("college"),
                "birth_date": sleeper_data.get("birth_date"),
                "fantasy_positions": sleeper_data.get("fantasy_positions", []),
                "player_ids": {
                    "sleeper_id": sleeper_data.get("player_id"),
                    "yahoo_id": sleeper_data.get("yahoo_id"),
                    "espn_id": sleeper_data.get("espn_id"),
                    "sportradar_id": sleeper_data.get("sportradar_id"),
                    "gsis_id": sleeper_data.get("gsis_id"),
                    "rotowire_id": sleeper_data.get("rotowire_id"),
                    "fantasy_data_id": sleeper_data.get("fantasy_data_id"),
                    "pandascore_id": sleeper_data.get("pandascore_id"),
                    "oddsjam_id": sleeper_data.get("oddsjam_id")
                }
            }
        
        # Extract Tank01 data
        tank01_enriched = {}
        if tank01_data:
            # Handle different Tank01 data structures
            if "yahoo_data" in tank01_data and "tank01_data" in tank01_data:
                # Tank01 available players structure: matched_players array with yahoo_data and tank01_data keys
                tank01_data_section = tank01_data.get("tank01_data", {})
                # For available players, projection data is at root level
                # For opponent rosters, projection data is in tank01_data.fantasy_projections
                if "projection" in tank01_data:
                    # Available players structure
                    projection_data = tank01_data.get("projection", {})
                else:
                    # Opponent roster structure - fantasy_projections is in tank01_data
                    fantasy_projections = tank01_data_section.get("fantasy_projections", {})
                    projection_data = {
                        "fantasyPoints": fantasy_projections.get("fantasyPoints"),
                        "fantasyPointsDefault": fantasy_projections.get("fantasyPointsDefault"),
                        "week_1": {
                            "fantasy_points": fantasy_projections.get("fantasyPoints"),
                            "fantasy_points_default": fantasy_projections.get("fantasyPointsDefault")
                        }
                    }
                news_data = tank01_data.get("news", []) or tank01_data_section.get("recent_news", [])
                game_stats_data = tank01_data.get("game_stats", {}) or tank01_data_section.get("game_stats", {})
                depth_chart_data = tank01_data.get("depth_chart", {}) or tank01_data_section.get("depth_chart", {})
            elif "yahoo_player" in tank01_data and "tank01_data" in tank01_data:
                # Tank01 roster structure: matched_players array with yahoo_player and tank01_data keys
                tank01_data_section = tank01_data.get("tank01_data", {})
                # For roster data, fantasy_projections is directly in tank01_data
                fantasy_projections = tank01_data_section.get("fantasy_projections", {})
                projection_data = {
                    "fantasyPoints": fantasy_projections.get("fantasyPoints"),
                    "fantasyPointsDefault": fantasy_projections.get("fantasyPointsDefault"),
                    "week_1": {
                        "fantasy_points": fantasy_projections.get("fantasyPoints"),
                        "fantasy_points_default": fantasy_projections.get("fantasyPointsDefault")
                    }
                }
                news_data = tank01_data_section.get("recent_news", [])
                game_stats_data = tank01_data_section.get("game_stats", {})
                depth_chart_data = tank01_data_section.get("depth_chart", {})
            else:
                # Fallback: assume it's a direct tank01_data structure
                tank01_data_section = tank01_data
                fantasy_projections = tank01_data_section.get("fantasy_projections", {})
                projection_data = {
                    "fantasyPoints": fantasy_projections.get("fantasyPoints"),
                    "fantasyPointsDefault": fantasy_projections.get("fantasyPointsDefault"),
                    "week_1": {
                        "fantasy_points": fantasy_projections.get("fantasyPoints"),
                        "fantasy_points_default": fantasy_projections.get("fantasyPointsDefault")
                    }
                }
                news_data = tank01_data_section.get("recent_news", [])
                game_stats_data = tank01_data_section.get("game_stats", {})
                depth_chart_data = tank01_data_section.get("depth_chart", {})
            
            tank01_enriched = {
                "player_id": tank01_data_section.get("playerID"),
                "name": {
                    "full": tank01_data_section.get("longName"),
                    "first": tank01_data_section.get("longName", "").split()[0] if tank01_data_section.get("longName") else "",
                    "last": tank01_data_section.get("longName", "").split()[-1] if tank01_data_section.get("longName") else ""
                },
                "display_position": tank01_data_section.get("pos"),
                "team": tank01_data_section.get("team"),
                "team_id": tank01_data_section.get("teamID"),
                "jersey_number": tank01_data_section.get("jerseyNum"),
                "age": tank01_data_section.get("age"),
                "height": tank01_data_section.get("height"),
                "weight": tank01_data_section.get("weight"),
                "college": tank01_data_section.get("school"),
                "years_exp": tank01_data_section.get("exp"),
                "last_game_played": tank01_data_section.get("lastGamePlayed"),
                "injury": tank01_data_section.get("injury", {}),
                "projection": projection_data,
                "news": news_data,
                "game_stats": game_stats_data,
                "depth_chart": depth_chart_data,
                "team_context": tank01_data_section.get("team_context", {}),
                "player_ids": {
                    "espn_id": tank01_data_section.get("espnID"),
                    "sleeper_id": tank01_data_section.get("sleeperBotID"),
                    "fantasypros_id": tank01_data_section.get("fantasyProsPlayerID"),
                    "yahoo_id": tank01_data_section.get("yahooPlayerID"),
                    "rotowire_id": tank01_data_section.get("rotoWirePlayerID"),
                    "cbs_id": tank01_data_section.get("cbsPlayerID"),
                    "fref_id": tank01_data_section.get("fRefID")
                }
            }
        
        return {
            "name": yahoo_data.get("name", {}).get("full", "Unknown"),
            "yahoo_data": yahoo_data,
            "sleeper_data": sleeper_enriched if sleeper_enriched else None,
            "tank01_data": tank01_enriched if tank01_enriched else None
        }
    
    def _find_matching_player(self, yahoo_player: Dict[str, Any], other_players: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching player in other API data (Sleeper matched_players)"""
        yahoo_player_key = yahoo_player.get("player_key")
        
        for matched_player in other_players:
            # Sleeper data structure: matched_players array with yahoo_data and sleeper_player keys
            if "yahoo_data" in matched_player and "sleeper_player" in matched_player:
                yahoo_data = matched_player["yahoo_data"]
                if yahoo_data.get("player_key") == yahoo_player_key:
                    return matched_player["sleeper_player"]
            # Also check for yahoo_player key (for backward compatibility)
            elif "yahoo_player" in matched_player and "sleeper_player" in matched_player:
                yahoo_data = matched_player["yahoo_player"]
                if yahoo_data.get("player_key") == yahoo_player_key:
                    return matched_player["sleeper_player"]
        
        return None
    
    def _find_matching_tank01_player(self, yahoo_player: Dict[str, Any], tank01_players: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching Tank01 player"""
        yahoo_player_key = yahoo_player.get("player_key")
        
        for matched_player in tank01_players:
            # Tank01 roster data structure: matched_players array with yahoo_player and tank01_data keys
            if "yahoo_player" in matched_player and "tank01_data" in matched_player:
                yahoo_data = matched_player["yahoo_player"]
                if yahoo_data.get("player_key") == yahoo_player_key:
                    return matched_player
            # Tank01 available players data structure: yahoo_data and tank01_data keys
            elif "yahoo_data" in matched_player and "tank01_data" in matched_player:
                yahoo_data = matched_player["yahoo_data"]
                if yahoo_data.get("player_key") == yahoo_player_key:
                    return matched_player
        
        return None
    
    def _find_current_week_opponent(self, yahoo_opponents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find current week opponent from Yahoo team matchups data"""
        try:
            # Load team matchups data to find current week opponent
            matchups_file = self._find_latest_file("yahoo/team_matchups", "*_raw_data.json")
            if not matchups_file:
                logger.warning("No team matchups file found")
                return None
                
            with open(matchups_file, 'r') as f:
                matchups_data = json.load(f)
            
            # Get current week from season context
            season_context = matchups_data.get("season_context", {})
            current_week = season_context.get("current_week", 1)
            
            # Get my team key from league info
            league_info = matchups_data.get("league_info", {})
            my_team_key = league_info.get("team_key")
            
            if not my_team_key:
                logger.warning("No team key found in matchups data")
                return None
            
            # Find my team's matchup for current week
            matchups = matchups_data.get("matchups", {})
            week_key = f"week_{current_week}"
            
            if week_key not in matchups:
                logger.warning(f"No matchups found for week {current_week}")
                return None
                
            week_matchups = matchups[week_key].get("matchups", [])
            
            for matchup in week_matchups:
                teams = matchup.get("teams", [])
                if len(teams) == 2:
                    team1_key = teams[0].get("team_key")
                    team2_key = teams[1].get("team_key")
                    
                    if team1_key == my_team_key:
                        # I'm team 1, opponent is team 2
                        opponent_team = teams[1]
                        logger.info(f"Found current week opponent: {opponent_team.get('name')} (team_key: {opponent_team.get('team_key')})")
                        return opponent_team
                    elif team2_key == my_team_key:
                        # I'm team 2, opponent is team 1
                        opponent_team = teams[0]
                        logger.info(f"Found current week opponent: {opponent_team.get('name')} (team_key: {opponent_team.get('team_key')})")
                        return opponent_team
            
            logger.warning(f"No matchup found for my team {my_team_key} in week {current_week}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding current week opponent: {e}")
            return None
    
    def _load_yahoo_roster(self) -> List[Dict[str, Any]]:
        """Load Yahoo roster data with position information"""
        try:
            roster_file = self._find_latest_file("yahoo/my_roster", "*_raw_data.json")
            if roster_file:
                with open(roster_file, 'r') as f:
                    data = json.load(f)
                
                # Get roster players from the processed data
                roster_players = data.get("roster_players", [])
                
                # Also get position info from raw roster data
                roster_raw = data.get("roster_raw", {})
                fantasy_content = roster_raw.get("fantasy_content", {})
                team = fantasy_content.get("team", [])
                
                position_map = {}
                if len(team) > 1 and 'roster' in team[1]:
                    roster_data = team[1]['roster']
                    if '0' in roster_data and 'players' in roster_data['0']:
                        players_data = roster_data['0']['players']
                        
                        # Extract position info for each player
                        for i in range(len(players_data) - 1):  # -1 to exclude 'count'
                            player_key = str(i)
                            if player_key in players_data:
                                player = players_data[player_key]
                                if 'player' in player and isinstance(player['player'], list) and len(player['player']) > 1:
                                    selected_pos = player['player'][1].get('selected_position', [])
                                    if isinstance(selected_pos, list) and len(selected_pos) > 1:
                                        position = selected_pos[1].get('position', 'Unknown')
                                        # Get player key to match with roster_players
                                        player_key_val = player['player'][0][0].get('player_key', '')
                                        position_map[player_key_val] = position
                
                # Add position info to roster players
                for player in roster_players:
                    player_key = player.get("player_key", "")
                    if player_key in position_map:
                        player["roster_position"] = position_map[player_key]
                    else:
                        player["roster_position"] = "Unknown"
                
                logger.info(f"Loaded {len(roster_players)} Yahoo roster players with position info")
                return roster_players
        except Exception as e:
            logger.error(f"Error loading Yahoo roster: {e}")
        return []
    
    def _load_sleeper_roster(self) -> List[Dict[str, Any]]:
        """Load Sleeper roster data"""
        try:
            roster_file = self._find_latest_file("sleeper/my_roster", "*_raw_data.json")
            if roster_file:
                with open(roster_file, 'r') as f:
                    data = json.load(f)
                # Sleeper data structure: matched_players array
                matched_players = data.get("matched_players", [])
                logger.info(f"Loaded {len(matched_players)} Sleeper roster players")
                return matched_players
        except Exception as e:
            logger.error(f"Error loading Sleeper roster: {e}")
        return []
    
    def _load_tank01_roster(self) -> List[Dict[str, Any]]:
        """Load Tank01 roster data"""
        try:
            roster_file = self._find_latest_file("tank01/my_roster", "*_raw_data.json")
            if roster_file:
                with open(roster_file, 'r') as f:
                    data = json.load(f)
                matched_players = data.get("matched_players", [])
                logger.info(f"Loaded {len(matched_players)} Tank01 roster players")
                return matched_players
        except Exception as e:
            logger.error(f"Error loading Tank01 roster: {e}")
        return []
    
    def _load_yahoo_opponents(self) -> List[Dict[str, Any]]:
        """Load Yahoo opponents data"""
        try:
            opponents_file = self._find_latest_file("yahoo/opponent_rosters", "*_raw_data.json")
            if opponents_file:
                with open(opponents_file, 'r') as f:
                    data = json.load(f)
                
                # Convert rosters dict to list of opponent data
                rosters = data.get("rosters", {})
                teams = data.get("teams", [])
                
                opponent_rosters = []
                for team_key, roster_data in rosters.items():
                    # Find team info
                    team_info = next((team for team in teams if team.get("team_key") == team_key), {})
                    
                    opponent_roster = {
                        "team_key": team_key,
                        "team_name": team_info.get("name", "Unknown Team"),
                        "players": roster_data.get("players", [])
                    }
                    opponent_rosters.append(opponent_roster)
                
                logger.info(f"Loaded {len(opponent_rosters)} opponent rosters")
                return opponent_rosters
        except Exception as e:
            logger.error(f"Error loading Yahoo opponents: {e}")
        return []
    
    def _load_sleeper_opponents(self) -> List[Dict[str, Any]]:
        """Load Sleeper opponents data"""
        try:
            opponent_file = self._find_latest_file("sleeper/opponent_roster", "*_raw_data.json")
            if opponent_file:
                with open(opponent_file, 'r') as f:
                    data = json.load(f)
                # Sleeper data structure: matched_players array
                matched_players = data.get("matched_players", [])
                logger.info(f"Loaded {len(matched_players)} Sleeper opponent players")
                return matched_players
        except Exception as e:
            logger.error(f"Error loading Sleeper opponents: {e}")
        return []
    
    def _load_tank01_opponents(self) -> List[Dict[str, Any]]:
        """Load Tank01 opponents data"""
        try:
            opponent_file = self._find_latest_file("tank01/opponent_roster", "*_raw_data.json")
            if opponent_file:
                with open(opponent_file, 'r') as f:
                    data = json.load(f)
                matched_players = data.get("matched_players", [])
                logger.info(f"Loaded {len(matched_players)} Tank01 opponent players")
                return matched_players
        except Exception as e:
            logger.error(f"Error loading Tank01 opponents: {e}")
        return []
    
    def _load_yahoo_available(self) -> List[Dict[str, Any]]:
        """Load Yahoo available players data"""
        try:
            available_file = self._find_latest_file("yahoo/available_players", "*_raw_data.json")
            if available_file:
                with open(available_file, 'r') as f:
                    data = json.load(f)
                available_players = data.get("available_players", [])
                logger.info(f"Loaded {len(available_players)} Yahoo available players")
                return available_players
        except Exception as e:
            logger.error(f"Error loading Yahoo available players: {e}")
        return []
    
    def _load_sleeper_available(self) -> List[Dict[str, Any]]:
        """Load Sleeper available players data"""
        try:
            available_file = self._find_latest_file("sleeper/available_players", "*_raw_data.json")
            if available_file:
                with open(available_file, 'r') as f:
                    data = json.load(f)
                # Sleeper data structure: matched_players array
                matched_players = data.get("matched_players", [])
                logger.info(f"Loaded {len(matched_players)} Sleeper available players")
                return matched_players
        except Exception as e:
            logger.error(f"Error loading Sleeper available players: {e}")
        return []
    
    def _load_tank01_available(self) -> List[Dict[str, Any]]:
        """Load Tank01 available players data"""
        try:
            available_file = self._find_latest_file("tank01/available_players", "*_raw_data.json")
            if available_file:
                with open(available_file, 'r') as f:
                    data = json.load(f)
                # Tank01 data structure: processed_data.available_players array
                if "processed_data" in data and "available_players" in data["processed_data"]:
                    available_players = data["processed_data"]["available_players"]
                    logger.info(f"Loaded {len(available_players)} Tank01 available players")
                    return available_players
                else:
                    logger.warning("No processed_data.available_players found in Tank01 data")
                    return []
        except Exception as e:
            logger.error(f"Error loading Tank01 available players: {e}")
        return []
    
    def _find_latest_file(self, subdirectory: str, pattern: str) -> Optional[str]:
        """Find the latest file matching pattern in subdirectory with YYYY/MM/DD structure"""
        try:
            directory = os.path.join(self.data_dir, subdirectory)
            # Use recursive search to find files in YYYY/MM/DD subdirectories
            files = glob.glob(f"{directory}/**/{pattern}", recursive=True)
            if files:
                return max(files, key=os.path.getctime)
        except Exception as e:
            logger.error(f"Error finding latest file in {subdirectory}: {e}")
        return None
    
    def _calculate_token_usage(self, players_by_position: Dict[str, List[Dict[str, Any]]]) -> int:
        """Calculate actual token usage for players using tiktoken"""
        try:
            import tiktoken
            encoding = tiktoken.get_encoding('cl100k_base')
            
            total_tokens = 0
            for position, players in players_by_position.items():
                for player in players:
                    # Convert player data to JSON string and calculate actual tokens
                    player_json = json.dumps(player, indent=2)
                    player_tokens = len(encoding.encode(player_json))
                    total_tokens += player_tokens
            return total_tokens
        except ImportError:
            # Fallback to rough estimate if tiktoken not available
            total_tokens = 0
            for position, players in players_by_position.items():
                for player in players:
                    # Rough estimate: 2000 tokens per player (more accurate)
                    total_tokens += 2000
            return total_tokens
    
    def _calculate_nfl_matchups_tokens(self, nfl_matchups: Dict[str, Any]) -> int:
        """Calculate token usage for NFL matchups data"""
        try:
            import tiktoken
            encoding = tiktoken.get_encoding('cl100k_base')
            
            # Convert NFL matchups data to JSON string and calculate tokens
            matchups_json = json.dumps(nfl_matchups, indent=2)
            return len(encoding.encode(matchups_json))
        except ImportError:
            # Fallback to rough estimate if tiktoken not available
            games_count = nfl_matchups.get("total_games", 0)
            return games_count * 100  # Rough estimate: 100 tokens per game
    
    def _extract_all_data_files(self) -> Dict[str, str]:
        """Extract all data file paths"""
        return {
            "yahoo_roster": self._find_latest_file("yahoo/my_roster", "*_raw_data.json"),
            "sleeper_roster": self._find_latest_file("sleeper/my_roster", "*_raw_data.json"),
            "tank01_roster": self._find_latest_file("tank01/my_roster", "*_raw_data.json"),
            "yahoo_opponents": self._find_latest_file("yahoo/opponent_rosters", "*_raw_data.json"),
            "yahoo_available": self._find_latest_file("yahoo/available_players", "*_raw_data.json"),
            "sleeper_available": self._find_latest_file("sleeper/available_players", "*_raw_data.json"),
            "tank01_available": self._find_latest_file("tank01/available_players", "*_raw_data.json"),
            "tank01_nfl_matchups": self._find_latest_file("tank01/nfl_matchups", "*_raw_data.json"),
            "yahoo_transactions": self._find_latest_file("yahoo/transaction_trends", "*_raw_data.json")
        }
