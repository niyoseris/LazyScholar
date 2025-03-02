#!/usr/bin/env python3
"""
Wrapper script for the AI search tool.
This script provides a more user-friendly interface for the simple_ai_search.py script.
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Search any website using AI-powered tools.")
    parser.add_argument("query", help="The search query")
    parser.add_argument("--website", default="https://scholar.google.com", 
                        help="The website URL to search (default: https://scholar.google.com)")
    parser.add_argument("--max-results", type=int, default=5, 
                        help="Maximum number of results to retrieve (default: 5)")
    parser.add_argument("--headless", action="store_true", 
                        help="Run browser in headless mode")
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="firefox", 
                        help="Browser to use (default: firefox)")
    parser.add_argument("--timeout", type=int, default=30, 
                        help="Timeout in seconds for page loading (default: 30)")
    parser.add_argument("--wait", type=int, default=3, 
                        help="Wait time in seconds after page loads (default: 3)")
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug mode with screenshots")
    parser.add_argument("--save", action="store_true", 
                        help="Save results to a JSON file")
    parser.add_argument("--output-dir", default="search_results", 
                        help="Directory to save results (default: search_results)")
    
    return parser.parse_args()

def ensure_directory(directory):
    """Ensure the directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def generate_filename(query, website, extension=".json"):
    """Generate a filename based on the query and website."""
    # Clean the query and website for use in a filename
    query = query.replace(" ", "_").lower()
    website = website.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{query}_{website}_{timestamp}{extension}"

def main():
    """Main function to run the search wrapper."""
    args = parse_arguments()
    
    # Prepare output directory if saving results
    if args.save or args.debug:
        output_dir = ensure_directory(args.output_dir)
    
    # Prepare command
    command = [
        "python", "simple_ai_search.py",
        args.query,
        args.website,
        "--max-results", str(args.max_results),
        "--browser", args.browser,
        "--timeout", str(args.timeout),
        "--wait", str(args.wait)
    ]
    
    # Add headless mode if specified
    if args.headless:
        command.append("--headless")
    
    # Add screenshot option if in debug mode
    if args.debug:
        screenshot_file = os.path.join(output_dir, generate_filename(args.query, args.website, ".png"))
        command.extend(["--screenshot", screenshot_file])
    
    # Add output option if saving results
    if args.save:
        output_file = os.path.join(output_dir, generate_filename(args.query, args.website))
        command.extend(["--output", output_file])
    
    # Print the command being run
    print("Running command:", " ".join(command))
    print("-" * 80)
    
    # Run the command
    try:
        result = subprocess.run(command, check=True, text=True)
        
        # Print a summary if results were saved
        if args.save:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                print("\nSummary of saved results:")
                print(f"- Query: {args.query}")
                print(f"- Website: {args.website}")
                print(f"- Results found: {len(results)}")
                print(f"- Results saved to: {output_file}")
            except Exception as e:
                print(f"Error reading saved results: {e}")
        
        # Print debug information
        if args.debug:
            print("\nDebug Information:")
            print(f"- Screenshots saved to: {screenshot_file}")
            if os.path.exists(screenshot_file.replace('.', '_results.')):
                print(f"- Results page screenshot: {screenshot_file.replace('.', '_results.')}")
            if os.path.exists(screenshot_file.replace('.', '_error.')):
                print(f"- Error page screenshot: {screenshot_file.replace('.', '_error.')}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error running search: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main() 