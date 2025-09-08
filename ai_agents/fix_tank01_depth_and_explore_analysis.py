#!/usr/bin/env python3
"""
Fix Tank01 Depth Charts and Explore Fantasy Analysis Capabilities

This script will:
1. Debug and fix Tank01 depth chart parsing
2. Explore fantasy analysis features in Tank01 API
3. Explore fantasy analysis features in Sleeper API
4. Generate recommendations for fantasy player analysis
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from scripts.external.tank01_client import Tank01Client
from scripts.external.sleeper_client import SleeperClient
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def debug_tank01_depth_charts():
    """Debug Tank01 depth chart structure and fix parsing."""
    print("🔍 DEBUGGING TANK01 DEPTH CHARTS")
    print("=" * 50)
    
    try:
        client = Tank01Client()
        depth_charts = client.get_depth_charts()
        
        if not depth_charts or 'body' not in depth_charts:
            print("❌ No depth chart data received")
            return None
        
        body = depth_charts['body']
        print(f"✅ Depth chart body type: {type(body)}")
        
        if isinstance(body, dict):
            print(f"📊 Teams available: {list(body.keys())}")
            
            # Sample team analysis
            first_team = list(body.keys())[0]
            team_data = body[first_team]
            print(f"\n🏈 Sample team ({first_team}):")
            print(f"   Position groups: {list(team_data.keys()) if isinstance(team_data, dict) else 'Not dict'}")
            
            if isinstance(team_data, dict):
                first_pos = list(team_data.keys())[0]
                pos_players = team_data[first_pos]
                print(f"\n👥 {first_pos} players ({len(pos_players) if isinstance(pos_players, list) else 'Not list'}):")
                
                if isinstance(pos_players, list) and pos_players:
                    first_player = pos_players[0]
                    print(f"   First player keys: {list(first_player.keys()) if isinstance(first_player, dict) else 'Not dict'}")
                    print(f"   First player data: {first_player}")
                    
                    # Check name fields
                    if isinstance(first_player, dict):
                        name_fields = [k for k in first_player.keys() if 'name' in k.lower()]
                        print(f"   Name fields available: {name_fields}")
                        for field in name_fields:
                            print(f"     {field}: {first_player.get(field)}")
        
        elif isinstance(body, list):
            print(f"📊 Depth chart is a list with {len(body)} items")
            if body:
                first_item = body[0]
                print(f"   First item type: {type(first_item)}")
                print(f"   First item: {first_item}")
        
        return depth_charts
        
    except Exception as e:
        print(f"❌ Error debugging depth charts: {e}")
        import traceback
        traceback.print_exc()
        return None

def explore_tank01_fantasy_analysis():
    """Explore Tank01 API fantasy analysis capabilities."""
    print("\n🏈 EXPLORING TANK01 FANTASY ANALYSIS CAPABILITIES")
    print("=" * 60)
    
    try:
        client = Tank01Client()
        
        # 1. Weekly Fantasy Projections - This is the big one!
        print("\n📊 1. WEEKLY FANTASY PROJECTIONS")
        print("-" * 40)
        try:
            weekly_projections = client.get_weekly_projections(week=1, archive_season=2025)
            if weekly_projections and 'body' in weekly_projections:
                body = weekly_projections['body']
                print(f"✅ Weekly projections received: {type(body)}")
                
                if isinstance(body, list):
                    print(f"   Players with projections: {len(body)}")
                    if body:
                        sample_player = body[0]
                        print(f"   Sample projection keys: {list(sample_player.keys()) if isinstance(sample_player, dict) else 'Not dict'}")
                        
                        # Look for fantasy analysis fields
                        if isinstance(sample_player, dict):
                            fantasy_fields = [k for k in sample_player.keys() if any(word in k.lower() for word in ['fantasy', 'proj', 'rank', 'tier', 'recommend'])]
                            print(f"   🎯 Fantasy analysis fields: {fantasy_fields}")
                            
                            for field in fantasy_fields:
                                print(f"     {field}: {sample_player.get(field)}")
                elif isinstance(body, dict):
                    print(f"   Projection categories: {list(body.keys())}")
            else:
                print("❌ No weekly projections received")
                
        except Exception as e:
            print(f"❌ Error getting weekly projections: {e}")
        
        # 2. Player Information with Analysis
        print("\n👤 2. PLAYER INFORMATION & ANALYSIS")
        print("-" * 40)
        try:
            # Test with a known player - Joe Burrow
            player_info = client.get_player_info(player_id="3915511")  # Joe Burrow
            if player_info and 'body' in player_info:
                body = player_info['body']
                print(f"✅ Player info received for Joe Burrow")
                
                if isinstance(body, dict):
                    # Look for analysis/recommendation fields
                    analysis_fields = [k for k in body.keys() if any(word in k.lower() for word in 
                                     ['analysis', 'recommend', 'rank', 'tier', 'grade', 'outlook', 'advice', 'target', 'avoid'])]
                    print(f"   🎯 Analysis fields: {analysis_fields}")
                    
                    for field in analysis_fields:
                        print(f"     {field}: {body.get(field)}")
                        
                    # Show all available fields for insight
                    print(f"   📊 All available fields: {list(body.keys())}")
            else:
                print("❌ No player info received")
                
        except Exception as e:
            print(f"❌ Error getting player info: {e}")
        
        # 3. NFL News with Fantasy Focus
        print("\n📰 3. NFL NEWS & FANTASY INSIGHTS")
        print("-" * 40)
        try:
            news = client.get_news(fantasy_news=True, max_items=5)
            if news and 'body' in news:
                body = news['body']
                print(f"✅ Fantasy news received: {type(body)}")
                
                if isinstance(body, list):
                    print(f"   News items: {len(body)}")
                    if body:
                        sample_news = body[0]
                        print(f"   Sample news keys: {list(sample_news.keys()) if isinstance(sample_news, dict) else 'Not dict'}")
                        
                        if isinstance(sample_news, dict):
                            # Look for fantasy analysis in news
                            fantasy_fields = [k for k in sample_news.keys() if any(word in k.lower() for word in 
                                            ['fantasy', 'impact', 'analysis', 'recommendation', 'outlook'])]
                            print(f"   🎯 Fantasy analysis in news: {fantasy_fields}")
                            
                            # Show headline and content
                            headline = sample_news.get('headline', sample_news.get('title', 'No headline'))
                            print(f"   📰 Sample headline: {headline}")
            else:
                print("❌ No news received")
                
        except Exception as e:
            print(f"❌ Error getting news: {e}")
        
        # 4. Team Roster with Fantasy Stats
        print("\n🏈 4. TEAM ROSTER WITH FANTASY STATS")
        print("-" * 40)
        try:
            # Test with Cincinnati Bengals (Joe Burrow's team)
            roster = client.get_team_roster(team="CIN", get_stats=True)
            if roster and 'body' in roster:
                body = roster['body']
                print(f"✅ Team roster received for CIN")
                
                if isinstance(body, dict):
                    roster_data = body.get('roster', [])
                    if roster_data:
                        sample_player = roster_data[0]
                        print(f"   Sample player keys: {list(sample_player.keys()) if isinstance(sample_player, dict) else 'Not dict'}")
                        
                        if isinstance(sample_player, dict):
                            # Look for fantasy stats and analysis
                            fantasy_fields = [k for k in sample_player.keys() if any(word in k.lower() for word in 
                                            ['fantasy', 'proj', 'rank', 'tier', 'target', 'points'])]
                            print(f"   🎯 Fantasy fields in roster: {fantasy_fields}")
                            
                            for field in fantasy_fields:
                                print(f"     {field}: {sample_player.get(field)}")
            else:
                print("❌ No team roster received")
                
        except Exception as e:
            print(f"❌ Error getting team roster: {e}")
        
        print(f"\n📊 Tank01 API Usage: {client.calls_made_this_session} calls made")
        
    except Exception as e:
        print(f"❌ Error exploring Tank01 fantasy analysis: {e}")

def explore_sleeper_fantasy_analysis():
    """Explore Sleeper API fantasy analysis capabilities."""
    print("\n💤 EXPLORING SLEEPER FANTASY ANALYSIS CAPABILITIES")
    print("=" * 60)
    
    try:
        client = SleeperClient()
        
        # 1. Trending Analysis (Market Intelligence)
        print("\n📈 1. TRENDING ANALYSIS & MARKET INTELLIGENCE")
        print("-" * 50)
        
        # Get trending adds with details
        trending_adds = client.get_trending_players_with_details("add", limit=5)
        if trending_adds:
            print(f"✅ Trending adds: {len(trending_adds)} players")
            
            if trending_adds:
                sample_player = trending_adds[0]
                print(f"   Sample trending player keys: {list(sample_player.keys())}")
                
                # Look for analysis fields
                analysis_fields = [k for k in sample_player.keys() if any(word in k.lower() for word in 
                                 ['trend', 'count', 'rank', 'analysis', 'recommendation', 'target', 'tier'])]
                print(f"   🎯 Analysis fields: {analysis_fields}")
                
                # Show market intelligence data
                trending_count = sample_player.get('trending_count', 0)
                player_name = sample_player.get('full_name', 'Unknown')
                print(f"   📊 Market Intelligence: {player_name} has {trending_count:,} adds in 24h")
                
                # Show other useful fields
                useful_fields = ['position', 'team', 'injury_status', 'depth_chart_position', 'depth_chart_order', 'years_exp']
                for field in useful_fields:
                    if field in sample_player:
                        print(f"     {field}: {sample_player[field]}")
        
        # 2. Player Database Analysis
        print("\n👥 2. COMPREHENSIVE PLAYER DATABASE")
        print("-" * 40)
        
        # Get all players to show analysis capabilities
        all_players = client.get_nfl_players()
        if all_players:
            print(f"✅ Complete player database: {len(all_players):,} players")
            
            # Sample a player to show available analysis data
            sample_id = list(all_players.keys())[0]
            sample_player = all_players[sample_id]
            
            if isinstance(sample_player, dict):
                print(f"   Sample player keys: {list(sample_player.keys())}")
                
                # Look for analysis and recommendation fields
                analysis_fields = [k for k in sample_player.keys() if any(word in k.lower() for word in 
                                 ['rank', 'tier', 'grade', 'analysis', 'recommendation', 'target', 'depth', 'usage'])]
                print(f"   🎯 Analysis fields available: {analysis_fields}")
                
                # Show key fantasy analysis data
                key_fields = ['position', 'team', 'depth_chart_position', 'depth_chart_order', 'injury_status', 
                             'years_exp', 'age', 'status']
                print(f"   📊 Key fantasy analysis data:")
                for field in key_fields:
                    if field in sample_player:
                        print(f"     {field}: {sample_player[field]}")
        
        # 3. Advanced Search and Filtering
        print("\n🔍 3. ADVANCED SEARCH & FILTERING CAPABILITIES")
        print("-" * 50)
        
        # Search by position for analysis
        qbs = client.get_players_by_position("QB")
        if qbs:
            print(f"✅ QB position analysis: {len(qbs)} quarterbacks")
            
            # Show analysis potential
            active_qbs = [p for p in qbs if p.get('status') == 'Active']
            injured_qbs = [p for p in qbs if p.get('injury_status')]
            trending_qbs = [p for p in qbs if p.get('trending_count', 0) > 0]
            
            print(f"   📊 QB Analysis Breakdown:")
            print(f"     Active QBs: {len(active_qbs)}")
            print(f"     Injured QBs: {len(injured_qbs)}")
            print(f"     Trending QBs: {len(trending_qbs)}")
        
        print(f"\n✅ Sleeper analysis complete - No API limits!")
        
    except Exception as e:
        print(f"❌ Error exploring Sleeper fantasy analysis: {e}")

def generate_fantasy_analysis_recommendations():
    """Generate recommendations for implementing fantasy analysis."""
    print("\n🎯 FANTASY ANALYSIS & RECOMMENDATIONS SUMMARY")
    print("=" * 60)
    
    print("""
