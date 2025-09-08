#!/usr/bin/env python3
"""
Comprehensive NFL Team Mapping Utility

This module provides comprehensive team abbreviation mapping between different APIs:
- Yahoo Fantasy API
- Sleeper API  
- Tank01 API

Based on actual data analysis from all three APIs to ensure 100% accuracy.
"""

# Comprehensive team mapping based on actual API data analysis
TEAM_MAPPING = {
    # Standard team abbreviations (used by Sleeper and Tank01)
    'ARI': {'yahoo': 'Ari', 'sleeper': 'ARI', 'tank01': 'ARI', 'team_id': '1'},
    'ATL': {'yahoo': 'Atl', 'sleeper': 'ATL', 'tank01': 'ATL', 'team_id': '2'},
    'BAL': {'yahoo': 'Bal', 'sleeper': 'BAL', 'tank01': 'BAL', 'team_id': '3'},
    'BUF': {'yahoo': 'Buf', 'sleeper': 'BUF', 'tank01': 'BUF', 'team_id': '4'},
    'CAR': {'yahoo': 'Car', 'sleeper': 'CAR', 'tank01': 'CAR', 'team_id': '5'},
    'CHI': {'yahoo': 'Chi', 'sleeper': 'CHI', 'tank01': 'CHI', 'team_id': '6'},
    'CIN': {'yahoo': 'Cin', 'sleeper': 'CIN', 'tank01': 'CIN', 'team_id': '7'},
    'CLE': {'yahoo': 'Cle', 'sleeper': 'CLE', 'tank01': 'CLE', 'team_id': '8'},
    'DAL': {'yahoo': 'Dal', 'sleeper': 'DAL', 'tank01': 'DAL', 'team_id': '9'},
    'DEN': {'yahoo': 'Den', 'sleeper': 'DEN', 'tank01': 'DEN', 'team_id': '10'},
    'DET': {'yahoo': 'Det', 'sleeper': 'DET', 'tank01': 'DET', 'team_id': '11'},
    'GB': {'yahoo': 'GB', 'sleeper': 'GB', 'tank01': 'GB', 'team_id': '12'},
    'HOU': {'yahoo': 'Hou', 'sleeper': 'HOU', 'tank01': 'HOU', 'team_id': '13'},
    'IND': {'yahoo': 'Ind', 'sleeper': 'IND', 'tank01': 'IND', 'team_id': '14'},
    'JAX': {'yahoo': 'Jax', 'sleeper': 'JAX', 'tank01': 'JAX', 'team_id': '15'},
    'KC': {'yahoo': 'KC', 'sleeper': 'KC', 'tank01': 'KC', 'team_id': '16'},
    'LV': {'yahoo': 'LV', 'sleeper': 'LV', 'tank01': 'LV', 'team_id': '17'},
    'LAC': {'yahoo': 'LAC', 'sleeper': 'LAC', 'tank01': 'LAC', 'team_id': '18'},
    'LAR': {'yahoo': 'LAR', 'sleeper': 'LAR', 'tank01': 'LAR', 'team_id': '19'},
    'MIA': {'yahoo': 'Mia', 'sleeper': 'MIA', 'tank01': 'MIA', 'team_id': '20'},
    'MIN': {'yahoo': 'Min', 'sleeper': 'MIN', 'tank01': 'MIN', 'team_id': '21'},
    'NE': {'yahoo': 'NE', 'sleeper': 'NE', 'tank01': 'NE', 'team_id': '22'},
    'NO': {'yahoo': 'NO', 'sleeper': 'NO', 'tank01': 'NO', 'team_id': '23'},
    'NYG': {'yahoo': 'NYG', 'sleeper': 'NYG', 'tank01': 'NYG', 'team_id': '24'},
    'NYJ': {'yahoo': 'NYJ', 'sleeper': 'NYJ', 'tank01': 'NYJ', 'team_id': '25'},
    'PHI': {'yahoo': 'Phi', 'sleeper': 'PHI', 'tank01': 'PHI', 'team_id': '27'},
    'PIT': {'yahoo': 'Pit', 'sleeper': 'PIT', 'tank01': 'PIT', 'team_id': '26'},
    'SF': {'yahoo': 'SF', 'sleeper': 'SF', 'tank01': 'SF', 'team_id': '28'},
    'SEA': {'yahoo': 'Sea', 'sleeper': 'SEA', 'tank01': 'SEA', 'team_id': '29'},
    'TB': {'yahoo': 'TB', 'sleeper': 'TB', 'tank01': 'TB', 'team_id': '30'},
    'TEN': {'yahoo': 'Ten', 'sleeper': 'TEN', 'tank01': 'TEN', 'team_id': '31'},
    'WAS': {'yahoo': 'Was', 'sleeper': 'WAS', 'tank01': 'WSH', 'team_id': '32'},
}

