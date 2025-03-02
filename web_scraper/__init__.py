"""
Web Scraper Package - Handles automated academic database searching using Selenium.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import submodules
from .config import (
    load_blocked_sites, 
    save_blocked_sites, 
    add_to_blocked_sites, 
    is_site_blocked,
    get_default_settings,
    update_settings
)

from .exceptions import BlockedSiteException

from .browser import (
    setup_browser,
    capture_screenshot
)

from .captcha import (
    detect_captcha,
    handle_captcha
)

from .utils import (
    sanitize_search_term,
    check_for_pdf_links,
    download_pdf,
    extract_text_from_pdf,
    show_search_progress,
    hide_search_progress,
    check_for_site_blocking,
    handle_cookie_consent
)

from .search_engines import (
    get_search_engine_function
)

def search_academic_databases(topics_subtopics: Optional[Union[List[str], List[Dict[str, Any]]]] = None, 
                             settings: Optional[Dict[str, Any]] = None, 
                             browsers: Optional[List[Any]] = None, 
                             headless: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search for academic papers from multiple academic databases.
    
    Args:
        topics_subtopics: Either a list of dictionaries with 'topic' and 'subtopics' keys,
                         or a list of topics (strings)
        settings: Dictionary of settings
        browsers: List of Selenium WebDriver instances (optional)
        headless: Whether to run browsers in headless mode
    
    Returns:
        dict: Dictionary mapping topics to lists of search results
    """
    # Update settings with defaults
    settings = update_settings(settings)
    
    # Ensure topics_subtopics is a list
    if topics_subtopics is None:
        topics_subtopics = []
    
    # Convert simple list of topics to the expected format
    formatted_topics = []
    for item in topics_subtopics:
        if isinstance(item, str):
            formatted_topics.append({"topic": item, "subtopics": []})
        elif isinstance(item, dict) and "topic" in item:
            if "subtopics" not in item:
                item["subtopics"] = []
            formatted_topics.append(item)
    
    # Load blocked sites at the start
    load_blocked_sites()
    
    # Ensure browsers is a list
    if browsers is None:
        browsers = []
    
    # Set up browsers if not provided
    if not browsers:
        browser_type = settings.get('browser_type', None)
        for i in range(settings.get('browser_count', 1)):
            try:
                browser = setup_browser(headless=headless, browser_type=browser_type)
                browsers.append(browser)
            except Exception as e:
                logger.error(f"Error setting up browser {i}: {e}")
                # Try to create at least one browser
                if i == 0:
                    continue
    
    # If no browsers are available, return empty results
    if not browsers:
        logger.error("No browsers available for searching")
        return {}
    
    # Get the list of search engines to use
    engines = settings.get('engines', ['google_scholar', 'research_gate'])
    
    # Initialize results dictionary
    all_results = {}
    
    # Search for each topic
    for topic_data in formatted_topics:
        topic = topic_data["topic"]
        subtopics = topic_data.get("subtopics", [])
        
        logger.info(f"Searching for topic: {topic}")
        
        # Initialize results for this topic
        topic_results = []
        
        # Search each engine for the main topic
        for engine_name in engines:
            # Get the search function for this engine
            search_function = get_search_engine_function(engine_name)
            
            if search_function is None:
                logger.warning(f"Search engine {engine_name} not supported")
                continue
            
            # Use the first browser for all searches
            browser = browsers[0]
            
            try:
                # Search for the topic
                engine_results = search_function(browser, topic, settings)
                
                # Add results to the topic results
                topic_results.extend(engine_results)
                
                logger.info(f"Found {len(engine_results)} results from {engine_name} for topic: {topic}")
            except Exception as e:
                logger.error(f"Error searching {engine_name} for topic {topic}: {e}")
        
        # Search for subtopics if any
        for subtopic in subtopics:
            combined_topic = f"{topic} {subtopic}"
            logger.info(f"Searching for subtopic: {combined_topic}")
            
            # Search each engine for the subtopic
            for engine_name in engines:
                # Get the search function for this engine
                search_function = get_search_engine_function(engine_name)
                
                if search_function is None:
                    continue
                
                # Use the first browser for all searches
                browser = browsers[0]
                
                try:
                    # Search for the subtopic
                    engine_results = search_function(browser, combined_topic, settings)
                    
                    # Add results to the topic results
                    topic_results.extend(engine_results)
                    
                    logger.info(f"Found {len(engine_results)} results from {engine_name} for subtopic: {combined_topic}")
                except Exception as e:
                    logger.error(f"Error searching {engine_name} for subtopic {combined_topic}: {e}")
        
        # Add the topic results to the overall results
        all_results[topic] = topic_results
    
    # Close browsers if we created them
    if browsers and not browsers[0] in browsers:
        for browser in browsers:
            try:
                browser.quit()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
    
    return all_results
