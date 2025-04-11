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
from urllib.parse import urljoin, quote_plus
import hashlib
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from io import BytesIO, StringIO
import random
import shutil

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
    
    def __init__(self, headless: bool = False, output_dir: str = "research_output", timeout: int = 120, search_suffix: str = "", max_pdfs_per_topic: int = 10, focus: str = "all", academic_format: bool = False, language: str = "en", site_tld: str = None, minimum_pdfs: int = 3, crawl_depth: int = 3, max_crawl_pages: int = 20, search_purpose: str = "academic", require_pdfs: bool = True, max_references_per_subtopic: int = 10, output_format: str = "md", optimize_final_paper: bool = True):
        """
        Initialize the LazyScholar research assistant.
        
        Args:
            headless (bool): Whether to run the browser in headless mode (default: False)
            output_dir (str): Directory to save research output (default: "research_output")
            timeout (int): Timeout for browser operations in seconds (default: 120)
            search_suffix (str): Additional text to append to search queries (default: "")
            max_pdfs_per_topic (int): Maximum number of PDFs to download per topic (default: 10)
            focus (str): Focus of the research ('all', 'papers', 'books', 'articles') (default: "all")
            academic_format (bool): Whether to format output as academic paper (default: False)
            language (str): Language code for search results (default: "en")
            site_tld (str): TLD for search results (e.g., "edu", "org") (default: None)
            minimum_pdfs (int): Minimum number of PDFs to find before proceeding (default: 3)
            crawl_depth (int): Depth of web crawling for PDFs (default: 3)
            max_crawl_pages (int): Maximum number of pages to visit during crawling (default: 20)
            search_purpose (str): Purpose of the search ('academic', 'news', 'practical', 'travel', or 'general') (default: 'academic')
            require_pdfs (bool): Whether PDFs are required for the search
            max_references_per_subtopic (int): Maximum number of references to collect per subtopic (default: 10)
            output_format (str): Format for the final output ('md', 'pdf', 'html', 'epub', etc.) (default: 'md')
            optimize_final_paper (bool): Whether to optimize the final paper with LLM (default: True)
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
        self.site_tld = site_tld
        self.minimum_pdfs = minimum_pdfs
        self.crawl_depth = crawl_depth
        self.max_crawl_pages = max_crawl_pages
        self.search_purpose = search_purpose
        self.require_pdfs = require_pdfs
        self.output_format = output_format
        self.max_references_per_subtopic = max_references_per_subtopic
        self.optimize_final_paper = optimize_final_paper
        self.browser = None
        self.topics = []
        self.problem_statement = ""
        self.driver = None
        self.llm_model = "gemini-2.0-flash-exp"  # Set default LLM model
        
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
                model_name="gemini-2.5-pro-exp-03-25",
                generation_config=generation_config
            )
            
            # Initialize the client reference for use in _optimize_subtopic_content_with_llm
            self.client = self.model
            
            logger.info("Gemini models initialized successfully")
            logger.info("LazyScholar initialized")
        except Exception as e:
            logger.error(f"Error initializing Gemini models: {str(e)}")
            raise
    
    def _api_call_with_retry(self, api_func, max_retries=5, retry_delay=3):
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
                error_msg = str(e)
                
                # Check if it's a timeout or deadline exceeded error (504)
                if "504" in error_msg or "deadline exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                    # For timeout errors, use a much longer delay
                    current_delay = retry_delay * (3 ** retries)  # Use exponential backoff with base 3
                    current_delay = min(current_delay, 300)  # Cap at 5 minutes
                    
                    logger.warning(f"Timeout error (504). Waiting for {current_delay} seconds before retry {retries}/{max_retries}")
                    time.sleep(current_delay)
                    continue  # Continue immediately to next attempt
                
                # Check if it's a rate limit error (429)
                if "429" in error_msg or "Resource has been exhausted" in error_msg or "quota" in error_msg.lower():
                    # For rate limit errors, use a longer delay
                    current_delay = retry_delay * (2 ** retries)  # Exponential backoff
                    current_delay = min(current_delay, 60)  # Cap at 60 seconds
                    
                    logger.warning(f"Rate limit error (429). Waiting for {current_delay} seconds before retry {retries}/{max_retries}")
                    time.sleep(current_delay)
                else:
                    # For other errors, use standard backoff
                    if retries >= max_retries:
                        logger.error(f"API call failed after {max_retries} retries: {error_msg}")
                        raise
                    
                    logger.warning(f"API call failed: {error_msg}. Retrying in {retry_delay} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 30)  # Exponential backoff, capped at 30 seconds
        
        return None  # This should only be reached for rate limit errors
    
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
        Analyze the problem statement and generate topics and subtopics using LLM.
        
        Args:
            problem_statement: The research problem statement
            
        Returns:
            List of topics and subtopics
        """
        logger.info("Analyzing problem statement with LLM...")
        
        try:
            # Construct the prompt for topic generation
            prompt = f"""
            Given this research problem: "{problem_statement}"
            
            Generate a comprehensive research outline with main topics and subtopics.
            The outline should be thorough and academically structured.
            
            For each topic:
            1. Create subtopics that cover key aspects
            2. Include a specific search phrase for each subtopic that will help find relevant academic sources
            3. Ensure topics and subtopics are clearly focused and well-defined
            
            Format the response as a JSON array with this structure:
            [
                {{
                    "title": "Main Topic Name",
                    "subtopics": [
                        {{
                            "title": "Subtopic Name",
                            "status": "pending",
                            "search_phrase": "Specific search terms for this subtopic"
                        }}
                    ]
                }}
            ]
            
            Return ONLY the JSON array, no other text.
            """
            
            # Get topics from LLM
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            # Extract and parse JSON from response
            topics_json = self._extract_json_from_text(response)
            topics = json.loads(topics_json)
            
            # Validate the structure
            self._validate_topics_structure(topics)
            
            # Ensure search phrases are in English and well-formatted
            for topic in topics:
                for subtopic in topic["subtopics"]:
                    # Ensure the search phrase is in English
                    if not all(ord(c) < 128 for c in subtopic["search_phrase"]):
                        logger.info(f"Converting non-English search phrase to English: {subtopic['search_phrase']}")
                        try:
                            # Generate an English search phrase
                            english_prompt = f"""
                            Translate this search phrase to English, keeping only the most important keywords (5-8 words maximum):
                            "{subtopic['search_phrase']}"
                            
                            Just return the translated phrase, nothing else.
                            """
                            english_phrase = self._api_call_with_retry(
                                lambda: self.model.generate_content(english_prompt).text
                            )
                            subtopic["search_phrase"] = english_phrase.strip().replace("'", "").replace('"', '')
                        except Exception as e:
                            logger.error(f"Error translating search phrase: {str(e)}")
                            # Fallback to a simple English phrase
                            subtopic["search_phrase"] = f"{topic['title']} {subtopic['title']}".replace("'", "").replace('"', '')
            
            logger.info(f"Generated {len(topics)} topics with {sum(len(topic['subtopics']) for topic in topics)} subtopics using LLM")
            return topics
            
        except Exception as e:
            logger.error(f"Error analyzing problem statement with LLM: {str(e)}")
            logger.warning("Falling back to default topics...")
            return self._generate_default_topics(problem_statement)
    
    def _generate_default_topics(self, problem_statement: str) -> List[Dict[str, Any]]:
        """
        Generate default topics and subtopics if the API call fails.
        
        Args:
            problem_statement: The research problem statement
            
        Returns:
            List of default topics and subtopics
        """
        logger.info("Generating default topics...")
        
        # Use the specified search purpose
        if self.search_purpose == 'practical':
            # Default topics for practical/how-to guides
            return [
                {
                    "title": "Introduction and Basics",
                "subtopics": [
                        {"title": f"What is {problem_statement}", "status": "pending", 
                         "search_phrase": f"definition explanation what is {problem_statement} introduction basics"},
                        {"title": f"Why {problem_statement} is Important", "status": "pending",
                         "search_phrase": f"importance benefits advantages why {problem_statement} matters"},
                        {"title": f"Required Tools and Materials", "status": "pending",
                         "search_phrase": f"tools equipment materials supplies needed for {problem_statement}"}
                    ]
                },
                {
                    "title": "Step-by-Step Process",
                    "subtopics": [
                        {"title": "Getting Started", "status": "pending",
                         "search_phrase": f"how to begin start getting started with {problem_statement} first steps"},
                        {"title": "Main Procedure", "status": "pending",
                         "search_phrase": f"main steps procedure process method technique for {problem_statement}"},
                        {"title": "Finishing Steps", "status": "pending",
                         "search_phrase": f"final steps finishing completing {problem_statement} process"}
                    ]
                },
                {
                    "title": "Tips and Best Practices",
                    "subtopics": [
                        {"title": "Common Mistakes to Avoid", "status": "pending",
                         "search_phrase": f"common mistakes errors problems pitfalls to avoid in {problem_statement}"},
                        {"title": "Expert Tips", "status": "pending",
                         "search_phrase": f"expert tips tricks advice recommendations for {problem_statement}"},
                        {"title": "Troubleshooting", "status": "pending",
                         "search_phrase": f"troubleshooting fixing solving problems issues with {problem_statement}"}
                    ]
                },
                {
                    "title": "Advanced Techniques",
                    "subtopics": [
                        {"title": "Taking it to the Next Level", "status": "pending",
                         "search_phrase": f"advanced techniques methods strategies for {problem_statement}"},
                        {"title": "Alternative Methods", "status": "pending",
                         "search_phrase": f"alternative different approaches methods techniques for {problem_statement}"}
                    ]
                }
            ]
        elif self.search_purpose == 'travel':
            # Default topics for travel guides
            return [
                {
                    "title": "Overview and Planning",
                    "subtopics": [
                        {"title": f"Introduction to {problem_statement}", "status": "pending",
                         "search_phrase": f"{problem_statement} overview introduction travel guide highlights"},
                        {"title": "Best Time to Visit", "status": "pending",
                         "search_phrase": f"{problem_statement} best time to visit weather seasons climate tourism peak season"},
                        {"title": "Planning Your Trip", "status": "pending",
                         "search_phrase": f"{problem_statement} trip planning itinerary vacation preparation travel tips"}
                    ]
                },
                {
                    "title": "Getting There and Around",
                "subtopics": [
                        {"title": "Transportation Options", "status": "pending",
                         "search_phrase": f"how to get to {problem_statement} flights trains buses transportation"},
                        {"title": "Local Transportation", "status": "pending",
                         "search_phrase": f"{problem_statement} local transportation public transit metro subway taxis getting around"}
                    ]
                },
                {
                    "title": "Accommodation",
                    "subtopics": [
                        {"title": "Where to Stay", "status": "pending",
                         "search_phrase": f"{problem_statement} best areas neighborhoods districts to stay accommodation"},
                        {"title": "Recommended Hotels and Areas", "status": "pending",
                         "search_phrase": f"{problem_statement} recommended hotels hostels apartments best places to stay"}
                    ]
                },
                {
                    "title": "Top Attractions and Activities",
                    "subtopics": [
                        {"title": "Must-See Attractions", "status": "pending",
                         "search_phrase": f"{problem_statement} top attractions must-see sights landmarks tourist spots"},
                        {"title": "Activities and Experiences", "status": "pending",
                         "search_phrase": f"{problem_statement} activities things to do experiences tours adventures"},
                        {"title": "Day Trips", "status": "pending",
                         "search_phrase": f"{problem_statement} day trips nearby excursions surrounding areas worth visiting"}
                    ]
                },
                {
                    "title": "Food and Dining",
                    "subtopics": [
                        {"title": "Local Cuisine", "status": "pending",
                         "search_phrase": f"{problem_statement} local food cuisine traditional dishes specialties what to eat"},
                        {"title": "Recommended Restaurants", "status": "pending",
                         "search_phrase": f"{problem_statement} best restaurants cafes bars dining places where to eat"}
                    ]
                },
                {
                    "title": "Practical Information",
                    "subtopics": [
                        {"title": "Budget and Costs", "status": "pending",
                         "search_phrase": f"{problem_statement} travel costs budget expenses prices how much money"},
                        {"title": "Safety and Health", "status": "pending",
                         "search_phrase": f"{problem_statement} safety security health tips travel advice precautions"},
                        {"title": "Cultural Tips", "status": "pending",
                         "search_phrase": f"{problem_statement} cultural customs etiquette traditions local behavior tips"}
                    ]
                }
            ]
        elif self.search_purpose == 'news':
            # Default topics for news content
            return [
                {
                    "title": "Latest Developments",
                    "subtopics": [
                        {"title": f"Recent Updates on {problem_statement}", "status": "pending",
                         "search_phrase": f"{problem_statement} latest recent updates news developments current"},
                        {"title": "Breaking News", "status": "pending",
                         "search_phrase": f"{problem_statement} breaking news latest headlines current events"},
                        {"title": "Timeline of Events", "status": "pending",
                         "search_phrase": f"{problem_statement} timeline chronology sequence of events history"}
                    ]
                },
                {
                    "title": "Key Figures and Stakeholders",
                    "subtopics": [
                        {"title": "Main Actors", "status": "pending",
                         "search_phrase": f"{problem_statement} key players main actors figures people involved"},
                        {"title": "Official Statements", "status": "pending",
                         "search_phrase": f"{problem_statement} official statements announcements press releases"}
                    ]
                },
                {
                    "title": "Analysis and Impact",
                    "subtopics": [
                        {"title": "Expert Analysis", "status": "pending",
                         "search_phrase": f"{problem_statement} expert analysis commentary opinions insights"},
                        {"title": "Social and Economic Impact", "status": "pending",
                         "search_phrase": f"{problem_statement} impact effects consequences implications social economic"},
                        {"title": "Public Reaction", "status": "pending",
                         "search_phrase": f"{problem_statement} public reaction response sentiment social media"}
                    ]
                },
                {
                    "title": "Background and Context",
                    "subtopics": [
                        {"title": "Historical Context", "status": "pending",
                         "search_phrase": f"{problem_statement} background history context previous events"},
                        {"title": "Related Issues", "status": "pending",
                         "search_phrase": f"{problem_statement} related connected issues topics cases similar examples"}
                    ]
                },
                {
                    "title": "Future Outlook",
                    "subtopics": [
                        {"title": "Predictions and Forecasts", "status": "pending",
                         "search_phrase": f"{problem_statement} predictions forecasts future outlook expectations"},
                        {"title": "Upcoming Events", "status": "pending",
                         "search_phrase": f"{problem_statement} upcoming scheduled planned future events developments"}
                    ]
                }
            ]
        elif self.search_purpose == 'general':
            # Default topics for general search content
            return [
                {
                    "title": "Overview and Fundamentals",
                    "subtopics": [
                        {"title": f"What is {problem_statement}", "status": "pending",
                         "search_phrase": f"what is {problem_statement} definition explanation meaning overview"},
                        {"title": "Key Concepts", "status": "pending",
                         "search_phrase": f"{problem_statement} key basic concepts terminology fundamentals elements"},
                        {"title": "Types and Categories", "status": "pending",
                         "search_phrase": f"{problem_statement} types categories classifications varieties kinds"}
                    ]
                },
                {
                    "title": "History and Development",
                    "subtopics": [
                        {"title": "Origins and History", "status": "pending",
                         "search_phrase": f"{problem_statement} origins history beginning development evolution"},
                        {"title": "Major Developments", "status": "pending",
                         "search_phrase": f"{problem_statement} major significant developments milestones advancements"}
                    ]
                },
                {
                    "title": "Applications and Uses",
                    "subtopics": [
                        {"title": "Common Applications", "status": "pending",
                         "search_phrase": f"{problem_statement} common applications uses purposes functions utilities"},
                        {"title": "Real-World Examples", "status": "pending",
                         "search_phrase": f"{problem_statement} examples cases instances real-world applications"},
                        {"title": "Benefits and Advantages", "status": "pending",
                         "search_phrase": f"{problem_statement} benefits advantages positive aspects good points"}
                    ]
                },
                {
                    "title": "Issues and Considerations",
                    "subtopics": [
                        {"title": "Common Challenges", "status": "pending",
                         "search_phrase": f"{problem_statement} challenges problems issues difficulties concerns"},
                        {"title": "Limitations", "status": "pending",
                         "search_phrase": f"{problem_statement} limitations restrictions drawbacks constraints weaknesses"},
                        {"title": "Ethical Considerations", "status": "pending",
                         "search_phrase": f"{problem_statement} ethical moral social considerations implications issues"}
                    ]
                },
                {
                    "title": "Future Directions",
                    "subtopics": [
                        {"title": "Current Trends", "status": "pending",
                         "search_phrase": f"{problem_statement} current recent trends patterns developments directions"},
                        {"title": "Future Outlook", "status": "pending",
                         "search_phrase": f"{problem_statement} future outlook predictions forecasts expectations"}
                    ]
                }
            ]
        else:
            # Default topics for academic research
            return [
                {
                    "title": "Introduction and Background",
                    "subtopics": [
                        {"title": f"Overview of {problem_statement}", "status": "pending",
                         "search_phrase": f"{problem_statement} overview introduction background context research"},
                        {"title": "Historical Context", "status": "pending",
                         "search_phrase": f"{problem_statement} history historical development evolution timeline"},
                        {"title": "Significance and Relevance", "status": "pending",
                         "search_phrase": f"{problem_statement} significance importance relevance impact implications"}
                    ]
                },
                {
                    "title": "Literature Review",
                    "subtopics": [
                        {"title": "Current Research", "status": "pending",
                         "search_phrase": f"{problem_statement} current recent research studies findings literature review"},
                        {"title": "Theoretical Frameworks", "status": "pending",
                         "search_phrase": f"{problem_statement} theoretical frameworks models concepts theories approaches"},
                        {"title": "Research Gaps", "status": "pending",
                         "search_phrase": f"{problem_statement} research gaps limitations challenges future directions"}
                    ]
                },
                {
                    "title": "Methodology and Approach",
                    "subtopics": [
                        {"title": "Research Methods", "status": "pending",
                         "search_phrase": f"{problem_statement} research methods methodology approaches techniques"},
                        {"title": "Data Collection", "status": "pending",
                         "search_phrase": f"{problem_statement} data collection gathering methods techniques instruments"},
                        {"title": "Analysis Techniques", "status": "pending",
                         "search_phrase": f"{problem_statement} data analysis techniques methods statistical approaches"}
                    ]
                },
                {
                    "title": "Findings and Results",
                    "subtopics": [
                        {"title": "Key Findings", "status": "pending",
                         "search_phrase": f"{problem_statement} key findings results outcomes discoveries research"},
                        {"title": "Data Analysis", "status": "pending",
                         "search_phrase": f"{problem_statement} data analysis results statistics interpretation"},
                        {"title": "Interpretation of Results", "status": "pending",
                         "search_phrase": f"{problem_statement} interpretation explanation meaning of results findings"}
                    ]
                },
                {
                    "title": "Discussion and Implications",
                    "subtopics": [
                        {"title": "Theoretical Implications", "status": "pending",
                         "search_phrase": f"{problem_statement} theoretical implications contributions to theory"},
                        {"title": "Practical Applications", "status": "pending",
                         "search_phrase": f"{problem_statement} practical applications real-world implications uses"},
                        {"title": "Limitations and Future Research", "status": "pending",
                         "search_phrase": f"{problem_statement} limitations constraints future research directions"}
                    ]
                }
            ]
    
    def update_topics_tracking_file(self) -> None:
        """
        Create topics_and_subtopics.md tracking file if it doesn't exist.
        If file already exists, load topics from it to update memory.
        """
        logger.info("Checking topics and subtopics tracking file")
        
        try:
            # Path to the tracking file
            tracking_file = os.path.join(self.output_dir, "topics_and_subtopics.md")
            
            # If file exists, load topics from it
            if os.path.exists(tracking_file):
                logger.info(f"Topics and subtopics file exists at {tracking_file}, loading topics from it")
                loaded_topics = self.load_topics_from_md(tracking_file)
                if loaded_topics:
                    self.topics = loaded_topics
                    logger.info("Successfully loaded topics from file into memory")
                return
                
            # If file doesn't exist, create it with initial topics
            markdown = self._generate_topics_markdown(self.topics)
            with open(tracking_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            logger.info(f"Created initial topics and subtopics tracking file: {tracking_file}")
            
        except Exception as e:
            logger.error(f"Error handling topics and subtopics tracking file: {e}")
    
    def _generate_topics_markdown(self, topics: List[Dict[str, Any]]) -> str:
        """
        Generate markdown content for topics and subtopics.
        
        Args:
            topics: List of topics with their subtopics
            
        Returns:
            Markdown formatted string
        """
        # Count total subtopics
        total_subtopics = sum(len(topic.get("subtopics", [])) for topic in topics)
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Generate markdown content
        markdown = f"""# LazyScholar Research Topics and Subtopics

This file tracks the generated topics and subtopics for your academic research project.

## Current Research Status

### Research Topics
"""
        
        # Add topics
        for topic in topics:
            markdown += f"- {topic['title']}\n"
        
        markdown += "\n### Subtopics Status\n"
        
        # Add subtopics with checkboxes
        for topic in topics:
            markdown += f"\n#### {topic['title']}\n"
            if 'subtopics' in topic:
                for subtopic in topic["subtopics"]:
                    markdown += f"- [ ] {subtopic}\n"
        
        markdown += f"""
## Research Progress
- Research initiated: {current_date}
- Topics generated: {len(topics)}
- Subtopics generated: {total_subtopics}
- Completed subtopics: 0
- In-progress subtopics: 0
- Remaining subtopics: {total_subtopics}

*Note: This file will be updated as research progresses. Checkboxes will be marked when subtopics are completed.*
"""
        
        return markdown
    
    def extract_web_content(self, html_path: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """
        Extract content from an HTML file using the LLM.
        
        Args:
            html_path: Path to the HTML file
            topic: The main topic
            subtopic: The subtopic to extract content for
            
        Returns:
            Dictionary with extracted content and source
        """
        try:
            logger.info(f"Extracting content from HTML file: {html_path}")
            
            # Read the HTML file
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Use BeautifulSoup to extract text and reduce token count
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "iframe", "nav", "footer", "header", "aside"]):
                script.extract()
                
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up text: remove extra whitespace
            text = ' '.join(text.split())
            
            # Limit text length to avoid token limit issues (approximately 100,000 characters)
            max_chars = 100000
            if len(text) > max_chars:
                text = text[:max_chars] + "... [content truncated due to length]"
            
            logger.info(f"Extracted {len(text)} characters of text from HTML")
            
            # Prepare the prompt for the LLM
            prompt = f"""
            You are a research assistant helping to extract relevant information from web content.
            
            TOPIC: {topic}
            SUBTOPIC: {subtopic}
            
            Please extract the most relevant information from the following web content related to the subtopic.
            Focus on factual information, statistics, and useful details.
            
            WEB CONTENT:
            {text}
            
            Please provide a concise summary of the relevant information (300-500 words).
            Include any relevant facts, figures, or data points that would be useful for the research.
            """
            
            # Call the LLM to extract content
            response = self._api_call_with_retry(
                lambda: genai.GenerativeModel('gemini-2.0-flash-exp').generate_content(prompt)
            )
            
            # Extract the content from the response
            extracted_content = response.text
            
            # Return the extracted content
            return {
                "content": extracted_content,
                "source": f"[HTML] {os.path.basename(html_path)}"
            }
        except Exception as e:
            logger.error(f"Error extracting content from HTML: {str(e)}")
            return None
    
    def _generate_conclusion_with_llm(self, topics: List[Dict[str, Any]]) -> str:
        """
        Generate a conclusion section by sending all topic content to the LLM.
        
        Args:
            topics: List of topics and subtopics
            
        Returns:
            A conclusion section in markdown format
        """
        logger.info("Generating conclusion section with LLM...")
        
        # Collect all the topic and subtopic content
        topic_contents = []
        
        # Process each topic
        for topic in topics:
            topic_title = topic.get("title", "")
            subtopics = topic.get("subtopics", [])
            
            # Add the topic to the content
            topic_contents.append(f"Topic: {topic_title}")
            
            # Process each subtopic
            for subtopic in subtopics:
                subtopic_title = subtopic.get("title", "")
                
                # Find the subtopic file path
                subtopic_file = subtopic.get("file", "")
                if not subtopic_file or not os.path.exists(subtopic_file):
                    # Try to find the file in the topics directory
                    topic_dir = os.path.join(self.output_dir, "topics", self._sanitize_filename(topic_title))
                    potential_file = os.path.join(topic_dir, f"{self._sanitize_filename(subtopic_title)}.md")
                    if os.path.exists(potential_file):
                        subtopic_file = potential_file
                
                # Read the subtopic file
                if subtopic_file and os.path.exists(subtopic_file):
                    try:
                        with open(subtopic_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Extract the content without references section
                        main_content = content.split("## References")[0].strip() if "## References" in content else content.strip()
                        
                        # Add summary to the list
                        topic_contents.append(f"Subtopic: {subtopic_title}\nSummary: {main_content[:300]}...")
                    except Exception as e:
                        logger.error(f"Error reading subtopic file {subtopic_file} for conclusion: {str(e)}")
        
        # If no content was found, return a default conclusion
        if not topic_contents:
            logger.warning("No topic content found for generating conclusion")
            return "# Conclusion\n\nNo content was available to generate a conclusion."
        
        # Prepare prompt for LLM
        prompt = f"""
        Please generate a comprehensive conclusion section in {self.language} language for a research paper with the following topics and subtopics:
        
        {os.linesep.join(topic_contents)}
        
        The conclusion should:
        1. Summarize the key findings and insights from all topics
        2. Connect the main themes across different sections
        3. Provide final thoughts and significance of the research
        4. Write at least 500-700 words in length
        5. Be written in {self.language} language
        6. Use a formal academic tone
        7. Be formatted in markdown with the title "# Conclusion"
        8. Don't be afraid to be exact and share your own thoughts and insights based on the topics and subtopics findings.
        9. Make the conclusion clear and direct.
        
        Return only the conclusion text in markdown format, starting with "# Conclusion".
        """
        
        try:
            # Call the LLM to generate the conclusion
            def generate_conclusion_wrapper():
                try:
                    response = self.model.generate_content(prompt)
                    # Check if response has the expected attributes
                    if hasattr(response, 'text'):
                        return response
                    else:
                        logger.warning(f"Unexpected response format from Gemini for conclusion: {response}")
                        raise ValueError(f"Unexpected response format: {response}")
                except Exception as e:
                    logger.error(f"Error in conclusion generation: {str(e)}")
                    raise
            
            # Use the retry mechanism with our wrapper function
            response = self._api_call_with_retry(generate_conclusion_wrapper)
            
            if response and hasattr(response, 'text'):
                # Extract content from response
                conclusion_text = response.text.strip()
                
                # Ensure the conclusion starts with the proper heading
                if not conclusion_text.startswith("# Conclusion"):
                    conclusion_text = "# Conclusion\n\n" + conclusion_text
                
                logger.info("Successfully generated conclusion with LLM")
                return conclusion_text
            else:
                logger.warning("Failed to generate conclusion with LLM, using default")
                return "# Conclusion\n\nThe research presented in this paper covers multiple aspects of the topic. Further research could explore additional dimensions and implications."
            
        except Exception as e:
            logger.error(f"Error generating conclusion with LLM: {str(e)}")
            # Return a default conclusion in case of error
            return "# Conclusion\n\nThe research presented in this paper provides valuable insights into the topic. The findings suggest several important implications for theory and practice."

    def generate_final_paper(self, topics: List[Dict[str, Any]]) -> str:
        """
        Generate the final paper from the topics and subtopics.
        
        Args:
            topics: List of topics and subtopics
            
        Returns:
            Path to the generated final paper
        """
        logger.info("Generating final paper...")
        
        # Determine the content type based on the topics
        content_type = self._determine_content_type(topics)
        
        # Create the output directory if it doesn't exist
        ensure_directory(self.output_dir)
        
        # Path to the final paper
        final_paper_path = os.path.join(self.output_dir, "final_paper.md")
        
        # Collect all the content
        all_content = []
        references = []
        
        # Process each topic
        for topic in topics:
            topic_title = topic.get("title", "")
            subtopics = topic.get("subtopics", [])
            
            # Add the topic to the content
            all_content.append(f"# {topic_title}\n")
            
            # Process each subtopic
            for subtopic in subtopics:
                subtopic_title = subtopic.get("title", "")
                
                # Find the subtopic file path
                subtopic_file = subtopic.get("file", "")
                if not subtopic_file or not os.path.exists(subtopic_file):
                    # Try to find the file in the topics directory
                    topic_dir = os.path.join(self.output_dir, "topics", self._sanitize_filename(topic_title))
                    potential_file = os.path.join(topic_dir, f"{self._sanitize_filename(subtopic_title)}.md")
                    if os.path.exists(potential_file):
                        subtopic_file = potential_file
                        subtopic["file"] = potential_file  # Update the file path
                
                # Add the subtopic to the content
                all_content.append(f"## {subtopic_title}\n")
                
                # Read the subtopic file
                if subtopic_file and os.path.exists(subtopic_file):
                    try:
                        with open(subtopic_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Extract the content and references
                        main_content = ""
                        refs = []
                        
                        # Check if the content has a references section
                        if "## References" in content:
                            content_parts = content.split("## References")
                            main_content = content_parts[0].strip()
                            refs_part = content_parts[1].strip()
                            
                            # Extract references
                            refs_lines = refs_part.split("\n")
                            for line in refs_lines:
                                line = line.strip()
                                if line and (line.startswith("1.") or line.startswith("-") or line.startswith("*")):
                                    refs.append(line)
                        else:
                            main_content = content.strip()
                        
                        # Remove the title if it exists
                        if main_content.startswith("# "):
                            main_content_lines = main_content.split("\n")
                            if len(main_content_lines) > 1:
                                main_content = "\n".join(main_content_lines[1:])
                        
                        # Add the cleaned content
                        all_content.append(f"{main_content.strip()}\n\n")
                        
                        # Add references
                        if refs:
                            for ref in refs:
                                references.append({
                                    "topic": topic_title,
                                    "subtopic": subtopic_title,
                                    "sources": [ref]
                                })
                    except Exception as e:
                        logger.error(f"Error reading subtopic file {subtopic_file}: {str(e)}")
                        all_content.append(f"Error reading content for {subtopic_title}.\n\n")
                else:
                    logger.warning(f"Subtopic file not found for {topic_title} - {subtopic_title}")
                    all_content.append(f"Content not available for {subtopic_title}.\n\n")
            
            # Add a separator between topics
            all_content.append("\n---\n\n")
        
        # Generate conclusion with LLM and add it
        conclusion = self._generate_conclusion_with_llm(topics)
        all_content.append(conclusion + "\n\n")
        
        # Enhance the references
        try:
            enhanced_refs = self._enhance_references(references)
            
            # Check if we got valid enhanced references
            if not enhanced_refs or all(ref.startswith("API quota exhausted") or ref.startswith("Error:") for ref in enhanced_refs):
                logger.warning("Failed to enhance references. Using simple format instead.")
                # Create simple references
                enhanced_refs = []
                for ref in references:
                    topic = ref.get("topic", "")
                    subtopic = ref.get("subtopic", "")
                    sources = ref.get("sources", [])
                    for source in sources:
                        enhanced_refs.append(f"{topic} - {subtopic}: {source}")
        except Exception as e:
            logger.error(f"Error enhancing references: {str(e)}")
            # Use simple references if enhancement fails
            enhanced_refs = []
            for ref in references:
                topic = ref.get("topic", "")
                subtopic = ref.get("subtopic", "")
                sources = ref.get("sources", [])
                for source in sources:
                    enhanced_refs.append(f"{topic} - {subtopic}: {source}")
        
        # Add the references section
        all_content.append("# References\n\n")
        for ref in enhanced_refs:
            all_content.append(f"- {ref}\n")
        
        # Write the final paper in markdown format first
        try:
            with open(final_paper_path, "w", encoding="utf-8") as f:
                f.write("\n".join(all_content))
            
            logger.info(f"Initial final paper generated at: {final_paper_path}")
            
            # Optimize the final paper content with LLM if enabled
            if self.optimize_final_paper:
                try:
                    logger.info("Optimizing final paper content with LLM...")
                    
                    # Read the paper content
                    with open(final_paper_path, "r", encoding="utf-8") as f:
                        paper_content = f.read()
                    
                    # Optimize the content
                    optimized_content = self._optimize_final_paper_with_llm(paper_content)
                    
                    # Write the optimized content back to the file
                    if optimized_content:
                        with open(final_paper_path, "w", encoding="utf-8") as f:
                            f.write(optimized_content)
                        logger.info("Final paper successfully optimized")
                    else:
                        logger.warning("Failed to optimize final paper, keeping original content")
                except Exception as e:
                    logger.error(f"Error during final paper optimization: {str(e)}")
                    logger.warning("Using unoptimized final paper due to optimization error")
            else:
                logger.info("Final paper optimization skipped (disabled by user)")
            
            # Convert to the requested format if not markdown
            if self.output_format != "md":
                try:
                    from format_converter import convert_file
                    converted_path = convert_file(final_paper_path, self.output_format)
                    
                    if converted_path:
                        logger.info(f"Converted final paper to {self.output_format} format: {converted_path}")
                        return converted_path
                    else:
                        logger.error(f"Failed to convert to {self.output_format} format. Using markdown instead.")
                        return final_paper_path
                except ImportError:
                    logger.error("format_converter module not found. Using markdown format instead.")
                    return final_paper_path
            
            return final_paper_path
        except Exception as e:
            logger.error(f"Error writing final paper: {str(e)}")
            return ""
    
    def _determine_content_type(self, topics: List[Dict[str, Any]]) -> str:
        """
        Determine the content type based on the topics.
        
        Args:
            topics: List of topics and subtopics
            
        Returns:
            Content type: "practical", "travel", or "academic"
        """
        # Extract all topic titles
        topic_titles = [topic["title"].lower() for topic in topics]
        all_text = " ".join(topic_titles)
        
        # Check for practical/how-to content
        practical_keywords = ["introduction", "step", "process", "tips", "techniques", "basics", "guide", 
                             "how to", "tutorial", "instructions", "learn", "method"]
        if any(keyword in all_text for keyword in practical_keywords):
            return "practical"
            
        # Check for travel content
        travel_keywords = ["travel", "visit", "tourism", "vacation", "destination", "trip", "tour", "places", 
                          "overview", "planning", "accommodation", "attractions", "dining", "practical"]
        if any(keyword in all_text for keyword in travel_keywords):
            return "travel"
            
        # Default to academic
        return "academic"
    
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
            try:
                topic = ref.get("topic", "")
                subtopic = ref.get("subtopic", "")
                sources = ref.get("sources", [])
                pdf_files = ref.get("pdf_files", [])
                
                # If no sources, create a simple reference
                if not sources and not pdf_files:
                    enhanced_references.append(f"{topic} - {subtopic}: No sources available")
                    continue
                
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
                
                Format your response as a list of citations, one per line, with no additional commentary.
                """
                
                # Generate enhanced references using the Gemini model with extended retry
                response = self._api_call_with_retry(
                    lambda: self.model.generate_content(prompt).text,
                    max_retries=5,
                    retry_delay=5
                )
                
                # Check if we got an error message back
                if response.startswith("API quota exhausted") or response.startswith("Error:"):
                    logger.warning(f"Could not enhance references due to API limits. Using simple format instead.")
                    # Create simple references instead
                    for source in sources:
                        enhanced_references.append(f"{topic} - {subtopic}: {source}")
                    for pdf_file in pdf_files:
                        enhanced_references.append(f"{topic} - {subtopic}: {pdf_file}")
                else:
                    # Process the response
                    lines = response.strip().split("\n")
                    for line in lines:
                        if line.strip():
                            enhanced_references.append(line.strip())
            
            except Exception as e:
                logger.error(f"Error enhancing references: {str(e)}")
                # Add a simple reference in case of error
                enhanced_references.append(f"{topic} - {subtopic}: Error generating citation")
        
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
        
        # Check if topics_and_subtopics.md exists
        tracking_file = os.path.join(self.output_dir, "topics_and_subtopics.md")
        if os.path.exists(tracking_file):
            logger.info("Found existing topics_and_subtopics.md file, loading topics from it")
            self.topics = self.load_topics_from_md(tracking_file)
        else:
            # Generate topics and subtopics only if file doesn't exist
            logger.info("No existing topics file found, generating new topics")
            self.topics = self.analyze_problem_statement(problem_statement)
        
        # Update the topics tracking file (this will now skip if file exists)
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
                    
                    # Use search_phrase for search if available, otherwise use the subtopic title
                    search_title = subtopic_data.get("search_phrase", subtopic_title)
                    
                    # Construct the search query
                    search_query = f"{search_title}"
                    if self.search_suffix:
                        search_query += f" {self.search_suffix}"
                    
                    # Add site restriction if site_tld is specified
                    if self.site_tld and f"site:{self.site_tld}" not in search_query.lower():
                        search_query += f" site:{self.site_tld}"
                    
                    # Search for PDFs
                    pdf_paths = self._search_for_pdfs(search_query, search_engine)
                    
                    # Process the PDFs
                    self._process_pdfs_for_subtopic(pdf_paths, topic_title, subtopic_title)
                    
                    # Update subtopic status
                    subtopic_data["status"] = "completed"
            
            # Generate the final paper
            final_paper_path = self.generate_final_paper(self.topics)
            logger.info(f"Final paper generated at: {final_paper_path}")
            
            return final_paper_path
        
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            raise
        finally:
            # Close the browser
            self.close_browser()
    
    def _search_for_pdfs(self, query: str, search_engine: str) -> List[str]:
        """
        Search for and download PDF files related to the query.
        
        Args:
            query: The search query
            search_engine: The search engine URL to use
            
        Returns:
            List of paths to downloaded PDFs
        """
        downloaded_pdfs = []  # Initialize the list to store downloaded PDF paths
        pdf_urls = []  # Initialize the list to store found PDF URLs
        max_pages = 5  # Maximum number of search result pages to check
        
        try:
            logger.info(f"Searching for PDFs with query: {query}")
            
            # Ensure query includes PDF requirement if not already present
            if "filetype:pdf" not in query.lower():
                query = f"{query} filetype:pdf"
            
            # For DuckDuckGo, use a direct search URL approach
            if "duckduckgo.com" in search_engine:
                # Loop through multiple pages of search results
                for page_num in range(1, max_pages + 1):
                    if len(pdf_urls) >= self.max_pdfs_per_topic:
                        break
                        
                    try:
                        # Construct a direct search URL with the query
                        encoded_query = urllib.parse.quote_plus(query)
                        
                        # For the first page, use the standard URL
                        if page_num == 1:
                            direct_search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"
                        else:
                            # For subsequent pages, add the page parameter
                            offset = (page_num - 1) * 30
                            direct_search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web&s={offset}"
                        
                        logger.info(f"Navigating to DuckDuckGo search results page {page_num}: {direct_search_url}")
                        
                        # Navigate to the search URL
                        self.browser.get(direct_search_url)
                        
                        # Wait for the page to load with increased timeout
                        try:
                            WebDriverWait(self.browser, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                            )
                        except TimeoutException:
                            logger.warning(f"Timeout waiting for search results on page {page_num}")
                            continue
                        
                        # Take a screenshot for debugging
                        screenshot_path = os.path.join(self.output_dir, f"duckduckgo_search_results_page{page_num}.png")
                        self.browser.save_screenshot(screenshot_path)
                        logger.info(f"DuckDuckGo search results page {page_num} screenshot saved to {screenshot_path}")
                        
                        # Find all links using multiple selectors
                        selectors = [
                            "article a",  # Main result links
                            ".result__body a",  # Alternative result links
                            "a[href*='.pdf']",  # Direct PDF links
                            ".result__url",  # URL-only links
                            ".result__a"  # Another common result link class
                        ]
                        
                        result_links = []
                        for selector in selectors:
                            try:
                                elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                                for element in elements:
                                    href = element.get_attribute("href")
                                    if href and href not in result_links:
                                        result_links.append(href)
                            except Exception as e:
                                logger.debug(f"Error finding links with selector {selector}: {str(e)}")
                                continue
                        
                        logger.info(f"Found {len(result_links)} links on page {page_num}")
                        
                        # Process each result link
                        for url in result_links:
                            if len(pdf_urls) >= self.max_pdfs_per_topic:
                                break
                                
                            try:
                                # Skip if URL is from DuckDuckGo or is JavaScript
                                if "duckduckgo.com" in url or url.startswith("javascript:"):
                                    continue
                                    
                                # Check if it's a direct PDF link
                                if url.lower().endswith('.pdf'):
                                    if url not in pdf_urls:
                                        logger.info(f"Found direct PDF link: {url}")
                                        pdf_urls.append(url)
                                        
                                        # Download the PDF
                                        pdf_path = self._download_pdf(url)
                                        if pdf_path:
                                            downloaded_pdfs.append(pdf_path)
                                            logger.info(f"Successfully downloaded PDF: {pdf_path}")
                                    else:
                                        # Visit the link to look for PDFs
                                        logger.info(f"Checking page for PDFs: {url}")
                                        
                                        # Open in a new tab
                                        original_window = self.browser.current_window_handle
                                        self.browser.execute_script("window.open('');")
                                        self.browser.switch_to.window(self.browser.window_handles[-1])
                                        
                                        try:
                                            # Navigate to the URL with timeout
                                            self.browser.set_page_load_timeout(10)
                                            self.browser.get(url)
                                            
                                            # Look for PDF links with multiple methods
                                            pdf_selectors = [
                                                "a[href$='.pdf']",  # Links ending with .pdf
                                                "a[href*='.pdf']",  # Links containing .pdf
                                                "a[download]",  # Download links
                                                "a[type='application/pdf']"  # Links with PDF type
                                            ]
                                            
                                            for selector in pdf_selectors:
                                                pdf_elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                                                for element in pdf_elements:
                                                    pdf_url = element.get_attribute("href")
                                                    if pdf_url and pdf_url not in pdf_urls:
                                                        logger.info(f"Found PDF link on page: {pdf_url}")
                                                        pdf_urls.append(pdf_url)
                                                        
                                                        # Download the PDF
                                                        pdf_path = self._download_pdf(pdf_url)
                                                        if pdf_path:
                                                            downloaded_pdfs.append(pdf_path)
                                                            logger.info(f"Successfully downloaded PDF: {pdf_path}")
                                                            
                                                        if len(pdf_urls) >= self.max_pdfs_per_topic:
                                                            break
                                                            
                                        except Exception as e:
                                            logger.warning(f"Error checking page {url}: {str(e)}")
                                        
                                        finally:
                                            # Close the tab and switch back
                                            try:
                                                self.browser.close()
                                                self.browser.switch_to.window(original_window)
                                            except:
                                                pass
                            
                            except Exception as e:
                                logger.error(f"Error processing URL {url}: {str(e)}")
                                continue
                        
                        # Check if we need to continue to the next page
                        if len(pdf_urls) >= self.max_pdfs_per_topic:
                            logger.info(f"Found enough PDFs ({len(pdf_urls)}), stopping search")
                            break
                        
                        # Add a small delay between pages
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error with DuckDuckGo search on page {page_num}: {str(e)}")
                        continue
            
            logger.info(f"Search completed. Found {len(pdf_urls)} PDF URLs, downloaded {len(downloaded_pdfs)} PDFs")
            return downloaded_pdfs
            
        except Exception as e:
            logger.error(f"Error during PDF search: {str(e)}")
            return downloaded_pdfs
    
    def _download_pdf(self, url: str) -> str:
        """
        Download a PDF from the given URL.
        
        Args:
            url: The URL of the PDF to download
            
        Returns:
            Path to the downloaded PDF, or None if download failed
        """
        try:
            logger.info(f"Downloading PDF: {url}")
            
            # Check if the URL is valid
            if not url or not url.startswith("http"):
                logger.warning(f"Invalid URL: {url}")
                return None
            
            # Check if the URL matches the site TLD filter (if specified)
            # Only apply this filter for direct search results, not for crawled PDFs
            if self.site_tld and not url.startswith("http://localhost") and not self._is_crawled_url(url):
                # Clean the TLD (remove any dots)
                clean_tld = self.site_tld.lower().strip('.')
                
                # Extract the domain from the URL
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                
                # Check if the domain contains the TLD
                if clean_tld not in domain:
                    logger.warning(f"Skipping URL {url} - does not contain '.{clean_tld}' in domain")
                    return None
            
            # Create the PDF directory if it doesn't exist
            pdf_dir = os.path.join(self.output_dir, "pdfs")
            ensure_directory(pdf_dir)
            
            # Find the next available number for the PDF
            existing_pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf') and f[0].isdigit()]
            if existing_pdfs:
                # Extract numbers from filenames and find the highest
                numbers = [int(os.path.splitext(f)[0]) for f in existing_pdfs if os.path.splitext(f)[0].isdigit()]
                next_number = max(numbers) + 1 if numbers else 1
            else:
                next_number = 1
            
            # Create the filename with the next number
            filename = f"{next_number}.pdf"
            
            # Full path to save the PDF
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Set headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.google.com/'
            }
            
            # Try to download normally first
            try:
                # Try a regular request first
                logger.info("Attempting direct download with requests")
                response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
                
                if response.status_code == 200:
                    # Check if content is actually a PDF
                    content = response.content
                    if content.startswith(b'%PDF-'):
                        # Save the PDF
                        with open(pdf_path, "wb") as f:
                            f.write(content)
                        
                        logger.info(f"Successfully downloaded PDF to {pdf_path}")
                        return pdf_path
                    else:
                        logger.warning(f"Downloaded content is not a PDF: {url}")
                else:
                    logger.warning(f"Failed to download PDF, status code: {response.status_code}")
            except Exception as e:
                logger.warning(f"Exception during direct download: {str(e)}")
            
            # If direct download failed, try with the browser
            logger.info("Direct download failed, attempting with browser")
            try:
                # Keep track of the current window handle
                original_window = None
                if self.browser:
                    try:
                        original_window = self.browser.current_window_handle
                    except:
                        # Browser might not be initialized or have windows
                        self.start_browser()
                        original_window = self.browser.current_window_handle
                else:
                    # Start the browser if it's not running
                    self.start_browser()
                    original_window = self.browser.current_window_handle
                
                # Create a temp directory for downloads
                import tempfile
                temp_download_dir = tempfile.mkdtemp()
                
                # Set up preferences for PDF download (no PDF viewer)
                options = webdriver.ChromeOptions()
                
                # Set download preferences
                prefs = {
                    'download.default_directory': temp_download_dir,
                    'download.prompt_for_download': False,
                    'download.directory_upgrade': True,
                    'plugins.always_open_pdf_externally': True,
                    'profile.default_content_settings.popups': 0
                }
                options.add_experimental_option('prefs', prefs)
                
                # Create a new browser instance for downloading
                download_browser = webdriver.Chrome(options=options)
                
                try:
                    # Navigate to the URL
                    logger.info(f"Navigating to PDF URL: {url}")
                    download_browser.set_page_load_timeout(30)
                    download_browser.get(url)
                    
                    # Wait a bit for download to potentially start
                    time.sleep(10)
                    
                    # Check if a file was downloaded
                    downloaded_files = os.listdir(temp_download_dir)
                    
                    if downloaded_files:
                        # Get the first downloaded file
                        downloaded_file = os.path.join(temp_download_dir, downloaded_files[0])
                        
                        # Check if it's a PDF
                        with open(downloaded_file, 'rb') as f:
                            content = f.read(10)  # Just read the first few bytes
                            if content.startswith(b'%PDF-'):
                                # Move the file to the target location
                                shutil.move(downloaded_file, pdf_path)
                                logger.info(f"Successfully downloaded PDF with browser to {pdf_path}")
                                return pdf_path
                            else:
                                logger.warning(f"Downloaded file is not a PDF: {downloaded_file}")
                    else:
                        # If no file was automatically downloaded, try to find and click download buttons
                        download_buttons = []
                        
                        # Possible selectors for download buttons/links
                        download_selectors = [
                            "a[download]",
                            "a[href$='.pdf']",
                            "a[href*='download']",
                            "button:contains('Download')",
                            "a:contains('Download')",
                            ".download-button",
                            "#download",
                            "[data-testid='download']"
                        ]
                        
                        for selector in download_selectors:
                            try:
                                elements = download_browser.find_elements(By.CSS_SELECTOR, selector)
                                download_buttons.extend(elements)
                            except:
                                pass
                        
                        if download_buttons:
                            # Try clicking the first download button
                            try:
                                logger.info(f"Found {len(download_buttons)} potential download buttons, clicking first one")
                                download_buttons[0].click()
                                
                                # Wait for download
                                time.sleep(10)
                                
                                # Check again for downloaded files
                                downloaded_files = os.listdir(temp_download_dir)
                                
                                if downloaded_files:
                                    # Get the first downloaded file
                                    downloaded_file = os.path.join(temp_download_dir, downloaded_files[0])
                                    
                                    # Check if it's a PDF
                                    with open(downloaded_file, 'rb') as f:
                                        content = f.read(10)
                                        if content.startswith(b'%PDF-'):
                                            # Move the file to the target location
                                            shutil.move(downloaded_file, pdf_path)
                                            logger.info(f"Successfully downloaded PDF after clicking button to {pdf_path}")
                                            return pdf_path
                                        else:
                                            logger.warning(f"Downloaded file after clicking is not a PDF: {downloaded_file}")
                            except Exception as e:
                                logger.warning(f"Error clicking download button: {str(e)}")
                        
                        # If we still don't have a PDF, try to save the page content directly
                        try:
                            page_source = download_browser.page_source
                            
                            # Check if the page might be a PDF displayed in the browser
                            if '<embed' in page_source and 'pdf' in page_source.lower():
                                logger.info("Page appears to be a PDF viewer, saving source")
                                
                                # Save the page source
                                with open(pdf_path, 'wb') as f:
                                    f.write(page_source.encode('utf-8'))
                                
                                # Check if the saved file is a PDF
                                if self._is_pdf_content(open(pdf_path, 'rb').read()):
                                    logger.info(f"Successfully saved embedded PDF to {pdf_path}")
                                    return pdf_path
                                else:
                                    logger.warning("Saved content is not a valid PDF")
                                    os.remove(pdf_path)  # Remove the invalid file
                        except Exception as e:
                            logger.warning(f"Error saving page content as PDF: {str(e)}")
                
                finally:
                    # Close the download browser
                    try:
                        download_browser.quit()
                    except:
                        pass
                    
                    # Clean up the temp directory
                    try:
                        shutil.rmtree(temp_download_dir)
                    except:
                        pass
                    
                    # Switch back to the original window if it exists
                    if original_window:
                        try:
                            self.browser.switch_to.window(original_window)
                        except:
                            pass
                
            except Exception as e:
                logger.error(f"Error downloading PDF with browser: {str(e)}")
            
            logger.error(f"All attempts to download PDF failed: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading PDF {url}: {str(e)}")
            return None
            
    def _download_pdf_with_browser(self, url: str, pdf_path: str) -> str:
        """
        Download a PDF using the Selenium browser for cases where direct download fails.
        
        Args:
            url: The URL of the PDF to download
            pdf_path: Path where to save the PDF
            
        Returns:
            Path to the downloaded PDF, or None if download failed
        """
        try:
            logger.info(f"Attempting to download PDF with browser: {url}")
            
            # Navigate to the URL
            self.browser.get(url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Take a screenshot for debugging
            screenshot_path = os.path.join(self.output_dir, "pdf_download_attempt.png")
            self.browser.save_screenshot(screenshot_path)
            
            # Get the page source
            page_source = self.browser.page_source
            
            # Check if we're looking at a PDF in the browser
            if '<embed' in page_source and 'application/pdf' in page_source:
                logger.info("PDF detected in browser embed tag")
                
                # Try to get the PDF content directly
                pdf_content = self.browser.execute_script(
                    "return document.querySelector('embed[type=\"application/pdf\"]').src;"
                )
                
                if pdf_content and pdf_content.startswith('data:application/pdf;base64,'):
                    # Extract and decode the base64 content
                    base64_content = pdf_content.replace('data:application/pdf;base64,', '')
                    pdf_bytes = base64.b64decode(base64_content)
                    
                    # Save the PDF
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    logger.info(f"PDF downloaded successfully via browser: {pdf_path}")
                    return pdf_path
            
            # If we can't get the PDF directly, try to save the page as PDF
            try:
                # Execute JavaScript to print the page as PDF
                self.browser.execute_script('window.print();')
                time.sleep(3)  # Wait for print dialog
                
                # This won't actually save the PDF, but it's worth trying
                logger.warning("Attempted to trigger browser print dialog, but this may not work headlessly")
            except Exception as print_error:
                logger.error(f"Error triggering print: {str(print_error)}")
            
            # As a last resort, try to save the page source and convert it
            try:
                html_path = pdf_path.replace('.pdf', '.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                logger.info(f"Saved page source to {html_path}, conversion to PDF may be needed")
                
                # TODO: Implement HTML to PDF conversion if needed
            except Exception as save_error:
                logger.error(f"Error saving page source: {str(save_error)}")
            
            logger.warning(f"Could not download PDF with browser: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading PDF with browser {url}: {str(e)}")
            return None
            
    def _is_pdf_content(self, content: bytes) -> bool:
        """
        Check if the content is a PDF by looking for the PDF signature.
        
        Args:
            content: The content to check
            
        Returns:
            True if the content appears to be a PDF, False otherwise
        """
        # Check for PDF signature at the beginning of the file
        return content.startswith(b'%PDF-')
    
    def _is_crawled_url(self, url: str) -> bool:
        """
        Check if a URL was found through crawling rather than direct search.
        This is used to determine whether to apply site_tld filtering.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL was found through crawling, False otherwise
        """
        # This is a simple heuristic - we consider a URL to be crawled if it's not from a search engine
        # and not from a common academic repository
        search_engines = ['google.com', 'scholar.google', 'bing.com', 'duckduckgo.com', 'yahoo.com', 'baidu.com']
        academic_repos = ['arxiv.org', 'researchgate.net', 'academia.edu', 'ssrn.com', 'jstor.org', 'ieee.org']
        
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # If the domain is not a search engine or academic repo, it's likely from crawling
        return not any(engine in domain for engine in search_engines + academic_repos)
    
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
            
            # Determine content type based on search_purpose first, then fallback to keyword detection
            content_type = "academic"  # Default
            
            # First check the search_purpose parameter
            if self.search_purpose == "practical":
                content_type = "practical"
            elif self.search_purpose == "travel":
                content_type = "travel"
            elif self.search_purpose == "news":
                content_type = "recent_news"
            elif self.search_purpose == "general":
                content_type = "general_search"
            # Only use keyword detection if search_purpose is "academic" or not specified
            elif self.search_purpose == "academic":
                # Check for practical/how-to content
                if any(keyword in topic.lower() for keyword in ["introduction", "step", "process", "tips", "techniques", "basics", "guide"]):
                    content_type = "practical"
                    
                # Check for travel content
                elif any(keyword in topic.lower() for keyword in ["travel", "visit", "tourism", "vacation", "destination", "trip", "tour", "places", 
                                                               "overview", "planning", "accommodation", "attractions", "dining"]):
                    content_type = "travel"
                
                # Check for recent news content
                elif any(keyword in topic.lower() for keyword in ["news", "current events", "latest", "update", "recent", "breaking", "today", 
                                                               "developments", "announcement", "headlines", "trending"]):
                    content_type = "recent_news"
                    
                # Check for general search content
                elif any(keyword in topic.lower() for keyword in ["overview", "general", "information", "introduction", "basics", "fundamental", 
                                                              "summary", "explained", "101", "beginner", "comprehensive"]):
                    content_type = "general_search"
            
            # Create prompt based on content type
            if content_type == "practical":
                prompt = f"""
                Extract practical information from this document for a how-to guide on:
            
            Topic: {topic}
            Subtopic: {subtopic}
            
                Focus on instructions, tips, methods, and explanations.
                Format as a helpful guide section with clear, organized information.
                
                {'' if self.language == 'en' else f'Ensure the content is in {self.language} language.'}
                
                IMPORTANT: Your response will be directly inserted into a markdown document. DO NOT include any meta-commentary, suggestions, or notes about the content. DO NOT start with phrases like "Here's the extracted information" or "Based on the document". Just provide the actual content.
                
                Document text:
                {text}

                """
            elif content_type == "travel":
                prompt = f"""
                Extract travel information from this document for a guide about:
                
                Topic: {topic}
                Subtopic: {subtopic}
                
                Focus on travel tips, descriptions, recommendations, and practical information.
                Format as an engaging travel guide section that would help travelers.
                
                {'' if self.language == 'en' else f'Ensure the content is in {self.language} language.'}
                
                IMPORTANT: Your response will be directly inserted into a markdown document. DO NOT include any meta-commentary, suggestions, or notes about the content. DO NOT start with phrases like "Here's the extracted information" or "Based on the document". Just provide the actual content.
                
                Document text:
                {text}
                """
            elif content_type == "recent_news":
                prompt = f"""
                Extract recent news information from this document about:
                
                Topic: {topic}
                Subtopic: {subtopic}
                
                Focus on current events, recent developments, news updates, and timely information.
                Format as a concise news article with clear headline, key points, and contextual information.
                Include dates, statistics, and quotes where relevant.
                
                {'' if self.language == 'en' else f'Ensure the content is in {self.language} language.'}
                
                IMPORTANT: Your response will be directly inserted into a markdown document. DO NOT include any meta-commentary, suggestions, or notes about the content. DO NOT start with phrases like "Here's the extracted information" or "Based on the document". Just provide the actual content.
                
                Document text:
                {text}
                """
            elif content_type == "general_search":
                prompt = f"""
                Extract comprehensive information from this document about:
                
                Topic: {topic}
                Subtopic: {subtopic}
                
                Focus on providing a balanced overview with useful facts, explanations, and key information.
                Format as an informative article with clear structure and accessible language.
                Cover both basic concepts and specific details that would be valuable to someone learning about this topic.
                
                {'' if self.language == 'en' else f'Ensure the content is in {self.language} language.'}
                
                IMPORTANT: Your response will be directly inserted into a markdown document. DO NOT include any meta-commentary, suggestions, or notes about the content. DO NOT start with phrases like "Here's the extracted information" or "Based on the document". Just provide the actual content.
                
                Document text:
                {text}
                """
            else:
                prompt = f"""
                Extract relevant information from this academic paper for a research on:
                
                Topic: {topic}
                Subtopic: {subtopic}
                
                Focus on facts, data, research findings, and academic insights.
                Format as a well-structured academic section with formal language.
                Include the most important findings, methodologies, and conclusions.
                
                {'' if self.language == 'en' else f'Ensure the content is in {self.language} language.'}
                
                IMPORTANT: Your response will be directly inserted into a markdown document. DO NOT include any meta-commentary, suggestions, or notes about the content. DO NOT start with phrases like "Here's the extracted information" or "Based on the document". Just provide the actual content.
                
                Document text:
                {text}
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
            
            logger.info(f"Successfully extracted content from PDF: {os.path.basename(pdf_path)}")
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from PDF: {str(e)}")
            return None
            
    def _process_pdfs_for_subtopic(self, pdf_paths: List[str], topic: str, subtopic: str) -> None:
        """
        Process all PDFs for a subtopic, extract content from each one, and create a markdown file.
        
        Args:
            pdf_paths: List of paths to PDFs
            topic: The topic
            subtopic: The subtopic
        """
        logger.info(f"Processing {len(pdf_paths)} PDFs for subtopic: {subtopic}")
        
        # Initialize content list
        pdf_contents = []
        
        # Process each PDF one by one
        for i, pdf_path in enumerate(pdf_paths):
            try:
                logger.info(f"Extracting content from PDF {i+1}/{len(pdf_paths)}: {pdf_path}")
                content = self._extract_pdf_content(pdf_path, topic, subtopic)
                if content:
                    print(content)
                    pdf_contents.append(content)
                    logger.info(f"Successfully added content from PDF {i+1}")
                else:
                    logger.warning(f"Failed to extract content from PDF {i+1}: {pdf_path}")
            except Exception as e:
                logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        
        # Create the subtopic directory
        topic_dir = os.path.join(self.output_dir, "topics", self._sanitize_filename(topic))
        ensure_directory(topic_dir)
        
        # Create the subtopic file path
        subtopic_file = os.path.join(topic_dir, f"{self._sanitize_filename(subtopic)}.md")
        
        # Only write the file if we have content
        if pdf_contents:
            try:
                # Write the subtopic file
                with open(subtopic_file, "w", encoding="utf-8") as f:
                    # Write the title
                    f.write(f"# {subtopic}\n\n")
                    
                    # Write the content
                    for content in pdf_contents:
                        f.write(content["content"] + "\n\n")
                    
                    # Write the references
                    f.write("## References\n\n")
                    for content in pdf_contents:
                        source = content.get("source", "Unknown source")
                        f.write(f"- {source}\n")
                
                logger.info(f"WWrote subtopic file: {subtopic_file}")
            except Exception as e:
                logger.error(f"Error writing subtopic file: {str(e)}")
        else:
            # If we have no content after all retries, make one final attempt with a broader search
            logger.warning(f"No content found for {subtopic} after multiple attempts. Making final attempt.")
            
            # Try a very broad search with the topic name
            final_search_query = f"{topic} {subtopic} comprehensive information"
            final_contents = []
            
            # Try different search engines as a last resort
            for engine in ["https://www.google.com", "https://duckduckgo.com", "https://www.bing.com"]:
                if not final_contents:
                    self._extract_html_content(final_search_query, final_contents, topic, subtopic, engine)
            
            if final_contents:
                # Write the file with the content from the final attempt
                try:
                    with open(subtopic_file, "w", encoding="utf-8") as f:
                        f.write(f"# {subtopic}\n\n")
                        
                        for content in final_contents:
                            f.write(content["content"] + "\n\n")
                        
                        f.write("## References\n\n")
                        for content in final_contents:
                            source = content.get("source", "Unknown source")
                            f.write(f"- {source}\n")
                    
                    logger.info(f"Wrote subtopic file after final attempt: {subtopic_file}")
                except Exception as e:
                    logger.error(f"Error writing subtopic file after final attempt: {str(e)}")
            else:
                logger.error(f"Failed to find any content for {subtopic} after all attempts.")
                # We don't write an empty file
        
        logger.info(f"Completed processing PDFs for subtopic: {subtopic}")
        
        # Return the content for further use if needed
        return pdf_contents
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from a PDF.
        
        Args:
            pdf_content: The PDF content as bytes
            
        Returns:
            Optional[str]: The extracted text, or None if extraction failed
        """
        # First, check if the content is actually a PDF
        if not pdf_content.startswith(b'%PDF-'):
            logger.error("Content does not appear to be a valid PDF (missing PDF signature)")
            return None
            
        try:
            # Try to import PyPDF2
            import PyPDF2
            from PyPDF2 import PdfReader
            
            # Create a BytesIO object from the PDF content
            pdf_file = BytesIO(pdf_content)
            
            try:
                # Extract text with PyPDF2
                reader = PdfReader(pdf_file)
                
                # Check if the PDF is encrypted
                if reader.is_encrypted:
                    logger.warning("PDF is encrypted, attempting to decrypt with empty password")
                    try:
                        # Try with empty password first (common case)
                        reader.decrypt('')
                    except:
                        logger.error("Failed to decrypt PDF with empty password")
                        # Try alternative PDF extraction method
                        return self._extract_text_from_pdf_alternative(pdf_content)
                
                text = ""
                
                for page in reader.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                    except Exception as page_error:
                        logger.warning(f"Error extracting text from page: {str(page_error)}")
                        continue
                
                if not text.strip():
                    logger.warning("No text extracted from PDF, trying alternative method")
                    return self._extract_text_from_pdf_alternative(pdf_content)
                
                return text.strip()
                
            except PyPDF2.errors.PdfReadError as pdf_error:
                logger.error(f"PyPDF2 error: {str(pdf_error)}")
                # Try alternative PDF extraction method
                return self._extract_text_from_pdf_alternative(pdf_content)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            # Try alternative PDF extraction method as a last resort
            return self._extract_text_from_pdf_alternative(pdf_content)
            
    def _extract_text_from_pdf_alternative(self, pdf_content: bytes) -> Optional[str]:
        """
        Alternative method to extract text from a PDF when PyPDF2 fails.
        
        Args:
            pdf_content: The PDF content as bytes
            
        Returns:
            Optional[str]: The extracted text, or None if extraction failed
        """
        try:
            logger.info("Attempting alternative PDF text extraction")
            
            # Try with pdfplumber if available
            try:
                import pdfplumber
                
                with BytesIO(pdf_content) as pdf_file:
                    try:
                        with pdfplumber.open(pdf_file) as pdf:
                            text = ""
                            for page in pdf.pages:
                                try:
                                    page_text = page.extract_text()
                                    if page_text:
                                        text += page_text + "\n\n"
                                except:
                                    continue
                            
                            if text.strip():
                                logger.info("Successfully extracted text with pdfplumber")
                                return text.strip()
                    except:
                        logger.warning("pdfplumber failed to open the PDF")
            except ImportError:
                logger.warning("pdfplumber not available")
            
            # Try with pdfminer if available
            try:
                from pdfminer.high_level import extract_text_to_fp
                from pdfminer.layout import LAParams
                
                output = StringIO()
                with BytesIO(pdf_content) as pdf_file:
                    try:
                        extract_text_to_fp(pdf_file, output, laparams=LAParams(), codec='utf-8')
                        text = output.getvalue()
                        if text.strip():
                            logger.info("Successfully extracted text with pdfminer")
                            return text.strip()
                    except:
                        logger.warning("pdfminer failed to extract text")
            except ImportError:
                logger.warning("pdfminer not available")
            
            # If we get here, all extraction methods failed
            logger.error("All PDF text extraction methods failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in alternative PDF text extraction: {str(e)}")
            return None
    
    def _write_subtopic_file(self, file_path: str, topic: str, subtopic: str, contents: List[Dict[str, Any]]) -> None:
        """
        Write the contents of a subtopic to a markdown file.
        
        Args:
            file_path: Path to the markdown file
            topic: The topic title
            subtopic: The subtopic title
            contents: List of content dictionaries, each with "content" and "source" keys
        """
        try:
            # Create the markdown content
            markdown = f"# {subtopic}\n\n"
            
            # Add the content from each source
            for content in contents:
                markdown += f"{content['content']}\n\n"
            
            # Add references section
            markdown += "## References\n\n"
            
            # Add each reference
            for i, content in enumerate(contents):
                source = content.get("source", "Unknown Source")
                title = content.get("title", "")
                domain = content.get("domain", "")
                
                # Format the reference properly
                if "[HTML]" in source and domain:
                    # For HTML sources, use the domain and title
                    reference = f"{i+1}. {title} - {domain}. {source}"
                else:
                    # For PDF sources, use the source as is
                    reference = f"{i+1}. {source}"
                
                markdown += f"{reference}\n\n"
            
            # Write the markdown to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"OWrote subtopic file: {file_path}")
            print(f"LWrote subtopic file: {file_path}")

            # Add this line to call the optimization function after writing the file
            self._optimize_subtopic_content_with_llm(file_path, topic, subtopic)
            
        except Exception as e:
            logger.error(f"Error writing subtopic file: {str(e)}")
            # Create a minimal file with error information
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {subtopic}\n\nError writing content: {str(e)}\n")
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
                if line.startswith('#### '):
                    # This is a topic
                    if current_topic:
                        topics.append(current_topic)
                    
                    topic_title = line[5:].strip()
                    current_topic = {
                        "title": topic_title,
                        "subtopics": []
                    }
                elif line.startswith('- [ ]') and current_topic:
                    # This is a subtopic
                    try:
                        subtopic_data = eval(line[5:].strip())
                        if isinstance(subtopic_data, dict):
                            current_topic["subtopics"].append(subtopic_data)
                    except:
                        # If eval fails, just use the text as title
                        subtopic_title = line[5:].strip()
                        current_topic["subtopics"].append({
                            "title": subtopic_title,
                            "status": "pending",
                            "search_phrase": f"{current_topic['title']} {subtopic_title}"
                        })
            
            # Add the last topic
            if current_topic:
                topics.append(current_topic)
            
            logger.info(f"Successfully loaded {len(topics)} topics from {file_path}")
            return topics
            
        except Exception as e:
            logger.error(f"Error loading topics from markdown file: {str(e)}")
            return []

    def _crawl_for_pdfs(self, start_url: str, max_depth: int = None, max_pages: int = None) -> List[str]:
        """
        Crawl a website starting from a URL to find PDF files.
        
        Args:
            start_url: The URL to start crawling from
            max_depth: Maximum depth of crawling (default: self.crawl_depth)
            max_pages: Maximum number of pages to visit (default: self.max_crawl_pages)
            
        Returns:
            List of PDF URLs found
        """
        # Use class parameters if not specified
        if max_depth is None:
            max_depth = self.crawl_depth
        if max_pages is None:
            max_pages = self.max_crawl_pages
            
        logger.info(f"Starting web crawl from: {start_url} with max depth {max_depth}")
        
        pdf_urls = []
        visited_urls = set()
        urls_to_visit = [(start_url, 0)]  # (url, depth)
        
        while urls_to_visit and len(visited_urls) < max_pages:
            current_url, current_depth = urls_to_visit.pop(0)
            
            # Skip if already visited or exceeds max depth
            if current_url in visited_urls or current_depth > max_depth:
                continue
            
            logger.info(f"Crawling: {current_url} (depth: {current_depth})")
            
            try:
                # Mark as visited
                visited_urls.add(current_url)
                
                # Open in browser
                original_window = self.browser.current_window_handle
                self.browser.execute_script("window.open('');")
                self.browser.switch_to.window(self.browser.window_handles[1])
                
                # Navigate to the URL
                self.browser.get(current_url)
                time.sleep(3)
                
                # Find PDF links on the page
                links = self.browser.find_elements(By.TAG_NAME, "a")
                
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                            
                        # Check if it's a PDF link
                        if href.lower().endswith('.pdf'):
                            if href not in pdf_urls:
                                logger.info(f"Found PDF: {href}")
                                pdf_urls.append(href)
                        
                        # Add to visit queue if within depth limit
                        elif current_depth < max_depth:
                            # Only add links to the same domain or subdomain
                            if self._is_same_domain(start_url, href):
                                if href not in visited_urls and (href, current_depth + 1) not in urls_to_visit:
                                    urls_to_visit.append((href, current_depth + 1))
                    except Exception as e:
                        logger.warning(f"Error processing link: {str(e)}")
                
                # Close the tab and switch back
                self.browser.close()
                self.browser.switch_to.window(original_window)
                
            except Exception as e:
                logger.warning(f"Error crawling {current_url}: {str(e)}")
                # Try to close the tab and switch back if there was an error
                try:
                    self.browser.close()
                    self.browser.switch_to.window(original_window)
                except:
                    pass
        
        logger.info(f"Crawling completed. Visited {len(visited_urls)} pages, found {len(pdf_urls)} PDFs")
        return pdf_urls
    
    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs belong to the same domain or subdomain.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if same domain, False otherwise
        """
        try:
            from urllib.parse import urlparse
            
            # Parse the URLs
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)
            
            # Extract domains
            domain1 = parsed1.netloc
            domain2 = parsed2.netloc
            
            # Check if one is a subdomain of the other
            return domain1 in domain2 or domain2 in domain1
        except:
            return False

    def _extract_json_from_text(self, text: str) -> str:
        """
        Extract JSON from text that might contain additional content.
        
        Args:
            text: Text that contains JSON
            
        Returns:
            Extracted JSON string
        """
        # Try to find JSON array
        array_start = text.find('[')
        array_end = text.rfind(']') + 1
        
        if array_start >= 0 and array_end > array_start:
            return text[array_start:array_end]
        
        # If no array found, try to find JSON object
        obj_start = text.find('{')
        obj_end = text.rfind('}') + 1
        
        if obj_start >= 0 and obj_end > obj_start:
            return text[obj_start:obj_end]
        
        # If no JSON found, return the original text
        return text
    
    def _validate_topics_structure(self, topics: List[Dict[str, Any]]) -> None:
        """
        Validate the structure of topics and subtopics.
        
        Args:
            topics: List of topics to validate
            
        Raises:
            ValueError: If the structure is invalid
        """
        if not isinstance(topics, list):
            raise ValueError("Topics must be a list")
        
        for topic in topics:
            if not isinstance(topic, dict):
                raise ValueError("Each topic must be a dictionary")
            
            if "title" not in topic:
                raise ValueError("Each topic must have a title")
            
            if "subtopics" not in topic:
                raise ValueError("Each topic must have subtopics")
            
            if not isinstance(topic["subtopics"], list):
                raise ValueError("Subtopics must be a list")
            
            for subtopic in topic["subtopics"]:
                if not isinstance(subtopic, dict):
                    raise ValueError("Each subtopic must be a dictionary")
                
                if "title" not in subtopic:
                    raise ValueError("Each subtopic must have a title")

    def _download_pdfs(self, pdf_urls: List[str]) -> List[str]:
        """
        Download PDFs from the given URLs.
        
        Args:
            pdf_urls: List of PDF URLs to download
            
        Returns:
            List of paths to downloaded PDFs
        """
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
        
        return successful_downloads
        
    def _extract_html_content(self, search_query: str, content_items: List[Dict[str, Any]], topic: str, subtopic: str, search_engine: str = None, retry_count: int = 0, page_num: int = 1) -> None:
        """
        Extract content from HTML pages for a given search query.
        
        Args:
            search_query: The search query
            content_items: List to append content to
            topic: The topic title
            subtopic: The subtopic title
            search_engine: The search engine to use
            retry_count: Current retry attempt (for alternative queries)
            page_num: Current search results page number
        """
        try:
            logger.info(f"Extracting HTML content for query: {search_query}")
            logger.info(f"Max sources per topic setting: {self.max_pdfs_per_topic}")
            logger.info(f"Retry attempt: {retry_count}, Page: {page_num}")
            
            # Increase timeout for better success rate
            self.browser.set_page_load_timeout(30)  # Increased from 10 seconds
            
            # Navigate directly to the search URL with page number if needed
            if search_engine and "duckduckgo.com" in search_engine.lower():
                if page_num > 1:
                    search_url = f"https://duckduckgo.com/?q={quote_plus(search_query)}&t=h_&ia=web&s={(page_num-1)*30}"
                else:
                    search_url = f"https://duckduckgo.com/?q={quote_plus(search_query)}&t=h_&ia=web"
            else:
                if page_num > 1:
                    search_url = f"https://www.google.com/search?q={quote_plus(search_query)}&start={(page_num-1)*10}"
                else:
                    search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
            
            logger.info(f"Navigating to search engine: {search_url} (Page {page_num})")
            
            # Increase timeout to prevent premature errors
            self.browser.set_page_load_timeout(60)  # Increased to 60 seconds
            
            try:
                self.browser.get(search_url)
                
                # Wait for the search results to load
                logger.info("Waiting for search results to load...")
                
                # Try to wait for specific elements based on the search engine
                try:
                    if "google.com" in search_url:
                        # Wait for Google search results
                        WebDriverWait(self.browser, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#search"))
                        )
                    elif "duckduckgo.com" in search_url:
                        # Wait for DuckDuckGo search results
                        WebDriverWait(self.browser, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".results"))
                        )
                    elif "bing.com" in search_url:
                        # Wait for Bing search results
                        WebDriverWait(self.browser, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#b_results"))
                        )
                    else:
                        # Generic wait for any search engine
                        WebDriverWait(self.browser, 20).until(
                            EC.presence_of_element_located((By.TAG_NAME, "a"))
                        )
                    
                    logger.info("Search results page loaded successfully")
                except Exception as e:
                    logger.warning(f"Timeout waiting for search results: {str(e)}")
                    # Continue anyway as the page might still have loaded
                
                # Additional delay to make sure JavaScript has finished rendering the page
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error loading search URL: {str(e)}")
                # If there's an error, still try to take a screenshot
            
            # Take a screenshot of the search results (only small screenshot instead of full page)
            screenshot_path = os.path.join(self.output_dir, f"search_results_page{page_num}.png")
            self.browser.save_screenshot(screenshot_path)
            logger.info(f"Search results page {page_num} screenshot saved")
            
            # Wait for the page to load
            time.sleep(3)
            
            # Store the search engine domain to avoid extracting content from it
            search_engine_domain = ""
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(self.browser.current_url)
                search_engine_domain = parsed_url.netloc
                logger.info(f"Search engine domain: {search_engine_domain}")
            except Exception as e:
                logger.warning(f"Error extracting search engine domain: {str(e)}")
            
            # Define excluded domains
            excluded_domains = [
                "google.com", "duckduckgo.com", "bing.com", "yahoo.com",
                "youtube.com", "facebook.com", "twitter.com", "instagram.com",
                "linkedin.com", "pinterest.com", "reddit.com", "tiktok.com",
                "amazon.com", "ebay.com", "etsy.com", "wikipedia.org"
            ]
            
            # Add the current search engine domain to excluded domains if not already there
            if search_engine_domain and search_engine_domain not in excluded_domains:
                excluded_domains.append(search_engine_domain)
            
            # Get all result links
            html_urls = []
            
            try:
                # Use vision model to identify search result links if available
                try:
                    logger.info("Using vision model to identify search result links")
                    screenshot_path = os.path.join(self.output_dir, f"search_results_for_links_page{page_num}.png")
                    
                    # Take a regular screenshot (without trying to capture full page)
                    self.browser.save_screenshot(screenshot_path)
                    logger.info("Screenshot for link detection saved")
                    
                    # Use the vision helper to find links
                    links = find_pdf_links(screenshot_path, self.browser, is_html=True, min_results=self.minimum_pdfs, max_results=self.max_pdfs_per_topic)
                    if links and len(links) > 0:
                        # Filter out excluded domains
                        filtered_links = []
                        for url in links:
                            try:
                                parsed_url = urlparse(url)
                                domain = parsed_url.netloc
                                if not any(excluded in domain.lower() for excluded in excluded_domains):
                                    filtered_links.append(url)
                            except:
                                # If parsing fails, still include the URL
                                filtered_links.append(url)
                        
                        html_urls.extend(filtered_links)
                        logger.info(f"Found {len(filtered_links)} content links using vision model")
                except Exception as e:
                    logger.warning(f"Error using vision model to find links: {str(e)}")
                
                # Fallback to more general selectors if vision model didn't find links
                if not html_urls:
                    logger.info("Using general selectors to find links")
                    
                    # Specific selectors for Google search results (these change frequently)
                    google_selectors = [
                        "div.g div.yuRUbf > a",  # Current main result links (April 2023+)
                        "div.g .tF2Cxc > a",     # Earlier result links
                        "div.rc > a",            # Old style results
                        "div.g a[href]",         # More general approach
                        ".r a",                  # Very old style
                        "#search a[href]:not([href*='webcache']):not([href*='google.com'])",  # General results, exclude some Google links
                        "h3.LC20lb",             # Result titles (may be clickable)
                    ]
                    
                    # Specific selectors for other search engines
                    duckduckgo_selectors = [
                        ".result__a",          # Standard results
                        ".result__body a",     # Result body links
                        ".result__url",        # URL display
                        ".results_links a",    # General result links
                        "article a[href]",     # Newer results
                        "[data-testid='result-title-a']", # Latest selector (2023+)
                        ".nrn-react-div a[href]" # General app container
                    ]
                    
                    # Bing selectors
                    bing_selectors = [
                        "h2 a[href]",                  # Main result links
                        ".b_algo a[href]:not([href*='bing.com'])",  # Standard results
                        "#b_results a[href]:not([href*='bing.com'])",  # All results
                        ".b_title a"                   # Title links
                    ]
                    
                    # Choose selectors based on current URL
                    current_url = self.browser.current_url.lower()
                    if "google" in current_url:
                        current_selectors = google_selectors
                        logger.info("Using Google-specific selectors")
                    elif "duckduckgo" in current_url:
                        current_selectors = duckduckgo_selectors
                        logger.info("Using DuckDuckGo-specific selectors")
                    elif "bing" in current_url:
                        current_selectors = bing_selectors
                        logger.info("Using Bing-specific selectors")
                    else:
                        # If on an unknown search engine, try all selectors
                        current_selectors = google_selectors + duckduckgo_selectors + bing_selectors
                        logger.info("Using all available search engine selectors")
                    
                    # Try each selector and log results for debugging
                    for selector in current_selectors:
                        try:
                            logger.debug(f"Trying selector: {selector}")
                            result_links = self.browser.find_elements(By.CSS_SELECTOR, selector)
                            logger.debug(f"Found {len(result_links)} elements with selector {selector}")
                            
                            # Extract URLs from links
                            for link in result_links:
                                try:
                                    url = link.get_attribute("href")
                                    # Filter out navigation links, ads, etc.
                                    if url and url.startswith("http") and not url.endswith('.pdf'):
                                        # Check if URL contains any excluded domain
                                        parsed_url = urlparse(url)
                                        domain = parsed_url.netloc
                                        
                                        if not any(excluded in domain.lower() for excluded in excluded_domains):
                                            # Check if the link text suggests it's a content result
                                            link_text = link.text.strip()
                                            if link_text and len(link_text) > 10:  # Likely a content link if it has substantial text
                                                html_urls.append(url)
                                                logger.debug(f"Added URL: {url}")
                                except Exception as e:
                                    logger.debug(f"Error extracting URL from link: {str(e)}")
                            
                            # If we found some links, we can stop trying selectors
                            if html_urls:
                                logger.info(f"Found {len(html_urls)} links with selector: {selector}")
                                break
                                
                        except Exception as e:
                            logger.debug(f"Error using selector {selector}: {str(e)}")
                    
                    # Last resort: get ALL links on the page
                    if not html_urls:
                        logger.warning("No links found with specific selectors, trying ALL links")
                        try:
                            all_links = self.browser.find_elements(By.TAG_NAME, "a")
                            logger.info(f"Found {len(all_links)} total links on page")
                            
                            for link in all_links:
                                try:
                                    url = link.get_attribute("href")
                                    if url and url.startswith("http") and not url.endswith('.pdf'):
                                        # Take screenshot of the link for debugging
                                        try:
                                            self.browser.execute_script("arguments[0].scrollIntoView();", link)
                                            time.sleep(0.5)
                                            link_screenshot = os.path.join(self.output_dir, f"link_{len(html_urls)}.png")
                                            self.browser.save_screenshot(link_screenshot)
                                            logger.debug(f"Saved link screenshot to {link_screenshot}")
                                        except:
                                            pass
                                    
                                        # Only include links that have visible text
                                        link_text = link.text.strip()
                                        is_visible = False
                                        try:
                                            is_visible = link.is_displayed() and link_text and len(link_text) > 5
                                        except:
                                            pass
                                            
                                        if is_visible:
                                            # Skip search engine domains
                                            parsed_url = urlparse(url)
                                            domain = parsed_url.netloc
                                            if not any(excluded in domain.lower() for excluded in excluded_domains):
                                                html_urls.append(url)
                                                logger.debug(f"Added URL from all-links: {url}")
                                except Exception as e:
                                    logger.debug(f"Error processing link: {str(e)}")
                            
                            # Take first 10 URLs max from all links (they're less likely to be good results)
                            html_urls = html_urls[:10]
                            logger.info(f"Added {len(html_urls)} URLs from all links on page")
                        except Exception as e:
                            logger.error(f"Error getting all links: {str(e)}")
                
                # Filter out duplicate URLs
                html_urls = list(dict.fromkeys(html_urls))
                
                # Try to get URLs up to max_pdfs_per_topic to increase chances of finding content
                max_urls = min(self.max_pdfs_per_topic * 2, len(html_urls))
                html_urls = html_urls[:max_urls]
                
                logger.info(f"Found {len(html_urls)} HTML URLs for content extraction")
                
                # If no URLs found, try next page or alternative query
                if not html_urls:
                    if page_num < 5:  # Try up to 5 pages of search results
                        logger.info(f"No URLs found on page {page_num}. Trying next page.")
                        return self._extract_html_content(search_query, content_items, topic, subtopic, search_engine, retry_count, page_num + 1)
                    elif retry_count < 3:  # Then try alternative queries
                        # Generate alternative search query
                        alternative_query = self._generate_alternative_query(search_query, topic, subtopic, retry_count)
                        logger.info(f"No URLs found after checking {page_num} pages. Trying alternative query: {alternative_query}")
                        # Recursive call with alternative query and incremented retry count
                        return self._extract_html_content(alternative_query, content_items, topic, subtopic, search_engine, retry_count + 1, 1)
                    else:
                        logger.error("No valid web page URLs found after multiple retries. Cannot extract HTML content.")
                        return
                
                # Visit each HTML page and extract content
                successful_extractions = 0
                for i, url in enumerate(html_urls):
                    try:
                        logger.info(f"Visiting HTML page {i+1}/{len(html_urls)}: {url}")
                        
                        # Navigate to the URL with a timeout
                        try:
                            self.browser.get(url)
                        except Exception as e:
                            logger.warning(f"Timeout or error loading page {url}: {str(e)}")
                            # Try one more time with a longer timeout and disabled screenshots
                            try:
                                self.browser.set_page_load_timeout(60)  # Set a 60-second timeout
                                self.browser.get(url)
                            except:
                                logger.error(f"Failed to load page {url} after retry. Skipping.")
                                continue
                        
                        # Wait for the page to load
                        time.sleep(5)
                        
                        # Get the current URL after navigation (might be different due to redirects)
                        current_url = self.browser.current_url
                        logger.info(f"Current URL after navigation: {current_url}")
                        
                        # Check if we're still on a search engine page
                        current_domain = ""
                        try:
                            parsed_url = urlparse(current_url)
                            current_domain = parsed_url.netloc
                            logger.info(f"Current domain: {current_domain}")
                            
                            # Skip if we're on an excluded domain
                            if any(excluded in current_domain.lower() for excluded in excluded_domains):
                                logger.warning(f"Skipping content extraction from excluded domain: {current_domain}")
                                continue
                        except Exception as e:
                            logger.warning(f"Error checking current domain: {str(e)}")
                        
                        # Get the page title
                        try:
                            page_title = self.browser.title
                            logger.info(f"Page title: {page_title}")
                            
                            # Skip if the page title contains search-related terms
                            search_terms = ["search", "results", "query", "buscar", "suche", "recherche", "arama"]
                            if any(term.lower() in page_title.lower() for term in search_terms):
                                logger.warning(f"Skipping content extraction from search page: {page_title}")
                                continue
                        except Exception as e:
                            logger.warning(f"Error getting page title: {str(e)}")
                            page_title = "Web Page"
                        
                        # Take a minimal screenshot if needed (not full page)
                        screenshot_path = os.path.join(self.output_dir, f"webpage_{i+1}_page{page_num}.png")
                        self.browser.save_screenshot(screenshot_path)
                        logger.info(f"Webpage screenshot saved")
                        
                        # Get the page HTML
                        html_content = self.browser.page_source
                        
                        # Save the HTML to a temporary file
                        html_dir = os.path.join(self.output_dir, "html")
                        ensure_directory(html_dir)
                        html_file = os.path.join(html_dir, f"temp_html_{i+1}_page{page_num}.html")
                        
                        with open(html_file, "w", encoding="utf-8") as f:
                            f.write(html_content)
                        
                        logger.info(f"Extracting content from HTML file: {html_file}")
                        
                        # Extract text from HTML
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Try to get the domain for citation
                        domain = current_domain if current_domain else "website"
                        
                        # Remove script, style, nav, header, footer, and other non-content elements
                        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "noscript", "button", "input"]):
                            element.decompose()
                        
                        # Get the main content
                        main_content = ""
                        
                        # Try to find the main content area
                        main_elements = soup.select("main, article, .content, .main, #content, #main, .article, .post, .entry, .blog-post")
                        if main_elements:
                            # Use the first main content element found
                            main_content = main_elements[0].get_text(separator=' ', strip=True)
                        else:
                            # If no main content area found, use the body
                            body = soup.find('body')
                            if body:
                                main_content = body.get_text(separator=' ', strip=True)
                        
                        # Clean up the text
                        main_content = re.sub(r'\s+', ' ', main_content).strip()
                        
                        # Skip if the content is too short (likely not a content page)
                        if len(main_content) < 500:
                            logger.warning(f"Content too short ({len(main_content)} chars), likely not a content page. Skipping.")
                            continue
                        
                        # Log the character count
                        logger.info(f"Extracted {len(main_content)} characters of text from HTML")
                        
                        # Create a prompt for the Gemini model to extract relevant information
                        prompt = f"""
                        Extract ONLY information relevant to the following research topic from this web page content:
                        
                        Topic: {topic}
                        Subtopic: {subtopic}
                        
                        IMPORTANT:
                        1. ONLY extract information that is directly relevant to the topic and subtopic
                        2. IGNORE any navigation elements, advertisements, or unrelated content
                        3. Format as a well-structured academic section
                        4. Your response will be directly inserted into a markdown document
                        5. DO NOT include any meta-commentary, suggestions, or notes about the content
                        6. DO NOT start with phrases like "Here's the extracted information" or "Based on the webpage", "a resarch shows" etc.
                        7. If there is NO relevant information, respond with ONLY: "No relevant information found on this webpage."
                        8. Do not summarize the findings, just provide the information.
                        9. Do not add any other text or phrases like "Here is the information" or "Based on the webpage" etc.
                        {'' if self.language == 'en' else f'8. Ensure the text is in {self.language} language'}
                        
                        Web page content:
                        {main_content}
                        """
                        
                        # Generate content using the Gemini model
                        response = self._api_call_with_retry(
                            lambda: self.model.generate_content(prompt).text
                        )
                        
                        # Skip if no relevant information was found
                        if response.strip() == "No relevant information found on this webpage.":
                            logger.info(f"No relevant information found on webpage {i+1}")
                            continue
                        
                        # Create the content dictionary with proper source information
                        content = {
                            "source": f"[HTML] {current_url}",
                            "content": response,
                            "title": page_title,
                            "domain": domain
                        }
                        
                        # Add the content to the list
                        content_items.append(content)
                        logger.info(f"Successfully extracted content from HTML page {i+1}")
                        successful_extractions += 1
                        
                        # If we've found enough content, we can stop
                        if successful_extractions >= self.max_pdfs_per_topic:
                            logger.info(f"Found {successful_extractions} successful content extractions, which is sufficient")
                            break
                        
                    except Exception as e:
                        logger.error(f"Error extracting content from HTML page {url}: {str(e)}")
                
                # If we didn't find enough content and there are more pages to check, try the next page
                if successful_extractions == 0 and page_num < 5:
                    logger.info(f"No content extracted from page {page_num}. Trying next page.")
                    return self._extract_html_content(search_query, content_items, topic, subtopic, search_engine, retry_count, page_num + 1)
                
                # If still no content found after checking multiple pages, try alternative search query
                if successful_extractions == 0 and retry_count < 3:
                    alternative_query = self._generate_alternative_query(search_query, topic, subtopic, retry_count)
                    logger.info(f"No content extracted after checking {page_num} pages. Trying alternative query: {alternative_query}")
                    return self._extract_html_content(alternative_query, content_items, topic, subtopic, search_engine, retry_count + 1, 1)
                    
            except Exception as e:
                logger.error(f"Error finding HTML URLs: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error extracting HTML content: {str(e)}")
            
        # If we didn't find any content after all retries, log a warning
        if not content_items:
            logger.warning(f"No content extracted for query: {search_query} after {retry_count + 1} attempts and {page_num} pages")
            
        return

    def _generate_alternative_query(self, original_query: str, topic: str, subtopic: str, retry_count: int) -> str:
        """
        Generate alternative search queries when the original query doesn't yield results.
        
        Args:
            original_query: The original search query
            topic: The topic title
            subtopic: The subtopic title
            retry_count: Current retry attempt
            
        Returns:
            An alternative search query
        """
        import random
        
        # Remove any site: filters for broader results
        query_without_filters = re.sub(r'site:\S+', '', original_query).strip()
        
        if retry_count == 0:
            # First retry: Add more specific terms from the topic
            return f"{topic} {subtopic} guide information"
        elif retry_count == 1:
            # Second retry: Try synonyms and alternative phrasings
            synonyms = {
                "guide": "handbook manual instructions",
                "tips": "advice suggestions recommendations",
                "best": "top popular recommended",
                "visit": "travel explore tour",
                "information": "details facts data",
                "how to": "ways methods techniques"
            }
            
            # Replace words with synonyms if found
            for word, alternatives in synonyms.items():
                if word in query_without_filters.lower():
                    alt_words = alternatives.split()
                    return query_without_filters.lower().replace(word, random.choice(alt_words))
            
            # If no synonyms found, add "comprehensive guide"
            return f"{query_without_filters} comprehensive guide"
        else:
            # Third retry: Use a completely different approach
            return f"everything you need to know about {topic} {subtopic}"

    def _url_matches_site_tld(self, url: str) -> bool:
        """
        Check if a URL matches the site_tld restriction.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL matches the site_tld restriction or if site_tld is None, False otherwise
        """
        if not self.site_tld:
            return True
            
        try:
            # Parse the URL to get the domain
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Check if the domain ends with the site_tld
            return domain.endswith(f".{self.site_tld}")
        except Exception as e:
            logger.warning(f"Error checking if URL matches site_tld: {str(e)}")
            return False

    def _optimize_subtopic_content_with_llm(self, file_path: str, topic: str, subtopic: str) -> None:
        """
        Send subtopic content to LLM for optimization, removing redundancies and creating a coherent text.
        Then write the optimized content back to the subtopic file.
        
        Args:
            file_path: Path to the subtopic file
            topic: The main topic
            subtopic: The subtopic name
        """
        if not os.path.exists(file_path):
            logger.warning(f"Cannot optimize non-existent file: {file_path}")
            return
            
        # Read existing content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Skip if content is too short to need optimization
        if len(original_content.strip()) < 500:  # Arbitrary threshold
            logger.info(f"Content too short to optimize: {file_path}")
            return
        
        logger.info(f"Optimizing content for {topic} - {subtopic} in language: {self.language}")
        
        # Prepare prompt for LLM
        prompt = f"""
        I have a research document about "{topic}" focusing on the subtopic "{subtopic}". 
        Please optimize the following content by:
        1. Make sure you are using all the information provided in the content
        2. The result MUST be in {self.language} language. Translate all content into {self.language} language except commonly used international words.
        3. Merge repetitive informations meaningfully.
        4. Do not use your own words to explain the content, just use the information provided in the content.
        5. Don't add the irrevelant parts of the content. Every information in the content should be relevant to the topic and subtopic.
        6. Do not add any other text or phrases like "Here is the information" or "Based on the webpage" etc.
        7. Do not summarize the findings, just provide the information.
        Here is the content:
        
        {original_content}
        
        Please return only the optimized content in {self.language} language without additional explanations or in text citations. Provide the citations and references as a list at the end of the content.
        """
        
        try:
            # Call Gemini model with safer error handling
            def generate_content_wrapper():
                try:
                    response = self.model.generate_content(prompt)
                    # Check if response has the expected attributes
                    if hasattr(response, 'text'):
                        return response
                    else:
                        logger.warning(f"Unexpected response format from Gemini: {response}")
                        raise ValueError(f"Unexpected response format: {response}")
                except Exception as e:
                    logger.error(f"Error in content generation: {str(e)}")
                    raise
            
            # Use the retry mechanism with our wrapper function
            response = self._api_call_with_retry(generate_content_wrapper)
            
            if response and hasattr(response, 'text'):
                # Extract content from response
                result = response.text
                
                # Skip if the result is empty or too short
                if not result or len(result.strip()) < 200:
                    logger.warning(f"Optimization produced too short content, keeping original: {len(result) if result else 0} chars")
                    return
                
                # Write optimized content back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                    
                logger.info(f"Successfully optimized content for {topic} - {subtopic} in {self.language} language")
            else:
                logger.warning(f"Invalid response from LLM, keeping original content")
            
        except Exception as e:
            logger.error(f"Error optimizing content with LLM: {str(e)}")
            # Keep original content in case of error
            logger.info("Keeping original content due to optimization error")

    def _optimize_final_paper_with_llm(self, paper_content: str) -> str:
        """
        Optimize the final paper content using the LLM.
        Uses a progressive chunking approach to handle large documents.
        
        Args:
            paper_content: The content of the final paper
            
        Returns:
            Optimized content of the final paper
        """
        logger.info("Optimizing final paper with LLM...")
        
        # Create a backup of the original content
        backup_content = paper_content
        
        # Count initial sections to validate result later
        initial_headings = len(re.findall(r'^#+\s+.+$', paper_content, re.MULTILINE))
        initial_paragraphs = len(re.findall(r'\n\n.+', paper_content))
        logger.info(f"Initial paper has {initial_headings} headings and approximately {initial_paragraphs} paragraphs")
        
        # First try with the entire content - simpler approach is better if it works
        try:
            logger.info("Attempting to optimize entire paper as one chunk")
            optimized_content = self._try_optimize_chunk(paper_content)
            if optimized_content and self._validate_optimized_content(paper_content, optimized_content):
                logger.info("Successfully optimized entire paper as one chunk")
                return optimized_content
        except Exception as e:
            error_msg = str(e)
            if "504" in error_msg or "deadline exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.warning(f"Timeout error while optimizing entire paper: {error_msg}")
            else:
                logger.error(f"Error optimizing entire paper: {error_msg}")
        
        # Progressive chunking approach - if the entire content fails, try with increasing numbers of chunks
        # Start with 2 chunks, then 3, then 4, etc. until it works or we reach the maximum
        max_chunks = 10  # Maximum number of chunks to try
        overlap = 150    # Overlap between chunks for better continuity
        
        for num_chunks in range(2, max_chunks + 1):
            logger.info(f"Trying to optimize with {num_chunks} chunks")
            try:
                result = self._optimize_with_n_chunks(paper_content, num_chunks, overlap)
                if result and self._validate_optimized_content(paper_content, result):
                    logger.info(f"Successfully optimized paper with {num_chunks} chunks")
                    return result
            except Exception as e:
                error_msg = str(e)
                if "504" in error_msg or "deadline exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                    logger.warning(f"Timeout error while optimizing with {num_chunks} chunks: {error_msg}")
                else:
                    logger.error(f"Error optimizing with {num_chunks} chunks: {error_msg}")
                # Continue with more chunks if we hit a timeout
                continue
        
        # If all chunking attempts failed, return the original content
        logger.warning("All chunking attempts failed, returning original content")
        return backup_content
        
    def _try_optimize_chunk(self, chunk_content: str) -> Optional[str]:
        """
        Attempt to optimize a single chunk of content.
        
        Args:
            chunk_content: Content chunk to optimize
            
        Returns:
            Optimized content or None if failed
        """
        try:
            prompt = f"""
            You are an expert academic editor. Your task is to optimize and improve the following research paper:

            1. Fix any grammatical errors and improve sentence structure
            2. Enhance coherence and flow between sections
            3. Standardize formatting and ensure consistent style
            4. IMPORTANT: Remove and merge repetitive information
            5. Ensure consistent terminology and voice throughout
            6. Maintain all academic references and citations exactly as they are
            7. Preserve the original structure, headings, and section organization
            8. Ensure the content is in {self.language} language
            9. Make sure your response is COMPLETE and includes ALL the content from the original paper

            IMPORTANT: Your response should contain ONLY the revised paper text. Do not include any meta-commentary,
            explanations of changes, or notes. Your output will be directly saved as the final paper.
            Make absolutely sure that you don't truncate or cut off the paper - include the ENTIRE content including all sections.

            Here is the research paper content:
            
            {chunk_content}
            """
            
            # Call the LLM with extended retry for timeout errors
            result = self._api_call_with_retry(
                lambda: self.gemini.generate_content(prompt).text,
                max_retries=3,  # Reduce max retries per chunk, since we'll try with more chunks anyway
                retry_delay=5
            )
            
            if result:
                logger.info("Successfully optimized content chunk")
                return result
            else:
                logger.warning("Failed to optimize content chunk, result was empty")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "504" in error_msg or "deadline exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.warning(f"Timeout error while optimizing chunk: {error_msg}")
                # Re-raise timeout exceptions to trigger chunking
                raise e
            else:
                logger.error(f"Error optimizing chunk: {error_msg}")
                return None

    def _optimize_with_n_chunks(self, paper_content: str, num_chunks: int, overlap: int) -> Optional[str]:
        """
        Split content into n chunks with overlap and optimize each.
        
        Args:
            paper_content: Full paper content
            num_chunks: Number of chunks to split into
            overlap: Number of characters overlap between chunks
            
        Returns:
            Optimized combined content or None if failed
        """
        # Calculate chunk size
        total_length = len(paper_content)
        base_chunk_size = total_length // num_chunks
        
        chunks = []
        optimized_chunks = []
        
        # Create overlapping chunks with more intelligent boundaries
        for i in range(num_chunks):
            # Calculate basic start and end positions
            start = max(0, i * base_chunk_size - (overlap if i > 0 else 0))
            end = min(total_length, (i + 1) * base_chunk_size + (overlap if i < num_chunks - 1 else 0))
            
            # Adjust start to paragraph or sentence boundary if possible
            if i > 0 and start > 0:
                # Look for paragraph breaks
                paragraph_start = paper_content.rfind('\n\n', max(0, start - 200), start + 200)
                if paragraph_start != -1 and paragraph_start < start + 200:
                    start = paragraph_start + 2  # +2 to start after the \n\n
                else:
                    # Look for sentence breaks
                    for punct in ['. ', '! ', '? ']:
                        sentence_start = paper_content.rfind(punct, max(0, start - 150), start + 150)
                        if sentence_start != -1 and sentence_start < start + 150:
                            start = sentence_start + 2  # +2 to start after the punctuation and space
                            break
            
            # Adjust end to paragraph or sentence boundary if possible
            if i < num_chunks - 1 and end < total_length:
                # Look for paragraph breaks
                paragraph_end = paper_content.find('\n\n', max(0, end - 200), min(total_length, end + 200))
                if paragraph_end != -1 and paragraph_end > end - 200:
                    end = paragraph_end
                else:
                    # Look for sentence breaks
                    for punct in ['. ', '! ', '? ']:
                        sentence_end = paper_content.find(punct, max(0, end - 150), min(total_length, end + 150))
                        if sentence_end != -1 and sentence_end > end - 150:
                            end = sentence_end + 2  # +2 to include the punctuation and space
                            break
            
            chunk = paper_content[start:end]
            chunks.append({"start": start, "end": end, "content": chunk})
            logger.info(f"Chunk {i+1}: {len(chunk)} chars ({start}-{end})")
        
        # Optimize each chunk
        for i, chunk_data in enumerate(chunks):
            chunk = chunk_data["content"]
            logger.info(f"Optimizing chunk {i+1}/{num_chunks} ({len(chunk)} chars)")
            try:
                optimized = self._try_optimize_chunk(chunk)
                if optimized:
                    optimized_chunks.append({"index": i, "content": optimized, "start": chunk_data["start"], "end": chunk_data["end"]})
                else:
                    logger.warning(f"Failed to optimize chunk {i+1}, using original")
                    optimized_chunks.append({"index": i, "content": chunk, "start": chunk_data["start"], "end": chunk_data["end"]})
            except Exception as e:
                if "504" in str(e) or "deadline exceeded" in str(e).lower() or "timeout" in str(e).lower():
                    # If we get a timeout on a chunk, it's too large. Try a smaller chunk next time.
                    logger.warning(f"Timeout on chunk {i+1}, using original content")
                    optimized_chunks.append({"index": i, "content": chunk, "start": chunk_data["start"], "end": chunk_data["end"]})
                else:
                    raise e
        
        # Validate that we have all chunks
        if len(optimized_chunks) != num_chunks:
            logger.warning(f"Not all chunks were processed ({len(optimized_chunks)}/{num_chunks})")
            return None
        
        # Sort chunks by index to ensure correct order
        optimized_chunks.sort(key=lambda x: x["index"])
        
        # Combine optimized chunks, handling overlap intelligently
        final_result = []
        for i, chunk_data in enumerate(optimized_chunks):
            chunk = chunk_data["content"]
            
            if i == 0:
                # For first chunk, use the whole thing
                final_result.append(chunk)
            else:
                prev_chunk = final_result[-1]
                
                # Find a good joining point between chunks
                if len(prev_chunk) > overlap and len(chunk) > overlap:
                    # Use the last part of previous chunk and first part of current chunk to find overlap
                    prev_end = prev_chunk[-overlap*2:]  # Use twice the overlap to find better matching
                    curr_start = chunk[:overlap*2]
                    
                    # Find best join point in the overlap
                    join_point = self._find_best_join_point(prev_end, curr_start)
                    
                    # Adjust join_point to be relative to the original chunks
                    relative_join = max(0, len(prev_chunk) - 2*overlap + join_point)
                    
                    # Join at the best point
                    final_result[-1] = prev_chunk[:relative_join]
                    final_result.append(chunk)
                else:
                    # If chunks are too small for proper overlap handling, just append
                    final_result.append(chunk)
        
        combined = "".join(final_result)
        
        # Final validation to ensure we have a complete document
        if self._validate_optimized_content(paper_content, combined):
            logger.info(f"Successfully combined {num_chunks} optimized chunks ({len(combined)} chars)")
            return combined
        else:
            logger.warning("Combined content failed validation, may be incomplete")
            return None

    def _find_best_join_point(self, text1: str, text2: str) -> int:
        """Find the best point to join two overlapping text segments."""
        # Look for sentence boundaries (., !, ?)
        sentence_breaks = [i for i, char in enumerate(text1) if char in ('.', '!', '?')]
        
        if sentence_breaks:
            # Use the last sentence break
            return sentence_breaks[-1] + 1
        
        # If no sentence breaks, look for paragraph breaks
        paragraph_breaks = [i for i, char in enumerate(text1) if char == '\n']
        
        if paragraph_breaks:
            # Use the last paragraph break
            return paragraph_breaks[-1] + 1
        
        # If no good break points, use the middle
        return len(text1) // 2
        
    def cleanse_document(self, file_path: str, cleanse_strength: str = "medium") -> Optional[str]:
        """
        Cleanse a document by removing repetitive content using LLM.
        Uses a progressive chunking approach similar to paper optimization.
        
        Args:
            file_path: Path to the document to cleanse
            cleanse_strength: Strength of the cleansing process (light, medium, aggressive)
            
        Returns:
            Path to the cleansed document or None if failed
        """
        logger.info(f"Cleansing document: {file_path} with {cleanse_strength} strength")
        
        # Validate cleanse_strength parameter
        if cleanse_strength not in ["light", "medium", "aggressive"]:
            logger.warning(f"Invalid cleanse_strength '{cleanse_strength}', defaulting to 'medium'")
            cleanse_strength = "medium"
        
        try:
            # Ensure the file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
                
            # Read the file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Create a backup of the original document
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup at: {backup_path}")
            
            # Prepare prompt for LLM based on cleanse strength
            cleanse_instructions = self._get_cleanse_instructions(cleanse_strength)
            
            prompt = f"""
            You are an expert academic editor. Your task is to review and cleanse the following document:

            {cleanse_instructions}

            IMPORTANT: Focus specifically on removing repetitive content that essentially says the same thing in different words.
            This is the primary goal of this cleansing process.

            Your response should ONLY contain the cleansed document without any additional explanations.
            Don't add any notes or comments about what you changed.

            Here is the document content:
            
            {content}
            """
            
            # First try to cleanse the entire document
            try:
                logger.info("Attempting to cleanse entire document as one chunk")
                result = self._api_call_with_retry(
                    lambda: self.gemini.generate_content(prompt).text,
                    max_retries=1,
                    retry_delay=5
                )
                
                if result:
                    logger.info("Successfully cleansed document as one chunk")
                else:
                    # If result is empty, we'll try chunking
                    logger.warning("Empty result when cleansing entire document, will try chunking")
                    result = None
            except Exception as e:
                error_msg = str(e)
                if "504" in error_msg or "deadline exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                    # If we got a timeout, we'll fall through to the progressive chunking approach
                    logger.warning(f"Timeout error while cleansing entire document: {error_msg}, will try chunking")
                else:
                    logger.warning(f"Error during full document cleansing: {error_msg}")
                result = None
                
            # If cleansing the entire document failed, try progressive chunking
            if not result:
                logger.info("Trying progressive chunking approach for document cleansing")
                
                # Start with 2 chunks and increase until successful or max reached
                max_chunks = 5  # Maximum number of chunks to try
                overlap = 100   # Overlap between chunks
                
                for num_chunks in range(2, max_chunks + 1):
                    logger.info(f"Trying to cleanse with {num_chunks} chunks")
                    try:
                        result = self._cleanse_with_chunks(content, num_chunks, overlap, cleanse_strength)
                        if result:
                            logger.info(f"Successfully cleansed document with {num_chunks} chunks")
                            break
                    except Exception as e:
                        error_msg = str(e)
                        if "504" in error_msg or "deadline exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                            logger.warning(f"Timeout error while cleansing with {num_chunks} chunks: {error_msg}")
                        else:
                            logger.error(f"Error cleansing with {num_chunks} chunks: {error_msg}")
                        # Continue with more chunks if we hit a timeout
                        continue
            
            # Check if cleansing was successful
            if not result:
                logger.error("Failed to cleanse document after all attempts")
                return None
                
            # Log the difference in content length
            original_length = len(content)
            cleansed_length = len(result)
            reduction_percentage = ((original_length - cleansed_length) / original_length) * 100
            logger.info(f"Original content length: {original_length} chars")
            logger.info(f"Cleansed content length: {cleansed_length} chars")
            logger.info(f"Content reduced by {reduction_percentage:.2f}%")
                
            # Generate a filename for the cleansed document
            # Extract path components
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_root, file_ext = os.path.splitext(file_name)
            
            # Create a new filename with '_cleansed' suffix
            cleansed_name = f"{file_root}_cleansed{file_ext}"
            cleansed_path = os.path.join(file_dir, cleansed_name)
            
            # Save the cleansed content to the new file
            with open(cleansed_path, "w", encoding="utf-8") as f:
                f.write(result)
                
            logger.info(f"Document successfully cleansed: {cleansed_path}")
            return cleansed_path
            
        except Exception as e:
            logger.error(f"Error cleansing document: {str(e)}")
            return None
            
    def _get_cleanse_instructions(self, cleanse_strength: str) -> str:
        """
        Get cleanse instructions based on the requested strength.
        
        Args:
            cleanse_strength: Strength of cleansing (light, medium, aggressive)
            
        Returns:
            Formatted cleanse instructions
        """
        if cleanse_strength == "light":
            return """
            1. Remove obviously repetitive content that appears multiple times in nearly identical form
            2. Merge clearly redundant sections that cover exactly the same information
            3. Make minor adjustments to improve clarity and conciseness
            4. Ensure consistency in formatting, terminology, and style
            5. Maintain all original headings, structure, and academic references
            6. Ensure the content flows logically
            7. Ensure the content remains in the same language
            8. Be conservative in your edits - when in doubt, retain the original text
            """
        elif cleanse_strength == "aggressive":
            return """
            1. MOST IMPORTANT: Aggressively remove ALL repetitive or redundant content, even if phrased differently
            2. Merge any sections that cover similar topics or information
            3. Significantly reduce verbosity and make the text as concise as possible
            4. Rewrite sections to be much more direct and compact
            5. Maintain core headings and academic references, but simplify where possible
            6. Restructure content for maximum efficiency and clarity
            7. Ensure the content remains in the same language
            8. Focus on substantial reduction while preserving essential meaning
            """
        else:  # medium (default)
            return """
            1. MOST IMPORTANT: Remove ALL repetitive or redundant content - look for passages that say the same thing in different words
            2. Merge similar sections that cover the same information
            3. Remove unnecessary verbosity and make the text more concise
            4. Ensure consistency in formatting, terminology, and style
            5. Maintain all original headings, structure, and academic references
            6. Ensure the content flows logically and has smooth transitions
            7. Ensure the content remains in the same language
            8. Keep all essential information intact while eliminating redundancies
            """
            
    def _get_min_content_ratio(self, cleanse_strength: str) -> float:
        """
        Get minimum content ratio based on cleanse strength.
        
        Args:
            cleanse_strength: Strength of cleansing (light, medium, aggressive)
            
        Returns:
            Minimum ratio of cleansed content length to original content length
        """
        if cleanse_strength == "light":
            return 0.7  # Light cleansing should remove at most 30%
        elif cleanse_strength == "medium":
            return 0.5  # Medium cleansing can remove up to 50%
        elif cleanse_strength == "aggressive":
            return 0.3  # Aggressive cleansing can remove up to 70%
        else:
            return 0.5  # Default to medium
            
    def _cleanse_with_chunks(self, content: str, num_chunks: int, overlap: int, cleanse_strength: str = "medium") -> Optional[str]:
        """
        Cleanse document by splitting into chunks and cleansing each chunk.
        
        Args:
            content: Document content
            num_chunks: Number of chunks to split into
            overlap: Number of characters overlap between chunks
            cleanse_strength: Strength of cleansing (light, medium, aggressive)
            
        Returns:
            Cleansed combined content or None if failed
        """
        # Calculate chunk size
        total_length = len(content)
        base_chunk_size = total_length // num_chunks
        
        chunks = []
        cleansed_chunks = []
        
        # Create overlapping chunks
        for i in range(num_chunks):
            # Calculate basic start and end positions
            start = max(0, i * base_chunk_size - (overlap if i > 0 else 0))
            end = min(total_length, (i + 1) * base_chunk_size + (overlap if i < num_chunks - 1 else 0))
            
            # Adjust start to paragraph boundary if possible
            if i > 0 and start > 0:
                paragraph_start = content.rfind('\n\n', max(0, start - 200), start + 100)
                if paragraph_start != -1 and paragraph_start < start + 100:
                    start = paragraph_start + 2  # +2 to start after the \n\n
            
            # Adjust end to paragraph boundary if possible
            if i < num_chunks - 1 and end < total_length:
                paragraph_end = content.find('\n\n', max(0, end - 100), min(total_length, end + 200))
                if paragraph_end != -1 and paragraph_end > end - 100:
                    end = paragraph_end
            
            chunk = content[start:end]
            chunks.append({"start": start, "end": end, "content": chunk})
            logger.info(f"Chunk {i+1}: {len(chunk)} chars ({start}-{end})")
        
        # Cleanse each chunk
        for i, chunk_data in enumerate(chunks):
            chunk = chunk_data["content"]
            logger.info(f"Cleansing chunk {i+1}/{num_chunks} ({len(chunk)} chars)")
            
            # Get cleanse instructions based on strength
            cleanse_instructions = self._get_cleanse_instructions(cleanse_strength)
            
            prompt = f"""
            You are an expert academic editor. Your task is to review and cleanse the following document segment:

            {cleanse_instructions}

            IMPORTANT: Focus specifically on removing repetitive content that essentially says the same thing in different words.
            This is the primary goal of this cleansing process.

            Your response should ONLY contain the cleansed document segment without any additional explanations.
            Don't add any notes or comments about what you changed.

            Here is the document segment:
            
            {chunk}
            """
            
            try:
                # Call the LLM
                result = self._api_call_with_retry(
                    lambda: self.gemini.generate_content(prompt).text,
                    max_retries=2,
                    retry_delay=5
                )
                
                if result:
                    cleansed_chunks.append({"index": i, "content": result, "start": chunk_data["start"], "end": chunk_data["end"]})
                else:
                    # If cleansing failed, use the original chunk
                    logger.warning(f"Failed to cleanse chunk {i+1}, using original")
                    cleansed_chunks.append({"index": i, "content": chunk, "start": chunk_data["start"], "end": chunk_data["end"]})
            except Exception as e:
                if "504" in str(e) or "deadline exceeded" in str(e).lower() or "timeout" in str(e).lower():
                    # If we get a timeout, use the original chunk
                    logger.warning(f"Timeout on chunk {i+1}, using original content")
                    cleansed_chunks.append({"index": i, "content": chunk, "start": chunk_data["start"], "end": chunk_data["end"]})
                else:
                    raise e
        
        # Validate that we have all chunks
        if len(cleansed_chunks) != num_chunks:
            logger.warning(f"Not all chunks were processed ({len(cleansed_chunks)}/{num_chunks})")
            return None
        
        # Sort chunks by index to ensure correct order
        cleansed_chunks.sort(key=lambda x: x["index"])
        
        # Combine cleansed chunks
        final_result = []
        for i, chunk_data in enumerate(cleansed_chunks):
            chunk = chunk_data["content"]
            
            if i == 0:
                # For first chunk, use the whole thing
                final_result.append(chunk)
            else:
                prev_chunk = final_result[-1]
                
                # Find a good joining point if chunks are large enough
                if len(prev_chunk) > overlap and len(chunk) > overlap:
                    # Use the last part of previous chunk and first part of current chunk to find overlap
                    prev_end = prev_chunk[-overlap*2:] if len(prev_chunk) >= overlap*2 else prev_chunk
                    curr_start = chunk[:overlap*2] if len(chunk) >= overlap*2 else chunk
                    
                    # Find the best joining point
                    join_point = self._find_best_join_point(prev_end, curr_start)
                    
                    # Adjust join_point to be relative to the original chunks
                    relative_join = max(0, len(prev_chunk) - len(prev_end) + join_point)
                    
                    # Join at the best point
                    final_result[-1] = prev_chunk[:relative_join]
                    final_result.append(chunk)
                else:
                    # If chunks are too small for proper overlap handling, just append
                    final_result.append(chunk)
        
        combined = "".join(final_result)
        
        # Log content reduction statistics
        original_length = len(content)
        combined_length = len(combined)
        reduction_percentage = ((original_length - combined_length) / original_length) * 100
        logger.info(f"Original content length: {original_length} chars")
        logger.info(f"Combined content length: {combined_length} chars")
        logger.info(f"Content reduced by {reduction_percentage:.2f}%")
        
        return combined

    def _validate_optimized_content(self, original_content: str, optimized_content: str) -> bool:
        """
        Validate that the optimized content is complete and contains all necessary sections.
        
        Args:
            original_content: Original content
            optimized_content: Optimized content
            
        Returns:
            Whether the optimized content is valid
        """
        # Check if content is significantly shorter than original
        if len(optimized_content) < len(original_content) * 0.8:
            logger.warning(f"Optimized content is too short: {len(optimized_content)} vs {len(original_content)} chars")
            return False
            
        # Check if all main headings are preserved (approximately)
        original_headings = len(re.findall(r'^#+\s+.+$', original_content, re.MULTILINE))
        optimized_headings = len(re.findall(r'^#+\s+.+$', optimized_content, re.MULTILINE))
        
        heading_ratio = optimized_headings / original_headings if original_headings > 0 else 1
        if heading_ratio < 0.8:
            logger.warning(f"Too few headings in optimized content: {optimized_headings} vs {original_headings}")
            return False
            
        # Check for abrupt ending (text ending in the middle of a sentence)
        last_chars = optimized_content[-100:].strip()
        if last_chars and not any(last_chars.endswith(ending) for ending in ['.', '!', '?', ':', ')', ']', '}']):
            logger.warning(f"Content appears to end abruptly: '{last_chars[-50:]}'")
            return False
            
        # Check for references section
        if "# Referans" in original_content and "# Referans" not in optimized_content:
            logger.warning("References section missing from optimized content")
            return False
            
        logger.info("Optimized content validation passed")
        return True

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
    
    parser.add_argument(
        "--crawl-depth",
        type=int,
        default=3,
        help="Maximum depth for website crawling (default: 3). Higher values will crawl more pages but take longer."
    )
    
    parser.add_argument(
        "--max-crawl-pages",
        type=int,
        default=20,
        help="Maximum number of pages to visit during crawling (default: 20). Higher values will find more PDFs but take longer."
    )
    
    parser.add_argument(
        "--min-pdfs",
        type=int,
        default=3,
        help="Minimum number of PDFs required for each subtopic before stopping search (default: 3)"
    )
    
    parser.add_argument(
        "--search-purpose",
        type=str,
        default="academic",
        choices=["academic", "news", "practical", "travel", "general"],
        help="Purpose of the search (default: academic). Options: academic, news, practical, travel, general"
    )
    
    parser.add_argument(
        "--require-pdfs",
        action="store_true",
        default=True,
        help="Whether PDFs are required for the search (default: True)"
    )
    
    parser.add_argument(
        "--output-format",
        type=str,
        default="md",
        choices=["md", "pdf", "html", "epub", "docx", "txt"],
        help="Format for the final paper output (default: md). Options: md, pdf, html, epub, docx, txt"
    )
    
    parser.add_argument(
        "--no-pdfs",
        action="store_true",
        help="Set this flag to make PDFs optional (equivalent to --require-pdfs=False)"
    )
    
    parser.add_argument(
        "--optimize-final-paper",
        action="store_true",
        default=True,
        help="Whether to optimize the final paper with LLM (default: True)"
    )

    parser.add_argument(
        "--no-optimize-final-paper",
        action="store_true",
        help="Disable final paper optimization with LLM (sets --optimize-final-paper=False)"
    )
    
    parser.add_argument(
        "--optimize-only",
        type=str,
        metavar="FINAL_PAPER_PATH",
        help="Only optimize an existing final paper without conducting research (provide path to the paper)"
    )
    
    args = parser.parse_args()
    
    # Handle the --no-optimize-final-paper flag (similar to how --no-pdfs is handled)
    if args.no_optimize_final_paper:
        args.optimize_final_paper = False
    
    return args

