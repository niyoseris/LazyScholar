#!/usr/bin/env python3
"""
Simple AI-powered search script.
This script demonstrates how to use Selenium to search any website.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List
from urllib.parse import urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementClickInterceptedException, StaleElementReferenceException
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
except ImportError:
    print("Error: Required packages not found.")
    print("Please install them with: pip install selenium webdriver-manager")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Search any website using Selenium.")
    parser.add_argument("query", help="The search query")
    parser.add_argument("website", help="The website URL to search (including https://)")
    parser.add_argument("--max-results", type=int, default=3, help="Maximum number of results to retrieve (default: 3)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--output", help="Output file path (JSON)")
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="chrome", help="Browser to use (default: chrome)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds for page loading (default: 30)")
    parser.add_argument("--wait", type=int, default=3, help="Wait time in seconds after page loads (default: 3)")
    parser.add_argument("--screenshot", help="Save a screenshot to the specified file")
    
    return parser.parse_args()

def setup_browser(browser_type="chrome", headless=False):
    """Set up and return a browser instance."""
    browser = None
    
    # Try Chrome first if requested
    if browser_type.lower() == "chrome":
        try:
            print("Setting up Chrome browser...")
            chrome_options = ChromeOptions()
            if headless:
                chrome_options.add_argument("--headless=new")
            
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Add user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Disable automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            service = ChromeService(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=chrome_options)
            return browser
        except Exception as e:
            print(f"Error setting up Chrome: {e}")
            print("Falling back to Firefox...")
            browser_type = "firefox"
    
    # Use Firefox as fallback or if explicitly requested
    if browser_type.lower() == "firefox":
        try:
            print("Setting up Firefox browser...")
            firefox_options = FirefoxOptions()
            if headless:
                firefox_options.add_argument("--headless")
            
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")
            
            # Add user agent to avoid detection
            firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0")
            
            # Disable automation flags
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            
            service = FirefoxService(GeckoDriverManager().install())
            browser = webdriver.Firefox(service=service, options=firefox_options)
            return browser
        except Exception as e:
            print(f"Error setting up Firefox: {e}")
            raise Exception("Failed to set up any browser. Please make sure Chrome or Firefox is installed.")
    
    return browser

def wait_for_page_load(browser, timeout=30):
    """Wait for the page to load completely."""
    try:
        # Wait for the document to be in ready state
        WebDriverWait(browser, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        print(f"Warning: Page load timed out after {timeout} seconds.")
        return False

def find_search_input(browser, wait_time=10):
    """Find the search input field on the page."""
    # Try common search input selectors
    selectors = [
        "input[type='search']", 
        "input[name='q']", 
        "input[name='query']", 
        "input[name='search']", 
        "input[placeholder*='search' i]",
        "input[aria-label*='search' i]",
        "textarea[placeholder*='search' i]",
        "textarea[aria-label*='search' i]"
    ]
    
    # Try to find the search input with explicit wait
    for selector in selectors:
        try:
            element = WebDriverWait(browser, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            # Check if the element is visible and enabled
            if element.is_displayed() and element.is_enabled():
                return element
        except (TimeoutException, NoSuchElementException):
            continue
    
    # If no search input found with selectors, try to find any input field
    try:
        inputs = browser.find_elements(By.TAG_NAME, "input")
        for input_element in inputs:
            if input_element.is_displayed() and input_element.is_enabled():
                input_type = input_element.get_attribute("type")
                if input_type in ["text", "search", None, ""]:
                    return input_element
    except NoSuchElementException:
        pass
    
    return None

def find_search_button(browser, wait_time=10):
    """Find the search button on the page."""
    # Try common search button selectors
    selectors = [
        "button[type='submit']", 
        "input[type='submit']", 
        "button.search", 
        "button[aria-label*='search' i]",
        "button:has(svg)",
        "button.searchButton",
        "button.search-button",
        "button.search-submit",
        "button[title*='search' i]",
        "button[name*='search' i]"
    ]
    
    # Try to find the search button with explicit wait
    for selector in selectors:
        try:
            element = WebDriverWait(browser, wait_time).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            return element
        except (TimeoutException, NoSuchElementException):
            continue
    
    return None

def safe_click(browser, element, max_attempts=3):
    """Safely click an element, handling common exceptions."""
    attempts = 0
    while attempts < max_attempts:
        try:
            # Try a direct click first
            element.click()
            return True
        except ElementClickInterceptedException:
            # If the element is intercepted, try JavaScript click
            try:
                browser.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                # If JavaScript click fails, try to scroll to the element and click
                try:
                    browser.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.click()
                    return True
                except Exception:
                    attempts += 1
                    time.sleep(1)
        except StaleElementReferenceException:
            # If the element is stale, we need to find it again
            return False
        except Exception as e:
            print(f"Click error: {e}")
            attempts += 1
            time.sleep(1)
    
    return False

def extract_search_results(browser, max_results=3, wait_time=5):
    """Extract search results from the page."""
    results = []
    
    # Wait for results to load
    time.sleep(wait_time)
    
    # Try to find result elements using common selectors
    result_selectors = [
        "article", 
        ".result", 
        ".search-result", 
        ".gs_ri",  # Google Scholar
        ".gs_r",   # Google Scholar
        ".g",      # Google
        ".rc",     # Google
        "li.b_algo", # Bing
        ".result__body", # DuckDuckGo
        ".paper-result", # Research papers
        ".document-result",
        ".serp-item",  # Semantic Scholar
        ".search-result-item",
        ".result-item",
        ".paper-card"
    ]
    
    result_elements = []
    for selector in result_selectors:
        try:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                result_elements = elements[:max_results]
                break
        except Exception:
            continue
    
    # If no results found with specific selectors, try a more generic approach
    if not result_elements:
        try:
            # Look for elements with links, which are often search results
            elements = browser.find_elements(By.TAG_NAME, "a")
            filtered_elements = []
            
            for element in elements:
                # Filter out navigation links, which are usually shorter
                if element.text and len(element.text) > 20:
                    filtered_elements.append(element)
            
            result_elements = filtered_elements[:max_results]
        except Exception:
            pass
    
    # Extract data from result elements
    for element in result_elements:
        try:
            result = {}
            
            # Try to extract title
            try:
                title_element = element.find_element(By.CSS_SELECTOR, "h3, h4, .title, [class*='title']")
                result["title"] = title_element.text
            except NoSuchElementException:
                result["title"] = element.text.split("\n")[0] if element.text else "Unknown Title"
            
            # Try to extract link
            try:
                if element.tag_name == "a":
                    result["link"] = element.get_attribute("href")
                else:
                    link_element = element.find_element(By.TAG_NAME, "a")
                    result["link"] = link_element.get_attribute("href")
            except NoSuchElementException:
                result["link"] = ""
            
            # Try to extract authors
            try:
                author_selectors = [".author", ".authors", "[class*='author']", ".contributor", ".contributors"]
                for selector in author_selectors:
                    try:
                        author_element = element.find_element(By.CSS_SELECTOR, selector)
                        result["authors"] = author_element.text
                        break
                    except NoSuchElementException:
                        continue
            except Exception:
                pass
            
            # Try to extract year/date
            try:
                year_selectors = [".year", ".date", "[class*='year']", "[class*='date']", ".pubdate"]
                for selector in year_selectors:
                    try:
                        year_element = element.find_element(By.CSS_SELECTOR, selector)
                        result["year"] = year_element.text
                        break
                    except NoSuchElementException:
                        continue
            except Exception:
                pass
            
            # Try to extract snippet
            try:
                snippet_selectors = [".snippet", ".abstract", ".summary", ".description", ".gs_rs", ".paper-abstract"]
                for selector in snippet_selectors:
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, selector)
                        result["snippet"] = snippet_element.text
                        break
                    except NoSuchElementException:
                        continue
                
                if "snippet" not in result:
                    # Use the full text as snippet if no specific snippet element found
                    full_text = element.text
                    title = result.get("title", "")
                    if full_text and title in full_text:
                        result["snippet"] = full_text.replace(title, "", 1).strip()
                    else:
                        result["snippet"] = full_text
            except Exception:
                result["snippet"] = ""
            
            results.append(result)
        except Exception as e:
            print(f"Error extracting data from result element: {e}")
    
    return results

def display_results(results):
    """Display the search results."""
    if not results:
        print("\nNo results found.")
        return
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        
        if 'authors' in result and result['authors']:
            print(f"Authors: {result['authors']}")
            
        if 'year' in result and result['year']:
            print(f"Year: {result['year']}")
        
        if 'link' in result and result['link']:
            print(f"Link: {result['link']}")
            
        if 'snippet' in result and result['snippet']:
            snippet = result['snippet']
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            print(f"Snippet: {snippet}")

def save_results(results, output_file):
    """Save the results to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"\nError saving results to {output_file}: {e}")

