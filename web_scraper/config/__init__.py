"""
Configuration module for the web scraper package.
Contains default settings and configuration loading functionality.
"""

import os
import json
import logging
from typing import Dict, List, Set, Any

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global list to track blocked sites
BLOCKED_SITES: Set[str] = set()

# File to persist blocked sites between runs
BLOCKED_SITES_FILE = "blocked_sites.json"

# CAPTCHA handling configuration
CAPTCHA_DETECTION_ENABLED = True
CAPTCHA_AUTO_SOLVE_ENABLED = False  # Disabled by default as it requires external services
CAPTCHA_WAIT_TIME = 60  # Default: wait up to 60 seconds for manual CAPTCHA solving
CAPTCHA_SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "captcha_screenshots")

# Create captcha_screenshots directory if it doesn't exist
os.makedirs(CAPTCHA_SCREENSHOT_DIR, exist_ok=True)

# Default search settings
DEFAULT_SEARCH_SETTINGS = {
    'captcha_wait_time': CAPTCHA_WAIT_TIME,
    'engines': ['google_scholar', 'research_gate', 'pubmed', 'arxiv', 'duckduckgo'],
    'max_results_per_topic': 10,
    'browser_count': 1
}

def load_blocked_sites() -> None:
    """Load previously blocked sites from file."""
    try:
        if os.path.exists(BLOCKED_SITES_FILE):
            with open(BLOCKED_SITES_FILE, 'r') as f:
                sites = json.load(f)
                BLOCKED_SITES.update(sites)
                logger.info(f"Loaded {len(sites)} blocked sites from file")
    except Exception as e:
        logger.error(f"Error loading blocked sites: {e}")
        # Continue with empty set if file can't be loaded

def save_blocked_sites() -> None:
    """Save blocked sites to file."""
    try:
        with open(BLOCKED_SITES_FILE, 'w') as f:
            json.dump(list(BLOCKED_SITES), f)
        logger.info(f"Saved {len(BLOCKED_SITES)} blocked sites to file")
    except Exception as e:
        logger.error(f"Error saving blocked sites: {e}")

def add_to_blocked_sites(url: str) -> str:
    """
    Add a URL to the blocked sites list.
    
    Args:
        url: The URL to block
        
    Returns:
        str: The base domain that was blocked
    """
    # Extract base domain for blocking
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc
    
    BLOCKED_SITES.add(base_domain)
    logger.warning(f"Added {base_domain} to blocked sites")
    save_blocked_sites()
    return base_domain

def is_site_blocked(url: str) -> bool:
    """
    Check if a site is in the blocked list.
    
    Args:
        url: The URL to check
        
    Returns:
        bool: True if the site is blocked, False otherwise
    """
    for pattern in BLOCKED_SITES:
        if pattern in url:
            return True
    return False

def get_default_settings() -> Dict[str, Any]:
    """
    Get a copy of the default settings.
    
    Returns:
        Dict[str, Any]: A copy of the default settings
    """
    return DEFAULT_SEARCH_SETTINGS.copy()

def update_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update settings with defaults for missing keys.
    
    Args:
        settings: The settings to update
        
    Returns:
        Dict[str, Any]: The updated settings
    """
    if settings is None:
        return get_default_settings()
        
    # Update settings with defaults for missing keys
    result = get_default_settings()
    result.update(settings)
    return result
