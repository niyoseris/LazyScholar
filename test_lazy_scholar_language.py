#!/usr/bin/env python3
"""
Test script for LazyScholar with language parameter
"""

import os
import sys
import argparse
from lazy_scholar import LazyScholar

def main():
    """Main function to test LazyScholar with language parameter."""
    parser = argparse.ArgumentParser(description="Test LazyScholar with language parameter")
    parser.add_argument(
        "--problem-statement",
        default="Aspartam usage on pregnancy",
        help="The research problem statement"
    )
    parser.add_argument(
        "--language",
        choices=["en", "tr"],
        default="tr",
        help="Preferred language for the paper (en, tr) (default: tr)"
    )
    parser.add_argument(
        "--output-dir",
        default="Aspartam_Test",
        help="Output directory for the research"
    )
    args = parser.parse_args()
    
    print(f"Testing LazyScholar with language: {args.language}")
    
    # Initialize LazyScholar
    scholar = LazyScholar(
        headless=True,
        output_dir=args.output_dir,
        timeout=10,
        search_suffix="site:edu filetype:pdf",
        max_pdfs_per_topic=1,
        focus="pdf",
        academic_format=True,
        language=args.language
    )
    
    # Generate topics and subtopics
    topics = scholar.analyze_problem_statement(args.problem_statement)
    
    # Generate final paper
    final_paper_path = scholar.generate_final_paper(topics)
    
    print(f"\n✅ Final paper generated at: {final_paper_path}")
    print(f"Language: {args.language}")
    
    # Format as academic paper
    try:
        import academic_formatter
        
        # Initialize model
        print("\nFormatting as academic paper...")
        model = academic_formatter.initialize_model()
        if not model:
            print("Error: Failed to initialize model")
            return
        
        # Extract references and content
        pdf_paths, content = academic_formatter.extract_references_from_final_paper(final_paper_path)
        
        # Format as academic paper
        formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_paths, args.language)
        
        # Save formatted paper
        output_path = academic_formatter.save_formatted_paper(final_paper_path, formatted_paper)
        
        print(f"\n✅ Academic paper formatting complete!")
        print(f"Output file: {output_path}")
        print(f"Language: {args.language}")
    except Exception as e:
        print(f"\n❌ Error formatting academic paper: {str(e)}")

if __name__ == "__main__":
    main() 