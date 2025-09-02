# Yahoo Fantasy Sports API - Roster Management Research

## Overview

This document provides comprehensive research on Yahoo Fantasy Sports API capabilities for roster management, specifically focusing on:
1. **Changing Player Positions** on the roster
2. **Add/Drop Transactions** for player acquisitions

**⚠️ CRITICAL**: This is research and documentation only. No implementation should be attempted without thorough testing in a controlled environment.

---

## 1. ROSTER POSITION CHANGES

### **API Endpoint**
```
PUT https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}/roster
```

### **Purpose**
- Move players between starting positions and bench
- Change eligible players to different positions (e.g., WR to FLEX)
- Optimize lineup for specific weeks/dates

### **Request Format**

#### **For NFL (Weekly Updates)**
```xml
<?xml version="1.0"?>
<fantasy_content>
  <roster>
    <coverage_type>week</coverage_type>
    <week>13</week>
    <players>
      <player>
        <player_key>242.p.8332</player_key>
        <position>WR</position>
      </player>
      <player>
        <player_key>242.p.1423</player_key>
        <position>BN</position>
      </player>
    </players>
  </roster>
</fantasy_content>
```

#### **For MLB/NBA/NHL (Daily Updates)**
```xml
<?xml version="1.0"?>
<fantasy_content>
  <roster>
    <coverage_type>date</coverage_type>
    <date>2025-09-02</date>
    <players>
      <player>
        <player_key>253.p.8332</player_key>
        <position>1B</position>
      </player>
      <player>
        <player_key>253.p.1423</player_key>
        <position>BN</position>
      </player>
    </players>
  </roster>
</fantasy_content>
```

### **Key Parameters**
- **`coverage_type`**: `"week"` for NFL, `"date"` for other sports
- **`week`**: Week number (NFL only)
- **`date`**: Date in YYYY-MM-DD format (MLB/NBA/NHL only)
- **`player_key`**: Full Yahoo player key (e.g., `"242.p.8332"`)
- **`position`**: Target position (e.g., `"WR"`, `"BN"`, `"FLEX"`)

### **Position Values**
- **Starting Positions**: `QB`, `RB`, `WR`, `TE`, `K`, `DEF`
- **Flex Positions**: `FLEX`, `W/R/T` (if league allows)
- **Bench**: `BN`
- **Injured Reserve**: `IR` (if league allows)

### **Response Handling**
- **Success**: Returns updated roster data
- **Error**: Returns error message if invalid move attempted
- **Validation**: API validates all position changes against league rules

### **Critical Considerations**
1. **Partial Updates**: Only include players you want to move
2. **Valid Positions**: Must be in player's `eligible_positions`
3. **League Rules**: Must comply with roster constraints
4. **Timing**: Changes must be made before game start times
5. **Error Handling**: Invalid moves result in no changes

---

## 2. ADD/DROP TRANSACTIONS

### **API Endpoint**
```
PUT https://fantasysports.yahooapis.com/fantasy/v2/transaction
```

### **Purpose**
- Add free agents to roster
- Drop players from roster
- Execute add/drop in single transaction (required when roster is full)

### **Request Format**

#### **Add/Drop Transaction XML**
```xml
<?xml version="1.0"?>
<fantasy_content>
  <transaction>
    <type>add/drop</type>
    <players>
      <player>
        <player_key>257.p.7847</player_key>
        <transaction_data>
          <type>add</type>
          <source_type>freeagents</source_type>
          <destination_type>team</destination_type>
          <destination_team_key>257.l.193.t.1</destination_team_key>
        </transaction_data>
      </player>
      <player>
        <player_key>257.p.6390</player_key>
        <transaction_data>
          <type>drop</type>
          <source_type>team</source_type>
          <source_team_key>257.l.193.t.1</source_team_key>
          <destination_type>waivers</destination_type>
        </transaction_data>
      </player>
    </players>
  </transaction>
</fantasy_content>
```

### **Transaction Data Parameters**

#### **For ADD Operations**
- **`type`**: `"add"`
- **`source_type`**: `"freeagents"` (for free agents)
- **`destination_type`**: `"team"`
- **`destination_team_key`**: Your team key (e.g., `"257.l.193.t.1"`)

#### **For DROP Operations**
- **`type`**: `"drop"`
- **`source_type`**: `"team"`
- **`source_team_key`**: Your team key
- **`destination_type`**: `"waivers"` (for dropped players)

### **Response Format (Success)**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<fantasy_content xmlns:yahoo="http://www.yahooapis.com/v1/base.rng" 
                 xmlns="http://fantasysports.yahooapis.com/fantasy/v2/base.rng" 
                 xml:lang="en-US" 
                 yahoo:uri="http://fantasysports.yahooapis.com/fantasy/v2/transaction/257.l.193.tr.2" 
                 time="51.784038543701ms" 
                 copyright="Data provided by Yahoo! and STATS, LLC">
  <transaction>
    <transaction_key>257.l.193.tr.2</transaction_key>
    <transaction_id>2</transaction_id>
    <type>add/drop</type>
    <status>successful</status>
    <timestamp>1310694660</timestamp>
    <players count="2">
      <player>
        <player_key>257.p.7847</player_key>
        <player_id>7847</player_id>
        <name>
          <full>Owen Daniels</full>
          <first>Owen</first>
          <last>Daniels</last>
          <ascii_first>Owen</ascii_first>
          <ascii_last>Daniels</ascii_last>
        </name>
        <transaction_data>
          <type>add</type>
          <source_type>freeagents</source_type>
          <destination_type>team</destination_type>
          <destination_team_key>257.l.193.t.1</destination_team_key>
        </transaction_data>
      </player>
      <player>
        <player_key>257.p.6390</player_key>
        <player_id>6390</player_id>
        <name>
          <full>Anquan Boldin</full>
          <first>Anquan</first>
          <last>Boldin</last>
          <ascii_first>Anquan</ascii_first>
          <ascii_last>Boldin</ascii_last>
        </name>
        <transaction_data>
          <type>drop</type>
          <source_type>team</source_type>
          <source_team_key>257.l.193.t.1</source_team_key>
          <destination_type>waivers</destination_type>
        </transaction_data>
      </player>
    </players>
  </transaction>