# Reverse mappings for quick lookup
YAHOO_TO_STANDARD = {data['yahoo']: team for team, data in TEAM_MAPPING.items()}
SLEEPER_TO_STANDARD = {data['sleeper']: team for team, data in TEAM_MAPPING.items()}
TANK01_TO_STANDARD = {data['tank01']: team for team, data in TEAM_MAPPING.items()}

# Team ID mappings
TEAM_ID_TO_STANDARD = {data['team_id']: team for team, data in TEAM_MAPPING.items()}
STANDARD_TO_TEAM_ID = {team: data['team_id'] for team, data in TEAM_MAPPING.items()}

def normalize_team_abbreviation(team_abbr: str, source_api: str = 'yahoo') -> str:
    """
    Normalize team abbreviation to standard format.
    
    Args:
        team_abbr: Team abbreviation from source API
        source_api: Source API ('yahoo', 'sleeper', 'tank01')
        
    Returns:
        Standard team abbreviation (e.g., 'CIN', 'WAS', 'PHI')
    """
    if not team_abbr:
        return team_abbr
    
    team_abbr = team_abbr.strip()
    
    if source_api == 'yahoo':
        return YAHOO_TO_STANDARD.get(team_abbr, team_abbr.upper())
    elif source_api == 'sleeper':
        return SLEEPER_TO_STANDARD.get(team_abbr, team_abbr.upper())
    elif source_api == 'tank01':
        return TANK01_TO_STANDARD.get(team_abbr, team_abbr.upper())
    else:
        return team_abbr.upper()

def get_team_abbreviation_for_api(standard_team: str, target_api: str) -> str:
    """
    Get team abbreviation for specific API.
    
    Args:
        standard_team: Standard team abbreviation (e.g., 'CIN', 'WAS')
        target_api: Target API ('yahoo', 'sleeper', 'tank01')
        
    Returns:
        Team abbreviation for target API
    """
    if standard_team not in TEAM_MAPPING:
        return standard_team
    
    return TEAM_MAPPING[standard_team][target_api]

def get_team_id(team_abbr: str, source_api: str = 'yahoo') -> str:
    """
    Get Tank01 team ID for team abbreviation.
    
    Args:
        team_abbr: Team abbreviation from source API
        source_api: Source API ('yahoo', 'sleeper', 'tank01')
        
    Returns:
        Tank01 team ID
    """
    standard_team = normalize_team_abbreviation(team_abbr, source_api)
    return STANDARD_TO_TEAM_ID.get(standard_team, '')

def get_team_name(team_abbr: str, source_api: str = 'yahoo') -> str:
    """
    Get full team name for team abbreviation.
    
    Args:
        team_abbr: Team abbreviation from source API
        source_api: Source API ('yahoo', 'sleeper', 'tank01')
        
    Returns:
        Full team name
    """
    team_names = {
        'ARI': 'Arizona Cardinals',
        'ATL': 'Atlanta Falcons', 
        'BAL': 'Baltimore Ravens',
        'BUF': 'Buffalo Bills',
        'CAR': 'Carolina Panthers',
        'CHI': 'Chicago Bears',
        'CIN': 'Cincinnati Bengals',
        'CLE': 'Cleveland Browns',
        'DAL': 'Dallas Cowboys',
        'DEN': 'Denver Broncos',
        'DET': 'Detroit Lions',
        'GB': 'Green Bay Packers',
        'HOU': 'Houston Texans',
        'IND': 'Indianapolis Colts',
        'JAX': 'Jacksonville Jaguars',
        'KC': 'Kansas City Chiefs',
        'LV': 'Las Vegas Raiders',
        'LAC': 'Los Angeles Chargers',
        'LAR': 'Los Angeles Rams',
        'MIA': 'Miami Dolphins',
        'MIN': 'Minnesota Vikings',
        'NE': 'New England Patriots',
        'NO': 'New Orleans Saints',
        'NYG': 'New York Giants',
        'NYJ': 'New York Jets',
        'PHI': 'Philadelphia Eagles',
        'PIT': 'Pittsburgh Steelers',
        'SF': 'San Francisco 49ers',
        'SEA': 'Seattle Seahawks',
        'TB': 'Tampa Bay Buccaneers',
        'TEN': 'Tennessee Titans',
        'WAS': 'Washington Commanders',
    }
    
    standard_team = normalize_team_abbreviation(team_abbr, source_api)
    return team_names.get(standard_team, f"{standard_team} Team")