def take_screenshot(browser, filename):
    """Take a screenshot of the current page."""
    try:
        browser.save_screenshot(filename)
        print(f"Screenshot saved to {filename}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def main():
    """Main function to run the search."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate website URL
    if not args.website.startswith(('http://', 'https://')):
        print("Error: Website URL must start with http:// or https://")
        sys.exit(1)
    
    # Extract domain for display
    domain = urlparse(args.website).netloc
    
    print(f"Searching {domain} for: '{args.query}'")
    print(f"Max results: {args.max_results}")
    print(f"Browser: {args.browser}")
    print(f"Headless mode: {'Yes' if args.headless else 'No'}")
    print(f"Timeout: {args.timeout} seconds")
    print(f"Wait time: {args.wait} seconds")
    print(f"Output file: {args.output if args.output else 'None'}")
    print(f"Screenshot: {args.screenshot if args.screenshot else 'None'}")
    print("-" * 50)
    
    browser = None
    try:
        # Set up the browser
        browser = setup_browser(browser_type=args.browser, headless=args.headless)
        
        # Navigate to the website
        print(f"Navigating to {args.website}...")
        browser.get(args.website)
        
        # Wait for the page to load
        wait_for_page_load(browser, timeout=args.timeout)
        time.sleep(args.wait)
        
        # Take a screenshot if requested
        if args.screenshot:
            take_screenshot(browser, args.screenshot)
        
        # Find the search input field
        print("Looking for search input field...")
        search_input = find_search_input(browser)
        
        if not search_input:
            print("Error: Could not find search input field on the page.")
            return
        
        # Enter the search query
        print(f"Entering search query: {args.query}")
        search_input.clear()
        search_input.send_keys(args.query)
        
        # Find and click the search button
        print("Looking for search button...")
        search_button = find_search_button(browser)
        
        # Submit the search
        print("Submitting search...")
        if search_button and safe_click(browser, search_button):
            print("Clicked search button")
        else:
            # If no search button found or click failed, try pressing Enter
            print("No search button found or click failed, trying Enter key")
            search_input.send_keys(Keys.RETURN)
        
        # Wait for results page to load
        wait_for_page_load(browser, timeout=args.timeout)
        
        # Take another screenshot if requested
        if args.screenshot:
            results_screenshot = args.screenshot.replace('.', '_results.')
            take_screenshot(browser, results_screenshot)
        
        # Extract search results
        print(f"Extracting up to {args.max_results} search results...")
        results = extract_search_results(browser, max_results=args.max_results, wait_time=args.wait)
        
        # Display the results
        display_results(results)
        
        # Save the results if an output file is specified
        if args.output:
            save_results(results, args.output)
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"\nError during search: {e}")
        if browser and args.screenshot:
            error_screenshot = args.screenshot.replace('.', '_error.')
            take_screenshot(browser, error_screenshot)
    finally:
        # Close the browser
        if browser:
            browser.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
        sys.exit(0) 