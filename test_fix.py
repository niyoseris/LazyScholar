#!/usr/bin/env python3
"""
Test script to verify the fix for the TypeError in identify_new_topics
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Test the identify_new_topics function with mixed input"""
    load_dotenv()
    
    # Import the necessary modules
    sys.path.append(os.getcwd())
    import content_analyzer
    
    # Create test data
    test_topics = [
        {"topic": "Test Topic 1", "subtopics": ["Subtopic 1", "Subtopic 2"]},
        {"topic": "Test Topic 2", "subtopics": ["Subtopic 3", "Subtopic 4"]}
    ]
    
    # Test Case 1: Empty list
    test_papers_empty = []
    print("Test with empty papers list:")
    result1 = content_analyzer.identify_new_topics(test_papers_empty, test_topics)
    print(f"Result: {result1}")
    
    # Test Case 2: List with dictionary having key_findings
    test_papers_dict = [
        {"title": "Paper 1", "key_findings": ["Finding 1", "Finding 2"]},
        {"title": "Paper 2", "key_findings": "Single finding string"}
    ]
    print("\nTest with dictionary papers:")
    result2 = content_analyzer.identify_new_topics(test_papers_dict, test_topics)
    print(f"Result: {result2}")
    
    # Test Case 3: List with string (previously caused error)
    test_papers_mixed = [
        {"title": "Paper 1", "key_findings": ["Finding 1", "Finding 2"]},
        "This is a string paper"
    ]
    print("\nTest with mixed papers (dict and string):")
    result3 = content_analyzer.identify_new_topics(test_papers_mixed, test_topics)
    print(f"Result: {result3}")
    
    print("\nAll tests completed. If no errors appear, the fix is working.")

if __name__ == "__main__":
    main()
