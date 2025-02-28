#!/usr/bin/env python3
"""
Test script to verify improvements to author name formatting
"""

import sys
import re
from content_analyzer import clean_authors

def test_clean_authors():
    """Test the enhanced clean_authors function with various inputs."""
    
    test_cases = [
        # Case 1: String with ellipses
        {"input": "...", "expected": "Author information incomplete"},
        
        # Case 2: Individual characters separated by commas
        {"input": "A, B, C, D", "expected": "ABCD"},
        
        # Case 3: Normal author string
        {"input": "John Smith, Jane Doe", "expected": "John Smith, Jane Doe"},
        
        # Case 4: Empty input
        {"input": "", "expected": "Unknown"},
        
        # Case 5: None input
        {"input": None, "expected": "Unknown"},
        
        # Case 6: List of individual characters
        {"input": ["A", "B", "C"], "expected": "ABC"},
        
        # Case 7: List of authors
        {"input": ["John Smith", "Jane Doe"], "expected": "John Smith, Jane Doe"},
        
        # Case 8: List with empty or None values
        {"input": ["", None, "John Smith"], "expected": "John Smith"},
        
        # Case 9: List with punctuation
        {"input": [",", ".", "John", "Smith"], "expected": "John, Smith"},
        
        # Case 10: String with journal information
        {"input": "Smith J - Journal of Science, 2023", "expected": "Smith J"},
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        result = clean_authors(test["input"])
        if result == test["expected"]:
            print(f"✅ Test {i} passed: '{test['input']}' -> '{result}'")
            passed += 1
        else:
            print(f"❌ Test {i} failed: '{test['input']}' -> '{result}' (expected: '{test['expected']}')")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = test_clean_authors()
    sys.exit(0 if success else 1)
