"""
Search engines module for the web scraper package.
Contains functions for searching different types of content.
"""

import logging
from typing import Dict, List, Optional, Any

# Configure logger
logger = logging.getLogger(__name__)

# Import search engine functions
from .google_scholar import search_google_scholar
from .research_gate import search_research_gate
from ..ai_engines.news_search import search as search_news
from ..ai_engines.travel_search import search as search_travel
from ..ai_engines.web_search import search as search_web

# Dictionary mapping engine names to their search functions
ENGINE_FUNCTIONS = {
    'google_scholar': search_google_scholar,
    'research_gate': search_research_gate,
    'news': search_news,
    'travel': search_travel,
    'web': search_web,
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
