"""
AI-powered ArXiv search module for the web scraper.
This module uses vision AI to automatically detect and interact with search elements on ArXiv.
"""

import logging
import time
import re
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from web_scraper.browser import setup_browser, close_browser
from web_scraper.utils import sanitize_search_term, check_for_pdf_links, download_pdf
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
    Search ArXiv for the given query using AI vision.
    
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
    pdf_download = settings.get("pdf_download", False)
    
    try:
        # Set up the browser
        logger.info(f"Setting up browser for ArXiv search: {query}")
        browser = setup_browser("chrome", headless=headless)
        
        # Navigate to ArXiv
        logger.info("Searching ArXiv")
        browser.get("https://arxiv.org/search/")
        
        # Wait for the page to load
        time.sleep(2)
        
        # Find the search input field using AI vision
        logger.info("Using AI vision to find the search input field")
        search_input = find_search_input(browser)
        
        if not search_input:
            logger.error("Could not find search input field on ArXiv")
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
        time.sleep(3)
        
        # Find the search result elements using AI vision
        logger.info("Using AI vision to find search results")
        result_elements = find_result_elements(browser, max_results)
        
        if not result_elements:
            logger.warning("No search results found on ArXiv")
            return results
        
        logger.info(f"Found {len(result_elements)} result elements on ArXiv")
        
        # Extract data from each result element
        for element in result_elements:
            try:
                result_data = extract_result_data(element)
                
                # Add source information
                result_data["source"] = "ArXiv"
                
                # Extract year using regex if not already extracted
                if "year" not in result_data:
                    # Try to find a date in the element text
                    element_text = element.text
                    year_match = re.search(r'\b(19|20)\d{2}\b', element_text)
                    if year_match:
                        result_data["year"] = year_match.group(0)
                
                # Check for PDF links if requested
                if pdf_download and "link" in result_data:
                    # ArXiv papers always have PDF links
                    pdf_link = result_data["link"].replace("/abs/", "/pdf/") + ".pdf"
                    pdf_path = download_pdf(pdf_link)
                    if pdf_path:
                        result_data["pdf_path"] = pdf_path
                
                results.append(result_data)
            except Exception as e:
                logger.warning(f"Error extracting data from ArXiv result: {e}")
        
        logger.info(f"Successfully extracted data for {len(results)} ArXiv results")
        
        # If we have fewer results than requested, try to load more
        if len(results) < max_results:
            try:
                # Look for "Next" button
                next_button = None
                for selector in ["a.pagination-next", "a:contains('Next')", "a[rel='next']", 
                                ".pagination a:last-child"]:
                    try:
                        next_button = browser.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if next_button:
                    logger.info("Loading more results from next page")
                    next_button.click()
                    
                    # Wait for results to load
                    time.sleep(3)
                    
                    # Find additional result elements
                    additional_elements = find_result_elements(browser, max_results - len(results))
                    
                    if additional_elements:
                        logger.info(f"Found {len(additional_elements)} additional result elements")
                        
                        # Extract data from each additional result element
                        for element in additional_elements:
                            try:
                                result_data = extract_result_data(element)
                                
                                # Add source information
                                result_data["source"] = "ArXiv"
                                
                                # Extract year using regex if not already extracted
                                if "year" not in result_data:
                                    element_text = element.text
                                    year_match = re.search(r'\b(19|20)\d{2}\b', element_text)
                                    if year_match:
                                        result_data["year"] = year_match.group(0)
                                
                                # Check for PDF links if requested
                                if pdf_download and "link" in result_data:
                                    pdf_link = result_data["link"].replace("/abs/", "/pdf/") + ".pdf"
                                    pdf_path = download_pdf(pdf_link)
                                    if pdf_path:
                                        result_data["pdf_path"] = pdf_path
                                
                                results.append(result_data)
                                
                                if len(results) >= max_results:
                                    break
                            except Exception as e:
                                logger.warning(f"Error extracting data from additional ArXiv result: {e}")
            except Exception as e:
                logger.warning(f"Error loading additional results: {e}")
        
    except TimeoutException:
        logger.error(f"Timeout while searching ArXiv for: {query}")
    except Exception as e:
        logger.error(f"Error searching ArXiv: {e}")
    finally:
        # Close the browser
        close_browser(browser)
    
    return results[:max_results] 