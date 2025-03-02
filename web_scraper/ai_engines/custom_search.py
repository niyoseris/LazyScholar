"""
AI-powered custom website search module for the web scraper.
This module uses vision AI to automatically detect and interact with search elements on any website.
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

def search(query: str, website_url: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search a custom website for the given query using AI vision.
    
    Args:
        query: The search query
        website_url: URL of the website to search
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
        logger.info(f"Setting up browser for custom website search: {website_url}")
        browser = setup_browser("chrome", headless=headless)
        
        # Navigate to the website
        browser.get(website_url)
        
        # Wait for the page to load
        time.sleep(3)
        
        # Find the search input field using AI vision
        logger.info("Using AI vision to find the search input field")
        search_input = find_search_input(browser)
        
        if not search_input:
            logger.error("Could not find search input field")
            return results
        
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
        time.sleep(5)
        
        # Find the search result elements using AI vision
        logger.info("Using AI vision to find search results")
        result_elements = find_result_elements(browser, max_results)
        
        if not result_elements:
            logger.warning("No search results found")
            return results
        
        logger.info(f"Found {len(result_elements)} result elements")
        
        # Extract data from each result element
        for element in result_elements:
            try:
                result_data = extract_result_data(element)
                
                # Add source information
                result_data["source"] = website_url
                
                results.append(result_data)
            except Exception as e:
                logger.warning(f"Error extracting data from result element: {e}")
        
        logger.info(f"Successfully extracted data for {len(results)} results")
        
    except TimeoutException:
        logger.error(f"Timeout while searching website: {website_url}")
    except Exception as e:
        logger.error(f"Error searching website: {e}")
    finally:
        # Close the browser
        close_browser(browser)
    
    return results 