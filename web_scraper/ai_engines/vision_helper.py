"""
Vision AI helper module for the web scraper.
This module provides functions to analyze screenshots and identify web elements using Gemini 2.0 Flash Exp.
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

def find_search_input(browser: webdriver.Chrome) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Find the search input field on the page using vision AI.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        WebElement for the search input or None if not found
    """
    # Directly try common search input selectors first (more reliable)
    logger.info("Trying common search input selectors first")
    for selector in ["input[type='search']", "input[name='q']", "input[name='query']", 
                    "input[name='search']", "input[placeholder*='search' i]"]:
        try:
            element = browser.find_element(By.CSS_SELECTOR, selector)
            # Skip hidden inputs
            if element.get_attribute("type") != "hidden" and element.is_displayed():
                logger.info(f"Found search input using selector: {selector}")
                return element
        except NoSuchElementException:
            continue
    
    # If common selectors didn't work, try vision-based approach
    logger.info("Common selectors didn't work, trying vision-based approach")
    
    # Take a screenshot of the page
    screenshot_path = take_screenshot(browser, "search_input")
    
    # Analyze the screenshot with Gemini Vision
    prompt = "Find the main search input field on this webpage. Look for text boxes where users can type search queries."
    result = analyze_screenshot(screenshot_path, prompt)
    
    # Check if we got a valid result
    if result.get("found", False):
        logger.info("Vision API found something, trying to locate the element")
        
        # Try to extract bounding box information
        bbox = None
        
        # Check different possible response formats
        if "bounding_box" in result:
            bbox = result["bounding_box"]
        elif "position" in result:
            bbox = result["position"]
        elif "coordinates" in result:
            bbox = result["coordinates"]
        
        # If we have bounding box information, try to use it
        if bbox and isinstance(bbox, dict):
            try:
                # Convert relative coordinates to absolute pixel coordinates
                window_size = browser.get_window_size()
                
                # Handle different coordinate formats
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                width = bbox.get("width", 0.2)
                height = bbox.get("height", 0.05)
                
                # If coordinates are given as percentages (0-1), convert to pixels
                if x <= 1.0:
                    x = int(x * window_size["width"])
                if y <= 1.0:
                    y = int(y * window_size["height"])
                if width <= 1.0:
                    width = int(width * window_size["width"])
                if height <= 1.0:
                    height = int(height * window_size["height"])
                
                # Use JavaScript to find the element at these coordinates
                script = """
                function getElementAtPosition(x, y) {
                    return document.elementFromPoint(x, y);
                }
                return getElementAtPosition(arguments[0], arguments[1]);
                """
                
                # Try the center point of the bounding box
                center_x = x + (width // 2)
                center_y = y + (height // 2)
                
                logger.info(f"Trying to find element at coordinates: ({center_x}, {center_y})")
                element = browser.execute_script(script, center_x, center_y)
                
                if element:
                    # Skip if the element is hidden
                    if element.get_attribute("type") == "hidden" or not element.is_displayed():
                        logger.info("Found element is hidden, skipping")
                    else:
                        # If the element is not an input, try to find an input within it or its parent
                        if element.tag_name.lower() != "input":
                            logger.info(f"Found element is not an input, it's a {element.tag_name}. Looking for input within it")
                            try:
                                # Try to find an input within this element
                                inputs = element.find_elements(By.TAG_NAME, "input")
                                for input_element in inputs:
                                    # Skip hidden inputs
                                    if input_element.get_attribute("type") != "hidden" and input_element.is_displayed():
                                        logger.info("Found input element within the element")
                                        return input_element
                            except NoSuchElementException:
                                pass
                                
                            # Try the parent element
                            logger.info("Trying parent element")
                            parent_script = "return arguments[0].parentElement;"
                            parent = browser.execute_script(parent_script, element)
                            try:
                                inputs = parent.find_elements(By.TAG_NAME, "input")
                                for input_element in inputs:
                                    # Skip hidden inputs
                                    if input_element.get_attribute("type") != "hidden" and input_element.is_displayed():
                                        logger.info("Found input element in parent")
                                        return input_element
                            except NoSuchElementException:
                                pass
                        
                        # If we got here and the element is an input that's not hidden, return it
                        if element.tag_name.lower() == "input" and element.get_attribute("type") != "hidden" and element.is_displayed():
                            logger.info("Found input element directly")
                            return element
            except Exception as e:
                logger.error(f"Error using bounding box information: {e}")
    
    # If all else fails, try a more aggressive approach with common search patterns
    logger.info("Trying aggressive approach to find any visible input")
    try:
        # Try to find any visible input that might be a search box
        inputs = browser.find_elements(By.TAG_NAME, "input")
        for input_element in inputs:
            # Skip hidden inputs and check if it's visible
            if (input_element.get_attribute("type") != "hidden" and 
                input_element.is_displayed() and
                input_element.get_attribute("type") not in ["checkbox", "radio", "submit", "button"]):
                logger.info("Found potential input element using aggressive approach")
                return input_element
    except Exception as e:
        logger.error(f"Error in aggressive search approach: {e}")
    
    logger.warning("Could not find search input field")
    return None

def find_search_button(browser: webdriver.Chrome) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Find the search button on the page using vision AI.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        WebElement for the search button or None if not found
    """
    # Try common search button selectors first (more reliable)
    logger.info("Trying common search button selectors first")
    for selector in ["button[type='submit']", "input[type='submit']", "button.search", 
                    "button[aria-label*='search' i]", "button:has(svg)", "input.search", 
                    "button[title*='search' i]", "button[name*='search' i]"]:
        try:
            element = browser.find_element(By.CSS_SELECTOR, selector)
            if element.is_displayed():
                logger.info(f"Found search button using selector: {selector}")
                return element
        except NoSuchElementException:
            continue
    
    # If common selectors didn't work, try vision-based approach
    logger.info("Common selectors didn't work, trying vision-based approach")
    
    # Take a screenshot of the page
    screenshot_path = take_screenshot(browser, "search_button")
    
    # Analyze the screenshot with Gemini Vision
    prompt = "Find the search button on this webpage. Look for buttons with search icons, magnifying glass icons, or 'Search' text."
    result = analyze_screenshot(screenshot_path, prompt)
    
    if result.get("found", False):
        logger.info("Vision API found something, trying to locate the element")
        
        # Try to extract bounding box information
        bbox = None
        
        # Check different possible response formats
        if "bounding_box" in result:
            bbox = result["bounding_box"]
        elif "position" in result:
            bbox = result["position"]
        elif "coordinates" in result:
            bbox = result["coordinates"]
        
        # If we have bounding box information, try to use it
        if bbox and isinstance(bbox, dict):
            try:
                # Convert relative coordinates to absolute pixel coordinates
                window_size = browser.get_window_size()
                
                # Handle different coordinate formats
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                width = bbox.get("width", 0.1)
                height = bbox.get("height", 0.05)
                
                # If coordinates are given as percentages (0-1), convert to pixels
                if x <= 1.0:
                    x = int(x * window_size["width"])
                if y <= 1.0:
                    y = int(y * window_size["height"])
                if width <= 1.0:
                    width = int(width * window_size["width"])
                if height <= 1.0:
                    height = int(height * window_size["height"])
                
                # Use JavaScript to find the element at these coordinates
                script = """
                function getElementAtPosition(x, y) {
                    return document.elementFromPoint(x, y);
                }
                return getElementAtPosition(arguments[0], arguments[1]);
                """
                
                # Try the center point of the bounding box
                center_x = x + (width // 2)
                center_y = y + (height // 2)
                
                logger.info(f"Trying to find element at coordinates: ({center_x}, {center_y})")
                element = browser.execute_script(script, center_x, center_y)
                
                if element and element.is_displayed():
                    logger.info(f"Found element: {element.tag_name}")
                    return element
            except Exception as e:
                logger.error(f"Error using bounding box information: {e}")
    
    # If all else fails, try a more aggressive approach
    logger.info("Trying aggressive approach to find any visible button")
    try:
        # Look for buttons or inputs that might be search buttons
        for tag in ["button", "input[type='submit']", "input[type='button']"]:
            elements = browser.find_elements(By.CSS_SELECTOR, tag)
            for element in elements:
                if element.is_displayed():
                    # Check if it has search-related text or attributes
                    text = element.text.lower()
                    if "search" in text or "find" in text or "go" in text:
                        logger.info(f"Found potential search button with text: {text}")
                        return element
                    
                    # Check attributes
                    for attr in ["title", "aria-label", "name", "id", "class"]:
                        attr_value = element.get_attribute(attr)
                        if attr_value and ("search" in attr_value.lower() or "find" in attr_value.lower()):
                            logger.info(f"Found potential search button with {attr}: {attr_value}")
                            return element
    except Exception as e:
        logger.error(f"Error in aggressive search approach: {e}")
    
        # Convert relative coordinates to absolute pixel coordinates
        window_size = browser.get_window_size()
        x = int(bbox.get("x", 0) * window_size["width"])
        y = int(bbox.get("y", 0) * window_size["height"])
        width = int(bbox.get("width", 0) * window_size["width"])
        height = int(bbox.get("height", 0) * window_size["height"])
        
        # Use JavaScript to find the element at these coordinates
        script = """
        function getElementAtPosition(x, y) {
            return document.elementFromPoint(x, y);
        }
        return getElementAtPosition(arguments[0], arguments[1]);
        """
        
        # Try the center point of the bounding box
        center_x = x + (width // 2)
        center_y = y + (height // 2)
        
        element = browser.execute_script(script, center_x, center_y)
        return element
    
    # Fallback to common search button selectors if vision AI fails
    for selector in ["button[type='submit']", "input[type='submit']", "button.search", 
                    "button[aria-label*='search' i]", "button:has(svg)"]:
        try:
            return browser.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            continue
    
    return None

def find_result_elements(browser: webdriver.Chrome, max_results: int = 10) -> List[webdriver.remote.webelement.WebElement]:
    """
    Find the search result elements on the page using vision AI.
    
    Args:
        browser: Selenium WebDriver instance
        max_results: Maximum number of results to return
        
    Returns:
        List of WebElements for the search results
    """
    # Take a screenshot of the page
    screenshot_path = take_screenshot(browser, "search_results")
    
    # Analyze the screenshot with Gemini Vision
    prompt = "Find the search results on this webpage. Identify the container with search results and individual result items."
    result = analyze_screenshot(screenshot_path, prompt)
    
    result_elements = []
    
    if result.get("found", False) and "result_items" in result:
        # Get the window size
        window_size = browser.get_window_size()
        
        # Process each result item
        for i, item_bbox in enumerate(result["result_items"]):
            if i >= max_results:
                break
                
            # Convert relative coordinates to absolute pixel coordinates
            x = int(item_bbox.get("x", 0) * window_size["width"])
            y = int(item_bbox.get("y", 0) * window_size["height"])
            
            # Use JavaScript to find the element at these coordinates
            script = """
            function getElementAtPosition(x, y) {
                return document.elementFromPoint(x, y);
            }
            return getElementAtPosition(arguments[0], arguments[1]);
            """
            
            element = browser.execute_script(script, x, y)
            
            # Add to results if not already included
            if element and element not in result_elements:
                result_elements.append(element)
    
    # If vision AI didn't find enough results, try common result selectors
    if len(result_elements) < max_results:
        for selector in [".result", ".search-result", ".item", "article", 
                        "[class*='result']", "[class*='item']", ".card"]:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Add elements not already in result_elements
                    for element in elements:
                        if element not in result_elements:
                            result_elements.append(element)
                            if len(result_elements) >= max_results:
                                break
                    
                    if len(result_elements) >= max_results:
                        break
            except Exception:
                continue
    
    return result_elements[:max_results]

def extract_result_data(result_element: webdriver.remote.webelement.WebElement) -> Dict[str, Any]:
    """
    Extract structured data from a search result element.
    
    Args:
        result_element: WebElement for the search result
        
    Returns:
        Dictionary with extracted data
    """
    result_data = {}
    
    # Extract title
    try:
        # Try common title selectors
        for selector in ["h1", "h2", "h3", "h4", ".title", "[class*='title']", 
                        "[class*='name']", "a", "strong"]:
            try:
                title_element = result_element.find_element(By.CSS_SELECTOR, selector)
                title = title_element.text.strip()
                if title:
                    result_data["title"] = title
                    break
            except NoSuchElementException:
                continue
        
        # If no title found, use the element's text as title
        if "title" not in result_data:
            result_data["title"] = result_element.text.strip()
    except Exception as e:
        logger.warning(f"Error extracting title: {e}")
    
    # Extract link
    try:
        link_element = result_element.find_element(By.TAG_NAME, "a")
        link = link_element.get_attribute("href")
        if link:
            result_data["link"] = link
    except NoSuchElementException:
        pass
    
    # Extract snippet/description
    try:
        for selector in ["p", "[class*='description']", "[class*='snippet']", 
                        "[class*='text']", "[class*='content']", "div"]:
            try:
                snippet_element = result_element.find_element(By.CSS_SELECTOR, selector)
                snippet = snippet_element.text.strip()
                if snippet and snippet != result_data.get("title", ""):
                    result_data["snippet"] = snippet
                    break
            except NoSuchElementException:
                continue
    except Exception as e:
        logger.warning(f"Error extracting snippet: {e}")
    
    # Extract other common data fields
    for field, selectors in [
        ("authors", ["[class*='author']", "[class*='by']", ".meta"]),
        ("date", ["[class*='date']", "time", "[datetime]"]),
        ("price", ["[class*='price']"]),
        ("rating", ["[class*='rating']", "[class*='stars']"])
    ]:
        try:
            for selector in selectors:
                try:
                    element = result_element.find_element(By.CSS_SELECTOR, selector)
                    value = element.text.strip()
                    if value:
                        result_data[field] = value
                        break
                except NoSuchElementException:
                    continue
        except Exception:
            pass
    
    return result_data 