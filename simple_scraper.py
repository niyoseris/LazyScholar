#!/usr/bin/env python3
"""
Simple interactive wrapper for the web scraper.
This script provides a user-friendly interface to scrape various websites without requiring command-line arguments.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
from urllib.parse import urlparse

# Ensure the web_scraper package is available
try:
    from web_scraper import search_academic_databases
    from web_scraper.config import get_default_settings
    from web_scraper.browser import setup_browser, close_browser
except ImportError:
    print("Error: web_scraper package not found.")
    print("Please make sure you have installed the package with 'pip install -e .'")
    sys.exit(1)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 80)
    print("AI-Powered Web Scraper - Interactive Mode".center(80))
    print("=" * 80)
    print()

def get_search_query():
    """Get the search query from the user."""
    while True:
        query = input("Enter your search query: ").strip()
        if query:
            return query
        print("Error: Search query cannot be empty. Please try again.")

def select_search_type():
    """Let the user select what type of search to perform."""
    print("\nWhat would you like to search?")
    print("1. Academic databases (Google Scholar, ResearchGate)")
    print("2. General web search (DuckDuckGo)")
    print("3. ArXiv papers")
    print("4. Any website (AI-powered)")
    
    while True:
        choice = input("\nSelect search type (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return int(choice)
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def get_custom_website():
    """Get the custom website URL from the user."""
    print("\nAI-powered website search can work with most websites that have a search function.")
    print("The AI will automatically detect search elements and extract results.")
    
    while True:
        url = input("\nEnter the website URL (including https://): ").strip()
        if url and (url.startswith('http://') or url.startswith('https://')):
            # Extract domain for display
            domain = urlparse(url).netloc
            print(f"\nUsing AI to search {domain}...")
            return url
        print("Please enter a valid URL starting with http:// or https://")

def get_max_results():
    """Get the maximum number of results to retrieve."""
    while True:
        try:
            max_results = int(input("\nEnter maximum number of results (1-50): ").strip())
            if 1 <= max_results <= 50:
                return max_results
            print("Please enter a number between 1 and 50.")
        except ValueError:
            print("Please enter a valid number.")

def get_yes_no(prompt):
    """Get a yes/no response from the user."""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'.")

def get_output_file():
    """Get the output file path from the user."""
    while True:
        file_path = input("\nEnter output file path (or press Enter to skip saving): ").strip()
        if not file_path:
            return None
        
        # Check if the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            print(f"Directory '{directory}' does not exist. Please enter a valid path.")
            continue
        
        # Check if the file has a .json extension
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        return file_path

def display_results(results):
    """Display the search results."""
    if not results:
        print("\nNo results found.")
        return
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        
        # Handle different result formats
        if 'authors' in result:
            print(f"Authors: {result['authors']}")
        
        if 'year' in result:
            print(f"Year: {result['year']}")
            
        if 'source' in result:
            print(f"Source: {result['source']}")
            
        if 'link' in result:
            print(f"Link: {result['link']}")
            
        if 'snippet' in result and result['snippet']:
            print(f"Snippet: {result['snippet'][:150]}...")
            
        # For custom websites that might have different fields
        for key, value in result.items():
            if key not in ['title', 'authors', 'year', 'source', 'link', 'snippet'] and value:
                print(f"{key.capitalize()}: {value}")

def save_results(results, output_file):
    """Save the results to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"\nError saving results to {output_file}: {e}")

def perform_search(query, search_type, settings, custom_website=None):
    """Perform the search based on the selected search type."""
    try:
        if search_type == 1:  # Academic databases
            # Use AI-powered academic search
            try:
                from web_scraper.ai_engines import academic_search
                return academic_search.search(query, settings)
            except (ImportError, AttributeError):
                print("\nError: AI academic search module not found.")
                raise
            
        elif search_type == 2:  # General web search
            # Use AI-powered web search
            try:
                from web_scraper.ai_engines import web_search
                return web_search.search(query, settings)
            except (ImportError, AttributeError):
                print("\nError: AI web search module not found.")
                raise
                
        elif search_type == 3:  # ArXiv papers
            # Use AI-powered ArXiv search
            try:
                from web_scraper.ai_engines import arxiv_search
                return arxiv_search.search(query, settings)
            except (ImportError, AttributeError):
                print("\nError: AI ArXiv search module not found.")
                raise
                
        elif search_type == 4:  # Custom website with AI
            if not custom_website:
                raise ValueError("Custom website URL is required for this search type")
                
            # Use AI-powered custom website search
            try:
                from web_scraper.ai_engines import custom_search
                return custom_search.search(query, custom_website, settings)
            except (ImportError, AttributeError):
                print("\nError: AI custom search module not found.")
                raise
        
        else:
            raise ValueError(f"Invalid search type: {search_type}")
            
    except Exception as e:
        print(f"\nError during search: {e}")
        raise

def main():
    """Main function to run the interactive web scraper."""
    print_header()
    
    # Get search query
    query = get_search_query()
    
    # Get search type
    search_type = select_search_type()
    
    # Get custom website URL if needed
    custom_website = None
    if search_type == 4:
        custom_website = get_custom_website()
    
    # Get max results
    max_results = get_max_results()
    
    # Get headless mode preference
    headless = get_yes_no("\nRun browser in headless mode (invisible)?")
    
    # Get output file
    output_file = get_output_file()
    
    # Prepare settings
    settings = get_default_settings()
    settings.update({
        "max_results": max_results,
        "headless": headless,
        "save_to_file": bool(output_file),
        "use_ai_vision": True,  # Enable AI vision capabilities
        "ai_model": "gemini-flash-2.0"  # Specify the AI model to use
    })
    
    # Add search type specific settings
    if search_type == 1:
        settings["pdf_download"] = get_yes_no("\nDownload PDFs when available?")
    
    print("\nStarting search with the following settings:")
    print(f"  Query: {query}")
    print(f"  Search type: {['Academic databases', 'General web search', 'ArXiv papers', 'Any website (AI-powered)'][search_type-1]}")
    if search_type == 4:
        print(f"  Website: {custom_website}")
    print(f"  Max results: {max_results}")
    print(f"  Headless mode: {'Yes' if headless else 'No'}")
    if search_type == 1:
        print(f"  PDF download: {'Yes' if settings.get('pdf_download', False) else 'No'}")
    print(f"  Using AI vision: Yes (Gemini Flash 2.0)")
    print(f"  Output file: {output_file if output_file else 'None'}")
    
    # Confirm before proceeding
    if not get_yes_no("\nProceed with these settings?"):
        print("\nSearch cancelled. Exiting...")
        return
    
    print("\nSearching... This may take a while.")
    
    try:
        # Perform the search
        results = perform_search(query, search_type, settings, custom_website)
        
        # Display the results
        display_results(results)
        
        # Save the results if an output file is specified
        if output_file:
            save_results(results, output_file)
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"\nError during search: {e}")
    
    # Ask if the user wants to perform another search
    if get_yes_no("\nWould you like to perform another search?"):
        main()  # Restart the process
    else:
        print("\nThank you for using the AI-Powered Web Scraper. Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
        sys.exit(0) 