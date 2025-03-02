"""
ArXiv search engine module for the web scraper.
"""

import logging
import re
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
    Search ArXiv for the given query.
    
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
        logger.info(f"Setting up browser for ArXiv search: {query}")
        browser = setup_browser("chrome", headless=headless)
        
        # Navigate to ArXiv
        browser.get("https://arxiv.org/search/")
        
        # Find the search box and enter the query
        search_box = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.NAME, "query"))
        )
        search_box.clear()
        search_box.send_keys(sanitize_search_term(query))
        
        # Submit the search
        search_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_button.click()
        
        # Wait for results to load
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.arxiv-result"))
        )
        
        # Extract results
        result_elements = browser.find_elements(By.CSS_SELECTOR, "li.arxiv-result")
        
        # Limit to max_results
        result_elements = result_elements[:max_results]
        
        for element in result_elements:
            try:
                # Extract title
                title_element = element.find_element(By.CSS_SELECTOR, "p.title")
                title = title_element.text
                
                # Extract authors
                authors_element = element.find_element(By.CSS_SELECTOR, "p.authors")
                authors = authors_element.text.replace("Authors:", "").strip()
                
                # Extract link
                link_element = element.find_element(By.CSS_SELECTOR, "p.list-title a")
                link = link_element.get_attribute("href")
                
                # Extract abstract
                abstract_element = element.find_element(By.CSS_SELECTOR, "span.abstract-full")
                abstract = abstract_element.text.replace("Abstract:", "").strip()
                
                # Extract submission date
                date_element = element.find_element(By.CSS_SELECTOR, "p.is-size-7")
                date_text = date_element.text
                
                # Extract year using regex
                year_match = re.search(r'\b(19|20)\d{2}\b', date_text)
                year = year_match.group(0) if year_match else "N/A"
                
                # Create result dictionary
                result = {
                    "title": title,
                    "authors": authors,
                    "link": link,
                    "snippet": abstract,
                    "year": year,
                    "source": "ArXiv"
                }
                
                results.append(result)
                
            except NoSuchElementException:
                # Skip results that don't have the expected structure
                continue
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
    except TimeoutException:
        logger.error(f"Timeout while searching ArXiv for: {query}")
    except Exception as e:
        logger.error(f"Error searching ArXiv: {e}")
    finally:
        # Close the browser
        close_browser(browser)
    
    return results 