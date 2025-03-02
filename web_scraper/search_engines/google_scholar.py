"""
Google Scholar search module for the web scraper package.
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

def search_google_scholar(browser: Any, search_term: str, settings: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Search Google Scholar for academic papers.
    
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
    
    # Google Scholar URL
    url = f"https://scholar.google.com/scholar?q={encoded_term}&hl=en"
    
    # Initialize results list
    results = []
    
    try:
        # Show progress
        show_search_progress(browser, "Searching Google Scholar", "Google Scholar", 10)
        
        # Navigate to Google Scholar
        logger.info(f"Navigating to Google Scholar: {url}")
        browser.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Check for site blocking
        check_for_site_blocking(browser, url)
        
        # Handle cookie consent if present
        handle_cookie_consent(browser)
        
        # Handle captcha if present
        handle_captcha(browser, url, captcha_wait_time)
        
        # Update progress
        show_search_progress(browser, "Extracting results from Google Scholar", "Google Scholar", 50)
        
        # Extract results
        try:
            from selenium.webdriver.common.by import By
            
            # Find all result entries
            result_elements = browser.find_elements(By.CSS_SELECTOR, ".gs_r.gs_or.gs_scl")
            
            # Process each result
            for i, element in enumerate(result_elements):
                if i >= max_results:
                    break
                    
                try:
                    # Extract title
                    title_element = element.find_element(By.CSS_SELECTOR, ".gs_rt a")
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    
                    # Extract authors, publication, year
                    meta_element = element.find_element(By.CSS_SELECTOR, ".gs_a")
                    meta_text = meta_element.text
                    
                    # Extract snippet
                    snippet_element = element.find_element(By.CSS_SELECTOR, ".gs_rs")
                    snippet = snippet_element.text
                    
                    # Extract citation info
                    citation_info = {}
                    try:
                        citation_links = element.find_elements(By.CSS_SELECTOR, ".gs_fl a")
                        for citation_link in citation_links:
                            citation_text = citation_link.text.lower()
                            if "cited by" in citation_text:
                                citation_count = ''.join(filter(str.isdigit, citation_text))
                                if citation_count:
                                    citation_info["citation_count"] = int(citation_count)
                    except Exception as e:
                        logger.debug(f"Error extracting citation info: {e}")
                    
                    # Create result entry
                    result_entry = {
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                        "meta": meta_text,
                        "source": "Google Scholar",
                        "citation_info": citation_info
                    }
                    
                    # Parse authors and publication info from meta text
                    try:
                        # Meta text format: "Author1, Author2... - Publication, Year - Source"
                        parts = meta_text.split(" - ")
                        if len(parts) >= 1:
                            authors = parts[0].strip()
                            result_entry["authors"] = authors
                        
                        if len(parts) >= 2:
                            publication_info = parts[1].strip()
                            result_entry["publication_info"] = publication_info
                            
                            # Try to extract year
                            import re
                            year_match = re.search(r'\b(19|20)\d{2}\b', publication_info)
                            if year_match:
                                result_entry["year"] = int(year_match.group(0))
                    except Exception as e:
                        logger.debug(f"Error parsing meta text: {e}")
                    
                    # Add to results
                    results.append(result_entry)
                    
                    # Update progress
                    progress = 50 + int((i + 1) / min(len(result_elements), max_results) * 50)
                    show_search_progress(browser, "Extracting results from Google Scholar", "Google Scholar", progress)
                    
                except Exception as e:
                    logger.error(f"Error processing Google Scholar result {i}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error extracting Google Scholar results: {e}")
        
        # Hide progress
        hide_search_progress(browser)
        
        logger.info(f"Found {len(results)} results from Google Scholar")
        return results
        
    except BlockedSiteException as e:
        logger.error(f"Google Scholar blocked access: {e}")
        hide_search_progress(browser)
        return results
    except Exception as e:
        logger.error(f"Error searching Google Scholar: {e}")
        hide_search_progress(browser)
        return results 