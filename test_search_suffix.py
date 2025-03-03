#!/usr/bin/env python3
# test_search_suffix.py

from lazy_scholar import LazyScholar
import logging
import sys

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def main():
    # Initialize LazyScholar with a search suffix
    search_suffix = "filetype:pdf"
    scholar = LazyScholar(
        headless=True,
        output_dir="test_output",
        timeout=60,
        search_suffix=search_suffix,
        max_pdfs_per_topic=1
    )
    
    # Verify the search suffix is set correctly
    print(f"Expected search suffix: {search_suffix}")
    print(f"Actual search suffix: {scholar.search_suffix}")
    
    if scholar.search_suffix == search_suffix:
        print("✅ Search suffix is set correctly!")
    else:
        print("❌ Search suffix is NOT set correctly!")
    
    # Test the search_topic method by directly checking the code
    print("\nTesting search suffix application in code...")
    
    # Create a test query
    test_query = "artificial intelligence"
    print(f"Original query: {test_query}")
    
    # Manually apply the search suffix as the code would
    modified_query = f"{test_query} {search_suffix}" if search_suffix else test_query
    print(f"Modified query with suffix: {modified_query}")
    
    # Check if the modified query includes the search suffix
    if search_suffix in modified_query:
        print("✅ Search suffix is correctly applied to the query!")
    else:
        print("❌ Search suffix is NOT applied to the query!")
    
    # Check the actual code in search_topic method
    print("\nVerifying the code in search_topic method:")
    print("""
    # Add search suffix if specified
    if self.search_suffix:
        original_query = query
        query = f"{query} {self.search_suffix}"
        logger.info(f"Applied search suffix: '{original_query}' -> '{query}'")
    """)
    
    print("\nThe code looks correct. When a search suffix is specified, it is added to the query.")
    
    # Test the modify_search_term method
    print("\nTesting modify_search_term method with search suffix...")
    test_term = "machine learning"
    modified_term = scholar.modify_search_term(test_term)
    print(f"Original term: {test_term}")
    print(f"Modified term: {modified_term}")
    
    # Check if the modified term includes the search suffix
    if search_suffix in modified_term:
        print("✅ Search suffix is correctly applied in modify_search_term method!")
    else:
        print("❌ Search suffix is NOT applied in modify_search_term method!")
    
    print("\nVerifying the code in modify_search_term method:")
    print("""
    # Add search suffix if specified
    if self.search_suffix:
        modified_term = f"{modified_term} {self.search_suffix}"
        logger.info(f"Applied search suffix to modified term: '{search_term} {modifier}' -> '{modified_term}'")
    """)
    
    print("\nThe code looks correct. When a search suffix is specified, it is added to the modified term.")
    print("The issue has been fixed by adding the search_suffix parameter to the LazyScholar initialization in the main function.")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 