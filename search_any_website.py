#!/usr/bin/env python3
"""
Script to demonstrate how to use the AI-powered custom website search.
This script allows searching any website using AI vision to detect search elements.
"""

import sys
import json
import argparse
from typing import Dict, Any, List
from urllib.parse import urlparse

# Try to import from the web_scraper package
try:
    # First try to import from the installed package
    from web_scraper.ai_engines import custom_search
    from web_scraper.config import get_default_settings
except ImportError:
    # If that fails, try to import from the local directory
    sys.path.append('.')
    try:
        from web_scraper.ai_engines import custom_search
        from web_scraper.config import get_default_settings
    except ImportError:
        print("Error: web_scraper package not found.")
        print("Please make sure you have installed the package with 'pip install -e .'")
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Search any website using AI vision.")
    parser.add_argument("query", help="The search query")
    parser.add_argument("website", help="The website URL to search (including https://)")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of results to retrieve (default: 5)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--output", help="Output file path (JSON)")
    
    return parser.parse_args()

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

def main():
    """Main function to run the custom website search."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate website URL
    if not args.website.startswith(('http://', 'https://')):
        print("Error: Website URL must start with http:// or https://")
        sys.exit(1)
    
    # Extract domain for display
    domain = urlparse(args.website).netloc
    
    # Prepare settings
    settings = get_default_settings()
    settings.update({
        "max_results": args.max_results,
        "headless": args.headless,
        "use_ai_vision": True,
        "ai_model": "gemini-flash-2.0"
    })
    
    print(f"Searching {domain} for: '{args.query}'")
    print(f"Max results: {args.max_results}")
    print(f"Headless mode: {'Yes' if args.headless else 'No'}")
    print(f"Output file: {args.output if args.output else 'None'}")
    print("-" * 50)
    
    try:
        # Use AI-powered custom website search
        results = custom_search.search(args.query, args.website, settings)
        
        # Display the results
        display_results(results)
        
        # Save the results if an output file is specified
        if args.output:
            save_results(results, args.output)
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"\nError during search: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
        sys.exit(0) 