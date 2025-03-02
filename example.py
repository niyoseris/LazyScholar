#!/usr/bin/env python3
"""
Example script demonstrating how to use the modular web scraper.
"""

import logging
from web_scraper import search_academic_databases
from web_scraper.config import get_default_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_basic_search():
    """
    Example of a basic search using the default settings.
    """
    print("\n=== Basic Search Example ===")
    
    # Define your search query
    search_query = "machine learning applications in healthcare"
    
    # Get default settings
    settings = get_default_settings()
    
    # For demonstration purposes, we'll just show the settings
    # To perform an actual search, uncomment the search_academic_databases line
    print(f"Searching for: '{search_query}'...")
    print("Settings:")
    print(f"  Engines: {settings.get('engines', ['google_scholar'])}")
    print(f"  Max results: {settings.get('max_results', 10)}")
    print(f"  Headless mode: {settings.get('headless', True)}")
    
    # Uncomment to perform actual search
    # results = search_academic_databases(search_query, settings)
    
    print("\nTo perform an actual search, uncomment the search_academic_databases line in the code.")

def example_advanced_search():
    """
    Example of an advanced search with custom settings.
    """
    print("\n=== Advanced Search Example ===")
    
    # Define your search query
    search_query = "quantum computing algorithms"
    
    # Get default settings and update them
    settings = get_default_settings()
    
    # Update settings manually
    settings["engines"] = ["google_scholar"]  # Only use Google Scholar
    settings["max_results"] = 3               # Limit to 3 results
    settings["headless"] = True               # Run in headless mode
    settings["timeout"] = 30                  # Set timeout to 30 seconds
    settings["pdf_download"] = False          # Don't download PDFs
    settings["save_to_file"] = False          # Don't save results to file
    
    # For demonstration purposes, we'll just show the settings
    # To perform an actual search, uncomment the search_academic_databases line
    print(f"Searching for: '{search_query}' with custom settings...")
    print("Settings:")
    print(f"  Engines: {settings['engines']}")
    print(f"  Max results: {settings['max_results']}")
    print(f"  Headless mode: {settings['headless']}")
    print(f"  Timeout: {settings['timeout']} seconds")
    print(f"  PDF download: {settings['pdf_download']}")
    
    # Uncomment to perform actual search
    # results = search_academic_databases(search_query, settings)
    
    print("\nTo perform an actual search, uncomment the search_academic_databases line in the code.")

def example_real_search():
    """
    Example of a real search using the web scraper.
    Note: This will actually perform web scraping and may trigger CAPTCHAs.
    """
    print("\n=== Real Search Example ===")
    print("Note: This will perform actual web scraping and may trigger CAPTCHAs.")
    
    # Define your search query
    search_query = "climate change mitigation strategies"
    
    # Get default settings and update them
    settings = get_default_settings()
    
    # Update settings manually
    settings["engines"] = ["google_scholar"]
    settings["max_results"] = 3
    settings["headless"] = False  # Set to False to see the browser
    settings["timeout"] = 60
    settings["pdf_download"] = False
    
    # Perform the search
    print(f"Searching for: '{search_query}'...")
    results = search_academic_databases(search_query, settings)
    
    # Display the results
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result['title']}")
        print(f"Authors: {result['authors']}")
        print(f"Year: {result['year']}")
        print(f"Source: {result['source']}")
        print(f"Link: {result['link']}")
        print(f"Snippet: {result['snippet'][:100]}...")

def main():
    """Main function to run the examples."""
    print("\n" + "="*80)
    print("Web Scraper Usage Examples".center(80))
    print("="*80)
    
    # Run the examples
    example_basic_search()
    example_advanced_search()
    example_real_search()
    
    print("\n" + "="*80)
    print("End of Examples".center(80))
    print("="*80)

if __name__ == "__main__":
    main() 