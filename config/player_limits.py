#!/usr/bin/env python3
"""
Configurable player limits for different positions
"""

# Default player limits per position
DEFAULT_PLAYER_LIMITS = {
    "QB": 20,
    "RB": 20, 
    "WR": 20,
    "TE": 20,
    "K": 20,
    "DEF": 10,  # Fewer defenses available
    "FLEX": 15  # Multi-position players
}

# Maximum limits (safety check)
MAX_PLAYER_LIMITS = {
    "QB": 50,
    "RB": 50,
    "WR": 50, 
    "TE": 50,
    "K": 50,
    "DEF": 25,
    "FLEX": 30
}

def get_player_limits(custom_limits=None):
    """
    Get player limits, allowing for custom overrides
    
    Args:
        custom_limits: Dict with position -> limit overrides
        
    Returns:
        Dict with position -> limit
    """
    limits = DEFAULT_PLAYER_LIMITS.copy()
    
    if custom_limits:
        for position, limit in custom_limits.items():
            if position in limits:
                # Validate limit is within max bounds
                max_limit = MAX_PLAYER_LIMITS.get(position, 50)
                limits[position] = min(limit, max_limit)
            else:
                print(f"Warning: Unknown position '{position}' in custom limits")
    
    return limits

def get_total_available_players(limits=None):
    """
    Calculate total number of available players based on limits
    
    Args:
        limits: Dict with position -> limit overrides
        
    Returns:
        Total number of available players
    """
    player_limits = get_player_limits(limits)
    return sum(player_limits.values())

def validate_limits(limits):
    """
    Validate that limits are reasonable
    
    Args:
        limits: Dict with position -> limit
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    for position, limit in limits.items():
        if position not in DEFAULT_PLAYER_LIMITS:
            return False, f"Unknown position: {position}"
        
        if limit < 1:
            return False, f"Limit for {position} must be at least 1"
        
        max_limit = MAX_PLAYER_LIMITS.get(position, 50)
        if limit > max_limit:
            return False, f"Limit for {position} cannot exceed {max_limit}"
    
    return True, None