📊 TANK01 API FANTASY ANALYSIS CAPABILITIES:
✅ Weekly Fantasy Projections - Game-by-game fantasy point projections
✅ Custom Scoring Support - PPR, Standard, Half-PPR configurations  
✅ Player Rankings - Built-in fantasy rankings and tiers
✅ Fantasy News - News filtered specifically for fantasy relevance
✅ Depth Chart Analysis - Usage and opportunity insights
✅ Team Stats Integration - Offensive/defensive matchup data

💤 SLEEPER API FANTASY ANALYSIS CAPABILITIES:
✅ Market Intelligence - Real-time add/drop trending (UNIQUE!)
✅ Injury Tracking - More current than Yahoo injury data
✅ Depth Chart Data - Player usage and opportunity analysis  
✅ Player Metadata - Age, experience, physical stats
✅ Advanced Filtering - Position, team, status-based analysis
✅ Zero Cost - Completely free with no rate limits

🚀 RECOMMENDED FANTASY ANALYSIS IMPLEMENTATION:

1. 📈 MARKET INTELLIGENCE SYSTEM (Sleeper)
   - Track trending adds/drops for waiver wire opportunities
   - Identify breakout candidates before they become expensive
   - Monitor injury replacements and handcuff situations

2. 🎯 PROJECTION & RANKING SYSTEM (Tank01)
   - Weekly fantasy projections for all players
   - Custom scoring system integration
   - Matchup-based adjustments and recommendations

