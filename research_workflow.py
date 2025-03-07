#!/usr/bin/env python3
"""
Research Workflow - A wrapper script to execute the research workflow

This script provides a user-friendly interface to:
1. Process PDF files and extract citations and key points
2. Generate subtopic papers from PDF data
3. Combine subtopic papers into topic papers
4. Combine topic papers into a final research paper

The workflow follows these steps:
1. Send PDF files to a language model to extract citation info and key points
2. Collect this information into JSON sketch files
3. Generate research papers for each subtopic
4. Combine subtopic papers into topic papers
5. Combine topic papers into a final paper
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
import shutil
from typing import Dict, Any, List, Optional

# Import functions from citation_processor
try:
    from citation_processor import (
        initialize_model, 
        process_pdf_file, 
        save_subtopic_sketch, 
        generate_subtopic_paper,
        combine_subtopic_papers,
        combine_topic_papers,
        ensure_directory
    )
except ImportError:
    print("Error: citation_processor.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("research_workflow.log")
    ]
)
logger = logging.getLogger(__name__)

def process_pdfs_for_subtopic(model, pdf_dir: str, subtopic: str, output_dir: str) -> str:
    """
    Process all PDFs in a directory for a specific subtopic.
    
    Args:
        model: The language model to use
        pdf_dir: Directory containing PDF files
        subtopic: Name of the subtopic
        output_dir: Directory to save output files
        
    Returns:
        Path to the generated subtopic paper
    """
    logger.info(f"Processing PDFs for subtopic: {subtopic}")
    
    # Get list of PDF files
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.error(f"No PDF files found in directory: {pdf_dir}")
        return None
    
    # Process each PDF file
    pdf_results = []
    for pdf_path in pdf_files:
        logger.info(f"Processing PDF: {pdf_path}")
        result = process_pdf_file(model, pdf_path)
        if "error" not in result:
            pdf_results.append(result)
    
    if not pdf_results:
        logger.error(f"No valid results extracted from PDFs for subtopic: {subtopic}")
        return None
    
    # Save subtopic sketch
    sketch_path = save_subtopic_sketch(subtopic, pdf_results, output_dir)
    
    # Generate subtopic paper
    return generate_subtopic_paper(model, sketch_path, subtopic, output_dir)

def process_subtopics_for_topic(model, subtopics: List[str], pdfs_dir: str, topic: str, output_dir: str) -> str:
    """
    Process multiple subtopics for a topic.
    
    Args:
        model: The language model to use
        subtopics: List of subtopic names
        pdfs_dir: Base directory containing PDF files (will look for subdirectories named after subtopics)
        topic: Name of the topic
        output_dir: Directory to save output files
        
    Returns:
        Path to the generated topic paper
    """
    logger.info(f"Processing subtopics for topic: {topic}")
    
    # Create topic directory
    topic_dir = ensure_directory(os.path.join(output_dir, topic))
    
    # Process each subtopic
    subtopic_papers = []
    for subtopic in subtopics:
        # Look for PDF directory for this subtopic
        subtopic_pdf_dir = os.path.join(pdfs_dir, subtopic)
        if not os.path.exists(subtopic_pdf_dir):
            logger.warning(f"PDF directory not found for subtopic: {subtopic}")
            continue
        
        # Process PDFs for this subtopic
        paper_path = process_pdfs_for_subtopic(model, subtopic_pdf_dir, subtopic, topic_dir)
        if paper_path:
            subtopic_papers.append(paper_path)
    
    if not subtopic_papers:
        logger.error(f"No subtopic papers generated for topic: {topic}")
        return None
    
    # Combine subtopic papers into a topic paper
    return combine_subtopic_papers(model, subtopic_papers, topic, output_dir)

def process_topics_for_paper(model, topics: List[str], output_dir: str, title: str) -> str:
    """
    Process multiple topics for a final paper.
    
    Args:
        model: The language model to use
        topics: List of topic names
        output_dir: Directory containing topic papers
        title: Title of the final paper
        
    Returns:
        Path to the generated final paper
    """
    logger.info(f"Processing topics for final paper: {title}")
    
    # Find topic papers
    topic_papers = []
    for topic in topics:
        topic_filename = topic.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        paper_path = os.path.join(output_dir, f"{topic_filename}_paper.md")
        if os.path.exists(paper_path):
            topic_papers.append(paper_path)
        else:
            logger.warning(f"Paper not found for topic: {topic}")
    
    if not topic_papers:
        logger.error("No topic papers found")
        return None
    
    # Combine topic papers into a final paper
    return combine_topic_papers(model, topic_papers, title, output_dir)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Execute research workflow")
    
    # Main operation mode
    parser.add_argument("--mode", type=str, choices=["subtopic", "topic", "paper"], required=True,
                        help="Operation mode: process a subtopic, a topic, or generate final paper")
    
    # Common arguments
    parser.add_argument("--output_dir", type=str, default="research_output",
                        help="Directory to save output files")
    
    # Subtopic mode arguments
    parser.add_argument("--subtopic", type=str,
                        help="Name of the subtopic (for subtopic mode)")
    parser.add_argument("--pdf_dir", type=str,
                        help="Directory containing PDF files (for subtopic mode)")
    
    # Topic mode arguments
    parser.add_argument("--topic", type=str,
                        help="Name of the topic (for topic mode)")
    parser.add_argument("--subtopics", type=str, nargs="+",
                        help="List of subtopics for the topic (for topic mode)")
    parser.add_argument("--pdfs_base_dir", type=str,
                        help="Base directory containing PDF files organized by subtopic (for topic mode)")
    
    # Paper mode arguments
    parser.add_argument("--title", type=str,
                        help="Title of the final paper (for paper mode)")
    parser.add_argument("--topics", type=str, nargs="+",
                        help="List of topics for the final paper (for paper mode)")
    
    return parser.parse_args()

def main():
    """Main function to run the research workflow."""
    args = parse_arguments()
    
    # Initialize model
    model = initialize_model()
    if not model:
        logger.error("Failed to initialize language model. Exiting.")
        sys.exit(1)
    
    # Ensure output directory exists
    output_dir = ensure_directory(args.output_dir)
    
    # Execute workflow based on mode
    if args.mode == "subtopic":
        # Validate arguments
        if not args.subtopic or not args.pdf_dir:
            logger.error("Subtopic mode requires --subtopic and --pdf_dir arguments")
            sys.exit(1)
        
        # Process PDFs for subtopic
        process_pdfs_for_subtopic(model, args.pdf_dir, args.subtopic, output_dir)
    
    elif args.mode == "topic":
        # Validate arguments
        if not args.topic or not args.subtopics or not args.pdfs_base_dir:
            logger.error("Topic mode requires --topic, --subtopics, and --pdfs_base_dir arguments")
            sys.exit(1)
        
        # Process subtopics for topic
        process_subtopics_for_topic(model, args.subtopics, args.pdfs_base_dir, args.topic, output_dir)
    
    elif args.mode == "paper":
        # Validate arguments
        if not args.title or not args.topics:
            logger.error("Paper mode requires --title and --topics arguments")
            sys.exit(1)
        
        # Process topics for final paper
        process_topics_for_paper(model, args.topics, output_dir, args.title)
    
    logger.info("Research workflow completed successfully")

if __name__ == "__main__":
    main() 