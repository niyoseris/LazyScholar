"""
AI-powered news search module for the web scraper.
This module uses vision AI to automatically detect and interact with search elements on news websites,
focusing on topic-specific recent news and developments.
"""

import logging
import time
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List, Optional, Tuple
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from web_scraper.browser import setup_browser, close_browser
from web_scraper.utils import sanitize_search_term
from web_scraper.ai_engines.vision_helper import (
    find_search_input, 
    find_search_button, 
    find_result_elements,
    extract_result_data
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_topic_type(query: str) -> Dict[str, Any]:
    """
    Detect if this is a general news query or a regional news query.
    
    Args:
        query: The search query
        
    Returns:
        Dict containing search parameters
    """
    query_lower = query.lower()
    
    # Simple patterns for news queries
    news_patterns = [
        r"news\s+from\s+([A-Za-z]+)",
        r"([A-Za-z]+)\s+news",
        r"what('s|\s+is)\s+happening",
        r"latest\s+news",
        r"recent\s+news",
        r"current\s+events"
    ]
    
    for pattern in news_patterns:
        if re.search(pattern, query_lower):
            return {
                "type": "news",
                "search_phrases": [
                    "{query}",
                    "latest {query}",
                    "news {query}",
                    "current {query}"
                ],
                "exclude_terms": [
                    "-analysis",
                    "-opinion",
                    "-history",
                    "-explained",
                    "-wiki"
                ]
            }
    
    # Default to simple search if no pattern matches
    return {
        "type": "general",
        "search_phrases": [
            "{query}",
            "latest {query}"
        ],
        "exclude_terms": [
            "-analysis",
            "-opinion",
            "-wiki"
        ]
    }

def optimize_news_query(query: str) -> List[str]:
    """
    Create simple search variations for the query.
    
    Args:
        query: Original search query
        
    Returns:
        List of search variations
    """
    # Get basic search strategy
    search_info = detect_topic_type(query)
    
    # Generate search variations
    search_variations = []
    for phrase in search_info["search_phrases"]:
        # Format the search phrase with the query
        search_query = phrase.format(query=query)
        # Add exclusion terms
        search_query = f"{search_query} {' '.join(search_info['exclude_terms'])}"
        search_variations.append(search_query)
    
    return search_variations

def parse_relative_time(time_str: str) -> Optional[datetime]:
    """
    Parse relative time strings like '2 hours ago', '5 minutes ago', etc.
    
    Args:
        time_str: Relative time string
        
    Returns:
        Optional[datetime]: Parsed datetime or None if parsing fails
    """
    try:
        time_str = time_str.lower().strip()
        now = datetime.now(pytz.UTC)
        
        if 'just now' in time_str or 'moments ago' in time_str:
            return now
            
        parts = time_str.split()
        if len(parts) >= 2:
            try:
                value = int(parts[0])
                unit = parts[1]
                
                if 'minute' in unit:
                    return now - timedelta(minutes=value)
                elif 'hour' in unit:
                    return now - timedelta(hours=value)
                elif 'day' in unit and value == 1:  # Only accept "1 day ago"
                    return now - timedelta(days=1)
            except ValueError:
                pass
    except Exception:
        pass
    return None

def parse_news_date(date_str: str) -> Optional[datetime]:
    """
    Parse news article date using multiple methods.
    
    Args:
        date_str: Date string from the article
        
    Returns:
        Optional[datetime]: Parsed datetime or None if parsing fails
    """
    try:
        # First try parsing relative time
        relative_date = parse_relative_time(date_str)
        if relative_date:
            return relative_date
            
        # Common absolute date formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",  # ISO format
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%b %d, %Y %H:%M",
            "%d %b %Y %H:%M",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        return None
    except Exception:
        return None

def is_very_recent_news(date: Optional[datetime]) -> bool:
    """
    Check if a news article is very recent (within 12 hours).
    
    Args:
        date: Article datetime
        
    Returns:
        bool: True if article is very recent
    """
    if not date:
        return False
        
    now = datetime.now(pytz.UTC)
    if not date.tzinfo:
        date = pytz.UTC.localize(date)
        
    time_diff = now - date
    return time_diff.total_seconds() <= 12 * 3600  # 12 hours in seconds

def search(query: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search for news using the selected search engine.
    Uses exactly the user's query without any modifications.
    Only adds time filtering parameter for recent news.
    """
    browser = None
    results = []
    max_results = settings.get("max_results", 10)
    timeout = settings.get("timeout", 60)
    headless = settings.get("headless", True)
    search_engine = settings.get("search_engine", "google")  # Default to Google if not specified
    
    # Search engine configurations
    search_engines = {
        "google": {
            "url": "https://www.google.com/search",
            "news_param": "tbm=nws",
            "time_param": "tbs=qdr:d",  # last 24 hours
            "query_param": "q"
        },
        "bing": {
            "url": "https://www.bing.com/news/search",
            "news_param": "",  # Already a news URL
            "time_param": "qft=interval=4",  # last 24 hours
            "query_param": "q"
        },
        "duckduckgo": {
            "url": "https://duckduckgo.com/",
            "news_param": "ia=news",
            "time_param": "df=d",  # last 24 hours
            "query_param": "q"
        }
    }
    
    try:
        logger.info(f"Starting news search with query: {query} using {search_engine}")
        browser = setup_browser("chrome", headless=headless)
        
        # Get search engine configuration
        engine_config = search_engines.get(search_engine.lower(), search_engines["google"])
        
        # Add time filter for recent news queries but keep the exact user query
        sanitized_query = sanitize_search_term(query)
        
        if "recent news" in sanitized_query.lower():
            # Add time filter parameter but don't change the query
            params = [
                f"{engine_config['query_param']}={sanitized_query}",
                engine_config['news_param'],
                engine_config['time_param']
            ]
        else:
            params = [
                f"{engine_config['query_param']}={sanitized_query}",
                engine_config['news_param']
            ]
            
        # Build search URL (filter out empty params)
        search_url = f"{engine_config['url']}?{'&'.join(filter(None, params))}"
        
        browser.get(search_url)
        time.sleep(2)
        
        result_elements = find_result_elements(browser, min_results=3, max_results=max_results)
        
        if result_elements:
            for element in result_elements:
                result_data = extract_result_data(element)
                if result_data:
                    try:
                        date_selectors = ["time", ".date", ".time", ".timestamp"]
                        
                        for selector in date_selectors:
                            try:
                                date_element = element.find_element(By.CSS_SELECTOR, selector)
                                date_str = date_element.text
                                
                                if date_str:
                                    parsed_date = parse_news_date(date_str)
                                    if parsed_date and is_very_recent_news(parsed_date):
                                        result_data.update({
                                            "type": "news",
                                            "published_date": parsed_date.isoformat(),
                                            "hours_ago": round((datetime.now(pytz.UTC) - parsed_date).total_seconds() / 3600, 1),
                                            "search_engine": search_engine
                                        })
                                        if not any(r.get("url") == result_data.get("url") for r in results):
                                            results.append(result_data)
                                        break
                            except NoSuchElementException:
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Error extracting date: {str(e)}")
                        continue
                        
    except Exception as e:
        logger.error(f"Error during news search: {str(e)}")
        
    finally:
        if browser:
            close_browser(browser)
            
    results.sort(key=lambda x: x.get("hours_ago", float('inf')))
    return results[:max_results] 