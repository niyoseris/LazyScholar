"""
Custom website search engine module for the web scraper.
This module allows searching any website with a search form, using user-provided CSS selectors.
"""

import logging
import time
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from web_scraper.browser import setup_browser, close_browser
from web_scraper.utils import sanitize_search_term

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def search(query: str, custom_website: Dict[str, Any], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search a custom website for the given query.
    
    Args:
        query: The search query
        custom_website: Dictionary with website URL and CSS selectors
        settings: Dictionary of settings
        
    Returns:
        List of search results
    """
    browser = None
    results = []
    max_results = settings.get("max_results", 10)
    timeout = settings.get("timeout", 60)
    headless = settings.get("headless", True)
    
    # Extract website details
    url = custom_website.get("url")
    selectors = custom_website.get("selectors", {})
    
    # Required selectors
    search_input_selector = selectors.get("search_input")
    search_button_selector = selectors.get("search_button")
    results_container_selector = selectors.get("results_container")
    result_item_selector = selectors.get("result_item")
    
    # Validate required selectors
    if not all([url, search_input_selector, search_button_selector, 
                results_container_selector, result_item_selector]):
        logger.error("Missing required website details or selectors")
        return results
    
    try:
        # Set up the browser
        logger.info(f"Setting up browser for custom website search: {url}")
        browser = setup_browser("chrome", headless=headless)
        
        # Navigate to the website
        browser.get(url)
        
        # Find the search box and enter the query
        search_box = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, search_input_selector))
        )
        search_box.clear()
        search_box.send_keys(sanitize_search_term(query))
        
        # Submit the search
        try:
            search_button = browser.find_element(By.CSS_SELECTOR, search_button_selector)
            search_button.click()
        except ElementNotInteractableException:
            # Some search forms submit on Enter key
            search_box.submit()
        
        # Wait for results to load
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, results_container_selector))
        )
        
        # Give the page a moment to fully load
        time.sleep(2)
        
        # Extract results
        result_elements = browser.find_elements(By.CSS_SELECTOR, result_item_selector)
        
        # Limit to max_results
        result_elements = result_elements[:max_results]
        
        for i, element in enumerate(result_elements, 1):
            try:
                # Try to extract common elements
                # Title - look for common title elements or use the first heading
                title = None
                for title_selector in ["h1", "h2", "h3", "h4", ".title", "[class*='title']", 
                                      "[class*='name']", "a", "strong"]:
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, title_selector)
                        title = title_element.text.strip()
                        if title:
                            break
                    except NoSuchElementException:
                        continue
                
                # If no title found, use a generic title
                if not title:
                    title = f"Result {i}"
                
                # Link - look for the first anchor tag
                link = None
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href")
                except NoSuchElementException:
                    link = browser.current_url
                
                # Description/snippet - try to find any descriptive text
                snippet = None
                for snippet_selector in ["p", "[class*='description']", "[class*='snippet']", 
                                        "[class*='text']", "[class*='content']", "div"]:
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, snippet_selector)
                        snippet = snippet_element.text.strip()
                        if snippet and snippet != title:
                            break
                    except NoSuchElementException:
                        continue
                
                # If no snippet found, use the element's text
                if not snippet:
                    snippet = element.text.replace(title, "").strip()
                
                # Create result dictionary
                result = {
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "source": url
                }
                
                # Try to extract any other useful information
                for key, selector in [
                    ("price", "[class*='price']"),
                    ("rating", "[class*='rating'], [class*='stars']"),
                    ("date", "[class*='date'], time"),
                    ("author", "[class*='author'], [class*='by']")
                ]:
                    try:
                        element_data = element.find_element(By.CSS_SELECTOR, selector)
                        result[key] = element_data.text.strip()
                    except NoSuchElementException:
                        pass
                
                results.append(result)
                
            except Exception as e:
                logger.warning(f"Error extracting result {i}: {e}")
                continue
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
    except TimeoutException:
        logger.error(f"Timeout while searching website: {url}")
    except Exception as e:
        logger.error(f"Error searching website: {e}")
    finally:
        # Close the browser
        close_browser(browser)
    
    return results 