#!/usr/bin/env python3
"""
Test script for academic formatter with language parameter
"""

import os
import sys
import argparse
import academic_formatter

def main():
    """Main function to test academic formatter with language parameter."""
    parser = argparse.ArgumentParser(description="Test academic formatter with language parameter")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input final paper"
    )
    parser.add_argument(
        "--language",
        choices=["auto", "en", "tr"],
        default="tr",
        help="Preferred language for the paper (auto, en, tr) (default: tr)"
    )
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}")
        return
    
    print(f"Testing academic formatter with language: {args.language}")
    
    # Initialize model
    print("Initializing AI model...")
    model = academic_formatter.initialize_model()
    if not model:
        print("Error: Failed to initialize model")
        return
    
    # Extract references and content
    print("Extracting references and content from paper...")
    pdf_paths, content = academic_formatter.extract_references_from_final_paper(args.input)
    
    if not content:
        print("Error: Failed to read content from the paper")
        return
    
    print(f"Found {len(pdf_paths)} PDF files for citation generation")
    
    # Format as academic paper
    print("\nFormatting paper as academic document...")
    print("This process may take some time as we ensure all sections are in the preferred language.")
    print("The system will automatically handle any API quota limitations by waiting when necessary.\n")
    
    formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_paths, args.language)
    
    # Validate the formatted paper
    if not formatted_paper or len(formatted_paper) < 100:
        print("Error: Formatting failed - output is too short or empty")
        return
    
    # Save formatted paper
    print("Saving formatted paper...")
    output_path = academic_formatter.save_formatted_paper(args.input, formatted_paper)
    
    print(f"\n✅ Academic paper formatting complete!")
    print(f"Output file: {output_path}")
    print("\nAll sections have been processed and translated to the preferred language.")

if __name__ == "__main__":
    main() 