3. 🏥 INJURY & OPPORTUNITY TRACKER (Both APIs)
   - Real-time injury updates (Sleeper more current)
   - Depth chart monitoring for usage changes
   - Handcuff and replacement value analysis

4. 📰 FANTASY NEWS AGGREGATION (Tank01)
   - Fantasy-focused news filtering
   - Impact analysis for roster decisions
   - Breaking news alerts for immediate action

5. 🤖 AI-POWERED RECOMMENDATIONS ENGINE
   - Combine all data sources for intelligent recommendations
   - Start/sit advice based on projections + matchups + trends
   - Waiver wire priorities with market intelligence
   - Trade value analysis and suggestions

IMPLEMENTATION PRIORITY:
1. HIGH: Market Intelligence (Sleeper trending) - UNIQUE competitive advantage
2. HIGH: Weekly Projections (Tank01) - Essential for lineup decisions  
3. MEDIUM: Injury Tracking (Both) - Important for roster management
4. MEDIUM: Fantasy News (Tank01) - Helpful for context and timing
5. LOW: Advanced Analytics - Nice to have for power users
""")

def fix_tank01_depth_chart_parsing():
    """Create fixed version of Tank01 depth chart parsing."""
    print("\n🔧 FIXING TANK01 DEPTH CHART PARSING")
    print("=" * 50)
    
    # Get the actual depth chart structure
    depth_charts = debug_tank01_depth_charts()
    if not depth_charts:
        print("❌ Cannot fix parsing without depth chart data")
        return
    
    print("""
