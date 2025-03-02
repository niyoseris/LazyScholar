"""
DuckDuckGo search engine module for the web scraper.
"""

import logging
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from web_scraper.browser import setup_browser, close_browser
from web_scraper.utils import sanitize_search_term

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def search(query: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo for the given query.
    
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
        logger.info(f"Setting up browser for DuckDuckGo search: {query}")
        browser = setup_browser("chrome", headless=headless)
        
        # Navigate to DuckDuckGo
        browser.get("https://duckduckgo.com/")
        
        # Find the search box and enter the query
        search_box = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.ID, "search_form_input_homepage"))
        )
        search_box.clear()
        search_box.send_keys(sanitize_search_term(query))
        
        # Submit the search
        search_button = browser.find_element(By.ID, "search_button_homepage")
        search_button.click()
        
        # Wait for results to load
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result"))
        )
        
        # Extract results
        result_elements = browser.find_elements(By.CSS_SELECTOR, ".result")
        
        # Limit to max_results
        result_elements = result_elements[:max_results]
        
        for element in result_elements:
            try:
                # Extract title
                title_element = element.find_element(By.CSS_SELECTOR, ".result__title a")
                title = title_element.text
                
                # Extract link
                link = title_element.get_attribute("href")
                
                # Extract snippet
                snippet_element = element.find_element(By.CSS_SELECTOR, ".result__snippet")
                snippet = snippet_element.text
                
                # Create result dictionary
                result = {
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "source": "DuckDuckGo"
                }
                
                results.append(result)
                
            except NoSuchElementException:
                # Skip results that don't have the expected structure
                continue
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
    except TimeoutException:
        logger.error(f"Timeout while searching DuckDuckGo for: {query}")
    except Exception as e:
        logger.error(f"Error searching DuckDuckGo: {e}")
    finally:
        # Close the browser
        close_browser(browser)
    
    return results 