def _optimize_existing_final_paper(paper_path: str, language: str = "en") -> str:
    """
    Optimizes an existing final paper without conducting research.
    
    Args:
        paper_path: Path to the existing final paper
        language: Language code for the output
        
    Returns:
        Path to the optimized paper
    """
    if not os.path.exists(paper_path):
        logger.error(f"Final paper not found at {paper_path}")
        return ""
        
    try:
        # Initialize LazyScholar with minimal configuration
        scholar = LazyScholar(
            output_dir=os.path.dirname(paper_path),
            language=language
        )
        
        # Read the paper content
        with open(paper_path, "r", encoding="utf-8") as f:
            paper_content = f.read()
            
        logger.info(f"Optimizing existing paper: {paper_path}")
        
        # Create a backup of the original paper
        backup_path = f"{paper_path}.bak"
        shutil.copy2(paper_path, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        
        # Optimize the content
        optimized_content = scholar._optimize_final_paper_with_llm(paper_content)
        
        # Write the optimized content back to the file
        if optimized_content:
            with open(paper_path, "w", encoding="utf-8") as f:
                f.write(optimized_content)
            logger.info(f"Paper successfully optimized: {paper_path}")
            return paper_path
        else:
            logger.error("Failed to optimize paper")
            # Restore from backup
            shutil.copy2(backup_path, paper_path)
            logger.info(f"Restored original content from backup")
            return ""
            
    except Exception as e:
        logger.error(f"Error optimizing paper: {str(e)}")
        return ""

def main():
    """Main entry point for the LazyScholar application."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Check if we only need to optimize an existing paper
        if args.optimize_only:
            logger.info("Running in optimize-only mode")
            result = _optimize_existing_final_paper(args.optimize_only, args.language)
            if result:
                logger.info("Optimization completed successfully")
                return
            else:
                logger.error("Optimization failed")
                return
        
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
        logger.info(f"Minimum PDFs per subtopic: {args.min_pdfs}")
        logger.info(f"Crawl depth: {args.crawl_depth}")
        logger.info(f"Max crawl pages: {args.max_crawl_pages}")
        logger.info(f"Search purpose: {args.search_purpose}")
        
        # Handle the --no-pdfs flag
        require_pdfs = not args.no_pdfs if args.no_pdfs else args.require_pdfs
        logger.info(f"Require PDFs: {require_pdfs}")
        logger.info(f"Output format: {args.output_format}")
        logger.info(f"Optimize final paper: {args.optimize_final_paper}")
        
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
            language=args.language,
            site_tld=args.site_tld,
            minimum_pdfs=args.min_pdfs,
            crawl_depth=args.crawl_depth,
            max_crawl_pages=args.max_crawl_pages,
            search_purpose=args.search_purpose,
            require_pdfs=require_pdfs,
            output_format=args.output_format,
            max_references_per_subtopic=args.max_references_per_subtopic,
            optimize_final_paper=args.optimize_final_paper
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
