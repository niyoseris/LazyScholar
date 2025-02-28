#!/usr/bin/env python3
"""
Comprehensive formatting test script for research results
"""

import os
import re
import sys

def enhance_author_format(author_text):
    """Improve author formatting by fixing common issues."""
    if not author_text:
        return "Unknown"
    
    # Fix case where authors are split into individual characters
    if isinstance(author_text, str) and (re.search(r'^([A-Za-z],\s*)+[A-Za-z]$', author_text) or all(len(c.strip(',')) <= 1 for c in author_text.split())):
        # Join characters, removing commas and spaces
        return ''.join(c for c in author_text if c not in [',', ' ', '\n'] and not c.isspace())
    
    # Fix case where authors are ellipses (...)
    if isinstance(author_text, str) and ('...' in author_text or author_text.strip() == '…'):
        return "Author information incomplete"
    
    # Fix case where journal name is mixed with author names
    # Common pattern: Last, First - Journal name, Year
    if isinstance(author_text, str):
        journal_pattern = r'(.+?)\s*-\s*(.+?),\s*(\d{4})'
        match = re.search(journal_pattern, author_text)
        if match:
            authors = match.group(1).strip()
            return authors
    
    # Handle list of authors
    if isinstance(author_text, list):
        if not author_text or all(not a for a in author_text):
            return "Unknown"
            
        # If the list contains single characters, join them without spaces
        if all(isinstance(a, str) and len(a.strip()) <= 1 for a in author_text):
            joined = "".join(a for a in author_text if a and not a.isspace())
            if not joined:
                return "Unknown"
            return joined
            
        # Otherwise, use proper formatting
        proper_authors = []
        for author in author_text:
            # Check if author name is broken into characters or is a punctuation mark
            if isinstance(author, str) and (len(author.strip()) <= 1 and author.strip() in [',', ' ', '-', '.'] or not author.strip()):
                continue
            if isinstance(author, str) and author.strip():
                proper_authors.append(author.strip())
        
        if not proper_authors:
            return "Unknown"
        return ", ".join(proper_authors)
    
    return author_text

def test_author_formatting():
    """Test the enhanced author formatting with various inputs."""
    
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
        result = enhance_author_format(test["input"])
        if result == test["expected"]:
            print(f"✅ Test {i} passed: '{test['input']}' -> '{result}'")
            passed += 1
        else:
            print(f"❌ Test {i} failed: '{test['input']}' -> '{result}' (expected: '{test['expected']}')")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def find_problematic_authors():
    """Scan all research results for problematic author formatting."""
    results_dir = os.path.join(os.getcwd(), "research_results")
    if not os.path.exists(results_dir):
        print("Research results directory not found.")
        return
    
    problematic_files = []
    author_pattern = r'\*\*Authors\*\*: (.*?)(?=\n\n)'
    
    for filename in os.listdir(results_dir):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(author_pattern, content, re.DOTALL)
        for match in matches:
            # Check for problematic patterns
            if '...' in match or match.strip() == '…' or re.search(r'^([A-Za-z],\s*)+[A-Za-z]$', match):
                problematic_files.append({
                    'file': filename,
                    'authors': match
                })
                break
    
    if problematic_files:
        print(f"\nFound {len(problematic_files)} files with problematic author formatting:")
        for item in problematic_files:
            print(f"- {item['file']}: '{item['authors']}'")
    else:
        print("\nNo problematic author formatting found!")
    
    return problematic_files

if __name__ == "__main__":
    print("TESTING AUTHOR FORMATTING FUNCTION:")
    success = test_author_formatting()
    
    print("\nSCANNING FOR PROBLEMATIC AUTHORS IN RESEARCH RESULTS:")
    problematic = find_problematic_authors()
    
    sys.exit(0 if success and not problematic else 1)
