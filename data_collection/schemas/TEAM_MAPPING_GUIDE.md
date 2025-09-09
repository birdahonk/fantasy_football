# Team Mapping System Guide

## Overview

The `team_mapping.py` script provides comprehensive NFL team abbreviation mapping between different APIs to ensure 100% accuracy in player matching across Yahoo Fantasy, Sleeper, and Tank01 APIs.

## Critical Importance

**⚠️ ALWAYS USE THIS SCRIPT** - Never hardcode team abbreviations or assume they match between APIs. This is the #1 cause of player matching failures.

## Quick Reference

### Import and Usage
```python
from team_mapping import normalize_team_abbreviation, get_team_abbreviation_for_api

# Normalize team from any API to standard format
standard_team = normalize_team_abbreviation("Cin", 'yahoo')  # Returns "CIN"
standard_team = normalize_team_abbreviation("CIN", 'sleeper')  # Returns "CIN"

# Get team abbreviation for specific API
yahoo_team = get_team_abbreviation_for_api("CIN", 'yahoo')  # Returns "Cin"
sleeper_team = get_team_abbreviation_for_api("CIN", 'sleeper')  # Returns "CIN"
```

### Common Team Mappings

| Standard | Yahoo | Sleeper | Tank01 | Team Name |
|----------|-------|---------|--------|-----------|
| CIN | Cin | CIN | CIN | Cincinnati Bengals |
| WAS | Was | WAS | WSH | Washington Commanders |
| LAC | LAC | LAC | LAC | Los Angeles Chargers |
| LAR | LAR | LAR | LAR | Los Angeles Rams |
| SF | SF | SF | SF | San Francisco 49ers |
| SEA | Sea | SEA | SEA | Seattle Seahawks |

## API-Specific Team Extraction

### Yahoo Fantasy API
```python
# CORRECT: Extract from editorial_team_abbr
team = yahoo_player.get('editorial_team_abbr') or yahoo_player.get('team', 'N/A')
normalized_team = normalize_team_abbreviation(team, 'yahoo')

# WRONG: Don't use just 'team' field
team = yahoo_player.get('team')  # Often returns None
```

### Sleeper API
```python
# CORRECT: Extract and normalize
sleeper_team_raw = sleeper_player.get('team')
sleeper_team = normalize_team_abbreviation(sleeper_team_raw, 'sleeper') if sleeper_team_raw else ''

# WRONG: Don't assume team abbreviations match
if yahoo_team == sleeper_team:  # This will fail!
```

### Tank01 API
```python
# CORRECT: Extract and normalize
tank01_team_raw = tank01_player.get('team')
tank01_team = normalize_team_abbreviation(tank01_team_raw, 'tank01') if tank01_team_raw else ''
```

## Validation Rules

### Required Team Extraction Patterns
1. **Yahoo**: Always check `editorial_team_abbr` first, fallback to `team`
2. **Sleeper**: Use `team` field, normalize with `'sleeper'` source
3. **Tank01**: Use `team` field, normalize with `'tank01'` source

### Team Matching Logic
```python
def match_players_by_team(yahoo_player, sleeper_player, tank01_player):
    # Extract teams
    yahoo_team = normalize_team_abbreviation(
        yahoo_player.get('editorial_team_abbr') or yahoo_player.get('team', 'N/A'), 
        'yahoo'
    )
    sleeper_team = normalize_team_abbreviation(
        sleeper_player.get('team', ''), 
        'sleeper'
    )
    tank01_team = normalize_team_abbreviation(
        tank01_player.get('team', ''), 
        'tank01'
    )
    
    # All should match the same standard team
    return yahoo_team == sleeper_team == tank01_team
```

## Common Pitfalls

### ❌ WRONG - Hardcoded Team Checks
```python
if yahoo_team == "Cin" and sleeper_team == "CIN":  # Will fail!
```

### ❌ WRONG - Assuming Direct Field Matching
```python
if yahoo_player.get('team') == sleeper_player.get('team'):  # Will fail!
```

### ❌ WRONG - Not Handling None Values
```python
team = yahoo_player.get('team').upper()  # Crashes if None
```

### ✅ CORRECT - Using Team Mapping
```python
yahoo_team = normalize_team_abbreviation(
    yahoo_player.get('editorial_team_abbr') or yahoo_player.get('team', 'N/A'), 
    'yahoo'
)
sleeper_team = normalize_team_abbreviation(
    sleeper_player.get('team', ''), 
    'sleeper'
)
if yahoo_team == sleeper_team and yahoo_team != 'N/A':
    # Match found!
```

## Defense Team Special Cases

Defense teams have special handling:
- **Sleeper**: Uses team abbreviations (e.g., "LAR", "LAC")
- **Yahoo**: Uses full team names (e.g., "Los Angeles", "Los Angeles")
- **Tank01**: Uses team abbreviations (e.g., "LAR", "LAC")

```python
# Defense matching example
def match_defense_teams(yahoo_defense, sleeper_defense):
    yahoo_team = normalize_team_abbreviation(yahoo_defense.get('editorial_team_abbr', ''), 'yahoo')
    sleeper_team = normalize_team_abbreviation(sleeper_defense.get('team', ''), 'sleeper')
    return yahoo_team == sleeper_team
```

## Testing Team Mappings

Use the built-in validation:
```python
from team_mapping import validate_team_mapping

validation = validate_team_mapping()
print(f"Total teams: {validation['total_teams']}")
print(f"Missing mappings: {validation['missing_yahoo']}")
```

## Integration Checklist

When working with team data:

- [ ] Import `team_mapping` module
- [ ] Use `normalize_team_abbreviation()` for all team extractions
- [ ] Specify correct source API ('yahoo', 'sleeper', 'tank01')
- [ ] Handle None values gracefully
- [ ] Test with defense teams specifically
- [ ] Validate team matches before proceeding

## File Location
`data_collection/scripts/shared/team_mapping.py`

---

**Remember**: Team mapping failures are the #1 cause of player matching issues. Always use this system!
