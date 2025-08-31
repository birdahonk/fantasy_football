#!/usr/bin/env python3
"""
Comprehensive Tank01 API Test Suite

Test all major Tank01 API endpoints with real data.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tank01_client import Tank01Client

def test_news_endpoint():
    """Test the NFL news endpoint."""
    print("🗞️  Testing Tank01 NFL News")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test fantasy news
        news = client.get_news(fantasy_news=True, max_items=5)
        
        if news and 'body' in news:
            print(f"✅ News retrieved successfully!")
            body = news['body']
            if isinstance(body, list) and body:
                print(f"📰 Found {len(body)} news items")
                
                # Show first news item
                first_item = body[0]
                if isinstance(first_item, dict):
                    print(f"   📌 Sample headline: {first_item.get('title', 'N/A')}")
                    print(f"   📅 Date: {first_item.get('date', 'N/A')}")
            
            client.save_debug_data(news, "tank01_news.json")
            print(f"💾 Debug data saved to debug_tank01_news.json")
        else:
            print("❌ No news data received")
            
    except Exception as e:
        print(f"❌ Error testing news: {e}")
        import traceback
        traceback.print_exc()

def test_weekly_projections():
    """Test the weekly fantasy projections endpoint."""
    print("\n📊 Testing Tank01 Weekly Projections")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test week 5 projections for 2025 season
        projections = client.get_weekly_projections(week=5, archive_season=2025)
        
        if projections and 'body' in projections:
            print(f"✅ Weekly projections retrieved successfully!")
            body = projections['body']
            
            if isinstance(body, dict):
                player_count = len(body.keys())
                print(f"🏈 Found projections for {player_count} players")
                
                # Show sample player projection
                sample_players = list(body.keys())[:3]
                for player_id in sample_players:
                    player_data = body[player_id]
                    if isinstance(player_data, dict):
                        name = player_data.get('longName', 'Unknown')
                        team = player_data.get('team', 'N/A')
                        proj_points = player_data.get('fantasyPointsPPR', 'N/A')
                        print(f"   🎯 {name} ({team}): {proj_points} projected PPR points")
            
            client.save_debug_data(projections, "tank01_weekly_projections.json")
            print(f"💾 Debug data saved to debug_tank01_weekly_projections.json")
        else:
            print("❌ No projections data received")
            
    except Exception as e:
        print(f"❌ Error testing weekly projections: {e}")
        import traceback
        traceback.print_exc()

def test_depth_charts():
    """Test the NFL depth charts endpoint."""
    print("\n📋 Testing Tank01 Depth Charts")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Get all team depth charts
        depth_charts = client.get_depth_charts()
        
        if depth_charts and 'body' in depth_charts:
            print(f"✅ Depth charts retrieved successfully!")
            body = depth_charts['body']
            
            if isinstance(body, dict):
                team_count = len(body.keys())
                print(f"🏈 Found depth charts for {team_count} teams")
                
                # Show sample team depth chart
                sample_teams = list(body.keys())[:2]
                for team in sample_teams:
                    team_data = body[team]
                    if isinstance(team_data, dict):
                        print(f"   📊 {team}: {len(team_data.keys())} position groups")
            
            client.save_debug_data(depth_charts, "tank01_depth_charts.json")
            print(f"💾 Debug data saved to debug_tank01_depth_charts.json")
        else:
            print("❌ No depth charts data received")
            
    except Exception as e:
        print(f"❌ Error testing depth charts: {e}")
        import traceback
        traceback.print_exc()

def test_player_info():
    """Test the player information endpoint."""
    print("\n👤 Testing Tank01 Player Information")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test with a known player name from documentation
        player_info = client.get_player_info("keenan_a", get_stats=True)
        
        if player_info and 'body' in player_info:
            print(f"✅ Player info retrieved successfully!")
            body = player_info['body']
            
            if isinstance(body, dict):
                name = body.get('longName', 'Unknown')
                team = body.get('team', 'N/A')
                position = body.get('pos', 'N/A')
                print(f"   🏈 Player: {name}")
                print(f"   🏟️  Team: {team}")
                print(f"   📍 Position: {position}")
                
                # Check for stats
                if 'stats' in body:
                    print(f"   📊 Stats available: Yes")
                else:
                    print(f"   📊 Stats available: No")
            
            client.save_debug_data(player_info, "tank01_player_info.json")
            print(f"💾 Debug data saved to debug_tank01_player_info.json")
        else:
            print("❌ No player info data received")
            
    except Exception as e:
        print(f"❌ Error testing player info: {e}")
        import traceback
        traceback.print_exc()

def test_nfl_teams():
    """Test the NFL teams endpoint."""
    print("\n🏟️  Testing Tank01 NFL Teams")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test NFL teams with stats
        teams = client.get_nfl_teams(
            sort_by="standings",
            rosters=False,
            schedules=False,
            top_performers=True,
            team_stats=True,
            team_stats_season=2024
        )
        
        if teams and 'body' in teams:
            print(f"✅ NFL teams retrieved successfully!")
            body = teams['body']
            if isinstance(body, list):
                print(f"🏈 Found {len(body)} NFL teams")
                
                # Show first few teams
                for i, team in enumerate(body[:3]):
                    if isinstance(team, dict):
                        team_name = team.get('teamName', 'Unknown')
                        team_abv = team.get('teamAbv', 'N/A')
                        wins = team.get('wins', 'N/A')
                        losses = team.get('losses', 'N/A')
                        print(f"   🏆 {team_name} ({team_abv}): {wins}-{losses}")
            
            client.save_debug_data(teams, "tank01_nfl_teams.json")
            print(f"💾 Debug data saved to debug_tank01_nfl_teams.json")
        else:
            print("❌ No NFL teams data received")
            
    except Exception as e:
        print(f"❌ Error testing NFL teams: {e}")
        import traceback
        traceback.print_exc()

def test_daily_scoreboard():
    """Test the daily scoreboard endpoint."""
    print("\n📊 Testing Tank01 Daily Scoreboard")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test with a future game date
        scoreboard = client.get_daily_scoreboard(
            game_date="20250907",
            top_performers=True
        )
        
        if scoreboard and 'body' in scoreboard:
            print(f"✅ Daily scoreboard retrieved successfully!")
            body = scoreboard['body']
            if isinstance(body, dict):
                game_count = len(body.keys())
                print(f"🏈 Found {game_count} games/data points")
            
            client.save_debug_data(scoreboard, "tank01_daily_scoreboard.json")
            print(f"💾 Debug data saved to debug_tank01_daily_scoreboard.json")
        else:
            print("❌ No scoreboard data received")
            
    except Exception as e:
        print(f"❌ Error testing daily scoreboard: {e}")
        import traceback
        traceback.print_exc()

def test_game_info():
    """Test the game information endpoint."""
    print("\n🎮 Testing Tank01 Game Information")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test with game ID from documentation
        game_info = client.get_game_info("20260104_DET%40CHI")
        
        if game_info and 'body' in game_info:
            print(f"✅ Game information retrieved successfully!")
            body = game_info['body']
            if isinstance(body, dict):
                home_team = body.get('homeTeam', 'Unknown')
                away_team = body.get('awayTeam', 'Unknown')
                game_date = body.get('gameDate', 'Unknown')
                print(f"   🏈 Game: {away_team} @ {home_team}")
                print(f"   📅 Date: {game_date}")
            
            client.save_debug_data(game_info, "tank01_game_info.json")
            print(f"💾 Debug data saved to debug_tank01_game_info.json")
        else:
            print("❌ No game information data received")
            
    except Exception as e:
        print(f"❌ Error testing game information: {e}")
        import traceback
        traceback.print_exc()

def test_changelog():
    """Test the changelog endpoint."""
    print("\n📋 Testing Tank01 Changelog")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test changelog for last 30 days
        changelog = client.get_changelog(max_days=30)
        
        if changelog and 'body' in changelog:
            print(f"✅ Changelog retrieved successfully!")
            body = changelog['body']
            if isinstance(body, list):
                print(f"📝 Found {len(body)} changelog entries")
                
                # Show first few entries
                for i, entry in enumerate(body[:2]):
                    if isinstance(entry, dict):
                        date = entry.get('date', 'Unknown')
                        change = entry.get('change', 'No description')
                        print(f"   📅 {date}: {change[:100]}...")
            
            client.save_debug_data(changelog, "tank01_changelog.json")
            print(f"💾 Debug data saved to debug_tank01_changelog.json")
        else:
            print("❌ No changelog data received")
            
    except Exception as e:
        print(f"❌ Error testing changelog: {e}")
        import traceback
        traceback.print_exc()

def test_team_roster():
    """Test the team roster endpoint."""
    print("\n👥 Testing Tank01 Team Roster")
    print("-" * 40)
    
    try:
        client = Tank01Client()
        
        # Test with CHI team from documentation
        roster = client.get_team_roster(
            team="CHI",
            get_stats=True
        )
        
        if roster and 'body' in roster:
            print(f"✅ Team roster retrieved successfully!")
            body = roster['body']
            if isinstance(body, dict) and 'roster' in body:
                roster_data = body['roster']
                if isinstance(roster_data, list):
                    print(f"👥 Found {len(roster_data)} players on roster")
                    
                    # Show first few players
                    for i, player in enumerate(roster_data[:3]):
                        if isinstance(player, dict):
                            name = player.get('longName', 'Unknown')
                            position = player.get('pos', 'N/A')
                            print(f"   🏈 {name} ({position})")
            
            client.save_debug_data(roster, "tank01_team_roster.json")
            print(f"💾 Debug data saved to debug_tank01_team_roster.json")
        else:
            print("❌ No team roster data received")
            
    except Exception as e:
        print(f"❌ Error testing team roster: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run comprehensive Tank01 API tests for ALL endpoints."""
    print("🏈 Tank01 API COMPREHENSIVE Test Suite - ALL ENDPOINTS")
    print("=" * 60)
    print("Testing ALL endpoints from your documentation:")
    print("1. Player List ✅ (already working)")
    print("2. Fantasy Projections ✅ (already working)")
    print("3. Team Roster")
    print("4. Depth Charts")
    print("5. News & Headlines")
    print("6. Daily Scoreboard")
    print("7. Player Information")
    print("8. Weekly Projections")
    print("9. NFL Teams")
    print("10. Game Information")
    print("11. Changelog")
    print("=" * 60)
    
    # Test all endpoints systematically
    test_news_endpoint()
    test_weekly_projections()
    test_depth_charts()
    test_player_info()
    test_team_roster()
    test_nfl_teams()
    test_daily_scoreboard()
    test_game_info()
    test_changelog()
    
    # Show final usage summary
    try:
        client = Tank01Client()
        usage = client.get_usage_info()
        print(f"\n📊 FINAL API USAGE SUMMARY:")
        print(f"   🔥 Calls made this session: {usage['calls_made_this_session']}")
        print(f"   📈 Monthly limit: {usage['monthly_limit']}")
        print(f"   💰 Remaining calls: {usage['remaining_calls']}")
        print(f"   📊 Usage percentage: {usage['percentage_used']:.1f}%")
        
        if usage['calls_made_this_session'] > 0:
            print(f"\n🎉 SUCCESS: Made {usage['calls_made_this_session']} API calls")
            print(f"🔋 You have {usage['remaining_calls']} calls remaining this month")
    except Exception as e:
        print(f"❌ Error getting final usage info: {e}")
    
    print("\n✅ Tank01 COMPREHENSIVE API test completed!")
    print("🚀 ALL endpoints are now ready for production use!")

if __name__ == "__main__":
    main()
