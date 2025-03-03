#!/usr/bin/env python3
"""
Setup Academic Format - A script to set up the academic formatting feature for LazyScholar

This script:
1. Runs the modify_lazy_scholar.py script to add the --academic-format option
2. Ensures the academic_formatter.py script is properly set up
3. Provides instructions on how to use the academic formatting feature
"""

import os
import subprocess
import sys

def check_requirements():
    """Check if the required packages are installed."""
    try:
        import google.generativeai
        import dotenv
        print("✅ Required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install the required packages with: pip install google-generativeai python-dotenv")
        return False

def check_api_key():
    """Check if the Google API key is set in the .env file."""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please create a .env file with your Google API key (GOOGLE_API_KEY=your_api_key)")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'GOOGLE_API_KEY' not in content:
        print("❌ GOOGLE_API_KEY not found in .env file")
        print("Please add your Google API key to the .env file (GOOGLE_API_KEY=your_api_key)")
        return False
    
    print("✅ Google API key found in .env file")
    return True

def run_modify_lazy_scholar():
    """Run the modify_lazy_scholar.py script."""
    print("\nRunning modify_lazy_scholar.py to add academic formatting option...")
    try:
        result = subprocess.run(
            [sys.executable, "modify_lazy_scholar.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Successfully modified LazyScholar to support academic formatting")
            return True
        else:
            print(f"❌ Failed to modify LazyScholar: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running modify_lazy_scholar.py: {str(e)}")
        return False

def check_academic_formatter():
    """Check if the academic_formatter.py script exists."""
    if not os.path.exists('academic_formatter.py'):
        print("❌ academic_formatter.py not found")
        print("Please ensure the academic_formatter.py script is in the current directory")
        return False
    
    print("✅ academic_formatter.py found")
    return True

def print_instructions():
    """Print instructions on how to use the academic formatting feature."""
    print("\n" + "="*80)
    print("ACADEMIC FORMATTING FEATURE SETUP COMPLETE")
    print("="*80)
    print("\nTo use the academic formatting feature, run LazyScholar with the --academic-format flag:")
    print("\npython lazy_scholar.py --problem-statement \"Your research topic\" --academic-format")
    print("\nThis will automatically format the final paper as an academic paper with proper")
    print("citations and references after the research is complete.")
    print("\nYou can also regenerate an existing paper with academic formatting:")
    print("\npython lazy_scholar.py --problem-statement \"Your research topic\" --regenerate-final-paper --academic-format")
    print("\nThe formatted academic paper will be saved as final_paper_academic_format.md")
    print("in the research_output directory.")
    print("\n" + "="*80)

def main():
    """Main function to set up the academic formatting feature."""
    print("Setting up academic formatting feature for LazyScholar...\n")
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check API key
    if not check_api_key():
        return
    
    # Run modify_lazy_scholar.py
    if not run_modify_lazy_scholar():
        return
    
    # Check academic_formatter.py
    if not check_academic_formatter():
        return
    
    # Print instructions
    print_instructions()

if __name__ == "__main__":
    main() 