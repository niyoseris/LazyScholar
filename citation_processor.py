#!/usr/bin/env python3
"""
Citation Processor - A tool to process PDFs, extract citations, and build research papers

This script implements a workflow to:
1. Process PDF files by sending them to a language model
2. Extract citation information and key points
3. Collect this information into JSON sketch files
4. Send these sketch files to the language model to generate research papers
5. Combine subtopics into topics and finally into a complete paper
"""

import os
import sys
import json
import time
import logging
import argparse
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import pdfplumber
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("citation_processor.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
    sys.exit(1)

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

def ensure_directory(directory_path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        The directory path
    """
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

def initialize_model():
    """Initialize the Gemini model for text generation."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Test the model with a simple prompt
        test_prompt = "Respond with 'OK' if you can process this message."
        response = model.generate_content(test_prompt)
        
        if response and hasattr(response, 'text'):
            logger.info("Successfully initialized Gemini model")
            return model
        else:
            logger.error("Failed to get valid response from Gemini model")
            return None
    except Exception as e:
        logger.error(f"Error initializing Gemini model: {str(e)}")
        return None

def api_call_with_retry(func, *args, max_retries=5, initial_delay=2, **kwargs):
    """Make API calls with exponential backoff retry logic."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                raise
            
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text or None if extraction failed
    """
    try:
        text = ""
        
        # First try with PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        # If PyPDF2 extraction is empty or very short, try with pdfplumber
        if len(text.strip()) < 100:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        
        return text if text.strip() else None
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return None

def get_citation_info(model, pdf_text: str) -> Dict[str, Any]:
    """
    Send PDF text to language model to extract citation information and key points.
    
    Args:
        model: The language model to use
        pdf_text: Text content of the PDF
        
    Returns:
        Dictionary containing citation information and key points
    """
    prompt = f"""
    Please analyze the following academic text and provide:
    
    1. Complete citation information (authors, title, journal/publication, year, DOI if available)
    2. Key findings and important points for research
    3. Methodology used in the research
    4. Limitations of the study
    5. Conclusions and implications
    
    Format your response as JSON with the following structure:
    {{
        "citation": {{
            "authors": [],
            "title": "",
            "publication": "",
            "year": "",
            "doi": ""
        }},
        "key_points": [],
        "methodology": "",
        "limitations": "",
        "conclusions": "",
        "quotes": []
    }}
    
    Here is the text to analyze:
    
    {pdf_text[:10000]}  # Limiting to first 10000 chars to avoid token limits
    """
    
    try:
        response = api_call_with_retry(model.generate_content, prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # Find JSON content (between curly braces)
        json_match = re.search(r'({.*})', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from response: {json_str}")
                return {"error": "Failed to parse JSON from response"}
        else:
            logger.error(f"No JSON found in response: {response_text}")
            return {"error": "No JSON found in response"}
    except Exception as e:
        logger.error(f"Error getting citation info: {str(e)}")
        return {"error": str(e)}

def process_pdf_file(model, pdf_path: str) -> Dict[str, Any]:
    """
    Process a PDF file to extract citation information and key points.
    
    Args:
        model: The language model to use
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing citation information and key points
    """
    logger.info(f"Processing PDF: {pdf_path}")
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    if not pdf_text:
        logger.error(f"Failed to extract text from PDF: {pdf_path}")
        return {"error": "Failed to extract text from PDF"}
    
    # Get citation information and key points
    return get_citation_info(model, pdf_text)

def save_subtopic_sketch(subtopic: str, pdf_results: List[Dict[str, Any]], output_dir: str) -> str:
    """
    Save PDF processing results for a subtopic to a JSON file.
    
    Args:
        subtopic: Name of the subtopic
        pdf_results: List of dictionaries containing PDF processing results
        output_dir: Directory to save the sketch file
        
    Returns:
        Path to the saved sketch file
    """
    # Create sanitized filename
    subtopic_filename = subtopic.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
    sketch_path = os.path.join(output_dir, f"{subtopic_filename}_sketch.json")
    
    # Save to JSON file
    with open(sketch_path, 'w', encoding='utf-8') as f:
        json.dump(pdf_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved subtopic sketch to: {sketch_path}")
    return sketch_path

def generate_subtopic_paper(model, sketch_path: str, subtopic: str, output_dir: str) -> str:
    """
    Generate a research paper for a subtopic based on the sketch file.
    
    Args:
        model: The language model to use
        sketch_path: Path to the subtopic sketch file
        subtopic: Name of the subtopic
        output_dir: Directory to save the paper
        
    Returns:
        Path to the saved paper file
    """
    logger.info(f"Generating paper for subtopic: {subtopic}")
    
    # Load sketch data
    with open(sketch_path, 'r', encoding='utf-8') as f:
        sketch_data = json.load(f)
    
    # Create prompt for the language model
    prompt = f"""
    Please write a comprehensive research paper section on the subtopic "{subtopic}" based on the following research data.
    
    Use proper academic writing style with in-text citations in APA format.
    Include all relevant information from the sources provided.
    Organize the content logically with clear structure.
    
    Research data:
    {json.dumps(sketch_data, indent=2)}
    
    Your response should be formatted as a well-structured academic paper section with:
    1. Introduction to the subtopic
    2. Main body with synthesis of the research findings
    3. Discussion of methodologies and limitations
    4. Conclusion about this subtopic
    
    Use proper in-text citations throughout (Author, Year) format.
    """
    
    try:
        response = api_call_with_retry(model.generate_content, prompt)
        paper_content = response.text
        
        # Save paper to file
        subtopic_filename = subtopic.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        paper_path = os.path.join(output_dir, f"{subtopic_filename}_paper.md")
        
        with open(paper_path, 'w', encoding='utf-8') as f:
            f.write(paper_content)
        
        logger.info(f"Saved subtopic paper to: {paper_path}")
        return paper_path
    except Exception as e:
        logger.error(f"Error generating subtopic paper: {str(e)}")
        return None

def combine_subtopic_papers(model, subtopic_papers: List[str], topic: str, output_dir: str) -> str:
    """
    Combine multiple subtopic papers into a single topic paper.
    
    Args:
        model: The language model to use
        subtopic_papers: List of paths to subtopic paper files
        topic: Name of the topic
        output_dir: Directory to save the combined paper
        
    Returns:
        Path to the saved topic paper file
    """
    logger.info(f"Combining subtopic papers for topic: {topic}")
    
    # Load content from all subtopic papers
    subtopic_contents = []
    for paper_path in subtopic_papers:
        with open(paper_path, 'r', encoding='utf-8') as f:
            subtopic_contents.append(f.read())
    
    # Create prompt for the language model
    prompt = f"""
    Please combine the following subtopic papers into a comprehensive research paper on the topic "{topic}".
    
    Use proper academic writing style with in-text citations in APA format.
    Organize the content logically with clear structure.
    Ensure smooth transitions between subtopics.
    Add an overall introduction and conclusion.
    
    Subtopic papers:
    
    {"".join([f"--- SUBTOPIC PAPER {i+1} ---\n{content}\n\n" for i, content in enumerate(subtopic_contents)])}
    
    Your response should be formatted as a well-structured academic paper with:
    1. Title
    2. Abstract
    3. Introduction
    4. Main body (organized by subtopics)
    5. Discussion
    6. Conclusion
    7. References (in APA format)
    """
    
    try:
        response = api_call_with_retry(model.generate_content, prompt)
        paper_content = response.text
        
        # Save paper to file
        topic_filename = topic.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        paper_path = os.path.join(output_dir, f"{topic_filename}_paper.md")
        
        with open(paper_path, 'w', encoding='utf-8') as f:
            f.write(paper_content)
        
        logger.info(f"Saved topic paper to: {paper_path}")
        return paper_path
    except Exception as e:
        logger.error(f"Error combining subtopic papers: {str(e)}")
        return None

def combine_topic_papers(model, topic_papers: List[str], title: str, output_dir: str) -> str:
    """
    Combine multiple topic papers into a final research paper.
    
    Args:
        model: The language model to use
        topic_papers: List of paths to topic paper files
        title: Title of the final paper
        output_dir: Directory to save the final paper
        
    Returns:
        Path to the saved final paper file
    """
    logger.info(f"Combining topic papers into final paper: {title}")
    
    # Load content from all topic papers
    topic_contents = []
    for paper_path in topic_papers:
        with open(paper_path, 'r', encoding='utf-8') as f:
            topic_contents.append(f.read())
    
    # Create prompt for the language model
    prompt = f"""
    Please combine the following topic papers into a comprehensive final research paper titled "{title}".
    
    Use proper academic writing style with in-text citations in APA format.
    Organize the content logically with clear structure.
    Ensure smooth transitions between topics.
    Add an overall introduction, discussion, and conclusion.
    
    Topic papers:
    
    {"".join([f"--- TOPIC PAPER {i+1} ---\n{content}\n\n" for i, content in enumerate(topic_contents)])}
    
    Your response should be formatted as a well-structured academic paper with:
    1. Title
    2. Abstract
    3. Introduction
    4. Literature Review
    5. Main body (organized by topics)
    6. Discussion
    7. Conclusion
    8. References (in APA format)
    """
    
    try:
        response = api_call_with_retry(model.generate_content, prompt)
        paper_content = response.text
        
        # Save paper to file
        filename = title.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        paper_path = os.path.join(output_dir, f"{filename}_final_paper.md")
        
        with open(paper_path, 'w', encoding='utf-8') as f:
            f.write(paper_content)
        
        logger.info(f"Saved final paper to: {paper_path}")
        return paper_path
    except Exception as e:
        logger.error(f"Error combining topic papers: {str(e)}")
        return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process PDFs and generate research papers")
    parser.add_argument("--pdf_dir", type=str, help="Directory containing PDF files")
    parser.add_argument("--output_dir", type=str, default="research_output", help="Directory to save output files")
    parser.add_argument("--subtopic", type=str, help="Name of the subtopic")
    parser.add_argument("--topic", type=str, help="Name of the topic")
    parser.add_argument("--title", type=str, help="Title of the final paper")
    return parser.parse_args()

def main():
    """Main function to run the citation processor."""
    args = parse_arguments()
    
    # Initialize model
    model = initialize_model()
    if not model:
        logger.error("Failed to initialize language model. Exiting.")
        sys.exit(1)
    
    # Ensure output directory exists
    output_dir = ensure_directory(args.output_dir)
    
    # Process PDFs for a subtopic
    if args.pdf_dir and args.subtopic:
        # Get list of PDF files
        pdf_files = [os.path.join(args.pdf_dir, f) for f in os.listdir(args.pdf_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.error(f"No PDF files found in directory: {args.pdf_dir}")
            sys.exit(1)
        
        # Process each PDF file
        pdf_results = []
        for pdf_path in pdf_files:
            result = process_pdf_file(model, pdf_path)
            if "error" not in result:
                pdf_results.append(result)
        
        # Save subtopic sketch
        sketch_path = save_subtopic_sketch(args.subtopic, pdf_results, output_dir)
        
        # Generate subtopic paper
        generate_subtopic_paper(model, sketch_path, args.subtopic, output_dir)
    
    # Combine subtopic papers into a topic paper
    elif args.output_dir and args.topic:
        # Find all subtopic paper files
        subtopic_papers = [os.path.join(args.output_dir, f) for f in os.listdir(args.output_dir) 
                          if f.endswith('_paper.md') and not f.endswith('_final_paper.md')]
        
        if not subtopic_papers:
            logger.error(f"No subtopic paper files found in directory: {args.output_dir}")
            sys.exit(1)
        
        # Combine subtopic papers
        combine_subtopic_papers(model, subtopic_papers, args.topic, output_dir)
    
    # Combine topic papers into a final paper
    elif args.output_dir and args.title:
        # Find all topic paper files
        topic_papers = [os.path.join(args.output_dir, f) for f in os.listdir(args.output_dir) 
                       if f.endswith('_paper.md') and not f.endswith('_final_paper.md')]
        
        if not topic_papers:
            logger.error(f"No topic paper files found in directory: {args.output_dir}")
            sys.exit(1)
        
        # Combine topic papers
        combine_topic_papers(model, topic_papers, args.title, output_dir)
    
    else:
        logger.error("Invalid arguments. Please provide either --pdf_dir and --subtopic, or --output_dir and --topic, or --output_dir and --title")
        sys.exit(1)

if __name__ == "__main__":
    main() 