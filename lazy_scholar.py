#!/usr/bin/env python3
"""
LazyScholar - Academic Research Assistant

This application helps users conduct academic research by:
1. Analyzing a problem statement to generate topics and subtopics
2. Searching academic sources for relevant information
3. Extracting information from PDF files
4. Compiling research into a structured academic paper with proper citations
"""

import os
import sys
import json
import time
import logging
import argparse
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import base64
import platform
import requests
import io
import re
from urllib.parse import urljoin
import hashlib
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from io import BytesIO

# Import required libraries
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import PyPDF2
import pdfplumber
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from PIL import Image
import urllib.parse
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add the current directory to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import from web_scraper module
try:
    from web_scraper.browser.browser_factory import create_browser
    from web_scraper.browser import close_browser
    from web_scraper.ai_engines.vision_helper import take_screenshot, find_search_input, find_search_button, analyze_screenshot, analyze_screenshot_for_pdf_links, find_pdf_links
    from web_scraper.utils.file_utils import ensure_directory
except ImportError as e:
    print(f"Error importing web_scraper modules: {e}")
    print("Make sure the web_scraper package is properly installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lazy_scholar.log"),
        logging.StreamHandler()
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

class LazyScholar:
    """Main class for the LazyScholar application."""
    
    def __init__(self, headless: bool = False, output_dir: str = "research_output", timeout: int = 120, search_suffix: str = "", max_pdfs_per_topic: int = 10, focus: str = "all", academic_format: bool = False, language: str = "en"):
        """
        Initialize the LazyScholar instance.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
            output_dir (str): Directory to store research output
            timeout (int): Timeout in seconds for browser operations
            search_suffix (str): Suffix to append to search queries
            max_pdfs_per_topic (int): Maximum number of PDFs to process per topic
            focus (str): Type of content to focus on ('pdf', 'html', or 'all')
            academic_format (bool): Whether to format the final paper as an academic paper
            language (str): Language code for the final paper (e.g., 'en', 'tr', 'es')
        """
        # Import required modules
        import google.generativeai as genai
        from dotenv import load_dotenv
        import os
        import json
        
        self.headless = headless
        self.output_dir = output_dir
        self.timeout = timeout
        self.search_suffix = search_suffix
        self.max_pdfs_per_topic = max_pdfs_per_topic
        self.focus = focus
        self.academic_format = academic_format
        self.language = language
        self.browser = None
        self.topics = []
        self.problem_statement = ""
        self.driver = None
        
        # Create output directories
        ensure_directory(output_dir)
        ensure_directory(os.path.join(output_dir, "topics"))
        ensure_directory(os.path.join(output_dir, "pdfs"))
        
        # Load environment variables
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
            raise ValueError("GOOGLE_API_KEY not found")
        
        # Configure Google Generative AI
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Initialize the models
        try:
            # Set up generation config
            generation_config = {
                "temperature": 0.2,  # Lower temperature for more consistent output
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            # Initialize the model for general use
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info(f"Successfully initialized Gemini model with name: gemini-2.0-flash-exp")
            
            # Initialize the vision model
            self.vision_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info(f"Successfully initialized Vision model with name: gemini-2.0-flash-exp")
            
            # Initialize the model for final paper generation
            self.gemini = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=generation_config
            )
            
            logger.info("Gemini models initialized successfully")
            logger.info("LazyScholar initialized")
        except Exception as e:
            logger.error(f"Error initializing Gemini models: {str(e)}")
            raise
    
    def _api_call_with_retry(self, api_func, max_retries=5, retry_delay=2):
        """
        Make an API call with retry logic.
        
        Args:
            api_func: Function to call the API
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries in seconds
            
        Returns:
            API response
        """
        retries = 0
        while retries < max_retries:
            try:
                return api_func()
            except Exception as e:
                retries += 1
                
                # Check if it's a rate limit error (429)
                if "429" in str(e) or "Resource has been exhausted" in str(e) or "quota" in str(e).lower():
                    # For rate limit errors, use a longer delay
                    current_delay = retry_delay * (2 ** retries)  # Exponential backoff
                    current_delay = min(current_delay, 60)  # Cap at 60 seconds
                    
                    logger.warning(f"Rate limit error (429). Waiting for {current_delay} seconds before retry {retries}/{max_retries}")
                    time.sleep(current_delay)
                else:
                    # For other errors, use standard backoff
                    if retries >= max_retries:
                        logger.error(f"API call failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    logger.warning(f"API call failed: {str(e)}. Retrying in {retry_delay} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 30)  # Exponential backoff, capped at 30 seconds
    
    def start_browser(self) -> None:
        """Initialize and start the web browser."""
        logger.info("Starting browser...")
        
        try:
            # Set up Chrome options
            chrome_options = webdriver.ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Add other Chrome options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Initialize the browser
            self.browser = webdriver.Chrome(options=chrome_options)
            self.browser.set_page_load_timeout(self.timeout)
            
            # Set window size
            self.browser.set_window_size(1920, 1080)
            
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}", exc_info=True)
            if "chromedriver" in str(e).lower():
                logger.error("ChromeDriver error. Make sure Chrome is installed and updated.")
            raise
    
    def close_browser(self) -> None:
        """
        Close the browser session and clean up resources.
        """
        if self.driver:
            try:
                logger.info("Closing browser session")
                
                # First try the standard quit method
                try:
                    self.driver.quit()
                except Exception as e:
                    logger.warning(f"Error during standard browser quit: {e}")
                    
                    # If standard quit fails, try to close all windows
                    try:
                        for window_handle in self.driver.window_handles:
                            self.driver.switch_to.window(window_handle)
                            self.driver.close()
                    except Exception as e2:
                        logger.warning(f"Error closing browser windows: {e2}")
                
                # Set browser to None to indicate it's closed
                self.driver = None
                logger.info("Browser session closed successfully")
                
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
                # Force set to None even if there was an error
                self.driver = None
    
    def analyze_problem_statement(self, problem_statement: str) -> List[Dict[str, Any]]:
        """
        Analyze the problem statement to identify research topics and subtopics.
        
        Args:
            problem_statement (str): The research problem to analyze
            
        Returns:
            List[Dict[str, Any]]: List of topics and their subtopics
        """
        logger.info(f"Analyzing problem statement: {problem_statement}")
        
        try:
            # Translate problem statement to English for better search results if not already in English
            english_problem_statement = problem_statement
            if self.language != "en":
                logger.info(f"Translating problem statement to English for better search results")
                translation_prompt = f"""Translate the following research problem to English for academic research purposes:

Problem: {problem_statement}

Provide only the translated text without any explanations or additional content."""

                english_problem_statement = self._api_call_with_retry(
                    lambda: self.model.generate_content(translation_prompt).text
                )
                logger.info(f"Translated problem statement: {english_problem_statement}")
            
            # Prepare the prompt for Gemini
            prompt = f"""Analyze this research problem and break it down into main topics and subtopics for an academic paper:

Problem: {english_problem_statement}

Focus on the key aspects that need to be investigated to thoroughly understand this problem.
Subtopics will be used as search keywords by their own. So it's important to make them short and related with the main topic. Mention problem sentence while creating subtopic.
Don't use generic subtopics like "Background", "Current Research", "Future Directions", etc.
Format your response as JSON with this structure:
{{
    "topics": [
        {{
            "title": "Main Topic 1",
            "subtopics": [
                {{
                    "title": "Subtopic 1.1",
                    "status": "pending"
                }},
                ...
            ]
        }},
        ...
    ]
}}"""

            logger.info("Sending prompt to Gemini model...")
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            try:
                # Parse the JSON response
                logger.info("Parsing Gemini response...")
                # Extract JSON from the response (in case there's additional text)
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)
                    
                    # Extract topics from the response
                    if "topics" in data:
                        topics = data["topics"]
                        
                        # If language is not English, add translations for each topic and subtopic
                        if self.language != "en":
                            logger.info(f"Adding translations for topics and subtopics to {self.language}")
                            for topic in topics:
                                # Store the English title for search purposes
                                topic["english_title"] = topic["title"]
                                
                                # Add translations for subtopics
                                for subtopic in topic["subtopics"]:
                                    # Store the English title for search purposes
                                    subtopic["english_title"] = subtopic["title"]
                            
                        return topics
                    else:
                        logger.error("Response JSON does not contain 'topics' key")
                        return self._generate_default_topics(problem_statement)
                else:
                    logger.error("Could not find JSON in response")
                    return self._generate_default_topics(problem_statement)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response: {response}")
                return self._generate_default_topics(problem_statement)
                
        except Exception as e:
            logger.error(f"Error analyzing problem statement: {str(e)}", exc_info=True)
            return self._generate_default_topics(problem_statement)
    
    def _generate_default_topics(self, problem_statement: str) -> List[Dict[str, Any]]:
        """
        Generate default topics and subtopics if the analysis fails.
        
        Args:
            problem_statement (str): The research problem
            
        Returns:
            List[Dict[str, Any]]: List of default topics and subtopics
        """
        logger.info("Generating default topics...")
        
        # Translate problem statement to English for better search results if not already in English
        english_problem_statement = problem_statement
        if self.language != "en":
            try:
                translation_prompt = f"""Translate the following research problem to English for academic research purposes:

Problem: {problem_statement}

Provide only the translated text without any explanations or additional content."""

                english_problem_statement = self._api_call_with_retry(
                    lambda: self.model.generate_content(translation_prompt).text
                )
                logger.info(f"Translated problem statement for default topics: {english_problem_statement}")
            except Exception as e:
                logger.error(f"Error translating problem statement for default topics: {str(e)}")
                # Continue with original problem statement if translation fails
        
        # Create default topics based on the problem statement
        default_topics = [
            {
                "title": "Overview of " + english_problem_statement[:50] + "..." if len(english_problem_statement) > 50 else english_problem_statement,
                "subtopics": [
                    {
                        "title": "Key Concepts in " + english_problem_statement[:40] + "..." if len(english_problem_statement) > 40 else english_problem_statement,
                        "status": "pending"
                    },
                    {
                        "title": "Current Research on " + english_problem_statement[:40] + "..." if len(english_problem_statement) > 40 else english_problem_statement,
                        "status": "pending"
                    }
                ]
            },
            {
                "title": "Applications and Implications",
                "subtopics": [
                    {
                        "title": "Practical Applications",
                        "status": "pending"
                    },
                    {
                        "title": "Future Directions",
                        "status": "pending"
                    }
                ]
            }
        ]
        
        # If language is not English, add translations for each topic and subtopic
        if self.language != "en":
            logger.info(f"Adding translations for default topics and subtopics to {self.language}")
            for topic in default_topics:
                # Store the English title for search purposes
                topic["english_title"] = topic["title"]
                
                # Add translations for subtopics
                for subtopic in topic["subtopics"]:
                    # Store the English title for search purposes
                    subtopic["english_title"] = subtopic["title"]
        
        return default_topics
    
    def update_topics_tracking_file(self) -> None:
        """
        Create or update the topics_and_subtopics.md tracking file.
        """
        logger.info("Updating topics and subtopics tracking file")
        
        try:
            # Path to the tracking file
            tracking_file = os.path.join(self.output_dir, "topics_and_subtopics.md")
            
            # Count total subtopics
            total_subtopics = sum(len(topic["subtopics"]) for topic in self.topics)
            
            # Get current date
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Generate markdown content
            markdown = f"""# LazyScholar Research Topics and Subtopics

This file tracks the generated topics and subtopics for your academic research project.

## Current Research Status

### Research Topics
"""
            
            # Add topics
            for topic in self.topics:
                markdown += f"- {topic['title']}\n"
            
            markdown += "\n### Subtopics Status\n"
            
            # Add subtopics with checkboxes
            for topic in self.topics:
                markdown += f"\n#### {topic['title']}\n"
                for subtopic in topic["subtopics"]:
                    markdown += f"- [ ] {subtopic}\n"
            
            markdown += f"""
## Research Progress
- Research initiated: {current_date}
- Topics generated: {len(self.topics)}
- Subtopics generated: {total_subtopics}
- Completed subtopics: 0
- In-progress subtopics: 0
- Remaining subtopics: {total_subtopics}

*Note: This file will be updated as research progresses. Checkboxes will be marked when subtopics are completed.*
"""
            
            # Write to file
            with open(tracking_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"Updated topics and subtopics tracking file: {tracking_file}")
            
        except Exception as e:
            logger.error(f"Error updating topics and subtopics tracking file: {e}")
    
    def extract_web_content(self, html_path: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """
        Extract content from an HTML file for a specific topic and subtopic.
        
        Args:
            html_path: The path to the HTML file
            topic: The topic
            subtopic: The subtopic
            
        Returns:
            Dict[str, Any]: The extracted content
        """
        try:
            # Read the HTML file
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract text from the HTML
            text = soup.get_text()
            
            # Create a prompt for the Gemini model
            prompt = f"""
            Extract relevant information from this web page for a research on the following topic and subtopic:
            
            Topic: {topic}
            Subtopic: {subtopic}
            
            Please analyze the following text and extract only the most relevant information related to the topic and subtopic.
            Do not organize the information into sections like "Key findings", "Analysis", etc.
            Just extract the relevant content in a concise form.
            
            {'' if self.language == 'en' else f'Ensure the extracted information is in {self.language} language.'}
            
            Text from the web page:
            {text[:10000]}  # Limit text to 10,000 characters to avoid token limits
            """
            
            # Generate content using the Gemini model
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            # Create the content dictionary
            content = {
                "source": os.path.basename(html_path),
                "content": response
            }
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from HTML: {str(e)}")
            return {
                "source": os.path.basename(html_path),
                "content": f"Error extracting content: {str(e)}"
            }

    def generate_final_paper(self, topics: List[Dict[str, Any]]) -> str:
        """
        Generate the final research paper by combining all subtopic content.
        """
        try:
            # Create the final paper path
            paper_path = os.path.join(self.output_dir, "final_paper.md")
            
            # Start building the paper
            markdown = f"""# Research Paper: {self.problem_statement}

## Abstract
"""
            # Generate abstract with LLM in the target language
            abstract_prompt = f"""
            Write a concise academic abstract (150-250 words) for a research paper on:
            {self.problem_statement}
            
            The paper covers these main topics:
            {", ".join([topic["title"] for topic in topics])}
            
            {'' if self.language == 'en' else f'Write the abstract in {self.language} language.'}
            """
            
            abstract = self._api_call_with_retry(
                lambda: self.model.generate_content(abstract_prompt).text
            )
            markdown += abstract + "\n\n"
            
            # Add table of contents
            markdown += "## Table of Contents\n"
            for topic in topics:
                markdown += f"\n### {topic['title']}\n"
                for subtopic in topic["subtopics"]:
                    markdown += f"* {subtopic['title']}\n"
            
            # Generate introduction in the target language
            intro_prompt = f"""
            Write a comprehensive academic introduction (400-600 words) for a research paper on:
            {self.problem_statement}
            
            The paper covers these main topics:
            {", ".join([topic["title"] for topic in topics])}
            
            Include proper in-text citations where appropriate using (Author, Year) format.
            {'' if self.language == 'en' else f'Write the introduction in {self.language} language.'}
            """
            
            introduction = self._api_call_with_retry(
                lambda: self.model.generate_content(intro_prompt).text
            )
            
            markdown += "\n## Introduction\n"
            markdown += introduction + "\n\n"
            
            # Collect all citations for the references section
            all_citations = []
            
            # Process each topic and its subtopics
            for topic in topics:
                markdown += f"\n## {topic['title']}\n"
                
                # Process each subtopic
                for subtopic in topic["subtopics"]:
                    # Get the subtopic file path
                    subtopic_file = os.path.join(
                        self.output_dir,
                        "topics",
                        self._sanitize_filename(topic["title"]),
                        f"{self._sanitize_filename(subtopic['title'])}.md"
                    )
                    
                    if os.path.exists(subtopic_file):
                        # Read the subtopic file
                        with open(subtopic_file, "r", encoding="utf-8") as f:
                            subtopic_content = f.read()
                        
                        # Extract references/citations
                        references_section = ""
                        references_match = re.search(r'## References\s*\n(.*?)(?:\n\n|\Z)', subtopic_content, re.DOTALL)
                        if references_match:
                            references_section = references_match.group(1).strip()
                            # Store citations for the final references section
                            citation_lines = references_section.split('\n')
                            for line in citation_lines:
                                line = line.strip()
                                if line and not line.startswith("No sources") and len(line) > 10:
                                    all_citations.append(line)
                        
                            # Remove the References section for processing
                            subtopic_content = re.sub(r'## References\s*\n.*?(?:\n\n|\Z)', '', subtopic_content, flags=re.DOTALL)
                        
                        # Also check for old Source section format
                        source_match = re.search(r'## Source\s*\n(.*?)(?:\n\n|\Z)', subtopic_content, re.DOTALL)
                        if source_match:
                            source_section = source_match.group(1).strip()
                            # Store citations for the final references section
                            source_lines = source_section.split('\n')
                            for line in source_lines:
                                line = line.strip()
                                if line and not line.startswith("No sources") and len(line) > 10:
                                    all_citations.append(line)
                        
                        # Remove the title header
                        subtopic_content = re.sub(r"^# [^\n]+\n+", "", subtopic_content)
                        
                        # If the content is already in the target language (from _write_subtopic_file),
                        # we don't need to translate it again, just enhance it
                        section_prompt = f"""
                        Rewrite and enhance the following content into a polished academic section for a research paper.
                        
                        Topic: {topic["title"]}
                        Subtopic: {subtopic["title"]}
                        
                        IMPORTANT:
                        1. Preserve ALL in-text citations in (Author, Year) format
                        2. Maintain all factual information
                        3. Organize into logical paragraphs with smooth transitions
                        4. Use academic language and tone
                        5. Do not add new citations that aren't in the original text
                        {'' if self.language == 'en' else f'6. Ensure the text is in {self.language} language'}
                        
                        Content to enhance:
                        {subtopic_content}
                        
                        References to cite from (use these exact citations):
                        {references_section if references_match else source_section if source_match else ""}
                        """
                        
                        enhanced_section = self._api_call_with_retry(
                            lambda: self.model.generate_content(section_prompt).text
                        )
                        
                        # Add the enhanced section to the paper
                        markdown += f"\n### {subtopic['title']}\n"
                        markdown += enhanced_section + "\n\n"
                    else:
                        markdown += f"\n### {subtopic['title']}\n"
                        markdown += f"No content available for this subtopic.\n\n"
            
            # Generate conclusion in the target language
            conclusion_prompt = f"""
            Write an academic conclusion (300-500 words) for a research paper on:
            {self.problem_statement}
            
            The conclusion should:
            1. Summarize key findings
            2. Discuss implications
            3. Acknowledge limitations
            4. Suggest directions for future research
            
            Include proper in-text citations where appropriate using (Author, Year) format.
            {'' if self.language == 'en' else f'Write the conclusion in {self.language} language.'}
            """
            
            conclusion = self._api_call_with_retry(
                lambda: self.model.generate_content(conclusion_prompt).text
            )
            
            markdown += "\n## Conclusion\n"
            markdown += conclusion + "\n\n"
            
            # Add references section
            markdown += "\n## References\n\n"
            
            # Process and deduplicate citations
            unique_citations = []
            seen_citations = set()
            
            for citation in all_citations:
                # Normalize citation to help with deduplication
                # Remove numbers at the beginning (e.g., "1. ")
                normalized = re.sub(r'^\d+\.\s+', '', citation)
                
                # Skip if we've seen this citation before
                if normalized in seen_citations:
                    continue
                    
                seen_citations.add(normalized)
                unique_citations.append(citation)
            
            # Sort citations alphabetically
            unique_citations.sort(key=lambda x: re.sub(r'^\d+\.\s+', '', x).lower())
            
            # Add citations to the references section
            for i, citation in enumerate(unique_citations, 1):
                # If citation already starts with a number, replace it
                citation = re.sub(r'^\d+\.\s+', '', citation)
                # Keep the citation simple, just the filename
                markdown += f"{i}. {citation}\n\n"
            
            if not unique_citations:
                markdown += "No references were found in the source materials.\n"
            
            # Write the paper
            with open(paper_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"Generated final paper at {paper_path}")
            return paper_path
            
        except Exception as e:
            logger.error(f"Error generating final paper: {str(e)}")
            return None
    
    def _enhance_references(self, references: List[Dict[str, Any]]) -> List[str]:
        """
        Enhance references with detailed academic citations.
        
        Args:
            references: List of references to enhance
            
        Returns:
            List of enhanced references
        """
        enhanced_references = []
        
        for ref in references:
            topic = ref.get("topic", "")
            subtopic = ref.get("subtopic", "")
            sources = ref.get("sources", [])
            pdf_files = ref.get("pdf_files", [])
            
            # Create a prompt for the Gemini model
            prompt = f"""
            You are an academic citation expert. Convert the following source references into detailed academic citations in APA format.
            
            Topic: {topic}
            Subtopic: {subtopic}
            Sources: {sources}
            PDF Files: {pdf_files}
            
            For each source, create a proper academic citation. If the source is an arXiv paper, use the arXiv ID to infer the publication year.
            If author names are not available, use placeholder [Author, A. A.] and mark the citation as [inferred].
            If the title is not available, use a placeholder [Title of paper] based on the topic and subtopic, and mark the citation as [inferred].
            """
            
            try:
                response = self.model.generate_content(prompt)
                enhanced_citations = response.text.strip().split('\n')
                enhanced_references.extend(enhanced_citations)
            except Exception as e:
                logger.error(f"Error enhancing references: {str(e)}")
                # Fallback to original format
                enhanced_references.append(f"{topic} - {subtopic}: Multiple sources: {sources}")
        
        return enhanced_references

    def conduct_research(self, problem_statement: str, search_engine: str) -> str:
        """
        Conduct research based on the problem statement using the specified search engine.
        
        Args:
            problem_statement: The research problem statement
            search_engine: The search engine URL to use
            
        Returns:
            Path to the generated final paper
        """
        logger.info(f"Conducting research on: {problem_statement}")
        logger.info(f"Using search engine: {search_engine}")
        
        # Store the problem statement
        self.problem_statement = problem_statement
        
        # Generate topics and subtopics
        self.topics = self.analyze_problem_statement(problem_statement)
        
        # Update the topics tracking file
        self.update_topics_tracking_file()
        
        # Start the browser
        logger.info("Starting browser...")
        self.start_browser()
        logger.info("Browser started successfully")
        
        try:
            # Process each topic and subtopic
            for topic_index, topic_data in enumerate(self.topics):
                topic_title = topic_data["title"]
                subtopics = topic_data["subtopics"]
                
                logger.info(f"Processing topic {topic_index + 1}/{len(self.topics)}: {topic_title}")
                
                # Create topic directory
                topic_dir = os.path.join(self.output_dir, "topics", self._sanitize_filename(topic_title))
                ensure_directory(topic_dir)
                
                # Process each subtopic
                for subtopic_index, subtopic_data in enumerate(subtopics):
                    subtopic_title = subtopic_data["title"]
                    
                    logger.info(f"Processing subtopic {subtopic_index + 1}/{len(subtopics)}: {subtopic_title}")
                    
                    # Set current topic and subtopic
                    self.current_topic = topic_title
                    self.current_subtopic = subtopic_title
                    
                    # Use English title for search if available
                    search_title = subtopic_data.get("english_title", subtopic_title)
                    
                    # Search for PDFs related to the subtopic
                    search_query = f"{search_title} {self.search_suffix}"
                    
                    # Perform the search based on the search engine
                    pdf_urls = self._search_for_pdfs(search_query, search_engine)
                    
                    # Download and process PDFs
                    pdf_contents = []
                    max_pdfs = self.max_pdfs_per_topic
                    
                    logger.info(f"Attempting to download and process up to {max_pdfs} PDFs")
                    
                    # First, try to download all PDFs
                    successful_downloads = []
                    for i, url in enumerate(pdf_urls):
                        try:
                            logger.info(f"Downloading PDF {i+1}/{len(pdf_urls)}: {url}")
                            pdf_path = self._download_pdf(url)
                            if pdf_path:
                                successful_downloads.append(pdf_path)
                                logger.info(f"Successfully downloaded PDF {i+1}: {pdf_path}")
                            else:
                                logger.warning(f"Failed to download PDF {i+1}: {url}")
                        except Exception as e:
                            logger.error(f"Error downloading PDF {url}: {str(e)}")
                    
                    logger.info(f"Successfully downloaded {len(successful_downloads)} PDFs out of {len(pdf_urls)} URLs")
                    
                    # If we don't have enough PDFs, try a different search query
                    if len(successful_downloads) < max_pdfs and self.focus in ["pdf", "all"]:
                        additional_query = f"{search_title} filetype:pdf {self.search_suffix}"
                        logger.info(f"Not enough PDFs downloaded. Trying additional search with query: {additional_query}")
                        
                        # Try with Google directly
                        try:
                            self.browser.get("https://www.google.com/")
                            
                            # Find the search box
                            search_box = WebDriverWait(self.browser, self.timeout).until(
                                EC.presence_of_element_located((By.NAME, "q"))
                            )
                            
                            # Enter the search query
                            search_box.clear()
                            search_box.send_keys(additional_query)
                            search_box.send_keys(Keys.RETURN)
                            
                            # Wait for results to load
                            time.sleep(5)
                            
                            # Find PDF links
                            pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                            additional_urls = []
                            
                            for link in pdf_links:
                                href = link.get_attribute("href")
                                if href and ".pdf" in href and href not in pdf_urls:
                                    additional_urls.append(href)
                            
                            logger.info(f"Found {len(additional_urls)} additional PDF URLs")
                            
                            # Download additional PDFs
                            for i, url in enumerate(additional_urls):
                                if len(successful_downloads) >= max_pdfs:
                                    break
                                    
                                try:
                                    logger.info(f"Downloading additional PDF {i+1}/{len(additional_urls)}: {url}")
                                    pdf_path = self._download_pdf(url)
                                    if pdf_path:
                                        successful_downloads.append(pdf_path)
                                        logger.info(f"Successfully downloaded additional PDF: {pdf_path}")
                                    else:
                                        logger.warning(f"Failed to download additional PDF: {url}")
                                except Exception as e:
                                    logger.error(f"Error downloading additional PDF {url}: {str(e)}")
                        except Exception as e:
                            logger.warning(f"Error with additional Google search: {str(e)}")
                    
                    # Now process all successfully downloaded PDFs
                    logger.info(f"Processing {len(successful_downloads)} PDFs")
                    for i, pdf_path in enumerate(successful_downloads):
                        try:
                            logger.info(f"Extracting content from PDF {i+1}/{len(successful_downloads)}: {pdf_path}")
                            content = self._extract_pdf_content(pdf_path, topic_title, subtopic_title)
                            if content:
                                pdf_contents.append(content)
                                logger.info(f"Successfully extracted content from PDF {i+1}")
                            else:
                                logger.warning(f"Failed to extract content from PDF {i+1}: {pdf_path}")
                        except Exception as e:
                            logger.error(f"Error extracting content from PDF {pdf_path}: {str(e)}")
                    
                    logger.info(f"Successfully processed {len(pdf_contents)} PDFs out of {len(successful_downloads)} downloaded")
                    
                    # Write subtopic file
                    subtopic_file = os.path.join(topic_dir, f"{self._sanitize_filename(subtopic_title)}.md")
                    self._write_subtopic_file(subtopic_file, topic_title, subtopic_title, pdf_contents)
                    
                    # Update subtopic status
                    subtopic_data["status"] = "completed"
            
            # Generate the final paper
            final_paper_path = self.generate_final_paper(self.topics)
            logger.info(f"Final paper generated at: {final_paper_path}")
            
            # Check if we should format as academic paper
            if self.academic_format:
                logger.info("Formatting final paper as academic paper...")
                try:
                    # Import the academic_formatter module
                    import academic_formatter
                    
                    # Initialize the model
                    model = academic_formatter.initialize_model()
                    if not model:
                        logger.error("Failed to initialize model for academic formatting")
                        return final_paper_path
                    
                    # Extract references and content
                    pdf_references, content = academic_formatter.extract_references_from_final_paper(final_paper_path)
                    
                    # Format as academic paper
                    formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_references, self.language)
                    
                    # Save formatted paper
                    output_path = academic_formatter.save_formatted_paper(final_paper_path, formatted_paper)
                    
                    if output_path:
                        logger.info(f"Successfully formatted final paper as academic paper at {output_path}")
                    else:
                        logger.error("Failed to save formatted academic paper")
                except Exception as e:
                    logger.error(f"Error formatting final paper: {str(e)}")
            
            return final_paper_path
        finally:
            # Close the browser
            self.close_browser()
    
    def _search_for_pdfs(self, query: str, search_engine: str) -> List[str]:
        """
        Search for PDFs related to the query using the specified search engine.
        
        Args:
            query: The search query
            search_engine: The search engine URL
            
        Returns:
            List of PDF URLs
        """
        try:
            logger.info(f"Searching for PDFs with query: {query}")
            logger.info(f"Using search engine: {search_engine}")
            
            pdf_urls = []
            
            # Different search engines have different search interfaces
            if "arxiv.org" in search_engine:
                # For ArXiv, use a direct search approach
                logger.info("Using ArXiv direct search approach")
                
                # Format the query for ArXiv search
                formatted_query = query.replace(" ", "+")
                search_url = f"https://arxiv.org/search/?query={formatted_query}&searchtype=all"
                
                logger.info(f"Navigating to search URL: {search_url}")
                self.browser.get(search_url)
                
                # Wait for results to load
                time.sleep(5)
                
                # Take a screenshot for debugging
                screenshot_path = os.path.join(self.output_dir, "arxiv_search_results.png")
                self.browser.save_screenshot(screenshot_path)
                
                # Try to find result items
                try:
                    # Look for the results list
                    results_container = WebDriverWait(self.browser, self.timeout).until(
                        EC.presence_of_element_located((By.ID, "main-container"))
                    )
                    
                    # Find all paper entries
                    paper_entries = results_container.find_elements(By.CSS_SELECTOR, ".arxiv-result")
                    logger.info(f"Found {len(paper_entries)} paper entries")
                    
                    # Process each paper entry
                    for entry in paper_entries[:self.max_pdfs_per_topic]:
                        try:
                            # Find the title link which contains the paper ID
                            title_link = entry.find_element(By.CSS_SELECTOR, "p.title > a")
                            paper_url = title_link.get_attribute("href")
                            
                            if paper_url and "/abs/" in paper_url:
                                # Extract the paper ID
                                paper_id = paper_url.split("/abs/")[1]
                                
                                # Construct the PDF URL
                                pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
                                logger.info(f"Found paper: {paper_url}, PDF: {pdf_url}")
                                pdf_urls.append(pdf_url)
                        except Exception as e:
                            logger.warning(f"Error processing paper entry: {str(e)}")
                            continue
                    
                except TimeoutException:
                    logger.warning("Timeout waiting for ArXiv results container")
                
                # If no results found with the above method, try a more generic approach
                if not pdf_urls:
                    logger.info("No results found with standard method, trying generic approach")
                    
                    # Look for any links that might be PDF links
                    links = self.browser.find_elements(By.TAG_NAME, "a")
                    
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if href and ("/pdf/" in href or href.endswith(".pdf")):
                                logger.info(f"Found PDF link with generic approach: {href}")
                                pdf_urls.append(href)
                        except:
                            continue
                    
                    # If still no results, try to find abstract links and convert them
                    if not pdf_urls:
                        logger.info("Trying to find abstract links")
                        
                        for link in links:
                            try:
                                href = link.get_attribute("href")
                                if href and "/abs/" in href:
                                    # Convert abstract URL to PDF URL
                                    pdf_url = href.replace("/abs/", "/pdf/") + ".pdf"
                                    logger.info(f"Converted abstract to PDF link: {pdf_url}")
                                    pdf_urls.append(pdf_url)
                            except:
                                continue
                
            elif "scholar.google.com" in search_engine:
                # Navigate to Google Scholar
                self.browser.get("https://scholar.google.com/")
                
                # Find the search box
                search_box = WebDriverWait(self.browser, self.timeout).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                
                # Enter the search query
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                
                # Wait for results to load
                time.sleep(5)
                
                # Take a screenshot for debugging
                screenshot_path = os.path.join(self.output_dir, "google_scholar_results.png")
                self.browser.save_screenshot(screenshot_path)
                
                # Try multiple approaches to find PDF links
                # 1. Direct PDF links
                pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                for link in pdf_links:
                    href = link.get_attribute("href")
                    if href and ".pdf" in href:
                        pdf_urls.append(href)
                
                # 2. Look for [PDF] links which are common in Google Scholar
                if len(pdf_urls) < self.max_pdfs_per_topic:
                    pdf_text_links = self.browser.find_elements(By.XPATH, "//a[contains(text(), '[PDF]')]")
                    for link in pdf_text_links:
                        href = link.get_attribute("href")
                        if href:
                            pdf_urls.append(href)
                
                # 3. Try to find links to publisher websites that might have PDFs
                if len(pdf_urls) < self.max_pdfs_per_topic:
                    # Get all result links
                    result_links = self.browser.find_elements(By.CSS_SELECTOR, ".gs_rt a")
                    
                    # Process only enough links to reach max_pdfs_per_topic
                    remaining_links = self.max_pdfs_per_topic - len(pdf_urls)
                    for link in result_links[:remaining_links]:
                        try:
                            href = link.get_attribute("href")
                            if href:
                                # Open the link in a new tab
                                original_window = self.browser.current_window_handle
                                self.browser.execute_script("window.open('');")
                                self.browser.switch_to.window(self.browser.window_handles[1])
                                
                                try:
                                    # Navigate to the link
                                    self.browser.get(href)
                                    time.sleep(3)
                                    
                                    # Look for PDF links on the page
                                    page_pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                                    for pdf_link in page_pdf_links:
                                        pdf_href = pdf_link.get_attribute("href")
                                        if pdf_href and ".pdf" in pdf_href:
                                            pdf_urls.append(pdf_href)
                                            break  # Only get one PDF per page
                                except Exception as e:
                                    logger.warning(f"Error exploring publisher page: {str(e)}")
                                
                                # Close the tab and switch back
                                self.browser.close()
                                self.browser.switch_to.window(original_window)
                                
                                # If we have enough PDFs, stop
                                if len(pdf_urls) >= self.max_pdfs_per_topic:
                                    break
                        except Exception as e:
                            logger.warning(f"Error processing result link: {str(e)}")
                
                # 4. Try to find more results by going to next page if needed
                if len(pdf_urls) < self.max_pdfs_per_topic:
                    try:
                        # Look for the "Next" button
                        next_button = self.browser.find_element(By.XPATH, "//button[@aria-label='Next']")
                        if next_button and next_button.is_enabled():
                            next_button.click()
                            time.sleep(5)
                            
                            # Find PDF links on the next page
                            pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                            for link in pdf_links:
                                href = link.get_attribute("href")
                                if href and ".pdf" in href:
                                    pdf_urls.append(href)
                                    if len(pdf_urls) >= self.max_pdfs_per_topic:
                                        break
                            
                            # Also look for [PDF] links
                            if len(pdf_urls) < self.max_pdfs_per_topic:
                                pdf_text_links = self.browser.find_elements(By.XPATH, "//a[contains(text(), '[PDF]')]")
                                for link in pdf_text_links:
                                    href = link.get_attribute("href")
                                    if href:
                                        pdf_urls.append(href)
                                        if len(pdf_urls) >= self.max_pdfs_per_topic:
                                            break
                    except Exception as e:
                        logger.warning(f"Error navigating to next page: {str(e)}")
            
            else:
                # Generic search approach
                # Navigate to the search engine
                self.browser.get(search_engine)
                
                # Try to find a search box
                try:
                    search_box = WebDriverWait(self.browser, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                    )
                    
                    # Enter the search query
                    search_box.clear()
                    search_box.send_keys(query)
                    search_box.send_keys(Keys.RETURN)
                    
                    # Wait for results to load
                    time.sleep(5)
                    
                    # Take a screenshot for debugging
                    screenshot_path = os.path.join(self.output_dir, "generic_search_results.png")
                    self.browser.save_screenshot(screenshot_path)
                    
                    # Find PDF links
                    pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    for link in pdf_links:
                        href = link.get_attribute("href")
                        if href and ".pdf" in href:
                            pdf_urls.append(href)
                    
                    # If we don't have enough PDFs, try to find more by exploring result links
                    if len(pdf_urls) < self.max_pdfs_per_topic:
                        # Get all links
                        all_links = self.browser.find_elements(By.TAG_NAME, "a")
                        
                        # Process only enough links to reach max_pdfs_per_topic
                        remaining_links = self.max_pdfs_per_topic - len(pdf_urls)
                        for link in all_links[:remaining_links * 3]:  # Check more links than needed
                            try:
                                href = link.get_attribute("href")
                                if href and not any(pdf_url in href for pdf_url in pdf_urls):
                                    # Open the link in a new tab
                                    original_window = self.browser.current_window_handle
                                    self.browser.execute_script("window.open('');")
                                    self.browser.switch_to.window(self.browser.window_handles[1])
                                    
                                    try:
                                        # Navigate to the link
                                        self.browser.get(href)
                                        time.sleep(3)
                                        
                                        # Look for PDF links on the page
                                        page_pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                                        for pdf_link in page_pdf_links:
                                            pdf_href = pdf_link.get_attribute("href")
                                            if pdf_href and ".pdf" in pdf_href:
                                                pdf_urls.append(pdf_href)
                                                break  # Only get one PDF per page
                                    except Exception as e:
                                        logger.warning(f"Error exploring result page: {str(e)}")
                                    
                                    # Close the tab and switch back
                                    self.browser.close()
                                    self.browser.switch_to.window(original_window)
                                    
                                    # If we have enough PDFs, stop
                                    if len(pdf_urls) >= self.max_pdfs_per_topic:
                                        break
                            except Exception as e:
                                logger.warning(f"Error processing link: {str(e)}")
                
                except TimeoutException:
                    logger.error("Timeout waiting for search box on generic search engine")
            
            # Limit the number of PDFs
            pdf_urls = pdf_urls[:self.max_pdfs_per_topic]
            logger.info(f"Found {len(pdf_urls)} PDF links")
            
            # If we still don't have enough PDFs, try a different search query
            if len(pdf_urls) < self.max_pdfs_per_topic:
                logger.info(f"Only found {len(pdf_urls)} PDFs, trying with a modified query")
                
                # Add "filetype:pdf" to the query if not already present
                if "filetype:pdf" not in query.lower():
                    modified_query = f"{query} filetype:pdf"
                    
                    # Try with Google directly
                    try:
                        self.browser.get("https://www.google.com/")
                        
                        # Find the search box
                        search_box = WebDriverWait(self.browser, self.timeout).until(
                            EC.presence_of_element_located((By.NAME, "q"))
                        )
                        
                        # Enter the search query
                        search_box.clear()
                        search_box.send_keys(modified_query)
                        search_box.send_keys(Keys.RETURN)
                        
                        # Wait for results to load
                        time.sleep(5)
                        
                        # Take a screenshot for debugging
                        screenshot_path = os.path.join(self.output_dir, "google_pdf_search_results.png")
                        self.browser.save_screenshot(screenshot_path)
                        
                        # Find PDF links
                        pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                        for link in pdf_links:
                            href = link.get_attribute("href")
                            if href and ".pdf" in href and href not in pdf_urls:
                                pdf_urls.append(href)
                                if len(pdf_urls) >= self.max_pdfs_per_topic:
                                    break
                    except Exception as e:
                        logger.warning(f"Error with modified Google search: {str(e)}")
            
            # Final limit check
            pdf_urls = pdf_urls[:self.max_pdfs_per_topic]
            logger.info(f"Final count: Found {len(pdf_urls)} PDF links")
            
            return pdf_urls
            
        except Exception as e:
            logger.error(f"Error searching for PDFs: {str(e)}")
            # Take a screenshot for debugging
            try:
                screenshot_path = os.path.join(self.output_dir, "search_error.png")
                self.browser.save_screenshot(screenshot_path)
                logger.info(f"Error screenshot saved to {screenshot_path}")
            except:
                pass
            return []
    
    def _download_pdf(self, url: str) -> Optional[str]:
        """
        Download a PDF from a URL.
        
        Args:
            url: The URL of the PDF to download
            
        Returns:
            Optional[str]: The path to the downloaded PDF, or None if download failed
        """
        try:
            logger.info(f"Attempting to download PDF from: {url}")
            
            # Create the PDF directory
            pdf_dir = os.path.join(self.output_dir, "pdfs")
            ensure_directory(pdf_dir)
            
            # Find the next available number for the PDF
            existing_pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf') and f[0].isdigit()]
            if existing_pdfs:
                # Extract numbers from filenames and find the highest
                numbers = [int(re.match(r'(\d+)', f).group(1)) for f in existing_pdfs if re.match(r'(\d+)', f)]
                next_number = max(numbers) + 1 if numbers else 1
            else:
                next_number = 1
            
            # Create the filename with the next number
            filename = f"{next_number}.pdf"
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Download the PDF
            logger.info(f"Downloading to: {pdf_path}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Implement retry logic with exponential backoff
            max_retries = 5
            retry_delay = 2
            
            for retry_count in range(max_retries):
                try:
                    response = requests.get(url, stream=True, timeout=self.timeout, headers=headers)
                    
                    # Handle rate limiting (429 Too Many Requests)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', retry_delay))
                        logger.warning(f"Rate limited (429). Waiting for {retry_after} seconds before retry {retry_count+1}/{max_retries}")
                        time.sleep(retry_after)
                        # Increase the delay for the next retry (exponential backoff)
                        retry_delay = min(retry_delay * 2, 60)  # Cap at 60 seconds
                        continue
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Check if the content is a PDF
                        content_type = response.headers.get('Content-Type', '')
                        if 'application/pdf' in content_type or url.endswith('.pdf'):
                            # Save the PDF
                            with open(pdf_path, "wb") as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            
                            logger.info(f"PDF downloaded successfully to: {pdf_path}")
                            return pdf_path
                        else:
                            logger.warning(f"URL does not point to a PDF. Content-Type: {content_type}")
                            
                            # Try to download anyway if the URL ends with .pdf
                            if url.endswith('.pdf'):
                                logger.info("URL ends with .pdf, attempting to download anyway")
                                with open(pdf_path, "wb") as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                logger.info(f"PDF downloaded successfully to: {pdf_path}")
                                return pdf_path
                    else:
                        logger.warning(f"Failed to download PDF. Status code: {response.status_code}")
                        
                        # If we get a server error, wait and retry
                        if response.status_code >= 500:
                            logger.warning(f"Server error ({response.status_code}). Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay = min(retry_delay * 2, 60)  # Cap at 60 seconds
                            continue
                    
                    # If we get here, either the download was successful or we got a non-retryable error
                    break
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error while downloading PDF: {str(e)}")
                    
                    # Wait and retry for network-related errors
                    if retry_count < max_retries - 1:  # Don't sleep on the last retry
                        logger.warning(f"Network error. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 60)  # Cap at 60 seconds
                        continue
                    break
            
            # If all retries failed, try using the browser as a fallback
            logger.info("Attempting to download using the browser")
            try:
                # Navigate to the PDF URL
                self.browser.get(url)
                
                # Wait for the PDF to load
                time.sleep(5)
                
                # Save the page source
                page_source = self.browser.page_source
                
                # Check if it's a PDF
                if "PDF" in page_source or "%PDF" in page_source:
                    # Save the PDF
                    with open(pdf_path, "wb") as f:
                        f.write(page_source.encode('utf-8'))
                    
                    logger.info(f"PDF downloaded using browser to: {pdf_path}")
                    return pdf_path
                else:
                    logger.warning("Browser download failed: Not a PDF")
            except Exception as browser_e:
                logger.error(f"Browser download error: {str(browser_e)}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            return None
    
    def _extract_pdf_content(self, pdf_path: str, topic: str, subtopic: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a PDF for a specific topic and subtopic.
        
        Args:
            pdf_path: The path to the PDF
            topic: The topic
            subtopic: The subtopic
            
        Returns:
            Optional[Dict[str, Any]]: The extracted content, or None if extraction failed
        """
        try:
            # Read the PDF
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
            
            # Extract text from the PDF
            text = self._extract_text_from_pdf(pdf_content)
            if not text:
                logger.error(f"Failed to extract text from PDF: {pdf_path}")
                return None
            
            # Create a prompt for the Gemini model
            prompt = f"""
            Extract relevant information from this academic paper for a research on the following topic and subtopic:
            
            Topic: {topic}
            Subtopic: {subtopic}
            
            Please analyze the following text and extract only the most relevant information related to the topic and subtopic.
            Do not organize the information into sections like "Key findings", "Analysis", etc.
            Just extract the relevant content in a concise form.
            
            {'' if self.language == 'en' else f'Ensure the extracted information is in {self.language} language.'}
            
            Text from the paper:
            {text[:10000]}  # Limit text to 10,000 characters to avoid token limits
            """
            
            # Generate content using the Gemini model
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            # Create the content dictionary
            content = {
                "source": os.path.basename(pdf_path),
                "content": response
            }
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from PDF: {str(e)}")
            return None
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from a PDF.
        
        Args:
            pdf_content: The PDF content as bytes
            
        Returns:
            Optional[str]: The extracted text, or None if extraction failed
        """
        try:
            # Try to import PyPDF2
            import PyPDF2
            from PyPDF2 import PdfReader
            
            # Create a BytesIO object from the PDF content
            pdf_file = BytesIO(pdf_content)
            
            # Extract text with PyPDF2
            reader = PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def _write_subtopic_file(self, file_path: str, topic: str, subtopic: str, contents: List[Dict[str, Any]]) -> None:
        """
        Write a subtopic file with the extracted content.
        
        Args:
            file_path: The path to the file
            topic: The topic
            subtopic: The subtopic
            contents: The extracted content
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Start building the markdown
            markdown = f"# {subtopic}\n\n"
            
            # If we have content, process it
            if contents:
                # Combine all content
                combined_content = "\n\n".join([content["content"] for content in contents])
                
                # Create a prompt for the Gemini model to summarize and format the content
                prompt = f"""
                Synthesize the following extracted information into a cohesive academic section for a research paper.
                
                Topic: {topic}
                Subtopic: {subtopic}
                
                IMPORTANT:
                1. Organize the information logically
                2. Use academic language and tone
                3. Include proper in-text citations in (Author, Year) format
                4. Maintain all factual information
                5. Do not add any information that is not in the source material
                {'' if self.language == 'en' else f'6. Ensure the text is in {self.language} language'}
                
                Extracted information:
                {combined_content}
                """
                
                # Generate content using the Gemini model
                response = self._api_call_with_retry(
                    lambda: self.model.generate_content(prompt).text
                )
                
                # Add the response to the markdown
                markdown += response + "\n\n"
            else:
                # If no content, add a placeholder
                markdown += "No relevant information found for this subtopic.\n\n"
            
            # Add references section
            markdown += "## References\n\n"
            
            # If we have content, add references
            if contents:
                for i, content in enumerate(contents, 1):
                    source_file = content["source"]
                    
                    # Check if it's a PDF file
                    if source_file.lower().endswith('.pdf'):
                        # Just use the filename as the citation
                        citation = f"{i}. {source_file}"
                        markdown += f"{citation}\n"
                    else:
                        markdown += f"{i}. SOURCE: {source_file}\n"
                
            else:
                markdown += "No sources were used for this subtopic.\n"
            
            # Write the markdown to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"Wrote subtopic file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing subtopic file: {str(e)}")
            # Create a minimal file with error information
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {subtopic}\n\nError extracting content: {str(e)}\n")
            except:
                pass

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        Args:
            filename: The string to sanitize
            
        Returns:
            A sanitized string that can be used as a filename
        """
        # Replace invalid characters with underscores
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Trim whitespace and limit length
        sanitized = sanitized.strip()
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
            
        return sanitized

    def load_topics_from_md(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load topics and subtopics from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of topics with their subtopics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the markdown content to extract topics and subtopics
            topics = []
            current_topic = None
            
            for line in content.split('\n'):
                if line.startswith('## '):
                    # This is a topic
                    if current_topic:
                        topics.append(current_topic)
                    
                    topic_title = line[3:].strip()
                    current_topic = {
                        "title": topic_title,
                        "subtopics": []
                    }
                elif line.startswith('- ') and current_topic:
                    # This is a subtopic
                    subtopic_title = line[2:].strip()
                    current_topic["subtopics"].append({
                        "title": subtopic_title,
                        "status": "completed"
                    })
            
            # Add the last topic
            if current_topic:
                topics.append(current_topic)
            
            return topics
        except Exception as e:
            logger.error(f"Error loading topics from markdown file: {str(e)}")
            return []

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LazyScholar - Academic Research Assistant")
    parser.add_argument("problem_statement", type=str, help="The research problem statement")
    parser.add_argument("--search-engine", type=str, default="https://scholar.google.com",
                        help="Search engine URL (default: https://scholar.google.com)")
    parser.add_argument("--output-dir", type=str, default="research_output",
                        help="Directory to store research output (default: research_output)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout in seconds for browser operations (default: 120)")
    parser.add_argument("--max-pdfs", type=int, default=10,
                        help="Maximum number of PDFs to process per topic (default: 10)")
    parser.add_argument("--search-suffix", type=str, default="",
                        help="Suffix to append to search queries (e.g., 'filetype:pdf')")
    parser.add_argument("--focus", type=str, default="all", choices=["pdf", "html", "all"],
                        help="Type of content to focus on (default: all)")
    parser.add_argument("--regenerate-final-paper", action="store_true",
                        help="Regenerate the final paper from existing subtopic files")
    
    parser.add_argument(
        "--academic-format",
        action="store_true",
        help="Format the final paper as an academic paper with proper citations and references"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language code for the final paper (e.g., 'en', 'tr', 'es'). Topics and subtopics will be in English for better search results, but the final paper will be in the specified language."
    )
    
    args = parser.parse_args()
    
    return args

def main():
    """Main entry point for the LazyScholar application."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Configure logging
        logger.info("Parsing command line arguments...")
        
        # Print banner
        print("\n" + "=" * 80)
        print(" " * 19 + "LazyScholar - Academic Research Assistant")
        print("=" * 80 + "\n")
        
        # Log configuration
        logger.info("Configuration:")
        logger.info(f"Problem statement: {args.problem_statement}")
        logger.info(f"Search engine: {args.search_engine}")
        logger.info(f"Output directory: {args.output_dir}")
        logger.info(f"Headless mode: {args.headless}")
        logger.info(f"Timeout: {args.timeout} seconds")
        logger.info(f"Max PDFs per topic: {args.max_pdfs}")
        logger.info(f"Focus mode: {args.focus}")
        
        # Initialize LazyScholar
        logger.info("Initializing LazyScholar...")
        scholar = LazyScholar(
            headless=args.headless,
            output_dir=args.output_dir,
            timeout=args.timeout,
            search_suffix=args.search_suffix,
            max_pdfs_per_topic=args.max_pdfs,
            focus=args.focus,
            academic_format=args.academic_format,
            language=args.language
        )
        
        # Log academic format setting
        logger.info(f"Academic format: {args.academic_format}")
        logger.info(f"Language: {args.language}")
        
        # Check if we should just regenerate the final paper
        if hasattr(args, 'regenerate_final_paper') and args.regenerate_final_paper:
            logger.info("Regenerating final paper from existing subtopic files...")
            
            # Load topics from tracking file
            topics_file = os.path.join(args.output_dir, "topics_and_subtopics.md")
            if os.path.exists(topics_file):
                topics = scholar.load_topics_from_md(topics_file)
                
                # Generate final paper
                logger.info("Generating final paper using LLM...")
                final_paper_path = scholar.generate_final_paper(topics)
                logger.info(f"Generated final paper at {final_paper_path}")
                
                # Format as academic paper if requested
                if hasattr(args, 'academic_format') and args.academic_format:
                    logger.info("Formatting final paper as academic paper...")
                    try:
                        import academic_formatter
                        
                        # Initialize model
                        model = academic_formatter.initialize_model()
                        if not model:
                            logger.error("Failed to initialize model for academic formatting")
                            return
                        
                        # Extract references and content
                        pdf_references, content = academic_formatter.extract_references_from_final_paper(final_paper_path)
                        
                        # Format paper
                        formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_references, args.language)
                        
                        # Save formatted paper
                        output_path = academic_formatter.save_formatted_paper(final_paper_path, formatted_paper)
                        logger.info(f"Successfully formatted final paper as academic paper at {output_path}")
                    except Exception as e:
                        logger.error(f"Error formatting final paper: {str(e)}")
            else:
                logger.error(f"Topics file not found at {topics_file}")
                return
        
        # Start research process
        logger.info("Starting research process...")
        final_paper_path = scholar.conduct_research(args.problem_statement, args.search_engine)
        
        logger.info("Research completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
