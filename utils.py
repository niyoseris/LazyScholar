"""
Utility Module - Common utility functions for the academic research assistant.
"""

import os
import logging
import time
from dotenv import load_dotenv
import google.generativeai as genai

logger = logging.getLogger(__name__)

def load_api_key():
    """
    Load the Google API key from environment variables.
    
    Returns:
        str: API key if found, None otherwise
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("Google API key not found in environment variables")
        return None
    
    return api_key

def validate_topics_structure(topics_subtopics):
    """
    Validate the structure of topics and subtopics data.
    
    Args:
        topics_subtopics (list): List of topic dictionaries
        
    Returns:
        bool: True if structure is valid, False otherwise
    """
    if not isinstance(topics_subtopics, list):
        logger.error("Topics data is not a list")
        return False
    
    for item in topics_subtopics:
        if not isinstance(item, dict):
            logger.error("Topic item is not a dictionary")
            return False
            
        if 'topic' not in item or 'subtopics' not in item:
            logger.error("Topic item missing required keys")
            return False
            
        if not isinstance(item['subtopics'], list):
            logger.error("Subtopics is not a list")
            return False
    
    return True

def format_reference(paper_info):
    """
    Format a paper's information into a citation reference.
    
    Args:
        paper_info (dict): Dictionary containing paper information
        
    Returns:
        str: Formatted reference string
    """
    title = paper_info.get('title', 'Unknown Title')
    authors = paper_info.get('authors', [])
    year = paper_info.get('year', '')
    source = paper_info.get('source', '')
    
    # Format authors
    if authors:
        if len(authors) == 1:
            author_text = authors[0]
        elif len(authors) == 2:
            author_text = f"{authors[0]} & {authors[1]}"
        else:
            author_text = f"{authors[0]} et al."
    else:
        author_text = "Unknown Author"
    
    # Create reference string
    if year:
        reference = f"{author_text} ({year}). {title}."
    else:
        reference = f"{author_text}. {title}."
    
    if source:
        reference += f" {source}."
    
    return reference

def retry_with_backoff(func, max_retries=3, backoff_factor=1.5):
    """
    Retry a function with exponential backoff on failure.
    
    Args:
        func: The function to execute
        max_retries: Maximum number of retry attempts
        backoff_factor: Backoff multiplier
        
    Returns:
        The result of the function or raises the last exception
    """
    retries = 0
    last_exception = None
    
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            last_exception = e
            wait_time = backoff_factor ** retries
            logger.warning(f"Retry {retries+1}/{max_retries} failed: {str(e)}. Waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            retries += 1
    
    if last_exception:
        raise last_exception
