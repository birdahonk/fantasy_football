#!/usr/bin/env python3
"""
Fantasy Football Web Application
Single-user web interface for fantasy football analysis and management
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
from pathlib import Path
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'fantasy_football_secret_key_2024'  # Simple secret key for single user

# Configuration
BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / 'analysis'
DATABASE_PATH = BASE_DIR / 'web_app' / 'database' / 'fantasy_football.db'

# Ensure database directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_database():
    """Initialize SQLite database with basic schema"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create tables for storing analysis data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER,
                analysis_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT
            )
        ''')
        
        # Create table for roster data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roster_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                status TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create table for free agents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS free_agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                availability TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def get_mock_data():
    """Generate mock data for development (will be replaced with real API data later)"""
    return {
        'roster': [
            {'name': 'Patrick Mahomes', 'position': 'QB', 'team': 'KC', 'status': 'Active'},
            {'name': 'Christian McCaffrey', 'position': 'RB', 'team': 'SF', 'status': 'Active'},
            {'name': 'Tyreek Hill', 'position': 'WR', 'team': 'MIA', 'status': 'Active'},
            {'name': 'Travis Kelce', 'position': 'TE', 'team': 'KC', 'status': 'Active'},
            {'name': 'Justin Tucker', 'position': 'K', 'team': 'BAL', 'status': 'Active'},
            {'name': 'San Francisco 49ers', 'position': 'DEF', 'team': 'SF', 'status': 'Active'}
        ],
        'free_agents': [
            {'name': 'Sam Howell', 'position': 'QB', 'team': 'SEA', 'availability': 'Available'},
            {'name': 'Zach Charbonnet', 'position': 'RB', 'team': 'SEA', 'availability': 'Available'},
            {'name': 'Jaxon Smith-Njigba', 'position': 'WR', 'team': 'SEA', 'availability': 'Available'}
        ],
        'current_week': 1,
        'opponent': 'Team Birdahonk',
        'matchup': 'Week 1: Your Team vs Team Birdahonk'
    }

@app.route('/')
def dashboard():
    """Main dashboard page with ASCII art header"""
    mock_data = get_mock_data()
    return render_template('dashboard.html', data=mock_data)

@app.route('/team')
def team():
    """Current roster view"""
    mock_data = get_mock_data()
    return render_template('team.html', data=mock_data)

@app.route('/analysis')
def analysis():
    """Weekly analysis reports"""
    mock_data = get_mock_data()
    return render_template('analysis.html', data=mock_data)

@app.route('/free-agents')
def free_agents():
    """Available players"""
    mock_data = get_mock_data()
    return render_template('free_agents.html', data=mock_data)

@app.route('/matchup')
def matchup():
    """Current week matchup"""
    mock_data = get_mock_data()
    return render_template('matchup.html', data=mock_data)

@app.route('/chat')
def chat():
    """AI chat interface"""
    return render_template('chat.html')

@app.route('/settings')
def settings():
    """Configuration and preferences"""
    return render_template('settings.html')

@app.route('/api/roster')
def api_roster():
    """API endpoint for roster data"""
    mock_data = get_mock_data()
    return jsonify({'status': 'success', 'data': mock_data['roster']})

@app.route('/api/free-agents')
def api_free_agents():
    """API endpoint for free agent data"""
    mock_data = get_mock_data()
    return jsonify({'status': 'success', 'data': mock_data['free_agents']})

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': 'development'
    })

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
