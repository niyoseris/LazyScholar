#!/usr/bin/env python3
"""
Script to specifically fix author formatting in research results.
"""

import os
import re
import logging
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

def fix_author_string(author_text):
    """Fix author strings that are broken into individual characters."""
    # Check if string appears to be broken into individual characters
    # Pattern: single characters separated by commas and/or spaces
    if re.search(r'^([A-Za-z],\s*)+[A-Za-z]$', author_text):
        # Remove commas and spaces, join the characters
        return ''.join(c for c in author_text if c not in [',', ' '])
    
    # If it's a series of individual letters with spaces/commas
    if all(len(c.strip(',')) <= 1 for c in author_text.split()):
        # Join but keep meaningful separators like hyphens
        return ''.join(c for c in author_text if c not in [','] and not c.isspace())
    
    return author_text

def fix_authors_in_file(filepath):
    """Fix author formatting in a research file."""
    try:
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find author blocks in the format **Authors**: [broken characters]
        author_pattern = r'(\*\*Authors\*\*: )(.*?)(\n\n)'
        
        def fix_author_match(match):
            prefix = match.group(1)
            author_text = match.group(2)
            suffix = match.group(3)
            
            # Check if author format needs fixing (appears to be broken into chars)
            if re.search(r'[A-Za-z], [A-Za-z]', author_text) or all(len(c.strip(',')) <= 1 for c in author_text.split()):
                # Try to reconstruct the author name
                fixed_author = fix_author_string(author_text)
                
                # Only use the fix if it seems better than original
                if len(fixed_author) < len(author_text) * 0.5:
                    fixed_author = author_text
                
                return prefix + fixed_author + suffix
            return match.group(0)
        
        # Apply the fix to all author blocks
        fixed_content = re.sub(author_pattern, fix_author_match, content)
        
        # Write back the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        display_process_status("AUTHORS FIXED", f"Fixed author formatting in: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error fixing authors in {filepath}: {str(e)}", exc_info=True)
        display_process_status("ERROR", f"Failed to fix authors in: {filepath}", {"error": str(e)})
        return False

def main():
    """Fix author formatting in all research results."""
    
    # Load environment variables
    load_dotenv()
    
    # Get all research result files
    results_dir = os.path.join(os.getcwd(), "research_results")
    if not os.path.exists(results_dir):
        print(f"Research results directory not found: {results_dir}")
        return
        
    result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('.md')]
    
    print(f"Found {len(result_files)} research result files to fix.")
    
    # Fix each file
    success_count = 0
    for filepath in result_files:
        print(f"Fixing authors in: {os.path.basename(filepath)}")
        if fix_authors_in_file(filepath):
            success_count += 1
            
    print(f"Successfully fixed authors in {success_count} out of {len(result_files)} research files.")

if __name__ == "__main__":
    main()
