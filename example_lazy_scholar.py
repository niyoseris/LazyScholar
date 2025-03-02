#!/usr/bin/env python3
"""
Example script demonstrating how to use the LazyScholar application.
"""

import os
import logging
from lazy_scholar import LazyScholar

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_topic_generation():
    """
    Example of generating topics and subtopics from a problem statement.
    """
    print("\n=== Topic Generation Example ===")
    
    # Create LazyScholar instance
    scholar = LazyScholar(headless=True)
    
    # Define a problem statement
    problem_statement = "The impact of artificial intelligence on healthcare delivery and patient outcomes"
    
    # Generate topics and subtopics
    print(f"Analyzing problem statement: '{problem_statement}'...")
    topics = scholar.analyze_problem_statement(problem_statement)
    
    # Display the generated topics and subtopics
    print("\nGenerated Topics and Subtopics:")
    for i, topic in enumerate(topics, 1):
        print(f"\nTopic {i}: {topic['topic']}")
        for j, subtopic in enumerate(topic['subtopics'], 1):
            print(f"  Subtopic {i}.{j}: {subtopic}")

def example_search_topic():
    """
    Example of searching for a topic on Google Scholar.
    """
    print("\n=== Topic Search Example ===")
    
    # Create LazyScholar instance
    scholar = LazyScholar(headless=False)  # Set to False to see the browser
    
    try:
        # Define a topic to search for
        topic = "machine learning applications in healthcare"
        
        # Search for the topic
        print(f"Searching for topic: '{topic}'...")
        results = scholar.search_topic(topic)
        
        # Display the search results
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"Authors: {result.get('authors', 'N/A')}")
            print(f"Year: {result.get('year', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            if 'description' in result:
                print(f"Description: {result['description'][:100]}...")
    finally:
        # Close the browser
        scholar.close_browser()

def example_mini_research():
    """
    Example of conducting a mini research on a single topic.
    """
    print("\n=== Mini Research Example ===")
    
    # Create LazyScholar instance with custom output directory
    output_dir = "mini_research_output"
    scholar = LazyScholar(headless=False, output_dir=output_dir)
    
    try:
        # Define a problem statement
        problem_statement = "The effectiveness of telemedicine during the COVID-19 pandemic"
        
        # Generate topics and subtopics
        print(f"Analyzing problem statement: '{problem_statement}'...")
        topics = scholar.analyze_problem_statement(problem_statement)
        
        if topics:
            # Take just the first topic for this mini example
            topic = topics[0]["topic"]
            subtopics = topics[0]["subtopics"]
            
            print(f"\nResearching topic: {topic}")
            print(f"Subtopics: {', '.join(subtopics)}")
            
            # Search for the topic
            results = scholar.search_topic(topic)
            
            # Process the first result only for this example
            if results:
                result = results[0]
                url = result.get("url", "")
                
                if url:
                    print(f"\nDownloading PDF from: {url}")
                    pdf_path = scholar.download_pdf(url)
                    
                    if pdf_path:
                        print(f"PDF downloaded to: {pdf_path}")
                        
                        # Extract content for the first subtopic
                        subtopic = subtopics[0]
                        print(f"\nExtracting content for subtopic: {subtopic}")
                        content = scholar.extract_pdf_content(pdf_path, topic, subtopic)
                        
                        # Write subtopic file
                        file_path = scholar.write_subtopic_file(topic, subtopic, content)
                        print(f"Subtopic file written to: {file_path}")
                    else:
                        print("Failed to download PDF")
                else:
                    print("No URL found in the search result")
            else:
                print("No search results found")
        else:
            print("No topics generated")
    finally:
        # Close the browser
        scholar.close_browser()

def main():
    """Main function to run the examples."""
    print("\n" + "="*80)
    print("LazyScholar Usage Examples".center(80))
    print("="*80)
    
    # Run the examples
    example_topic_generation()
    example_search_topic()
    example_mini_research()
    
    print("\n" + "="*80)
    print("End of Examples".center(80))
    print("="*80)

if __name__ == "__main__":
    main() 