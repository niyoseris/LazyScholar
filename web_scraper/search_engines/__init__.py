"""
Search engines module for the web scraper package.
Contains functions for searching different academic databases.
"""

import logging
from typing import Dict, List, Optional, Any

# Configure logger
logger = logging.getLogger(__name__)

# Import search engine functions
from .google_scholar import search_google_scholar
from .research_gate import search_research_gate

# Dictionary mapping engine names to their search functions
ENGINE_FUNCTIONS = {
    'google_scholar': search_google_scholar,
    'research_gate': search_research_gate,
}

def get_search_engine_function(engine_name: str) -> Optional[Any]:
    """
    Get the search function for a given engine name.
    
    Args:
        engine_name: The name of the search engine
        
    Returns:
        Optional[Any]: The search function or None if not found
    """
    return ENGINE_FUNCTIONS.get(engine_name.lower())
