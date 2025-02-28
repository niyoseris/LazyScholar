#!/usr/bin/env python3
"""
Script to enhance research result content by fixing formatting issues, improving authors,
and replacing ellipses (...) with more meaningful content.
"""

import os
import re
import logging
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enhance_content.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def display_process_status(stage, message, content=None):
    """Display process status."""
    print(f"\n{'-' * 80}")
    print(f"[{stage}] {message}")
    if content:
        for key, value in content.items():
            if isinstance(value, list) and value:
                print(f"  {key}:")
                for i, item in enumerate(value, 1):
                    print(f"    {i}. {item}")
            else:
                print(f"  {key}: {value}")
    print(f"{'-' * 80}")

def enhance_author_format(author_text):
    """Improve author formatting by fixing common issues."""
    if not author_text:
        return "Unknown"
    
    # Fix case where authors are split into individual characters
    if re.search(r'^([A-Za-z],\s*)+[A-Za-z]$', author_text) or all(len(c.strip(',')) <= 1 for c in author_text.split()):
        # Join characters, removing commas and spaces
        return ''.join(c for c in author_text if c not in [',', ' ', '\n'] and not c.isspace())
    
    # Fix case where authors are ellipses (...)
    if '...' in author_text or author_text.strip() == '…':
        return "Author information incomplete"
    
    # Fix case where journal name is mixed with author names
    # Common pattern: Last, First - Journal name, Year
    journal_pattern = r'(.+?)\s*-\s*(.+?),\s*(\d{4})'
    match = re.search(journal_pattern, author_text)
    if match:
        authors = match.group(1).strip()
        return authors
    
    return author_text

def process_abstract(abstract_text):
    """Process abstract text to replace ellipses and improve readability."""
    if not abstract_text:
        return "Abstract not available"
    
    # Replace ellipses at the beginning or end of sentences
    abstract_text = re.sub(r'(^|\.\s*)…\s*', r'\1', abstract_text)
    abstract_text = re.sub(r'\s*…(\s*\.|$)', r'\1', abstract_text)
    
    # Replace multiple ellipses
    abstract_text = re.sub(r'…\s*…', '…', abstract_text)
    
    # If abstract consists entirely of ellipses
    if abstract_text.strip() == '…' or abstract_text.strip() == '...':
        return "Abstract excerpt unavailable"
    
    return abstract_text

def enhance_content_in_file(filepath):
    """Enhance content in a research file."""
    try:
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find author blocks in the format **Authors**: [text]
        author_pattern = r'(\*\*Authors\*\*: )(.*?)(\n\n)'
        
        def fix_author_match(match):
            prefix = match.group(1)
            author_text = match.group(2)
            suffix = match.group(3)
            
            # Enhance the author text
            fixed_author = enhance_author_format(author_text)
            
            return prefix + fixed_author + suffix
        
        # Apply author fixes
        content = re.sub(author_pattern, fix_author_match, content)
        
        # Find abstract/snippet blocks
        abstract_pattern = r'(\*\*Abstract/Snippet\*\*:\n> )(.*?)(\n\n)'
        
        def fix_abstract_match(match, flags=re.DOTALL):
            prefix = match.group(1)
            abstract_text = match.group(2)
            suffix = match.group(3)
            
            # Process the abstract
            processed_abstract = process_abstract(abstract_text)
            
            return prefix + processed_abstract + suffix
        
        # Apply abstract fixes
        content = re.sub(abstract_pattern, fix_abstract_match, content, flags=re.DOTALL)
        
        # Write back the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        display_process_status("CONTENT ENHANCED", f"Enhanced content in: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error enhancing content in {filepath}: {str(e)}", exc_info=True)
        display_process_status("ERROR", f"Failed to enhance content in: {filepath}", {"error": str(e)})
        return False

def main():
    """Enhance content in all research results."""
    
    # Load environment variables
    load_dotenv()
    
    # Get all research result files
    results_dir = os.path.join(os.getcwd(), "research_results")
    if not os.path.exists(results_dir):
        print(f"Research results directory not found: {results_dir}")
        return
        
    result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('.md')]
    
    print(f"Found {len(result_files)} research result files to enhance.")
    
    # Enhance each file
    success_count = 0
    for filepath in result_files:
        print(f"Enhancing content in: {os.path.basename(filepath)}")
        if enhance_content_in_file(filepath):
            success_count += 1
            
    print(f"Successfully enhanced content in {success_count} out of {len(result_files)} research files.")

if __name__ == "__main__":
    main()
