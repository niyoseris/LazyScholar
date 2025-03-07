#!/usr/bin/env python3
"""
Example Workflow - Demonstrates how to use the research workflow

This script shows how to:
1. Download a sample PDF
2. Process it to extract citation information and key points
3. Generate a subtopic paper
4. (Optionally) combine multiple subtopic papers into a topic paper
5. (Optionally) combine multiple topic papers into a final paper
"""

import os
import sys
import requests
import tempfile
import shutil
from pathlib import Path

# Import functions from citation_processor and research_workflow
try:
    from citation_processor import initialize_model, process_pdf_file, save_subtopic_sketch, generate_subtopic_paper
    from research_workflow import ensure_directory
except ImportError:
    print("Error: citation_processor.py or research_workflow.py not found. Make sure they're in the same directory.")
    sys.exit(1)

def download_sample_pdf(output_dir):
    """Download a sample PDF for demonstration purposes."""
    # Sample PDF URL (a publicly available academic paper)
    pdf_url = "https://arxiv.org/pdf/2303.08774.pdf"  # "GPT-4 Technical Report" from OpenAI
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the PDF
    pdf_path = os.path.join(output_dir, "sample_paper.pdf")
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded sample PDF to: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error downloading sample PDF: {str(e)}")
        return None

def main():
    """Run the example workflow."""
    # Create temporary directories for the example
    temp_dir = tempfile.mkdtemp()
    pdf_dir = os.path.join(temp_dir, "pdfs")
    output_dir = os.path.join(temp_dir, "research_output")
    
    try:
        # Ensure directories exist
        ensure_directory(pdf_dir)
        ensure_directory(output_dir)
        
        print("=== Example Research Workflow ===")
        print(f"Working directory: {temp_dir}")
        
        # Step 1: Download a sample PDF
        print("\n1. Downloading sample PDF...")
        pdf_path = download_sample_pdf(pdf_dir)
        if not pdf_path:
            print("Failed to download sample PDF. Exiting.")
            sys.exit(1)
        
        # Step 2: Initialize the language model
        print("\n2. Initializing language model...")
        model = initialize_model()
        if not model:
            print("Failed to initialize language model. Exiting.")
            sys.exit(1)
        
        # Step 3: Process the PDF
        print("\n3. Processing PDF to extract citation information and key points...")
        subtopic = "Language Models"
        result = process_pdf_file(model, pdf_path)
        
        if "error" in result:
            print(f"Error processing PDF: {result['error']}")
            sys.exit(1)
        
        # Step 4: Save subtopic sketch
        print("\n4. Saving subtopic sketch...")
        sketch_path = save_subtopic_sketch(subtopic, [result], output_dir)
        print(f"Saved subtopic sketch to: {sketch_path}")
        
        # Step 5: Generate subtopic paper
        print("\n5. Generating subtopic paper...")
        paper_path = generate_subtopic_paper(model, sketch_path, subtopic, output_dir)
        if paper_path:
            print(f"Generated subtopic paper: {paper_path}")
            
            # Display the first few lines of the paper
            with open(paper_path, 'r', encoding='utf-8') as f:
                paper_content = f.read()
                preview_lines = paper_content.split('\n')[:10]
                print("\nPaper preview:")
                for line in preview_lines:
                    print(f"  {line}")
                print("  ...")
        else:
            print("Failed to generate subtopic paper.")
        
        # Step 6: Explain next steps
        print("\n6. Next steps:")
        print("   - To process multiple PDFs for a subtopic:")
        print("     python research_workflow.py --mode subtopic --subtopic \"Your Subtopic\" --pdf_dir path/to/pdfs --output_dir research_output")
        print("   - To combine multiple subtopics into a topic paper:")
        print("     python research_workflow.py --mode topic --topic \"Your Topic\" --subtopics \"Subtopic1\" \"Subtopic2\" --pdfs_base_dir path/to/pdfs_base_dir --output_dir research_output")
        print("   - To combine multiple topics into a final paper:")
        print("     python research_workflow.py --mode paper --title \"Your Paper Title\" --topics \"Topic1\" \"Topic2\" --output_dir research_output")
        
        print("\nExample workflow completed successfully!")
        print(f"Output files are in: {output_dir}")
        
        # Ask if user wants to keep the output files
        keep_files = input("\nDo you want to keep the output files? (y/n): ").lower().strip() == 'y'
        if keep_files:
            # Copy output files to current directory
            current_dir = os.path.abspath(os.path.dirname(__file__))
            dest_dir = os.path.join(current_dir, "example_output")
            ensure_directory(dest_dir)
            
            for file in os.listdir(output_dir):
                src_file = os.path.join(output_dir, file)
                dst_file = os.path.join(dest_dir, file)
                shutil.copy2(src_file, dst_file)
            
            print(f"Output files copied to: {dest_dir}")
    
    finally:
        # Clean up temporary directory
        if 'keep_files' not in locals() or not keep_files:
            shutil.rmtree(temp_dir)
            print(f"Temporary files removed from: {temp_dir}")

if __name__ == "__main__":
    main() 