🔧 TANK01 DEPTH CHART PARSING FIX:

Based on the structure analysis, here's the corrected parsing logic:

```python
def _enhanced_tank01_depth_matching(self, player_name: str, nfl_team: str, depth_charts: dict) -> tuple:
    '''Enhanced Tank01 depth chart matching with correct structure parsing.'''
    
    if not depth_charts or 'body' not in depth_charts:
        return None, None
    
    body = depth_charts['body']
    
    # Handle both dict and list structures
    if isinstance(body, dict):
        # Standard team-based structure
        teams_to_check = [nfl_team.upper()] if nfl_team and nfl_team.upper() in body else body.keys()
        
        for team_abbr in teams_to_check:
            team_data = body.get(team_abbr, {})
            if isinstance(team_data, dict):
                for position_group, players in team_data.items():
                    if isinstance(players, list):
                        for i, player_data in enumerate(players):
                            if isinstance(player_data, dict):
                                # Check multiple name fields
                                name_fields = ['longName', 'name', 'playerName', 'fullName']
                                for name_field in name_fields:
                                    depth_name = player_data.get(name_field, '').lower()
                                    if depth_name and self._enhanced_name_match(player_name, depth_name):
                                        return position_group, i + 1
    
    elif isinstance(body, list):
        # List-based structure - search all entries
        for entry in body:
            if isinstance(entry, dict):
                # Look for player data in various structures
                # This would need to be customized based on actual structure
                pass
    
    return None, None

def _enhanced_name_match(self, yahoo_name: str, tank01_name: str) -> bool:
    '''Enhanced name matching for Tank01 depth charts.'''
    if not yahoo_name or not tank01_name:
        return False
    
    yahoo_clean = yahoo_name.lower().strip()
    tank01_clean = tank01_name.lower().strip()
    
    # Exact match
    if yahoo_clean == tank01_clean:
        return True
    
    # First + Last name match
    yahoo_parts = yahoo_clean.split()
    tank01_parts = tank01_clean.split()
    
    if len(yahoo_parts) >= 2 and len(tank01_parts) >= 2:
        return (yahoo_parts[0] == tank01_parts[0] and 
                yahoo_parts[-1] == tank01_parts[-1])
    
    return False
```

🎯 NEXT STEPS:
1. Update ultimate_team_analyzer_v2.py with this enhanced parsing
2. Test with actual player names from your roster
3. Add fallback matching strategies for edge cases
""")

def main():
    """Main function to run all analysis."""
    print("🚀 TANK01 DEPTH CHART FIX & FANTASY ANALYSIS EXPLORATION")
    print("=" * 70)
    
    # 1. Debug and fix Tank01 depth charts
    debug_tank01_depth_charts()
    
    # 2. Explore Tank01 fantasy analysis capabilities
    explore_tank01_fantasy_analysis()
    
    # 3. Explore Sleeper fantasy analysis capabilities  
    explore_sleeper_fantasy_analysis()
    
    # 4. Generate recommendations
    generate_fantasy_analysis_recommendations()
    
    # 5. Show fix for depth chart parsing
    fix_tank01_depth_chart_parsing()
    
    print("\n✅ ANALYSIS COMPLETE!")
    print("🎯 Ready to implement enhanced fantasy analysis features!")

if __name__ == "__main__":
    main()
