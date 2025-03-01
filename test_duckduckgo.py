#!/usr/bin/env python3
import sys
import logging
import time
import argparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import geckodriver_autoinstaller

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
try:
    import web_scraper
except ImportError:
    logger.error("Failed to import web_scraper module")
    sys.exit(1)

def setup_firefox_browser(headless=False):
    """Set up a Firefox browser for testing."""
    try:
        # Install geckodriver if needed
        geckodriver_autoinstaller.install()
        
        # Set up Firefox options
        options = Options()
        if headless:
            options.add_argument("--headless")
            
        # Set up DuckDuckGo specific options
        options.set_preference("general.useragent.override", 
                             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0 DuckDuckGo/1.0")
        options.set_preference("browser.privatebrowsing.autostart", True)
        
        # Create Firefox browser
        browser = webdriver.Firefox(options=options)
        
        # Disable webdriver flag to avoid detection
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return browser
    except Exception as e:
        logger.error(f"Failed to set up Firefox browser: {e}")
        return None

def test_duckduckgo_search(headless=False, search_term=None, prioritize_pdf=True, max_results=5):
    """Test the DuckDuckGo search functionality."""
    print("\n=== Testing DuckDuckGo Search with PDF Priority ===\n")
    
    browser = None
    try:
        # Set up browser
        browser = setup_firefox_browser(headless=headless)
        if not browser:
            logger.error("Browser setup failed")
            return
        
        # Test search
        if search_term is None:
            search_term = "python programming filetype:pdf"
        
        logger.info(f"Searching for: {search_term}")
        
        # Set search settings
        settings = {
            'prioritize_pdf': prioritize_pdf,
            'max_results': max_results,
            'debug': True
        }
        
        # Use the search_duckduckgo function from web_scraper
        results = web_scraper.search_duckduckgo(browser, search_term, settings)
        
        # Print results
        print(f"\nFound {len(results)} results:")
        
        pdf_count = 0
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print(f"   Is PDF: {result['is_pdf']}")
            
            # Print additional metadata if available
            if 'year' in result:
                print(f"   Year: {result['year']}")
            if 'authors' in result:
                print(f"   Authors: {result['authors']}")
            if 'journal' in result:
                print(f"   Journal: {result['journal']}")
            
            if result.get('is_pdf', False):
                pdf_count += 1
        
        # Print summary
        print("\n=== Summary ===")
        print(f"Total results: {len(results)}")
        print(f"PDF results: {pdf_count}")
        pdf_percentage = pdf_count / len(results) * 100 if results else 0
        print(f"% PDF: {pdf_percentage:.1f}%")
        print("==============")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return []
    finally:
        # Close browser
        if browser:
            time.sleep(1)  # Brief pause to see results
            browser.quit()
    
    print("\nTest completed.")

def test_using_built_in_browser():
    """Test using the built-in browser setup."""
    print("\n=== Testing DuckDuckGo with built-in browser setup ===\n")
    
    try:
        # Use the browser setup from web_scraper
        with web_scraper.setup_browser(headless=False, browser_type='duckduckgo') as browser:
            search_term = "machine learning pdf"
            logger.info(f"Using web_scraper's browser with search term: {search_term}")
            
            settings = {
                'prioritize_pdf': True,
                'max_results': 3,
                'debug': True
            }
            
            results = web_scraper.search_duckduckgo(browser, search_term, settings)
            
            # Print results
            print(f"\nFound {len(results)} results:")
            
            for i, result in enumerate(results):
                print(f"\n{i+1}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Is PDF: {result['is_pdf']}")
            
            print("\nTest using built-in browser completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error testing with built-in browser: {e}")
        return False

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Test DuckDuckGo search functionality')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--search', type=str, help='Search term to use', default='machine learning techniques filetype:pdf')
    parser.add_argument('--no-pdf', action='store_true', help='Do not prioritize PDF results')
    parser.add_argument('--max-results', type=int, default=5, help='Maximum number of results to return')
    parser.add_argument('--builtin-browser', action='store_true', help='Test using built-in browser setup')
    
    args = parser.parse_args()
    
    print("Starting DuckDuckGo search test...")
    
    if args.builtin_browser:
        test_using_built_in_browser()
    else:
        test_duckduckgo_search(
            headless=args.headless,
            search_term=args.search,
            prioritize_pdf=not args.no_pdf,
            max_results=args.max_results
        )
    
    print("\nAll tests completed.")
