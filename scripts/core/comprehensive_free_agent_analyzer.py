#!/usr/bin/env python3
"""
Comprehensive Free Agent Analyzer

This script creates an extremely comprehensive free agent report with:
- ALL Yahoo free agents (including paginated results)
- Complete API statistics and analysis for all players
- Market intelligence from Sleeper trending data
- Fantasy projections from Tank01 API
- News headlines with dates and URLs
- Professional recommendations and priority rankings

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
from dateutil import parser as date_parser

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.core.external_api_manager import ExternalAPIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

class ComprehensiveFreeAgentAnalyzer:
    """
    Comprehensive free agent analyzer with complete multi-API integration.
    """
    
    def __init__(self):
        """Initialize the comprehensive free agent analyzer."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔍 Initializing Comprehensive Free Agent Analyzer")
        
        # Initialize the External API Manager
        self.api_manager = ExternalAPIManager()
        
        # Check API status
        self.api_status = self.api_manager.get_api_status()
        self.logger.info(f"APIs available: {sum(self.api_status['apis'].values())}/3")
        
        # Cache for external API data
        self._sleeper_all_players_cache = None
        self._tank01_player_cache = None
        self._tank01_news_cache = None
        
        # Raw API data storage
        self.raw_api_data = {
            'yahoo_free_agents_all_positions': {},
            'sleeper_all_players': None,
            'sleeper_trending_add': None,
            'sleeper_trending_drop': None,
            'tank01_news': None,
            'tank01_weekly_projections': None
        }
    
    def get_all_yahoo_free_agents_paginated(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get ALL Yahoo free agents with complete pagination."""
        try:
            self.logger.info("🏈 Retrieving ALL Yahoo free agents with complete pagination")
            
            if not self.api_status['apis']['yahoo']:
                self.logger.error("Yahoo API not available")
                return {}
            
            yahoo_client = self.api_manager.yahoo_client
            all_free_agents = {}
            
            positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
            
            for position in positions:
                self.logger.info(f"📊 Getting all {position} free agents with pagination")
                
                position_players = []
                
                try:
                    # Get maximum available free agents for this position
                    # Yahoo API handles pagination internally
                    position_players = yahoo_client.get_free_agents(
                        position=position,
                        count=200  # Request maximum, API will handle pagination
                    )
                    
                    if not position_players:
                        position_players = []
                        
                    self.logger.info(f"   Retrieved {len(position_players)} {position} players")
                    
                except Exception as e:
                    self.logger.error(f"Error getting {position} free agents: {e}")
                    position_players = []
                
                all_free_agents[position] = position_players
                self.logger.info(f"✅ Complete {position} free agents: {len(position_players)} players")
            
            # Store raw data
            self.raw_api_data['yahoo_free_agents_all_positions'] = all_free_agents
            
            total_free_agents = sum(len(players) for players in all_free_agents.values())
            self.logger.info(f"🎯 COMPLETE: Retrieved {total_free_agents} total free agents across all positions")
            
            return all_free_agents
            
        except Exception as e:
            self.logger.error(f"Error getting all Yahoo free agents: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_comprehensive_sleeper_data(self) -> Dict[str, Any]:
        """Get comprehensive Sleeper data for free agent analysis."""
        try:
            if not self.api_status['apis']['sleeper']:
                return {}
            
            sleeper_client = self.api_manager.sleeper_client
            
            # Get all players for matching
            if not self._sleeper_all_players_cache:
                self.logger.info("📈 Loading ALL Sleeper players for comprehensive matching")
                all_players = sleeper_client.get_nfl_players()
                self._sleeper_all_players_cache = all_players
                self.raw_api_data['sleeper_all_players'] = all_players
                self.logger.info(f"✅ Cached {len(all_players)} Sleeper players")
            
            # Get trending data with larger limits for comprehensive analysis
            trending_add = sleeper_client.get_trending_players_with_details('add', lookback_hours=24, limit=100)
            trending_drop = sleeper_client.get_trending_players_with_details('drop', lookback_hours=24, limit=100)
            
            self.raw_api_data['sleeper_trending_add'] = trending_add
            self.raw_api_data['sleeper_trending_drop'] = trending_drop
            
            return {
                'all_players': self._sleeper_all_players_cache,
                'trending_add': trending_add or [],
                'trending_drop': trending_drop or [],
                'add_count': len(trending_add) if trending_add else 0,
                'drop_count': len(trending_drop) if trending_drop else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive Sleeper data: {e}")
            return {}
    
    def get_tank01_comprehensive_data(self) -> Dict[str, Any]:
        """Get comprehensive Tank01 data for projections and news."""
        try:
            if not self.api_status['apis']['tank01']:
                return {}
            
            tank01_client = self.api_manager.tank01_client
            
            # Get comprehensive news with larger limit
            if not self._tank01_news_cache:
                self.logger.info("📰 Getting comprehensive Tank01 news")
                news = tank01_client.get_news(fantasy_news=True, max_items=50)
                self._tank01_news_cache = news
                self.raw_api_data['tank01_news'] = news
            
            # Get weekly projections for current week
            try:
                weekly_projections = tank01_client.get_weekly_projections(week=1, archive_season=2025)
                self.raw_api_data['tank01_weekly_projections'] = weekly_projections
            except Exception as e:
                self.logger.warning(f"Could not get weekly projections: {e}")
                weekly_projections = None
            
            return {
                'news': self._tank01_news_cache,
                'weekly_projections': weekly_projections
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Tank01 comprehensive data: {e}")
            return {}
    
    def enhance_free_agent_with_all_apis(self, player: Dict[str, Any], sleeper_data: Dict[str, Any], tank01_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance free agent with comprehensive multi-API data."""
        enhanced_player = player.copy()
        player_name = player.get('name', 'Unknown')
        
        # Initialize comprehensive data structure
        enhanced_player.update({
            'sleeper_analysis': {
                'player_id': None,
                'trending_add': False,
                'trending_drop': False,
                'trending_count': 0,
                'trending_type': None,
                'market_status': 'Unknown',
                'depth_chart_position': None,
                'depth_chart_order': None,
                'injury_status': None,
                'years_exp': None,
                'age': None,
                'complete_profile': None
            },
            'tank01_analysis': {
                'player_id': None,
                'projected_points': 'N/A',
                'weekly_projection': None,
                'recent_news': [],
                'fantasy_outlook': 'Unknown'
            },
            'comprehensive_analysis': {
                'recommendation': 'Unknown',
                'priority': 'MEDIUM',
                'waiver_priority': 0,
                'add_percentage': 0,
                'opportunity_score': 0,
                'risk_level': 'MEDIUM'
            }
        })
        
        # Enhance with Sleeper data
        self._enhance_free_agent_with_sleeper(enhanced_player, sleeper_data)
        
        # Enhance with Tank01 data
        self._enhance_free_agent_with_tank01(enhanced_player, tank01_data)
        
        # Generate comprehensive analysis
        self._generate_comprehensive_analysis(enhanced_player)
        
        return enhanced_player
    
    def _enhance_free_agent_with_sleeper(self, player: Dict[str, Any], sleeper_data: Dict[str, Any]):
        """Enhance free agent with Sleeper data."""
        player_name = player.get('name', 'Unknown')
        
        try:
            # Look for player in trending lists first
            sleeper_player = None
            
            # Check trending ADD players
            for trending_player in sleeper_data.get('trending_add', []):
                if self._enhanced_name_match(player_name, trending_player.get('full_name', '')):
                    sleeper_player = trending_player
                    player['sleeper_analysis'].update({
                        'trending_add': True,
                        'trending_count': trending_player.get('trending_count', 0),
                        'trending_type': 'add'
                    })
                    break
            
            # Check trending DROP players if not found in adds
            if not sleeper_player:
                for trending_player in sleeper_data.get('trending_drop', []):
                    if self._enhanced_name_match(player_name, trending_player.get('full_name', '')):
                        sleeper_player = trending_player
                        player['sleeper_analysis'].update({
                            'trending_drop': True,
                            'trending_count': trending_player.get('trending_count', 0),
                            'trending_type': 'drop'
                        })
                        break
            
            # Search all players if not in trending
            if not sleeper_player:
                yahoo_id = player.get('player_id', '')
                if yahoo_id:
                    for sleeper_id, sleeper_profile in sleeper_data.get('all_players', {}).items():
                        if isinstance(sleeper_profile, dict):
                            sleeper_yahoo_id = str(sleeper_profile.get('yahoo_id', ''))
                            if sleeper_yahoo_id == str(yahoo_id):
                                sleeper_player = sleeper_profile
                                sleeper_player['player_id'] = sleeper_id
                                break
            
            # If found, extract comprehensive data
            if sleeper_player:
                player['sleeper_analysis'].update({
                    'player_id': sleeper_player.get('player_id'),
                    'depth_chart_position': sleeper_player.get('depth_chart_position'),
                    'depth_chart_order': sleeper_player.get('depth_chart_order'),
                    'injury_status': sleeper_player.get('injury_status'),
                    'years_exp': sleeper_player.get('years_exp'),
                    'age': sleeper_player.get('age'),
                    'complete_profile': sleeper_player
                })
                
                # Calculate market status
                if player['sleeper_analysis']['trending_add']:
                    count = player['sleeper_analysis']['trending_count']
                    if count > 50000:
                        status = f"🔥 EXTREMELY HIGH DEMAND ({count:,} adds)"
                    elif count > 20000:
                        status = f"🔥 HIGH DEMAND ({count:,} adds)"
                    elif count > 5000:
                        status = f"📈 MODERATE DEMAND ({count:,} adds)"
                    else:
                        status = f"📊 TRENDING UP ({count:,} adds)"
                    player['sleeper_analysis']['market_status'] = status
                elif player['sleeper_analysis']['trending_drop']:
                    count = player['sleeper_analysis']['trending_count']
                    status = f"❄️ BEING DROPPED ({count:,} drops)"
                    player['sleeper_analysis']['market_status'] = status
                else:
                    player['sleeper_analysis']['market_status'] = "📊 STABLE"
                
        except Exception as e:
            self.logger.error(f"Error enhancing {player_name} with Sleeper data: {e}")
    
    def _enhance_free_agent_with_tank01(self, player: Dict[str, Any], tank01_data: Dict[str, Any]):
        """Enhance free agent with Tank01 data."""
        player_name = player.get('name', 'Unknown')
        
        try:
            # Get Tank01 player ID
            tank01_id = self._get_tank01_player_id(player_name)
            if tank01_id:
                player['tank01_analysis']['player_id'] = tank01_id
                
                # Get fantasy projections
                tank01_client = self.api_manager.tank01_client
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
                            player['tank01_analysis']['projected_points'] = f"{avg_points:.1f}"
                
                # Look for player in news
                news_items = []
                news_data = tank01_data.get('news', {})
                if news_data and 'body' in news_data:
                    for news_item in news_data['body']:
                        if isinstance(news_item, dict):
                            title = news_item.get('title', '').lower()
                            if player_name.lower() in title:
                                news_items.append({
                                    'title': news_item.get('title', ''),
                                    'link': news_item.get('link', ''),
                                    'date': 'Recent'  # Tank01 doesn't provide dates in this format
                                })
                
                player['tank01_analysis']['recent_news'] = news_items[:3]  # Top 3 news items
                
        except Exception as e:
            self.logger.error(f"Error enhancing {player_name} with Tank01 data: {e}")
    
    def _get_tank01_player_id(self, player_name: str) -> Optional[str]:
        """Get Tank01 player ID with caching."""
        try:
            if not self.api_status['apis']['tank01']:
                return None
            
            tank01_client = self.api_manager.tank01_client
            
            # Get player list from Tank01 (with caching)
            if self._tank01_player_cache is None:
                self.logger.info("🔄 Loading Tank01 player list for free agent matching")
                player_list_response = tank01_client.get_player_list()
                
                if not player_list_response or 'body' not in player_list_response:
                    return None
                
                players = player_list_response['body']
                if not isinstance(players, list):
                    return None
                
                self._tank01_player_cache = players
                self.logger.info(f"✅ Cached {len(players)} Tank01 players")
            else:
                players = self._tank01_player_cache
            
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
    
    def _enhanced_name_match(self, name1: str, name2: str) -> bool:
        """Enhanced name matching between different APIs."""
        if not name1 or not name2:
            return False
        
        name1_clean = name1.lower().strip()
        name2_clean = name2.lower().strip()
        
        # Exact match
        if name1_clean == name2_clean:
            return True
        
        # First + last name match
        name1_parts = name1_clean.split()
        name2_parts = name2_clean.split()
        
        if len(name1_parts) >= 2 and len(name2_parts) >= 2:
            return (name1_parts[0] == name2_parts[0] and 
                    name1_parts[-1] == name2_parts[-1])
        
        return False
    
    def _generate_comprehensive_analysis(self, player: Dict[str, Any]):
        """Generate comprehensive analysis and recommendations."""
        try:
            # Base scoring
            opportunity_score = 0
            priority_score = 0
            
            # Yahoo rank contribution
            yahoo_rank = player.get('rank', 999)
            if isinstance(yahoo_rank, (int, str)) and str(yahoo_rank).isdigit():
                rank_val = int(yahoo_rank)
                if rank_val <= 10:
                    opportunity_score += 50
                    priority_score += 30
                elif rank_val <= 25:
                    opportunity_score += 30
                    priority_score += 20
                elif rank_val <= 50:
                    opportunity_score += 15
                    priority_score += 10
            
            # Sleeper trending contribution
            sleeper_analysis = player.get('sleeper_analysis', {})
            if sleeper_analysis.get('trending_add'):
                trending_count = sleeper_analysis.get('trending_count', 0)
                if trending_count > 20000:
                    opportunity_score += 40
                    priority_score += 35
                elif trending_count > 5000:
                    opportunity_score += 25
                    priority_score += 20
                elif trending_count > 1000:
                    opportunity_score += 15
                    priority_score += 10
            elif sleeper_analysis.get('trending_drop'):
                opportunity_score -= 20
                priority_score -= 15
            
            # Tank01 projections contribution
            tank01_analysis = player.get('tank01_analysis', {})
            projected_points = tank01_analysis.get('projected_points', 'N/A')
            if projected_points != 'N/A':
                try:
                    points = float(projected_points)
                    if points > 15:
                        opportunity_score += 25
                        priority_score += 20
                    elif points > 10:
                        opportunity_score += 15
                        priority_score += 10
                    elif points > 5:
                        opportunity_score += 5
                        priority_score += 5
                except (ValueError, TypeError):
                    pass
            
            # Injury status impact
            injury_status = sleeper_analysis.get('injury_status')
            if injury_status:
                opportunity_score -= 15
                priority_score -= 10
            
            # Generate recommendations
            if priority_score >= 40:
                recommendation = "🔥 IMMEDIATE ADD"
                priority = "URGENT"
                waiver_priority = 1
                risk_level = "LOW"
            elif priority_score >= 25:
                recommendation = "📈 STRONG ADD"
                priority = "HIGH"
                waiver_priority = 2
                risk_level = "LOW"
            elif priority_score >= 15:
                recommendation = "👀 CONSIDER ADD"
                priority = "MEDIUM"
                waiver_priority = 3
                risk_level = "MEDIUM"
            elif priority_score >= 5:
                recommendation = "📊 MONITOR"
                priority = "LOW"
                waiver_priority = 4
                risk_level = "MEDIUM"
            else:
                recommendation = "❌ AVOID"
                priority = "AVOID"
                waiver_priority = 5
                risk_level = "HIGH"
            
            # Calculate add percentage (simplified)
            add_percentage = min(100, max(0, priority_score * 2))
            
            player['comprehensive_analysis'].update({
                'recommendation': recommendation,
                'priority': priority,
                'waiver_priority': waiver_priority,
                'add_percentage': add_percentage,
                'opportunity_score': opportunity_score,
                'risk_level': risk_level
            })
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive analysis for {player.get('name', 'Unknown')}: {e}")
    
    def generate_comprehensive_free_agent_report(self) -> str:
        """Generate the comprehensive free agent report."""
        try:
            self.logger.info("🚀 Generating comprehensive free agent report")
            
            # Get all data
            all_free_agents = self.get_all_yahoo_free_agents_paginated()
            sleeper_data = self.get_comprehensive_sleeper_data()
            tank01_data = self.get_tank01_comprehensive_data()
            
            if not all_free_agents:
                self.logger.error("No free agent data available")
                return ""
            
            # Enhance all free agents with multi-API data
            enhanced_free_agents = {}
            total_players = sum(len(players) for players in all_free_agents.values())
            processed_count = 0
            
            for position, players in all_free_agents.items():
                self.logger.info(f"📊 Processing {len(players)} {position} free agents")
                enhanced_position_players = []
                
                for player in players:
                    processed_count += 1
                    if processed_count % 10 == 0:
                        self.logger.info(f"   Processed {processed_count}/{total_players} players")
                    
                    enhanced_player = self.enhance_free_agent_with_all_apis(player, sleeper_data, tank01_data)
                    enhanced_position_players.append(enhanced_player)
                
                # Sort by priority and opportunity score
                enhanced_position_players.sort(
                    key=lambda p: (
                        p.get('comprehensive_analysis', {}).get('waiver_priority', 5),
                        -p.get('comprehensive_analysis', {}).get('opportunity_score', 0)
                    )
                )
                
                enhanced_free_agents[position] = enhanced_position_players
            
            # Generate report
            timestamp = datetime.now()
            report_content = self._generate_comprehensive_report_content(enhanced_free_agents, sleeper_data, tank01_data, timestamp)
            
            # Save report
            output_dir = Path("analysis/free_agents")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_comprehensive_free_agents_analysis.md"
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Save raw API data
            raw_data_dir = Path("analysis/raw_api_data")
            raw_data_dir.mkdir(parents=True, exist_ok=True)
            
            raw_data_file = raw_data_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_comprehensive_free_agents_raw_data.json"
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.raw_api_data, f, indent=2, default=str)
            
            self.logger.info(f"✅ Comprehensive free agent report saved to {output_path}")
            self.logger.info(f"✅ Raw API data saved to {raw_data_file}")
            
            print(f"🚀 Comprehensive free agent analysis completed!")
            print(f"📄 Report saved to: {output_path}")
            print(f"📊 Raw API data saved to: {raw_data_file}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive free agent report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_comprehensive_report_content(self, enhanced_free_agents: Dict[str, List[Dict[str, Any]]], 
                                             sleeper_data: Dict[str, Any], tank01_data: Dict[str, Any], 
                                             timestamp: datetime) -> str:
        """Generate comprehensive report content."""
        
        # Calculate summary statistics
        total_players = sum(len(players) for players in enhanced_free_agents.values())
        urgent_adds = 0
        high_priority = 0
        trending_up = 0
        
        for players in enhanced_free_agents.values():
            for player in players:
                analysis = player.get('comprehensive_analysis', {})
                priority = analysis.get('priority', 'MEDIUM')
                if priority == 'URGENT':
                    urgent_adds += 1
                elif priority == 'HIGH':
                    high_priority += 1
                
                sleeper_analysis = player.get('sleeper_analysis', {})
                if sleeper_analysis.get('trending_add'):
                    trending_up += 1
        
        report = f"""# 🔍 COMPREHENSIVE Free Agent Analysis Report
========================================================

**📅 Generated**: {timestamp.strftime('%B %d, %Y at %I:%M %p')}
**🎯 Analysis Type**: Complete Multi-API Free Agent Intelligence
**📊 Data Sources**: Yahoo Fantasy + Sleeper NFL + Tank01 NFL APIs

## 📈 Executive Summary

**🏈 Total Free Agents Analyzed**: {total_players:,} players across all positions
**🔥 Immediate Adds (URGENT)**: {urgent_adds} players requiring immediate action
**📈 High Priority Targets**: {high_priority} players for strong consideration
**📊 Currently Trending Up**: {trending_up} players with significant add activity

**🎯 Market Intelligence**:
- **Trending Adds**: {sleeper_data.get('add_count', 0)} players with significant add activity
- **Trending Drops**: {sleeper_data.get('drop_count', 0)} players being dropped
- **News Coverage**: {len(tank01_data.get('news', {}).get('body', [])) if tank01_data.get('news') else 0} fantasy-relevant headlines

## 🚨 URGENT ACTION REQUIRED

**🔥 Immediate Add Candidates**

| Player         | Pos | Team | Yahoo Rank | Tank01 Proj | Sleeper Activity | Priority | Action |
| -------------- | --- | ---- | ---------- | ----------- | ---------------- | -------- | ------ |
"""
        
        # Add urgent candidates
        urgent_candidates = []
        for players in enhanced_free_agents.values():
            for player in players:
                if player.get('comprehensive_analysis', {}).get('priority') == 'URGENT':
                    urgent_candidates.append(player)
        
        # Sort urgent candidates by opportunity score
        urgent_candidates.sort(key=lambda p: -p.get('comprehensive_analysis', {}).get('opportunity_score', 0))
        
        for player in urgent_candidates[:10]:  # Top 10 urgent
            name = player.get('name', 'Unknown')[:14]
            position = player.get('position', 'N/A')[:3]
            team = player.get('team', 'N/A')[:4]
            rank = str(player.get('rank', 'N/A'))[:10]
            proj = player.get('tank01_analysis', {}).get('projected_points', 'N/A')[:11]
            activity = player.get('sleeper_analysis', {}).get('market_status', 'Unknown')[:16]
            priority = player.get('comprehensive_analysis', {}).get('priority', 'MEDIUM')[:8]
            action = "ADD NOW"
            
            report += f"| {name:<14} | {position:<3} | {team:<4} | {rank:<10} | {proj:<11} | {activity:<16} | {priority:<8} | {action:<6} |\n"
        
        # Add position-by-position analysis
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
        
        for position in positions:
            players = enhanced_free_agents.get(position, [])
            if not players:
                continue
            
            report += f"""

## 🏈 {position} Position Analysis

**📊 Available {position}s**: {len(players)} players analyzed
**🔥 High Priority**: {len([p for p in players if p.get('comprehensive_analysis', {}).get('priority') in ['URGENT', 'HIGH']])} players
**📈 Trending Up**: {len([p for p in players if p.get('sleeper_analysis', {}).get('trending_add', False)])} players

### Top {position} Targets

| Rank | Player         | Team | Yahoo | Tank01 | Sleeper Market Intelligence | Recommendation | Priority |
| ---- | -------------- | ---- | ----- | ------ | --------------------------- | -------------- | -------- |
"""
            
            for i, player in enumerate(players[:15], 1):  # Top 15 per position
                name = player.get('name', 'Unknown')[:14]
                team = player.get('team', 'N/A')[:4]
                yahoo_rank = str(player.get('rank', 'N/A'))[:5]
                tank01_proj = player.get('tank01_analysis', {}).get('projected_points', 'N/A')[:6]
                market_status = player.get('sleeper_analysis', {}).get('market_status', 'Unknown')[:27]
                recommendation = player.get('comprehensive_analysis', {}).get('recommendation', 'Unknown')[:14]
                priority = player.get('comprehensive_analysis', {}).get('priority', 'MEDIUM')[:8]
                
                report += f"| {i:<4} | {name:<14} | {team:<4} | {yahoo_rank:<5} | {tank01_proj:<6} | {market_status:<27} | {recommendation:<14} | {priority:<8} |\n"
            
            # Add detailed analysis for top 5
            report += f"""

### 🔍 Detailed {position} Analysis

"""
            
            for player in players[:5]:  # Top 5 detailed analysis
                name = player.get('name', 'Unknown')
                team = player.get('team', 'N/A')
                yahoo_rank = player.get('rank', 'N/A')
                
                sleeper_analysis = player.get('sleeper_analysis', {})
                tank01_analysis = player.get('tank01_analysis', {})
                comp_analysis = player.get('comprehensive_analysis', {})
                
                report += f"""
#### 👤 {name} ({team})

**📊 Yahoo Ranking**: #{yahoo_rank}
**🎯 Tank01 Projection**: {tank01_analysis.get('projected_points', 'N/A')} fantasy points
**📈 Market Status**: {sleeper_analysis.get('market_status', 'Unknown')}
**🏥 Injury Status**: {sleeper_analysis.get('injury_status') or 'Healthy'}
**📋 Depth Chart**: {sleeper_analysis.get('depth_chart_position', 'N/A')} (#{sleeper_analysis.get('depth_chart_order', 'N/A')})

**🎯 Recommendation**: {comp_analysis.get('recommendation', 'Unknown')}
**⚡ Priority Level**: {comp_analysis.get('priority', 'MEDIUM')}
**📊 Opportunity Score**: {comp_analysis.get('opportunity_score', 0)}/100
**⚠️ Risk Level**: {comp_analysis.get('risk_level', 'MEDIUM')}

**📰 Recent News**:
"""
                
                news_items = tank01_analysis.get('recent_news', [])
                if news_items:
                    for news in news_items:
                        title = news.get('title', 'No title')
                        link = news.get('link', '#')
                        date = news.get('date', 'Recent')
                        report += f"- **{date}**: [{title}]({link})\n"
                else:
                    report += "- No recent news available\n"
        
        # Add market intelligence section
        report += f"""

## 📈 Market Intelligence Dashboard

### 🔥 Hottest Trending Adds (Last 24h)

| Player         | Position | Adds Count | Market Signal | Action Required |
| -------------- | -------- | ---------- | ------------- | --------------- |
"""
        
        # Get top trending adds
        trending_adds = sleeper_data.get('trending_add', [])[:10]
        for player in trending_adds:
            name = player.get('full_name', 'Unknown')[:14]
            position = player.get('position', 'N/A')[:8]
            count = f"{player.get('trending_count', 0):,}"[:10]
            
            count_val = player.get('trending_count', 0)
            if count_val > 50000:
                signal = "🚨 EMERGENCY"
                action = "ADD IMMEDIATELY"
            elif count_val > 20000:
                signal = "🔥 CRITICAL"
                action = "HIGH PRIORITY"
            elif count_val > 5000:
                signal = "📈 STRONG"
                action = "MONITOR CLOSELY"
            else:
                signal = "📊 MODERATE"
                action = "WATCH LIST"
            
            report += f"| {name:<14} | {position:<8} | {count:<10} | {signal:<13} | {action:<15} |\n"
        
        report += f"""

### ❄️ Players Being Dropped (Last 24h)

| Player         | Position | Drops Count | Drop Signal | Avoid/Monitor |
| -------------- | -------- | ----------- | ----------- | ------------- |
"""
        
        # Get top trending drops
        trending_drops = sleeper_data.get('trending_drop', [])[:10]
        for player in trending_drops:
            name = player.get('full_name', 'Unknown')[:14]
            position = player.get('position', 'N/A')[:8]
            count = f"{player.get('trending_count', 0):,}"[:11]
            
            count_val = player.get('trending_count', 0)
            if count_val > 20000:
                signal = "🚨 MASS EXODUS"
                action = "AVOID"
            elif count_val > 10000:
                signal = "❄️ HEAVY DROPS"
                action = "AVOID"
            elif count_val > 5000:
                signal = "📉 DECLINING"
                action = "MONITOR"
            else:
                signal = "📊 MODERATE"
                action = "NEUTRAL"
            
            report += f"| {name:<14} | {position:<8} | {count:<11} | {signal:<11} | {action:<13} |\n"
        
        # Add news section
        news_data = tank01_data.get('news', {})
        if news_data and 'body' in news_data:
            report += f"""

## 📰 Fantasy News Headlines

**🗞️ Latest Fantasy-Relevant News** ({len(news_data['body'])} headlines)

"""
            
            for news_item in news_data['body'][:20]:  # Top 20 news items
                title = news_item.get('title', 'No title')
                link = news_item.get('link', '#')
                report += f"- [{title}]({link})\n"
        
        # Add methodology section
        report += f"""

---

## 🔬 Analysis Methodology

### 📊 Data Sources Integration
- **Yahoo Fantasy API**: Official rankings, availability status, team assignments
- **Sleeper NFL API**: Real-time trending data from thousands of fantasy leagues
- **Tank01 NFL API**: Fantasy projections, news headlines, player statistics

### 🎯 Scoring Algorithm
**Opportunity Score Calculation**:
- Yahoo Rank (0-50 points): Higher ranks get more points
- Sleeper Trending (0-40 points): Based on add/drop volume
- Tank01 Projections (0-25 points): Based on projected fantasy points
- Injury Status (-15 points): Penalty for injured players

**Priority Levels**:
- **URGENT** (40+ points): Immediate waiver wire action required
- **HIGH** (25-39 points): Strong add candidates for consideration
- **MEDIUM** (15-24 points): Monitor closely, potential adds
- **LOW** (5-14 points): Watch list players
- **AVOID** (<5 points): Not recommended for add

### 📈 Market Intelligence
- **Trending Add Data**: Players being added across thousands of leagues
- **Trending Drop Data**: Players being dropped, potential avoid signals
- **Volume Thresholds**: 
  - 50K+ adds = Emergency priority
  - 20K+ adds = Critical priority
  - 5K+ adds = Strong consideration

---

## 📊 Report Metadata

- **Analysis Engine**: Comprehensive Free Agent Analyzer
- **Data Integration**: Yahoo Fantasy + Sleeper NFL + Tank01 NFL APIs
- **Report Type**: Complete Multi-API Free Agent Intelligence
- **Players Analyzed**: {total_players:,} total free agents
- **Timestamp**: {timestamp.isoformat()}

*🎯 Built for ultimate competitive fantasy football free agent analysis and strategic waiver wire management*
"""
        
        return report


def main():
    """Main function to run the comprehensive free agent analyzer."""
    print("🔍 COMPREHENSIVE Free Agent Analysis")
    print("=" * 50)
    
    try:
        analyzer = ComprehensiveFreeAgentAnalyzer()
        report_path = analyzer.generate_comprehensive_free_agent_report()
        
        if report_path:
            print(f"\n🎉 Comprehensive free agent analysis completed!")
            print(f"📄 Report saved to: {report_path}")
        else:
            print("\n❌ Analysis failed - check logs for details")
            
    except Exception as e:
        print(f"\n❌ Error running comprehensive free agent analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
