#!/usr/bin/env python3
"""
Test script to verify improvements to the research results generation.
"""

import os
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("research_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import modules from the research assistant
from main import save_subtopic_results
from content_analyzer import extract_paper_information

def test_author_formatting():
    """Test the improved author formatting."""
    
    # Test data with problematic author formatting
    paper_result = {
        'title': 'Test Paper',
        'authors': ['T', ' ', 'Z', 'a', 'c', 'h', 'a', 'r', 'i', 'a', 'd', 'i', 's'],
        'year': '2023',
        'url': 'https://example.com/paper',
        'snippet': 'This is a test paper about climate change impacts on ecosystems.',
    }
    
    # Extract paper information using the improved function
    paper_info = extract_paper_information(paper_result)
    
    # Print the results
    print("\n=== EXTRACTED PAPER INFORMATION ===")
    print(f"Title: {paper_info.get('title')}")
    print(f"Authors: {paper_info.get('authors')}")
    print(f"Key Findings: {paper_info.get('key_findings')}")
    print(f"Cited Authors: {paper_info.get('cited_authors')}")
    
    return paper_info

def test_save_results(paper_info):
    """Test saving results with improved formatting."""
    
    # Create test aggregated findings
    aggregate_findings = {
        'key_findings': ['Finding 1', 'Finding 2'],
        'methodologies': ['Method 1', 'Method 2'],
        'research_gaps': ['Gap 1', 'Unknown'],
        'theoretical_frameworks': ['Framework 1', 'Unknown'],
        'cited_authors': ['Author 1', 'Author 2', 'Unknown'],
    }
    
    # Create a list with the test paper
    analyzed_papers = [paper_info]
    
    # Save the results
    save_subtopic_results(
        subtopic="Test Improvements",
        parent_topic="Research Quality",
        aggregate_findings=aggregate_findings,
        analyzed_papers=analyzed_papers
    )
    
    print("\n=== RESULTS SAVED ===")
    print("Check the research_results folder for the generated file.")

def main():
    """Main function to run the tests."""
    
    # Load environment variables
    load_dotenv()
    
    # Test author formatting
    paper_info = test_author_formatting()
    
    # Test saving results
    test_save_results(paper_info)

if __name__ == "__main__":
    main()
