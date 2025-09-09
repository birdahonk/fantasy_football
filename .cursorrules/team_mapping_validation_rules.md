# Team Mapping & Validation Rules

## Critical Team Mapping Requirements

**⚠️ ALWAYS USE TEAM MAPPING SYSTEM** - Never hardcode team abbreviations or assume they match between APIs.

### Team Mapping Rules:
1. **ALWAYS import and use `team_mapping.py`** for any team-related operations
2. **NEVER hardcode team abbreviations** - they differ between Yahoo, Sleeper, and Tank01 APIs
3. **ALWAYS normalize team abbreviations** using `normalize_team_abbreviation(team, source_api)`
4. **ALWAYS handle None values** when extracting team data
5. **ALWAYS use `editorial_team_abbr`** for Yahoo team extraction, not `team` field

### Required Team Extraction Patterns:
```python
# Yahoo API - CORRECT
yahoo_team = yahoo_player.get('editorial_team_abbr') or yahoo_player.get('team', 'N/A')
normalized_team = normalize_team_abbreviation(yahoo_team, 'yahoo')

# Sleeper API - CORRECT  
sleeper_team_raw = sleeper_player.get('team')
sleeper_team = normalize_team_abbreviation(sleeper_team_raw, 'sleeper') if sleeper_team_raw else ''

# Tank01 API - CORRECT
tank01_team_raw = tank01_player.get('team')
tank01_team = normalize_team_abbreviation(tank01_team_raw, 'tank01') if tank01_team_raw else ''
```

### Documentation Reference:
- **Team Mapping Guide**: `data_collection/schemas/TEAM_MAPPING_GUIDE.md`
- **Team Mapping Script**: `data_collection/scripts/shared/team_mapping.py`

## Data Collection Script Requirements

### 100% Accuracy Requirements:
1. **Yahoo scripts**: Must collect ALL players from roster/opponent/available
2. **Sleeper scripts**: Must match and enrich EVERY player from Yahoo data (0 unmatched)
3. **Tank01 scripts**: Must match and enrich EVERY player from Yahoo data (0 unmatched)
4. **Final output**: Must have 100% enrichment with NO missing data

### Validation Requirements:
- **ALWAYS run validation** after making changes to data collection scripts
- **NEVER commit** code that fails validation
- **ALWAYS check** for unmatched players in Sleeper/Tank01 outputs

### Validation Commands:
```bash
# Run all validations
python3 validate_all_data.py

# Run individual validations
python3 data_collection/scripts/validation/script_health_check.py
python3 data_collection/scripts/validation/comprehensive_data_validator.py
```

## Code Quality Standards

### Error Handling:
- **ALWAYS handle None values** when extracting data
- **ALWAYS use try/catch** for API calls
- **ALWAYS log errors** with descriptive messages
- **NEVER assume** data fields exist

### Team Matching Logic:
- **ALWAYS normalize** both Yahoo and target API team abbreviations
- **ALWAYS compare** normalized team abbreviations
- **ALWAYS handle** defense team special cases
- **NEVER assume** team abbreviations match directly

### Data Structure Requirements:
- **ALWAYS use** YYYY/MM/DD directory structure for outputs
- **ALWAYS include** both raw JSON and clean markdown outputs
- **ALWAYS include** execution logs with timing and error counts
- **ALWAYS validate** output file structure before proceeding

## Common Pitfalls to Avoid

### ❌ WRONG - Hardcoded Team Checks:
```python
if yahoo_team == "Cin" and sleeper_team == "CIN":  # Will fail!
```

### ❌ WRONG - Direct Field Matching:
```python
if yahoo_player.get('team') == sleeper_player.get('team'):  # Will fail!
```

### ❌ WRONG - Not Handling None Values:
```python
team = yahoo_player.get('team').upper()  # Crashes if None
```

### ✅ CORRECT - Using Team Mapping:
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

## File Organization

### Data Collection Scripts:
- **Yahoo**: `data_collection/scripts/yahoo/`
- **Sleeper**: `data_collection/scripts/sleeper/`
- **Tank01**: `data_collection/scripts/tank01/`
- **Shared**: `data_collection/scripts/shared/`

### Validation Scripts:
- **Health Check**: `data_collection/scripts/validation/script_health_check.py`
- **Data Validator**: `data_collection/scripts/validation/comprehensive_data_validator.py`
- **Master Validator**: `validate_all_data.py`

### Documentation:
- **Team Mapping**: `data_collection/schemas/TEAM_MAPPING_GUIDE.md`
- **API Schemas**: `data_collection/schemas/`

## Testing Requirements

### Before Committing:
1. **Run all validations**: `python3 validate_all_data.py`
2. **Check for unmatched players**: All Sleeper/Tank01 scripts must show 0 unmatched
3. **Verify enrichment**: All players must have both Tank01 and Sleeper data
4. **Test team matching**: Verify defense teams match correctly

### Validation Success Criteria:
- ✅ All 14 data collection scripts pass health check
- ✅ 0 unmatched players in Sleeper/Tank01 outputs
- ✅ 100% enrichment rate for all player data
- ✅ All team abbreviations properly normalized
- ✅ No missing or null enrichment data

---

**Remember**: Team mapping failures are the #1 cause of player matching issues. Always use the team mapping system!
