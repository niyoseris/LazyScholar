"""
File utility functions for the web scraper package.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
        
    Returns:
        str: Path to the directory
    """
    if not os.path.exists(directory):
        logger.info(f"Creating directory: {directory}")
        os.makedirs(directory)
    return directory

def save_json(data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Path to the output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filename)
        if directory:
            ensure_directory(directory)
            
        # Save the data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {e}")
        return False

def load_json(filename: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    """
    Load data from a JSON file.
    
    Args:
        filename: Path to the input file
        
    Returns:
        Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]: Loaded data, or None if loading failed
    """
    try:
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return None
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        logger.info(f"Data loaded from {filename}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {e}")
        return None

def create_temp_file(prefix: str = "web_scraper_", suffix: str = ".tmp") -> str:
    """
    Create a temporary file.
    
    Args:
        prefix: Prefix for the temporary file
        suffix: Suffix for the temporary file
        
    Returns:
        str: Path to the temporary file
    """
    try:
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)  # Close the file descriptor
        logger.debug(f"Created temporary file: {path}")
        return path
    except Exception as e:
        logger.error(f"Error creating temporary file: {e}")
        return ""

def generate_output_filename(base_name: str, extension: str = ".json") -> str:
    """
    Generate an output filename with timestamp.
    
    Args:
        base_name: Base name for the file
        extension: File extension
        
    Returns:
        str: Generated filename
    """
    # Clean the base name
    base_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in base_name)
    base_name = base_name.replace(" ", "_").lower()
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure extension starts with a dot
    if not extension.startswith("."):
        extension = "." + extension
        
    return f"{base_name}_{timestamp}{extension}" 