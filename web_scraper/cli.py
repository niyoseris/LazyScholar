#!/usr/bin/env python3
"""
Command-line interface for the web scraper.
"""

import argparse
import json
import logging
import sys
from typing import Dict, Any, List

from web_scraper import search_academic_databases
from web_scraper.config import get_default_settings, update_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Web scraper for academic research",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "query",
        help="Search query or topic"
    )
    
    parser.add_argument(
        "--engines",
        nargs="+",
        choices=["google_scholar", "research_gate"],
        default=["google_scholar"],
        help="Search engines to use"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to retrieve"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for browser operations"
    )
    
    parser.add_argument(
        "--pdf-download",
        action="store_true",
        help="Download PDFs when available"
    )
    
    parser.add_argument(
        "--output",
        help="Output file to save results (JSON format)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def setup_logging(verbose: bool) -> None:
    """Set up logging based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add the new handler
    root_logger.addHandler(console_handler)

def save_results(results: List[Dict[str, Any]], output_file: str) -> None:
    """Save results to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to {output_file}: {e}")

def display_results(results: List[Dict[str, Any]]) -> None:
    """Display results in the console."""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result['title']}")
        print(f"Authors: {result['authors']}")
        print(f"Year: {result.get('year', 'N/A')}")
        print(f"Source: {result.get('source', 'N/A')}")
        print(f"Link: {result.get('link', 'N/A')}")
        if 'snippet' in result and result['snippet']:
            print(f"Snippet: {result['snippet'][:150]}...")

def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Get default settings and update with command-line arguments
    settings = get_default_settings()
    custom_settings = {
        "engines": args.engines,
        "max_results": args.max_results,
        "headless": args.headless,
        "timeout": args.timeout,
        "pdf_download": args.pdf_download,
        "save_to_file": bool(args.output),
    }
    # Update the settings dictionary directly
    settings.update(custom_settings)
    
    # Log the settings
    logger.debug(f"Using settings: {settings}")
    
    try:
        # Perform the search
        logger.info(f"Searching for query: {args.query}")
        results = search_academic_databases(args.query, settings)
        
        # Display the results
        display_results(results)
        
        # Save the results if an output file is specified
        if args.output:
            save_results(results, args.output)
        
        return 0
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=args.verbose)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 