"""
Vision AI helper module for the web scraper.
This module provides functions to analyze screenshots and identify web elements using Gemini 2.0 Flash Exp.

Vision usage is restricted to link detection on search pages only.
Other functionalities use traditional DOM-based approaches.
"""

import base64
import logging
import os
import tempfile
import time
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables and configure Gemini API
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Gemini Vision model
vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')

def load_image_bytes(image_path: str) -> bytes:
    """
    Load image bytes from a file path.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Image bytes
    """
    with open(image_path, "rb") as img_file:
        return img_file.read()

def take_screenshot(browser: webdriver.Chrome, name: str) -> str:
    """
    Take a screenshot of the current page.
    
    Args:
        browser: Selenium WebDriver instance
        name: Name for the screenshot
        
    Returns:
        Path to the saved screenshot
    """
    # Create directory if it doesn't exist
    screenshot_dir = os.path.join(tempfile.gettempdir(), 'web_scraper_screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = int(time.time())
    safe_name = name.replace(' ', '_')
    filename = f"{safe_name}_{timestamp}.png"
    filepath = os.path.join(screenshot_dir, filename)
    
    # Take screenshot
    browser.save_screenshot(filepath)
    logger.info(f"Screenshot saved to {filepath}")
    
    return filepath

def analyze_screenshot(screenshot_path: str, prompt: str) -> Dict[str, Any]:
    """
    Analyze a screenshot using Gemini 2.0 Flash Exp Vision API.
    
    Args:
        screenshot_path: Path to the screenshot
        prompt: Prompt for the vision model
        
    Returns:
        Dictionary with the analysis results
    """
    try:
        # Load the image
        with open(screenshot_path, "rb") as img_file:
            image_bytes = img_file.read()
        
        # Create the vision model
        vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare the image for the API
        image_parts = [
            {
                "mime_type": "image/png",
                "data": base64.b64encode(image_bytes).decode("utf-8")
            }
        ]
        
        # Generate the response
        response = vision_model.generate_content(
            contents=[{"role": "user", "parts": [{"text": prompt}, {"inline_data": image_parts[0]}]}]
        )
        response_text = response.text
        
        # Log the first part of the response for debugging
        logger.info(f"Vision API response: {response_text[:200]}...")
        
        # Try to extract JSON from the response
        json_data = None
        
        # First, try to find a JSON block in the response using regex
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            logger.info("Found JSON block in response")
            json_text = json_match.group(1)
            try:
                json_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from block: {e}")
        
        # If no JSON block found or parsing failed, try to extract JSON directly
        if json_data is None:
            # Look for array or object patterns
            if (response_text.strip().startswith('[') and response_text.strip().endswith(']')) or \
               (response_text.strip().startswith('{') and response_text.strip().endswith('}')):
                try:
                    json_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing direct JSON: {e}")
        
        # If JSON parsing failed, create a structured result with the raw text
        if json_data is None:
            # Check if the response contains any useful information
            if "no results" in response_text.lower() or "cannot extract" in response_text.lower():
                logger.info("Vision API found no results")
                return {
                    "found": False,
                    "raw_text": response_text,
                    "results": []
                }
            else:
                # Try to extract structured information from the text response
                logger.info("Creating structured result from text response")
                return {
                    "found": True,
                    "raw_text": response_text,
                    "results": [{"title": "Result from text analysis", "description": response_text}]
                }
        
        # Ensure the result has a 'found' flag
        if isinstance(json_data, list):
            return {
                "found": len(json_data) > 0,
                "results": json_data
            }
        elif isinstance(json_data, dict):
            if "found" not in json_data:
                json_data["found"] = True
            return json_data
        else:
            logger.warning(f"Unexpected JSON data type: {type(json_data)}")
            return {
                "found": True,
                "raw_text": response_text,
                "results": [{"title": "Unexpected result format", "description": str(json_data)}]
            }
            
    except Exception as e:
        logger.error(f"Error in analyze_screenshot: {e}")
        return {
            "found": False,
            "error": str(e),
            "results": []
        }

def analyze_screenshot_for_pdf_links(screenshot_path: str, is_html: bool = False) -> Dict[str, Any]:
    """
    Analyze a screenshot to identify PDF links using Gemini Vision.
    
    Args:
        screenshot_path: Path to the screenshot image
        is_html: Whether to look for HTML links instead of PDF links
        
    Returns:
        Dictionary with analysis results, including found (boolean) and 
        pdf_links (array of objects with text, position, and is_direct_pdf fields).
    """
    link_type = "HTML" if is_html else "PDF"
    prompt = f"""
    Analyze this screenshot of a search results page and identify all {link_type} links.
    
    IMPORTANT: Focus ONLY on actual content links, NOT navigation links, tabs, or UI elements.
    Look for links that appear to be search results leading to actual websites with content.
    
    For each {link_type} link, provide:
    1. The exact text of the link
    2. The approximate position (x, y coordinates)
    3. Whether it appears to be a direct link to content
    
    Format your response as a JSON object with the following structure:
    {{
        "found": true/false,
        "pdf_links": [
            {{
                "text": "link text",
                "position": {{
                    "x": x_coordinate,
                    "y": y_coordinate
                }},
                "is_direct_pdf": true/false
            }}
        ]
    }}
    
    Only include links that are likely to be actual search results leading to content websites.
    EXCLUDE navigation links, tabs, UI elements, and links to the search engine itself.
    """
    
    return analyze_screenshot(screenshot_path, prompt)

def find_pdf_links(screenshot_path: str, browser: webdriver.Chrome, is_html: bool = False, min_results: int = 1, max_results: int = 5) -> List[str]:
    """
    Find PDF or HTML links on the current page using vision AI.
    
    Args:
        screenshot_path: Path to the screenshot image
        browser: Selenium WebDriver instance
        is_html: Whether to look for HTML links instead of PDF links
        min_results: Minimum number of results to return
        max_results: Maximum number of results to return
        
    Returns:
        List of URLs for the found links
    """
    result_urls = []
    
    # Analyze the screenshot with Gemini Vision
    vision_result = analyze_screenshot_for_pdf_links(screenshot_path, is_html)
    
    # Extract links from vision analysis
    if vision_result and vision_result.get("found", False) and "pdf_links" in vision_result:
        for link_info in vision_result.get("pdf_links", []):
            # Try to find the element by text
            if "text" in link_info and link_info["text"]:
                try:
                    # Use JavaScript to find elements by text content
                    script = """
                    function findElementsByText(text) {
                        const elements = Array.from(document.querySelectorAll('a, button, [role="button"]'));
                        return elements.filter(element => 
                            element.textContent.trim().toLowerCase().includes(text.toLowerCase())
                        ).map(element => {
                            const rect = element.getBoundingClientRect();
                            return {
                                text: element.textContent.trim(),
                                href: element.href || null,
                                tag: element.tagName.toLowerCase(),
                                position: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                }
                            };
                        });
                    }
                    return findElementsByText(arguments[0]);
                    """
                    
                    elements = browser.execute_script(script, link_info["text"])
                    
                    if elements and len(elements) > 0:
                        for element in elements:
                            if element.get("href") and element.get("tag") == "a":
                                url = element.get("href")
                                # For PDF links, check if it ends with .pdf
                                # For HTML links, check if it's a valid URL and not a PDF
                                if (not is_html and url.lower().endswith('.pdf')) or \
                                   (is_html and not url.lower().endswith('.pdf') and url.startswith('http')):
                                    if url not in result_urls:
                                        result_urls.append(url)
                                        logger.info(f"Found {'HTML' if is_html else 'PDF'} link via vision AI text match: {url}")
                                        
                                        # If we've reached max_results, stop searching
                                        if len(result_urls) >= max_results:
                                            return result_urls
                except Exception as e:
                    logger.warning(f"Error finding element by text: {str(e)}")
            
            # Try to find element by position if we need more results
            if "position" in link_info and len(result_urls) < min_results:
                try:
                    pos = link_info["position"]
                    script = """
                    function findElementAtPosition(x, y) {
                        const element = document.elementFromPoint(x, y);
                        if (element) {
                            // Find closest anchor parent
                            let current = element;
                            while (current && current.tagName !== 'A' && current !== document.body) {
                                current = current.parentElement;
                            }
                            
                            if (current && current.tagName === 'A') {
                                const rect = current.getBoundingClientRect();
                                return {
                                    text: current.textContent.trim(),
                                    href: current.href || null,
                                    tag: current.tagName.toLowerCase(),
                                    position: {
                                        x: rect.x,
                                        y: rect.y,
                                        width: rect.width,
                                        height: rect.height
                                    }
                                };
                            }
                            return null;
                        }
                        return null;
                    }
                    return findElementAtPosition(arguments[0], arguments[1]);
                    """
                    
                    element = browser.execute_script(script, pos["x"], pos["y"])
                    
                    if element and element.get("href"):
                        url = element.get("href")
                        # For PDF links, check if it ends with .pdf
                        # For HTML links, check if it's a valid URL and not a PDF
                        if (not is_html and url.lower().endswith('.pdf')) or \
                           (is_html and not url.lower().endswith('.pdf') and url.startswith('http')):
                            if url not in result_urls:
                                result_urls.append(url)
                                logger.info(f"Found {'HTML' if is_html else 'PDF'} link via vision AI position match: {url}")
                                
                                # If we've reached max_results, stop searching
                                if len(result_urls) >= max_results:
                                    return result_urls
                except Exception as e:
                    logger.warning(f"Error finding element by position: {str(e)}")
    
    # Fallback: Use traditional methods to find links if we haven't met minimum requirements
    if len(result_urls) < min_results:
        logger.info(f"Using traditional methods to find {'HTML' if is_html else 'PDF'} links")
        try:
            # For PDF links, look for links ending with .pdf
            # For HTML links, look for all links that don't end with .pdf
            if not is_html:
                elements = browser.find_elements(By.XPATH, "//a[contains(translate(@href, 'PDF', 'pdf'), '.pdf')]")
            else:
                elements = browser.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                try:
                    url = element.get_attribute("href")
                    if url:
                        # For PDF links, check if it ends with .pdf
                        # For HTML links, check if it's a valid URL and not a PDF
                        if (not is_html and url.lower().endswith('.pdf')) or \
                           (is_html and not url.lower().endswith('.pdf') and url.startswith('http')):
                            # Filter out search engine domains for HTML links
                            if is_html and any(domain in url.lower() for domain in ["google.com", "duckduckgo.com", "bing.com"]):
                                continue
                            
                            if url not in result_urls:
                                result_urls.append(url)
                                logger.info(f"Found {'HTML' if is_html else 'PDF'} link via traditional method: {url}")
                                
                                # If we've reached max_results, stop searching
                                if len(result_urls) >= max_results:
                                    break
                except Exception as e:
                    logger.debug(f"Error getting href attribute: {str(e)}")
        except Exception as e:
            logger.warning(f"Error finding links with traditional method: {str(e)}")
    
    return result_urls

def find_search_input(browser: webdriver.Chrome) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Find the search input field on the page using traditional DOM methods.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        WebElement for the search input or None if not found
    """
    logger.info("Finding search input using traditional selectors")
    
    # Try common search input selectors
    selectors = [
        "input[type='search']", 
        "input[name='q']", 
        "input[name='query']", 
        "input[name='search']", 
        "input[placeholder*='search' i]",
        "input[id*='search' i]",
        "input[class*='search' i]",
        "input[title*='search' i]",
        ".searchbox input",
        ".search-box input",
        ".search-form input",
        ".searchForm input",
        "form[action*='search' i] input[type='text']",
        "input[aria-label*='search' i]"
    ]
    
    for selector in selectors:
        try:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.get_attribute("type") != "hidden" and element.is_displayed():
                    logger.info(f"Found search input using selector: {selector}")
                    return element
        except Exception as e:
            logger.debug(f"Error with selector '{selector}': {str(e)}")
    
    # If no specific selectors worked, try a more general approach with text/search inputs
    try:
        for input_type in ["text", "search"]:
            elements = browser.find_elements(By.CSS_SELECTOR, f"input[type='{input_type}']")
            for element in elements:
                if element.is_displayed() and element.get_attribute("type") != "hidden":
                    # Check if it looks like a search box
                    parent = element.find_element(By.XPATH, "./..")
                    parent_text = parent.text.lower()
                    parent_html = parent.get_attribute("innerHTML").lower()
                    
                    # Look for search-related terms in the parent
                    if ('search' in parent_text or 
                        'find' in parent_text or 
                        'search' in parent_html or 
                        'magnifi' in parent_html):  # For "magnifying glass" icons
                        logger.info(f"Found search input by context analysis")
                        return element
    except Exception as e:
        logger.debug(f"Error with context analysis: {str(e)}")
    
    # Last resort: Get all inputs and find the most prominent one
    try:
        inputs = browser.find_elements(By.TAG_NAME, "input")
        visible_inputs = [i for i in inputs if i.is_displayed() and i.get_attribute("type") in ["text", "search", ""]]
        
        if visible_inputs:
            # Find the input with the largest width (usually the main search)
            largest_input = max(visible_inputs, key=lambda i: 
                                int(i.get_attribute("offsetWidth") or 0))
            
            if int(largest_input.get_attribute("offsetWidth") or 0) > 150:  # Reasonably wide
                logger.info("Found search input by size analysis")
                return largest_input
    except Exception as e:
        logger.debug(f"Error with size analysis: {str(e)}")
    
    logger.warning("No search input found using any method")
    return None

def find_search_button(browser: webdriver.Chrome) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Find the search button on the page using traditional DOM methods.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        WebElement for the search button or None if not found
    """
    logger.info("Finding search button using traditional selectors")
    
    # Try common search button selectors
    selectors = [
        "button[type='submit']", 
        "input[type='submit']", 
        "button.search", 
        "button[aria-label*='search' i]", 
        "button:has(svg)", 
        "input.search", 
        "button[title*='search' i]", 
        "button[name*='search' i]",
        ".searchbox button",
        ".search-box button",
        ".search-form button",
        ".searchForm button",
        "form[action*='search' i] button",
        "form[action*='search' i] input[type='submit']",
        "button[aria-label*='search' i]",
        "button i.fa-search",
        "button i.fa-magnifying-glass",
        "button svg[title*='search' i]"
    ]
    
    for selector in selectors:
        try:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    logger.info(f"Found search button using selector: {selector}")
                    return element
        except Exception as e:
            logger.debug(f"Error with selector '{selector}': {str(e)}")
    
    # Look for buttons with common search icons or text
    try:
        buttons = browser.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if not button.is_displayed():
                continue
                
            button_text = button.text.lower()
            button_html = button.get_attribute("innerHTML").lower()
            
            # Check for search-related text or icons
            if ('search' in button_text or 
                'find' in button_text or 
                'search' in button_html or 
                'magnifi' in button_html or  # For "magnifying glass" icons
                '🔍' in button_html):  # Search emoji
                logger.info("Found search button by text/content analysis")
                return button
    except Exception as e:
        logger.debug(f"Error with button analysis: {str(e)}")
    
    # Try finding the button near the search input
    try:
        search_input = find_search_input(browser)
        if search_input:
            # Get the parent form or container
            parent = search_input.find_element(By.XPATH, "./..")
            
            # Look for submit buttons within the parent
            submit_buttons = parent.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
            if submit_buttons:
                for button in submit_buttons:
                    if button.is_displayed():
                        logger.info("Found search button near search input")
                        return button
    except Exception as e:
        logger.debug(f"Error finding button near search input: {str(e)}")
    
    # If no button found, the search might work with Enter key
    logger.info("No search button found. Search might work with Enter key.")
    return None

def find_result_elements(browser: webdriver.Chrome, min_results: int = 3, max_results: int = 10) -> List[webdriver.remote.webelement.WebElement]:
    """
    Find the search result elements on the page using traditional DOM methods.
    
    Args:
        browser: Selenium WebDriver instance
        min_results: Minimum number of results to return
        max_results: Maximum number of results to return
        
    Returns:
        List of WebElements for the search results
    """
    logger.info("Finding search results using traditional selectors")
    
    result_elements = []
    
    # Common search result selectors for different search engines
    result_selectors = [
        # Google
        ".g .yuRUbf", "div.g", ".rc", "div.tF2Cxc", "div.yuRUbf", ".card-section", 
        
        # DuckDuckGo
        ".result", ".results--main .result", ".web-result", ".nrn-react-div",
        
        # Bing
        ".b_algo", ".b_results .b_algo", "#b_results .b_algo",
        
        # Yahoo
        ".algo", ".algo-sr", ".searchCenterMiddle li", 
        
        # General selectors that might work across search engines
        ".result", ".search-result", ".searchResult", ".result-item", "article", ".card"
    ]
    
    # Try each selector
    for selector in result_selectors:
        try:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            if elements and len(elements) > 0:
                logger.info(f"Found {len(elements)} search results with selector: {selector}")
                
                # Keep only visible elements
                visible_elements = [e for e in elements if e.is_displayed()]
                
                # Add to result_elements up to max_results
                for element in visible_elements[:max_results]:
                    if element not in result_elements:
                        result_elements.append(element)
                
                if len(result_elements) >= min_results:
                    logger.info(f"Found {len(result_elements)} result elements, which meets the minimum requirement")
                    return result_elements[:max_results]
        except Exception as e:
            logger.debug(f"Error with selector '{selector}': {str(e)}")
    
    # If we didn't find enough results with specific selectors, look for links that look like results
    if len(result_elements) < min_results:
        try:
            # Find all links
            links = browser.find_elements(By.TAG_NAME, "a")
            
            # Process only visible links with sufficient text
            for link in links:
                if not link.is_displayed():
                    continue
                    
                # Check if the link has substantial text (likely a search result)
                link_text = link.text.strip()
                if link_text and len(link_text) > 20:  # Arbitrary threshold for meaningful content
                    # Check if it has an href attribute
                    href = link.get_attribute("href")
                    if href and href.startswith("http"):
                        # Add the link to results if it's not already included
                        if link not in result_elements:
                            result_elements.append(link)
                            
                            if len(result_elements) >= max_results:
                                break
        except Exception as e:
            logger.debug(f"Error finding links as results: {str(e)}")
    
    logger.info(f"Found {len(result_elements)} result elements using traditional methods")
    return result_elements[:max_results]

def extract_result_data(result_element: webdriver.remote.webelement.WebElement) -> Dict[str, Any]:
    """
    Extract data from a search result element.
    
    Args:
        result_element: WebElement for the search result
        
    Returns:
        Dictionary with result data
    """
    result_data = {
        "title": "",
        "link": "",
        "description": "",
        "is_pdf": False
    }
    
    try:
        # Try to find the link within the result
        links = result_element.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and href.startswith("http"):
                result_data["link"] = href
                # Check if it's a PDF
                if href.lower().endswith(".pdf"):
                    result_data["is_pdf"] = True
                break
        
        # If the element itself is a link, use its href
        if not result_data["link"]:
            if result_element.tag_name == "a":
                href = result_element.get_attribute("href")
                if href:
                    result_data["link"] = href
                    if href.lower().endswith(".pdf"):
                        result_data["is_pdf"] = True
        
        # Extract title - look for heading tags or elements with title-like classes
        title_candidates = result_element.find_elements(
            By.CSS_SELECTOR, "h2, h3, h4, .title, .result-title, [class*='title'], [class*='heading']"
        )
        if title_candidates:
            result_data["title"] = title_candidates[0].text.strip()
        
        # If no specific title found, use the text of the first link
        if not result_data["title"] and links:
            result_data["title"] = links[0].text.strip()
        
        # Extract description
        desc_candidates = result_element.find_elements(
            By.CSS_SELECTOR, ".snippet, .description, [class*='desc'], [class*='snippet'], [class*='summary']"
        )
        if desc_candidates:
            result_data["description"] = desc_candidates[0].text.strip()
        
        # If no description found, get all text and remove the title
        if not result_data["description"]:
            full_text = result_element.text.strip()
            if result_data["title"] and result_data["title"] in full_text:
                desc_text = full_text.replace(result_data["title"], "", 1).strip()
                result_data["description"] = desc_text
        
    except Exception as e:
        logger.warning(f"Error extracting result data: {str(e)}")
    
    return result_data 