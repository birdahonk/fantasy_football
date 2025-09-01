#!/usr/bin/env python3
"""
Data Formatting Utilities for Clean Markdown Output

Provides consistent formatting functions for converting raw API data
into clean, organized markdown files for human readability and AI consumption.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class MarkdownFormatter:
    """
    Formats raw API data into clean, organized markdown.
    
    Provides consistent table formatting, section organization,
    and data presentation for all data extraction scripts.
    """
    
    def __init__(self):
        """Initialize the markdown formatter."""
        self.logger = logging.getLogger(__name__)
    
    def create_header(self, title: str, subtitle: str = None, timestamp: str = None) -> str:
        """
        Create a standard header for markdown files.
        
        Args:
            title: Main title
            subtitle: Optional subtitle
            timestamp: Optional timestamp
            
        Returns:
            Formatted markdown header
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"# {title}\n\n"
        
        if subtitle:
            header += f"## {subtitle}\n\n"
        
        header += f"**Generated:** {timestamp}\n\n"
        header += "---\n\n"
        
        return header
    
    def create_section(self, title: str, content: str, level: int = 2) -> str:
        """
        Create a markdown section.
        
        Args:
            title: Section title
            content: Section content
            level: Header level (2-6)
            
        Returns:
            Formatted markdown section
        """
        header_prefix = "#" * level
        return f"{header_prefix} {title}\n\n{content}\n\n"
    
    def format_table(self, headers: List[str], rows: List[List[str]], 
                    caption: str = None) -> str:
        """
        Format data as a markdown table.
        
        Args:
            headers: Table headers
            rows: Table rows (list of lists)
            caption: Optional table caption
            
        Returns:
            Formatted markdown table
        """
        if not headers or not rows:
            return "No data available.\n\n"
        
        # Create table header
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        # Add data rows
        for row in rows:
            # Ensure row has same number of columns as headers
            padded_row = row + [""] * (len(headers) - len(row))
            padded_row = padded_row[:len(headers)]  # Trim if too long
            
            # Clean up any None values or complex objects
            clean_row = []
            for cell in padded_row:
                if cell is None:
                    clean_row.append("")
                elif isinstance(cell, (dict, list)):
                    clean_row.append(str(cell)[:50] + "..." if len(str(cell)) > 50 else str(cell))
                else:
                    clean_row.append(str(cell))
            
            table += "| " + " | ".join(clean_row) + " |\n"
        
        if caption:
            table = f"**{caption}**\n\n{table}"
        
        return table + "\n"
    
    def format_player_list(self, players: List[Dict], title: str = "Players") -> str:
        """
        Format a list of players into a standard table.
        
        Args:
            players: List of player dictionaries
            title: Section title
            
        Returns:
            Formatted markdown table
        """
        if not players:
            return f"## {title}\n\nNo players found.\n\n"
        
        # Define standard player table headers
        headers = ["Name", "Position", "Team", "Player ID", "Status", "Notes"]
        rows = []
        
        for player in players:
            # Extract common player fields with fallbacks
            name = self._extract_player_name(player)
            position = self._extract_field(player, ['position', 'display_position', 'primary_position', 'pos'])
            team = self._extract_field(player, ['team', 'editorial_team_abbr', 'teamABV'])
            player_id = self._extract_field(player, ['player_id', 'playerID', 'player_key'])
            status = self._extract_field(player, ['status', 'injury_status', 'injuryStatus'])
            notes = self._extract_field(player, ['injury_note', 'status_full', 'notes'])
            
            rows.append([name, position, team, player_id, status, notes])
        
        table = self.format_table(headers, rows)
        return self.create_section(title, table)
    
    def format_team_info(self, team: Dict, title: str = "Team Information") -> str:
        """
        Format team information into markdown.
        
        Args:
            team: Team dictionary
            title: Section title
            
        Returns:
            Formatted markdown section
        """
        if not team:
            return f"## {title}\n\nNo team information available.\n\n"
        
        info = []
        
        # Common team fields
        team_fields = [
            ('Team Name', ['name', 'team_name', 'teamName']),
            ('Team Key', ['team_key', 'teamID']),
            ('Manager', ['manager', 'manager_name']),
            ('Waiver Priority', ['waiver_priority']),
            ('FAAB Balance', ['faab_balance']),
            ('Moves Made', ['number_of_moves']),
            ('Trades Made', ['number_of_trades'])
        ]
        
        for label, field_names in team_fields:
            value = self._extract_field(team, field_names)
            if value:
                info.append(f"- **{label}**: {value}")
        
        content = "\n".join(info) if info else "No team information available."
        return self.create_section(title, content)
    
    def format_matchup(self, matchup: Dict, title: str = "Matchup") -> str:
        """
        Format matchup information into markdown.
        
        Args:
            matchup: Matchup dictionary
            title: Section title
            
        Returns:
            Formatted markdown section
        """
        if not matchup:
            return f"## {title}\n\nNo matchup information available.\n\n"
        
        content = []
        
        # Matchup metadata
        week = self._extract_field(matchup, ['week'])
        if week:
            content.append(f"**Week**: {week}")
        
        status = self._extract_field(matchup, ['status'])
        if status:
            content.append(f"**Status**: {status}")
        
        # Teams in matchup
        teams = self._extract_field(matchup, ['teams'])
        if teams and isinstance(teams, list):
            content.append("\n**Teams:**")
            for i, team in enumerate(teams, 1):
                team_name = self._extract_field(team, ['name', 'team_name'])
                projected_points = self._extract_field(team, ['projected_points', 'team_projected_points'])
                if team_name:
                    team_info = f"Team {i}: {team_name}"
                    if projected_points:
                        team_info += f" (Projected: {projected_points} points)"
                    content.append(f"- {team_info}")
        
        content_str = "\n".join(content) if content else "No matchup details available."
        return self.create_section(title, content_str)
    
    def format_json_section(self, data: Dict, title: str = "Raw Data Summary") -> str:
        """
        Format a JSON object as a readable markdown section.
        
        Args:
            data: Dictionary to format
            title: Section title
            
        Returns:
            Formatted markdown section
        """
        if not data:
            return f"## {title}\n\nNo data available.\n\n"
        
        # Create a readable summary without overwhelming detail
        summary = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                summary.append(f"- **{key}**: {len(value)} items")
            elif isinstance(value, list):
                summary.append(f"- **{key}**: {len(value)} items")
            elif isinstance(value, str) and len(value) > 100:
                summary.append(f"- **{key}**: {value[:100]}...")
            else:
                summary.append(f"- **{key}**: {value}")
        
        content = "\n".join(summary)
        return self.create_section(title, content)
    
    def _extract_player_name(self, player: Dict) -> str:
        """Extract player name from various possible formats."""
        # Try different name field structures
        if 'name' in player and isinstance(player['name'], dict):
            full_name = player['name'].get('full')
            if full_name:
                return full_name
            
            first = player['name'].get('first', '')
            last = player['name'].get('last', '')
            if first and last:
                return f"{first} {last}"
        
        # Try direct name fields
        name_fields = ['full_name', 'longName', 'name', 'player_name']
        for field in name_fields:
            if field in player and player[field]:
                return str(player[field])
        
        return "Unknown Player"
    
    def _extract_field(self, data: Dict, field_names: List[str]) -> str:
        """Extract a field from data using multiple possible field names."""
        for field_name in field_names:
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                
                # Handle nested structures
                if isinstance(value, dict):
                    # Look for common sub-fields
                    for subfield in ['total', 'value', 'full', 'name']:
                        if subfield in value:
                            return str(value[subfield])
                    return str(value)
                elif isinstance(value, list) and value:
                    # Return first item or length
                    if len(value) == 1:
                        return str(value[0])
                    else:
                        return f"{len(value)} items"
                else:
                    return str(value)
        
        return ""
    
    def create_summary_footer(self, stats: Dict[str, Any]) -> str:
        """
        Create a summary footer with extraction statistics.
        
        Args:
            stats: Dictionary with extraction statistics
            
        Returns:
            Formatted footer
        """
        footer = "\n---\n\n## Extraction Summary\n\n"
        
        for key, value in stats.items():
            footer += f"- **{key}**: {value}\n"
        
        footer += f"\n**Extraction completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return footer

def main():
    """Test the markdown formatter."""
    print("📝 Testing Markdown Formatter")
    print("=" * 50)
    
    formatter = MarkdownFormatter()
    
    # Test header creation
    header = formatter.create_header("Test Report", "Data Collection Test")
    print("Header created:")
    print(header)
    
    # Test table formatting
    headers = ["Name", "Position", "Team"]
    rows = [["Test Player 1", "QB", "BUF"], ["Test Player 2", "RB", "KC"]]
    table = formatter.format_table(headers, rows, "Test Players")
    print("Table created:")
    print(table)
    
    # Test player list formatting
    test_players = [
        {"name": {"full": "Josh Allen"}, "position": "QB", "team": "BUF", "player_id": "123"},
        {"full_name": "Travis Kelce", "pos": "TE", "teamABV": "KC", "playerID": "456"}
    ]
    
    player_section = formatter.format_player_list(test_players, "Test Players")
    print("Player section created:")
    print(player_section)

if __name__ == "__main__":
    main()
