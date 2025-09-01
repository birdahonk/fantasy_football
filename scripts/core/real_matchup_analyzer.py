#!/usr/bin/env python3
"""
Real Matchup Analysis Report Generator

This script creates a comprehensive matchup analysis comparing user's roster
vs the actual Week 1 opponent with side-by-side presentation and start/sit recommendations.

Features:
- Gets actual Week 1 opponent from Yahoo API
- Side-by-side roster comparison with real opponent roster
- Start/sit recommendations with data justification
- Multi-API integration (Yahoo + Sleeper + Tank01)
- Proper column formatting

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

class RealMatchupAnalyzer:
    """
    Real matchup analyzer that gets actual Week 1 opponent and their roster.
    """
    
    def __init__(self):
        """Initialize the real matchup analyzer."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏈 Initializing Real Matchup Analyzer")
        
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
            'opponent_team_info': None
        }
    
    def get_week_1_matchup(self) -> Dict[str, Any]:
        """Get Week 1 matchup information including opponent."""
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
            
            # Parse matchup response to find Week 1 opponent
            matchup_data = matchup_response.get('parsed', {})
            week1_opponent = self._find_week1_opponent(matchup_data, our_team_key)
            
            if not week1_opponent:
                self.logger.error("Could not find Week 1 opponent")
                return {}
            
            self.raw_api_data['matchup_data'] = matchup_data
            
            matchup_info = {
                'week': 1,
                'my_team_key': our_team_key,
                'opponent_team_key': week1_opponent.get('team_key'),
                'opponent_team_name': week1_opponent.get('name', 'Unknown Opponent'),
                'opponent_manager': week1_opponent.get('manager', 'Unknown Manager')
            }
            
            self.logger.info(f"✅ Week 1 Matchup: My Team vs {matchup_info['opponent_team_name']}")
            
            return matchup_info
            
        except Exception as e:
            self.logger.error(f"Error getting Week 1 matchup: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _find_week1_opponent(self, matchup_data: Dict[str, Any], our_team_key: str) -> Optional[Dict[str, Any]]:
        """Find Week 1 opponent from matchup data."""
        try:
            fantasy_content = matchup_data.get('fantasy_content', {})
            team_data = fantasy_content.get('team', [])
            
            if isinstance(team_data, list):
                for item in team_data:
                    if isinstance(item, dict) and 'matchups' in item:
                        matchups = item.get('matchups', {})
                        
                        # Look for Week 1 matchup
                        for matchup_key, matchup_info in matchups.items():
                            if matchup_key.isdigit():
                                matchup = matchup_info.get('matchup', {})
                                
                                # Check if this is Week 1
                                week = matchup.get('week')
                                if week == '1' or week == 1:
                                    # Find the opponent team in this matchup
                                    teams = matchup.get('teams', {})
                                    for team_key, team_info in teams.items():
                                        if team_key.isdigit():
                                            team = team_info.get('team', {})
                                            team_key_val = team.get('team_key')
                                            
                                            # If this isn't our team, it's the opponent
                                            if team_key_val and team_key_val != our_team_key:
                                                return {
                                                    'team_key': team_key_val,
                                                    'name': team.get('name', 'Unknown Team'),
                                                    'manager': team.get('managers', {}).get('manager', {}).get('nickname', 'Unknown Manager')
                                                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding Week 1 opponent: {e}")
            return None
    
    def get_enhanced_roster(self, team_key: str, is_my_team: bool = False) -> List[Dict[str, Any]]:
        """Get enhanced roster with multi-API data."""
        try:
            team_type = "my" if is_my_team else "opponent"
            self.logger.info(f"📊 Getting enhanced {team_type} roster")
            
            if not self.api_status['apis']['yahoo']:
                return []
            
            yahoo_client = self.api_manager.yahoo_client
            
            # Get roster
            roster_response = yahoo_client.oauth_client.make_request(f"team/{team_key}/roster")
            if not roster_response or roster_response.get('status') != 'success':
                self.logger.error(f"Failed to get {team_type} roster")
                return []
            
            # Parse roster response
            roster_data = roster_response.get('parsed', {})
            roster = self._parse_roster_response(roster_data)
            
            if not roster:
                self.logger.error(f"No {team_type} roster data available")
                return []
            
            # Store raw data
            if is_my_team:
                self.raw_api_data['my_roster'] = roster
            else:
                self.raw_api_data['opponent_roster'] = roster
            
            # Enhance each player with multi-API data (simplified for opponent)
            enhanced_roster = []
            
            for i, player in enumerate(roster):
                self.logger.info(f"   Processing {team_type} player {i+1}/{len(roster)}: {player.get('name', 'Unknown')}")
                
                if is_my_team:
                    # Full enhancement for my team
                    enhanced_player = self._enhance_player_with_all_apis(player)
                else:
                    # Basic enhancement for opponent (just Tank01 projections)
                    enhanced_player = self._enhance_opponent_player(player)
                
                enhanced_roster.append(enhanced_player)
            
            self.logger.info(f"✅ Enhanced {team_type} roster: {len(enhanced_roster)} players")
            
            return enhanced_roster
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced roster for {team_key}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_roster_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse roster response from Yahoo API."""
        try:
            players = []
            
            # Navigate through the nested structure - Yahoo uses fantasy_content
            fantasy_content = response.get('fantasy_content', {})
            team_data = fantasy_content.get('team', [])
            
            # Navigate the complex nested structure
            roster_data = None
            if isinstance(team_data, list):
                for item in team_data:
                    if isinstance(item, dict) and 'roster' in item:
                        roster_data = item['roster']
                        break
            
            if not roster_data:
                self.logger.warning("No roster data found in response")
                return players
            
            # Extract players from roster
            roster_players = roster_data.get('0', {}).get('players', {})
            
            for player_key in roster_players:
                if player_key.isdigit():  # Only process numeric keys
                    player_info = roster_players[player_key].get('player', [])
                    
                    if isinstance(player_info, list) and len(player_info) > 0:
                        player_data = player_info[0]
                        
                        # Extract basic player information
                        player = {
                            'name': player_data.get('name', {}).get('full', 'Unknown'),
                            'player_id': player_data.get('player_id', ''),
                            'position': player_data.get('display_position', 'Unknown'),
                            'team': player_data.get('editorial_team_abbr', ''),
                            'selected_position': player_info[1].get('selected_position', {}).get('position', 'BN') if len(player_info) > 1 else 'BN',
                            'status': player_data.get('status', 'A')
                        }
                        
                        players.append(player)
            
            self.logger.info(f"Parsed {len(players)} players from roster")
            return players
            
        except Exception as e:
            self.logger.error(f"Error parsing roster response: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _enhance_player_with_all_apis(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance my team player with comprehensive multi-API data."""
        enhanced_player = player.copy()
        player_name = player.get('name', 'Unknown')
        
        # Initialize comprehensive data structure
        enhanced_player.update({
            'tank01_data': {
                'projected_points': 'N/A',
                'recent_news': []
            },
            'matchup_analysis': {
                'start_recommendation': 'Unknown',
                'confidence_level': 'Medium',
                'key_factors': []
            }
        })
        
        # Enhance with Tank01 data
        self._enhance_with_tank01_data(enhanced_player)
        
        # Generate matchup analysis
        self._generate_start_sit_analysis(enhanced_player)
        
        return enhanced_player
    
    def _enhance_opponent_player(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance opponent player with basic Tank01 projections."""
        enhanced_player = player.copy()
        
        # Initialize basic data structure
        enhanced_player.update({
            'tank01_data': {
                'projected_points': 'N/A'
            }
        })
        
        # Enhance with Tank01 data
        self._enhance_with_tank01_data(enhanced_player)
        
        return enhanced_player
    
    def _enhance_with_tank01_data(self, player: Dict[str, Any]):
        """Enhance player with Tank01 projections."""
        try:
            if not self.api_status['apis']['tank01']:
                return
            
            tank01_client = self.api_manager.tank01_client
            player_name = player.get('name', 'Unknown')
            
            # Get Tank01 player ID
            tank01_id = self._get_tank01_player_id(player_name)
            
            if tank01_id:
                # Get fantasy projections
                projections = tank01_client.get_fantasy_projections(
                    player_id=tank01_id,
                    scoring_settings={'fantasyPoints': 'true'}
                )
                
                if projections and 'body' in projections:
                    proj_data = projections['body']
                    if isinstance(proj_data, dict):
                        # Calculate average projected points
                        total_points = 0
                        valid_games = 0
                        
                        for game_data in proj_data.values():
                            if isinstance(game_data, dict):
                                fantasy_points = game_data.get('fantasyPoints')
                                if fantasy_points:
                                    try:
                                        pts = float(fantasy_points)
                                        total_points += pts
                                        valid_games += 1
                                    except (ValueError, TypeError):
                                        pass
                        
                        if valid_games > 0:
                            avg_points = total_points / valid_games
                            player['tank01_data']['projected_points'] = f"{avg_points:.1f}"
                
        except Exception as e:
            self.logger.error(f"Error enhancing {player.get('name', 'Unknown')} with Tank01 data: {e}")
    
    def _get_tank01_player_id(self, player_name: str) -> Optional[str]:
        """Get Tank01 player ID with simplified matching."""
        try:
            if not self.api_status['apis']['tank01']:
                return None
            
            tank01_client = self.api_manager.tank01_client
            
            # Get player list from Tank01 (this should be cached from previous calls)
            player_list_response = tank01_client.get_player_list()
            
            if not player_list_response or 'body' not in player_list_response:
                return None
            
            players = player_list_response['body']
            if not isinstance(players, list):
                return None
            
            # Enhanced name matching
            search_name = player_name.strip().lower()
            name_parts = search_name.split()
            
            if len(name_parts) < 2:
                return None
            
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            # Try exact match first
            for tank_player in players:
                if not isinstance(tank_player, dict):
                    continue
                
                tank_name = tank_player.get('longName', '').lower().strip()
                tank_id = tank_player.get('playerID')
                
                if not tank_name or not tank_id:
                    continue
                
                if search_name == tank_name:
                    return tank_id
            
            # Try first + last name match
            for tank_player in players:
                if not isinstance(tank_player, dict):
                    continue
                
                tank_name = tank_player.get('longName', '').lower().strip()
                tank_id = tank_player.get('playerID')
                
                if not tank_name or not tank_id:
                    continue
                
                if first_name in tank_name and last_name in tank_name:
                    return tank_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Tank01 player ID for {player_name}: {e}")
            return None
    
    def _generate_start_sit_analysis(self, player: Dict[str, Any]):
        """Generate start/sit recommendations based on available data."""
        try:
            position = player.get('position', 'Unknown')
            selected_pos = player.get('selected_position', 'BN')
            projected_points = player.get('tank01_data', {}).get('projected_points', 'N/A')
            
            # Initialize scoring
            start_score = 50  # Base neutral score
            key_factors = []
            
            # Factor 1: Projected Points
            if projected_points != 'N/A':
                try:
                    points = float(projected_points)
                    if points > 15:
                        start_score += 20
                        key_factors.append(f"High projection ({points:.1f} pts)")
                    elif points > 10:
                        start_score += 10
                        key_factors.append(f"Good projection ({points:.1f} pts)")
                    elif points > 5:
                        start_score += 5
                        key_factors.append(f"Decent projection ({points:.1f} pts)")
                    else:
                        start_score -= 10
                        key_factors.append(f"Low projection ({points:.1f} pts)")
                except (ValueError, TypeError):
                    pass
            else:
                key_factors.append("No projection available")
            
            # Factor 2: Current lineup status
            if selected_pos != 'BN':
                start_score += 10
                key_factors.append(f"Currently starting ({selected_pos})")
            else:
                key_factors.append("Currently on bench")
            
            # Factor 3: Position-based adjustments
            if position in ['QB', 'RB', 'WR']:
                start_score += 5  # High-scoring positions
            elif position in ['TE', 'K', 'DEF']:
                start_score -= 5  # Lower-scoring positions
            
            # Generate recommendation
            if start_score >= 70:
                recommendation = "🔥 MUST START"
                confidence = "High"
            elif start_score >= 60:
                recommendation = "✅ START"
                confidence = "Medium-High"
            elif start_score >= 50:
                recommendation = "👍 LEAN START"
                confidence = "Medium"
            elif start_score >= 40:
                recommendation = "🤔 TOSS-UP"
                confidence = "Low"
            else:
                recommendation = "❌ SIT"
                confidence = "Medium"
            
            # Update player data
            player['matchup_analysis'].update({
                'start_recommendation': recommendation,
                'confidence_level': confidence,
                'key_factors': key_factors
            })
            
        except Exception as e:
            self.logger.error(f"Error generating start/sit analysis for {player.get('name', 'Unknown')}: {e}")
    
    def generate_real_matchup_report(self) -> str:
        """Generate comprehensive real matchup analysis report."""
        try:
            self.logger.info("🚀 Generating real matchup analysis report")
            
            # Get Week 1 matchup information
            matchup_info = self.get_week_1_matchup()
            if not matchup_info:
                self.logger.error("Unable to retrieve matchup information")
                return ""
            
            # Get enhanced rosters
            my_roster = self.get_enhanced_roster(matchup_info['my_team_key'], is_my_team=True)
            opponent_roster = self.get_enhanced_roster(matchup_info['opponent_team_key'], is_my_team=False)
            
            if not my_roster or not opponent_roster:
                self.logger.error("Unable to retrieve roster data")
                return ""
            
            # Generate report content
            timestamp = datetime.now()
            report_content = self._generate_real_matchup_report_content(
                matchup_info, my_roster, opponent_roster, timestamp
            )
            
            # Save report
            output_dir = Path("analysis/matchups")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_real_matchup_analysis.md"
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Save raw API data
            raw_data_dir = Path("analysis/raw_api_data")
            raw_data_dir.mkdir(parents=True, exist_ok=True)
            
            raw_data_file = raw_data_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_real_matchup_raw_data.json"
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.raw_api_data, f, indent=2, default=str)
            
            self.logger.info(f"✅ Real matchup analysis report saved to {output_path}")
            self.logger.info(f"✅ Raw API data saved to {raw_data_file}")
            
            print(f"🚀 Real matchup analysis completed!")
            print(f"📄 Report saved to: {output_path}")
            print(f"📊 Raw API data saved to: {raw_data_file}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating real matchup report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_real_matchup_report_content(self, matchup_info: Dict[str, Any], 
                                            my_roster: List[Dict[str, Any]], 
                                            opponent_roster: List[Dict[str, Any]], 
                                            timestamp: datetime) -> str:
        """Generate comprehensive real matchup report content."""
        
        opponent_name = matchup_info['opponent_team_name']
        opponent_manager = matchup_info['opponent_manager']
        week = matchup_info.get('week', 1)
        
        # Calculate total projected points
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
        
        report = f"""# 🏈 REAL MATCHUP ANALYSIS REPORT
========================================================

**📅 Generated**: {timestamp.strftime('%B %d, %Y at %I:%M %p')}
**🏆 Week {week} Matchup**: My Team vs {opponent_name}
**👤 Opponent Manager**: {opponent_manager}
**📊 Data Sources**: Yahoo Fantasy + Tank01 NFL API

## 📊 Matchup Overview

### 🎯 Projected Points Comparison

**My Team**: {my_total_projected:.1f} points
**{opponent_name}**: {opponent_total_projected:.1f} points
**Difference**: {'+' if point_diff > 0 else ''}{point_diff:.1f} points

"""
        
        # Create diverging bar chart for projected points
        max_points = max(my_total_projected, opponent_total_projected) if my_total_projected > 0 or opponent_total_projected > 0 else 100
        if max_points > 0:
            my_bar_length = int((my_total_projected / max_points) * 30)
            opponent_bar_length = int((opponent_total_projected / max_points) * 30)
            
            # Diverging bar chart
            report += f"""
```
My Team        {'█' * my_bar_length:<30} {my_total_projected:.1f}
{opponent_name[:14]:<14} {'█' * opponent_bar_length:<30} {opponent_total_projected:.1f}
```

"""
        
        # Add matchup summary
        if point_diff > 5:
            advantage = f"✅ **You have a significant advantage** (+{point_diff:.1f} points)"
        elif point_diff > 0:
            advantage = f"👍 **You have a slight advantage** (+{point_diff:.1f} points)"
        elif point_diff > -5:
            advantage = f"🤔 **Close matchup** with slight disadvantage ({point_diff:.1f} points)"
        else:
            advantage = f"⚠️ **{opponent_name} has a significant advantage** ({abs(point_diff):.1f} points)"
        
        report += f"""
**🎯 Matchup Prediction**: {advantage}

## 🔥 START/SIT RECOMMENDATIONS

### 🚨 KEY DECISIONS

"""
        
        # Find key start/sit decisions with proper column formatting
        critical_decisions = []
        
        for player in my_roster:
            analysis = player.get('matchup_analysis', {})
            recommendation = analysis.get('start_recommendation', 'Unknown')
            
            if 'MUST START' in recommendation or 'SIT' in recommendation or 'TOSS-UP' in recommendation:
                critical_decisions.append(player)
        
        if critical_decisions:
            report += """
| Player               | Position | Current | Recommendation   | Tank01 Proj | Key Factor        |
| -------------------- | -------- | ------- | ---------------- | ----------- | ----------------- |
"""
            
            for player in critical_decisions[:10]:  # Top 10 critical decisions
                name = player.get('name', 'Unknown')[:20]
                position = player.get('position', 'N/A')[:8]
                current_pos = player.get('selected_position', 'BN')[:7]
                recommendation = player.get('matchup_analysis', {}).get('start_recommendation', 'Unknown')[:16]
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')[:11]
                factors = player.get('matchup_analysis', {}).get('key_factors', [])
                key_factor = factors[0] if factors else 'N/A'
                key_factor = key_factor[:17] if len(key_factor) > 17 else key_factor
                
                report += f"| {name:<20} | {position:<8} | {current_pos:<7} | {recommendation:<16} | {proj:<11} | {key_factor:<17} |\n"
        else:
            report += "No critical start/sit decisions identified.\n"
        
        # Side-by-side roster comparison
        report += f"""

## 🔄 SIDE-BY-SIDE ROSTER COMPARISON

### 🏆 Starting Lineups

| Position | My Player            | My Proj | {opponent_name[:12]:<12} | Opp Proj | Advantage   |
| -------- | -------------------- | ------- | {'':<12} | -------- | ----------- |
"""
        
        # Group starters by position
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
        
        # Create side-by-side comparison
        for pos in positions:
            my_players = my_starters_by_pos.get(pos, [])
            opp_players = opponent_starters_by_pos.get(pos, [])
            
            max_players = max(len(my_players), len(opp_players), 1)
            
            for i in range(max_players):
                my_player = my_players[i] if i < len(my_players) else {}
                opp_player = opp_players[i] if i < len(opp_players) else {}
                
                # My player info
                my_name = my_player.get('name', 'Empty')[:20]
                my_proj = my_player.get('tank01_data', {}).get('projected_points', 'N/A')[:7]
                
                # Opponent player info
                opp_name = opp_player.get('name', 'Empty')[:12]
                opp_proj = opp_player.get('tank01_data', {}).get('projected_points', 'N/A')[:8]
                
                # Calculate advantage
                advantage = 'TIE'[:11]
                if my_proj != 'N/A' and opp_proj != 'N/A':
                    try:
                        my_pts = float(my_proj)
                        opp_pts = float(opp_proj)
                        diff = my_pts - opp_pts
                        if diff > 2:
                            advantage = f"+{diff:.1f} ME"[:11]
                        elif diff < -2:
                            advantage = f"+{abs(diff):.1f} OPP"[:11]
                        else:
                            advantage = "CLOSE"[:11]
                    except (ValueError, TypeError):
                        pass
                
                pos_display = pos if i == 0 else ''
                report += f"| {pos_display:<8} | {my_name:<20} | {my_proj:<7} | {opp_name:<12} | {opp_proj:<8} | {advantage:<11} |\n"
        
        # Add strategic recommendations
        report += f"""

## 💡 STRATEGIC RECOMMENDATIONS

### 🎯 Key Matchup Insights

**Projected Outcome**: {advantage}

**🔑 Keys to Victory**:
"""
        
        # Generate strategic insights
        if point_diff > 0:
            report += f"- You're projected to win by {point_diff:.1f} points - play it safe with your studs\n"
            report += "- Consider high-floor players over boom-bust options\n"
            report += f"- Monitor {opponent_name}'s top threats for any last-minute changes\n"
        else:
            report += f"- You're trailing by {abs(point_diff):.1f} points - need upside plays\n"
            report += "- Consider high-ceiling players who could have breakout games\n"
            report += "- Look for contrarian plays that could provide an edge\n"
        
        # Add top performers comparison
        my_top_performers = sorted(
            [p for p in my_starters if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A'],
            key=lambda p: float(p.get('tank01_data', {}).get('projected_points', '0')),
            reverse=True
        )[:3]
        
        opp_top_performers = sorted(
            [p for p in opponent_starters if p.get('tank01_data', {}).get('projected_points', 'N/A') != 'N/A'],
            key=lambda p: float(p.get('tank01_data', {}).get('projected_points', '0')),
            reverse=True
        )[:3]
        
        if my_top_performers:
            report += "\n**🌟 Your Top Projected Performers**:\n"
            for i, player in enumerate(my_top_performers, 1):
                name = player.get('name', 'Unknown')
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
                pos = player.get('selected_position', 'N/A')
                report += f"{i}. **{name}** ({pos}): {proj} projected points\n"
        
        if opp_top_performers:
            report += f"\n**⚠️ {opponent_name}'s Top Threats**:\n"
            for i, player in enumerate(opp_top_performers, 1):
                name = player.get('name', 'Unknown')
                proj = player.get('tank01_data', {}).get('projected_points', 'N/A')
                pos = player.get('selected_position', 'N/A')
                report += f"{i}. **{name}** ({pos}): {proj} projected points\n"
        
        # Add methodology
        report += f"""

---

## 🔬 Analysis Methodology

### 📊 Start/Sit Scoring System
**Factors Considered**:
- **Projected Points**: Tank01 weekly fantasy projections
- **Current Lineup Status**: Whether player is currently starting
- **Position Impact**: High-scoring vs lower-scoring positions

**Recommendation Scale**:
- 🔥 **MUST START**: Elite plays with high projections
- ✅ **START**: Strong plays worth starting
- 👍 **LEAN START**: Slight edge to start
- 🤔 **TOSS-UP**: Could go either way
- ❌ **SIT**: Better options available

### 🎯 Data Sources
- **Yahoo Fantasy API**: Official roster, matchup, and league data
- **Tank01 NFL API**: Weekly fantasy point projections
- **Real Opponent**: Actual Week {week} matchup from Yahoo Fantasy

---

## 📊 Report Metadata

- **Analysis Engine**: Real Matchup Analyzer
- **My Team Players**: {len(my_roster)} total ({len(my_starters)} starters, {len([p for p in my_roster if p.get('selected_position') == 'BN'])} bench)
- **Opponent Players**: {len(opponent_roster)} total ({len(opponent_starters)} starters, {len([p for p in opponent_roster if p.get('selected_position') == 'BN'])} bench)
- **Opponent**: {opponent_name} (Manager: {opponent_manager})
- **Timestamp**: {timestamp.isoformat()}

*🏈 Built for competitive fantasy football real matchup analysis and strategic lineup optimization*
"""
        
        return report


def main():
    """Main function to run the real matchup analyzer."""
    print("🏈 REAL MATCHUP ANALYSIS REPORT GENERATOR")
    print("=" * 50)
    
    try:
        analyzer = RealMatchupAnalyzer()
        report_path = analyzer.generate_real_matchup_report()
        
        if report_path:
            print(f"\n🎉 Real matchup analysis completed!")
            print(f"📄 Report saved to: {report_path}")
        else:
            print("\n❌ Analysis failed - check logs for details")
            
    except Exception as e:
        print(f"\n❌ Error running real matchup analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
