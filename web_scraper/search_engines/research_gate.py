"""
ResearchGate search module for the web scraper package.
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus

from ..utils import sanitize_search_term, show_search_progress, hide_search_progress, check_for_site_blocking, handle_cookie_consent
from ..captcha import handle_captcha
from ..exceptions import BlockedSiteException

# Configure logger
logger = logging.getLogger(__name__)

def search_research_gate(browser: Any, search_term: str, settings: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Search ResearchGate for academic papers.
    
    Args:
        browser: The browser instance
        search_term: The search term to search for
        settings: Optional settings for the search
        
    Returns:
        List[Dict[str, Any]]: A list of search results
    """
    if settings is None:
        settings = {}
        
    # Default settings
    max_results = settings.get('max_results_per_topic', 10)
    captcha_wait_time = settings.get('captcha_wait_time', 60)
    
    # Sanitize search term
    sanitized_term = sanitize_search_term(search_term)
    encoded_term = quote_plus(sanitized_term)
    
    # ResearchGate URL
    url = f"https://www.researchgate.net/search/publication?q={encoded_term}"
    
    # Initialize results list
    results = []
    
    try:
        # Show progress
        show_search_progress(browser, "Searching ResearchGate", "ResearchGate", 10)
        
        # Navigate to ResearchGate
        logger.info(f"Navigating to ResearchGate: {url}")
        browser.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Check for site blocking
        check_for_site_blocking(browser, url)
        
        # Handle cookie consent if present
        handle_cookie_consent(browser)
        
        # Handle captcha if present
        handle_captcha(browser, url, captcha_wait_time)
        
        # Update progress
        show_search_progress(browser, "Extracting results from ResearchGate", "ResearchGate", 50)
        
        # Extract results
        try:
            from selenium.webdriver.common.by import By
            
            # Find all result entries
            result_elements = browser.find_elements(By.CSS_SELECTOR, ".nova-legacy-c-card.nova-legacy-c-card--elevation-1.research-result-item")
            
            # Process each result
            for i, element in enumerate(result_elements):
                if i >= max_results:
                    break
                    
                try:
                    # Extract title
                    title_element = element.find_element(By.CSS_SELECTOR, ".nova-legacy-e-text.nova-legacy-e-text--size-l.nova-legacy-e-text--family-sans-serif.nova-legacy-e-text--spacing-none.nova-legacy-e-text--color-inherit.research-result-item__title a")
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    
                    # Extract authors
                    authors = ""
                    try:
                        author_elements = element.find_elements(By.CSS_SELECTOR, ".nova-legacy-e-link.nova-legacy-e-link--color-inherit.research-result-item__author")
                        authors = ", ".join([author.text for author in author_elements])
                    except Exception as e:
                        logger.debug(f"Error extracting authors: {e}")
                    
                    # Extract publication info
                    publication_info = ""
                    try:
                        publication_element = element.find_element(By.CSS_SELECTOR, ".nova-legacy-e-text.nova-legacy-e-text--size-s.nova-legacy-e-text--family-sans-serif.nova-legacy-e-text--spacing-none.nova-legacy-e-text--color-grey-600.research-result-item__journal")
                        publication_info = publication_element.text
                    except Exception as e:
                        logger.debug(f"Error extracting publication info: {e}")
                    
                    # Extract year
                    year = None
                    try:
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', publication_info)
                        if year_match:
                            year = int(year_match.group(0))
                    except Exception as e:
                        logger.debug(f"Error extracting year: {e}")
                    
                    # Extract snippet/abstract
                    snippet = ""
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, ".nova-legacy-e-text.nova-legacy-e-text--size-m.nova-legacy-e-text--family-sans-serif.nova-legacy-e-text--spacing-none.nova-legacy-e-text--color-grey-800.research-result-item__abstract")
                        snippet = snippet_element.text
                    except Exception as e:
                        logger.debug(f"Error extracting snippet: {e}")
                    
                    # Create result entry
                    result_entry = {
                        "title": title,
                        "link": link,
                        "authors": authors,
                        "publication_info": publication_info,
                        "snippet": snippet,
                        "source": "ResearchGate"
                    }
                    
                    if year:
                        result_entry["year"] = year
                    
                    # Add to results
                    results.append(result_entry)
                    
                    # Update progress
                    progress = 50 + int((i + 1) / min(len(result_elements), max_results) * 50)
                    show_search_progress(browser, "Extracting results from ResearchGate", "ResearchGate", progress)
                    
                except Exception as e:
                    logger.error(f"Error processing ResearchGate result {i}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error extracting ResearchGate results: {e}")
        
        # Hide progress
        hide_search_progress(browser)
        
        logger.info(f"Found {len(results)} results from ResearchGate")
        return results
        
    except BlockedSiteException as e:
        logger.error(f"ResearchGate blocked access: {e}")
        hide_search_progress(browser)
        return results
    except Exception as e:
        logger.error(f"Error searching ResearchGate: {e}")
        hide_search_progress(browser)
        return results 