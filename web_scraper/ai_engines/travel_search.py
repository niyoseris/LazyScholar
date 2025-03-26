"""
AI-powered travel search module for the web scraper.
This module uses vision AI to automatically detect and interact with search elements on travel websites.
"""

import logging
import time
from typing import Dict, Any, List
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

def search(query: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search travel websites for the given query using AI vision.
    
    Args:
        query: The search query
        settings: Dictionary of settings
        
    Returns:
        List of search results
    """
    browser = None
    results = []
    max_results = settings.get("max_results", 10)
    timeout = settings.get("timeout", 60)
    headless = settings.get("headless", True)
    
    try:
        # Set up the browser
        logger.info(f"Setting up browser for travel search: {query}")
        browser = setup_browser("chrome", headless=headless)
        
        # List of travel websites to search
        travel_sites = [
            "https://www.tripadvisor.com",
            "https://www.lonelyplanet.com",
            "https://www.wikitravel.org"
        ]
        
        for site in travel_sites:
            try:
                # Navigate to the travel website
                logger.info(f"Searching {site}")
                browser.get(site)
                
                # Wait for the page to load
                time.sleep(2)
                
                # Find the search input field using AI vision
                logger.info("Using AI vision to find the search input field")
                search_input = find_search_input(browser)
                
                if not search_input:
                    logger.error(f"Could not find search input field on {site}")
                    continue
                
                # Enter the search query
                search_input.clear()
                search_input.send_keys(sanitize_search_term(query))
                
                # Find and click the search button using AI vision
                logger.info("Using AI vision to find the search button")
                search_button = find_search_button(browser)
                
                # Submit the search
                if search_button:
                    search_button.click()
                else:
                    # If no search button found, try pressing Enter
                    logger.info("No search button found, trying to submit with Enter key")
                    search_input.send_keys(Keys.RETURN)
                
                # Wait for results to load
                time.sleep(3)
                
                # Find the search result elements using AI vision
                logger.info("Using AI vision to find search results")
                result_elements = find_result_elements(browser, min_results=3, max_results=max_results)
                
                if result_elements:
                    # Extract data from each result
                    for element in result_elements:
                        result_data = extract_result_data(element)
                        if result_data:
                            result_data["source"] = site
                            result_data["type"] = "travel"
                            results.append(result_data)
                
                # If we have enough results, break
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                logger.error(f"Error searching {site}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error during travel search: {str(e)}")
        
    finally:
        if browser:
            close_browser(browser)
            
    return results[:max_results] 