def validate_team_mapping():
    """
    Validate that all team mappings are complete and consistent.
    
    Returns:
        Dict with validation results
    """
    validation_results = {
        'total_teams': len(TEAM_MAPPING),
        'missing_yahoo': [],
        'missing_sleeper': [],
        'missing_tank01': [],
        'missing_team_ids': [],
        'inconsistent_mappings': []
    }
    
    for team, data in TEAM_MAPPING.items():
        # Check for missing mappings
        if 'yahoo' not in data:
            validation_results['missing_yahoo'].append(team)
        if 'sleeper' not in data:
            validation_results['missing_sleeper'].append(team)
        if 'tank01' not in data:
            validation_results['missing_tank01'].append(team)
        if 'team_id' not in data:
            validation_results['missing_team_ids'].append(team)
    
    # Check for inconsistencies
    for team, data in TEAM_MAPPING.items():
        if team != data.get('sleeper', '').upper():
            validation_results['inconsistent_mappings'].append(f"{team}: sleeper={data.get('sleeper')}")
        if team != data.get('tank01', '').upper() and team != 'WAS':  # WAS is special case
            validation_results['inconsistent_mappings'].append(f"{team}: tank01={data.get('tank01')}")
    
    return validation_results

def get_all_team_abbreviations():
    """
    Get all team abbreviations used across all APIs.
    
    Returns:
        Dict with lists of abbreviations for each API
    """
    return {
        'yahoo': [data['yahoo'] for data in TEAM_MAPPING.values()],
        'sleeper': [data['sleeper'] for data in TEAM_MAPPING.values()],
        'tank01': [data['tank01'] for data in TEAM_MAPPING.values()],
        'standard': list(TEAM_MAPPING.keys())
    }

if __name__ == "__main__":
    """Test the team mapping utility."""
    print("🏈 NFL Team Mapping Utility Test")
    print("=" * 50)
    
    # Test validation
    validation = validate_team_mapping()
    print(f"Total teams: {validation['total_teams']}")
    print(f"Missing Yahoo mappings: {len(validation['missing_yahoo'])}")
    print(f"Missing Sleeper mappings: {len(validation['missing_sleeper'])}")
    print(f"Missing Tank01 mappings: {len(validation['missing_tank01'])}")
    print(f"Missing team IDs: {len(validation['missing_team_ids'])}")
    print(f"Inconsistent mappings: {len(validation['inconsistent_mappings'])}")
    
    if validation['inconsistent_mappings']:
        print("\nInconsistent mappings:")
        for mapping in validation['inconsistent_mappings']:
            print(f"  - {mapping}")
    
    # Test some conversions
    print("\n🧪 Testing conversions:")
    test_teams = ['Cin', 'Was', 'SF', 'Hou', 'Det']
    
    for team in test_teams:
        standard = normalize_team_abbreviation(team, 'yahoo')
        tank01 = get_team_abbreviation_for_api(standard, 'tank01')
        team_id = get_team_id(team, 'yahoo')
        team_name = get_team_name(team, 'yahoo')
        
        print(f"  {team} (Yahoo) -> {standard} (Standard) -> {tank01} (Tank01) -> ID: {team_id} -> {team_name}")
    
    print("\n✅ Team mapping utility test complete!")
