#!/usr/bin/env python3
"""
Interactive script for web searching.
This script provides a simple interactive interface for searching.
"""

import os
import sys
import platform
from urllib.parse import urlparse

def clear_screen():
    """Clear the terminal screen based on the operating system."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_header(title):
    """Print a formatted header."""
    clear_screen()
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)
    print()

def get_search_query():
    """Get the search query from the user."""
    while True:
        query = input("Enter your search query: ").strip()
        if query:
            return query
        print("Please enter a valid search query.")

def select_search_type():
    """Let the user select the type of search to perform."""
    print("\nSelect search type:")
    print("1. Academic search")
    print("2. General web search")
    print("3. Custom website search")
    print("4. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if 1 <= choice <= 4:
                return choice
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")

def get_max_results():
    """Get the maximum number of results from the user."""
    while True:
        try:
            max_results = int(input("Enter maximum number of results (1-20): "))
            if 1 <= max_results <= 20:
                return max_results
            print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")

def get_custom_website():
    """Get a custom website URL from the user."""
    while True:
        website = input("Enter website URL (including https://): ").strip()
        if website.startswith(('http://', 'https://')):
            try:
                domain = urlparse(website).netloc
                if domain:
                    return website, domain
                print("Invalid URL. Please include a valid domain.")
            except Exception:
                print("Invalid URL format. Please try again.")
        else:
            print("URL must start with http:// or https://")

def main():
    """Main function to run the interactive search."""
    try:
        while True:
            print_header("Interactive Web Search")
            
            # Get search query
            query = get_search_query()
            
            # Select search type
            search_type = select_search_type()
            if search_type == 4:  # Exit
                print("\nExiting program...")
                break
            
            # Get maximum results
            max_results = get_max_results()
            
            # Get custom website if needed
            website = None
            if search_type == 3:  # Custom website search
                website, domain = get_custom_website()
                print(f"\nSelected website: {domain}")
            
            # Inform the user that real search functionality requires the web_scraper package
            print("\nThis interactive script does not include real search functionality.")
            print("To perform actual web searches, you need to install the web_scraper package.")
            print("Please refer to the README.md file for installation instructions.")
            print("\nAlternatively, you can use the search_any_website.py script which includes")
            print("the necessary functionality to search real websites.")
            
            # Ask if user wants to continue
            continue_search = input("\nDo you want to try another search? (y/n): ").lower()
            if continue_search not in ['y', 'yes']:
                print("\nExiting program...")
                break
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    print("\nThank you for using the Interactive Web Search!")

if __name__ == "__main__":
    main() 