</fantasy_content>
```

### **Response Data Points**
- **`transaction_key`**: Unique transaction identifier
- **`transaction_id`**: Numeric transaction ID
- **`type`**: Transaction type (`"add/drop"`)
- **`status`**: Transaction status (`"successful"`, `"failed"`, etc.)
- **`timestamp`**: Unix timestamp of transaction
- **`players`**: Array of players involved in transaction

### **Critical Considerations for Add/Drop**

#### **⚠️ CATASTROPHIC ERROR PREVENTION**
1. **Roster Full Check**: If roster is full, add/drop must be in same transaction
2. **Player Validation**: Verify player_key exists and is available
3. **Team Key Validation**: Ensure destination_team_key is correct
4. **Transaction Atomicity**: Either both add and drop succeed, or both fail
5. **Waiver Periods**: Dropped players may go to waivers, not free agents

#### **Error Scenarios**
- **Invalid Player**: Player not found or not available
- **Roster Full**: Cannot add without dropping (must be same transaction)
- **Waiver Period**: Player on waivers, not free agents
- **League Rules**: Transaction violates league settings
- **Timing**: Transaction outside allowed time window

#### **Response Validation**
- **Check `status`**: Must be `"successful"`
- **Verify `transaction_key`**: Should be returned for successful transactions
- **Count Players**: Should match expected number of players
- **Validate Names**: Confirm correct players were added/dropped

---

## 3. IMPLEMENTATION CONSIDERATIONS

### **Authentication Requirements**
- **OAuth 2.0**: Required for all PUT operations
- **Scopes**: `fspt-w` (Fantasy Sports read/write)
- **Rate Limits**: Monitor API usage to avoid throttling

### **Error Handling Strategy**
1. **Pre-validation**: Check all parameters before API call
2. **Response Parsing**: Parse XML response for success/error status
3. **Rollback Planning**: Have strategy for failed transactions
4. **Logging**: Log all transactions for audit trail

### **Testing Strategy**
1. **Sandbox Environment**: Test with non-production data
2. **Small Changes**: Start with minor position changes
3. **Validation**: Verify changes in Yahoo interface
4. **Edge Cases**: Test error scenarios

### **Data Tracking Requirements**
- **Transaction Log**: Record all attempted transactions
- **Response Data**: Store complete API responses
- **Error Logs**: Track failed attempts with reasons
- **Audit Trail**: Maintain history of all roster changes

---

## 4. PYTHON LIBRARY ALTERNATIVES

### **yahoo_fantasy_api Library**
```python
from yahoo_fantasy_api import Team

# Position changes
team.change_positions(time_frame, modified_lineup)

# Add/drop transactions
team.add_player(player_key)
team.drop_player(player_key)
```

### **Advantages of Library**
- **Simplified API**: Abstracts XML complexity
- **Error Handling**: Built-in validation
- **Type Safety**: Python objects instead of XML

### **Disadvantages of Library**
- **Less Control**: Limited customization
- **Dependency**: Additional library requirement
- **Updates**: May lag behind API changes

---

## 5. RECOMMENDED IMPLEMENTATION APPROACH

### **Phase 1: Research & Validation**
1. **API Testing**: Test endpoints with minimal changes
2. **Response Analysis**: Understand all response formats
3. **Error Scenarios**: Document all possible error conditions
4. **League Rules**: Understand specific league constraints

### **Phase 2: Safe Implementation**
1. **Position Changes**: Start with bench/starting swaps
2. **Validation**: Implement comprehensive pre-checks
3. **Logging**: Add detailed transaction logging
4. **Testing**: Extensive testing with small changes

### **Phase 3: Add/Drop Implementation**
1. **Roster Analysis**: Check roster status before transactions
2. **Atomic Transactions**: Ensure add/drop in single request
3. **Response Validation**: Verify successful completion
4. **Error Recovery**: Handle failed transactions gracefully

---

## 6. CRITICAL WARNINGS

### **⚠️ DO NOT IMPLEMENT WITHOUT:**
1. **Thorough Testing**: Test all scenarios in controlled environment
2. **Error Handling**: Comprehensive error handling and recovery
3. **Validation**: Pre-transaction validation of all parameters
4. **Logging**: Complete audit trail of all operations
5. **Backup Strategy**: Plan for failed transactions

### **⚠️ CATASTROPHIC RISKS:**
1. **Wrong Player**: Adding/dropping wrong player
2. **Roster Violations**: Creating invalid roster configurations
3. **Transaction Failures**: Partial transactions leaving roster in bad state
4. **Rate Limiting**: Exceeding API limits and losing access
5. **League Violations**: Breaking league rules and penalties

---

**Status**: Research Complete - Ready for Implementation Planning
**Next Steps**: Create implementation plan with safety measures
**Last Updated**: September 1, 2025
